"""Network edge lists for the event corpora, in Gephi-ready CSV (Source, Target, Weight).

Descriptive tables only; no community detection, centrality or interpretation.
Open a pair in Gephi with File > Import spreadsheet (nodes first, then edges).

Networks, one pair of files per event x window (subreddits pooled):
  1. term_cooc   undirected: two terms are linked when they appear in the same post
                 (title + selftext; comments too if --comments). Weight = number of
                 documents with both. Only the --terms most frequent non-stopword terms
                 per event x window are used, and edges with Weight < --min-cooc are dropped.
  2. sub_domain  undirected, bipartite: subreddit <-> linked web domain (link posts only;
                 self posts and reddit/imgur/redd.it hosts are skipped). Weight = posts.
  3. reply       directed, only with --comments: comment author -> author of the post or
                 comment they replied to. Weight = replies. Deleted authors and
                 AutoModerator are dropped; self-replies are kept and flagged in nodes.
                 Needs post authors (posts CSV 'author' column, or the posts file written by
                 fetch_comments.py) for replies to the top-level post.
  4. user_sub    undirected, bipartite, only with --comments: author <-> subreddit.
                 Weight = comments + posts by that author in that subreddit.

Files (in --out, default ./exploration/networks/):
  <network>_<event>_<window>_edges.csv  Source, Target, Weight, Type
  <network>_<event>_<window>_nodes.csv  Id, Label, kind, count
  networks_summary.csv                 network, event, window, nodes, edges, total_weight

Example:
  python3 explore_networks.py ../../sample_*.csv
  python3 explore_networks.py corpus/ comments/posts_with_authors.csv --comments comments/
"""
import argparse, collections, itertools, pathlib, urllib.parse
from corpus_io import (DELETED_AUTHORS, WINDOW_ORDER, clean_text, post_text, read_rows, tokenize, write_csv)
from explore_language import HERE, load_stopwords

SKIP_HOSTS = ("reddit.com", "redd.it", "imgur.com", "reddituploads.com")


def domain(url):
    host = urllib.parse.urlparse(url or "").netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    if not host or any(host == h or host.endswith("." + h) for h in SKIP_HOSTS):
        return None
    return host


def write_net(out, name, ev, win, edges, nodes, directed, summary):
    t = "Directed" if directed else "Undirected"
    erows = [[s, d, w, t] for (s, d), w in sorted(edges.items(), key=lambda kv: (-kv[1], kv[0]))]
    nrows = [[n, n, kind, c] for n, (kind, c) in sorted(nodes.items())]
    if not erows:
        return
    write_csv(f"{out}/{name}_{ev}_{win}_edges.csv", ["Source", "Target", "Weight", "Type"], erows)
    write_csv(f"{out}/{name}_{ev}_{win}_nodes.csv", ["Id", "Label", "kind", "count"], nrows)
    summary.append([name, ev, win, len(nrows), len(erows), sum(edges.values())])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--comments", nargs="*", default=[])
    ap.add_argument("--out", default="exploration/networks")
    ap.add_argument("--terms", type=int, default=100)
    ap.add_argument("--min-cooc", type=int, default=2)
    ap.add_argument("--stopwords", default=str(HERE / "stopwords.txt"))
    a = ap.parse_args()

    stop = load_stopwords(a.stopwords)
    posts = read_rows(a.posts)
    # de-duplicate posts by id (a posts file from fetch_comments.py may repeat the corpus)
    by_id = {}
    for r in posts:
        prev = by_id.get(r["id"], {})
        by_id[r["id"]] = {**prev, **{k: v for k, v in r.items() if v not in (None, "")}}
    posts = list(by_id.values())
    comments = read_rows(a.comments)
    groups = sorted({(r["event"], r["window"]) for r in posts + comments},
                    key=lambda k: (k[0], WINDOW_ORDER.index(k[1]) if k[1] in WINDOW_ORDER else 9))
    summary = []

    for ev, win in groups:
        gp = [r for r in posts if (r["event"], r["window"]) == (ev, win)]
        gc = [r for r in comments if (r["event"], r["window"]) == (ev, win)]

        # 1. term co-occurrence
        docs = [set(t for t in tokenize(post_text(r)) if t not in stop and len(t) > 1) for r in gp]
        docs += [set(t for t in tokenize(clean_text(r.get("body"))) if t not in stop and len(t) > 1) for r in gc]
        df = collections.Counter(t for d in docs for t in d)
        keep = {t for t, _ in df.most_common(a.terms)}
        edges = collections.Counter()
        for d in docs:
            for s, t in itertools.combinations(sorted(d & keep), 2):
                edges[(s, t)] += 1
        edges = collections.Counter({k: v for k, v in edges.items() if v >= a.min_cooc})
        used = {n for e in edges for n in e}
        write_net(a.out, "term_cooc", ev, win, edges, {t: ("term", df[t]) for t in used}, False, summary)

        # 2. subreddit <-> domain
        edges, nodes = collections.Counter(), {}
        for r in gp:
            dom = domain(r.get("url"))
            if dom:
                edges[("r/" + r["subreddit"], dom)] += 1
        for (s, d), w in edges.items():
            nodes[s] = ("subreddit", nodes.get(s, ("", 0))[1] + w)
            nodes[d] = ("domain", nodes.get(d, ("", 0))[1] + w)
        write_net(a.out, "sub_domain", ev, win, edges, nodes, False, summary)

        if not gc:
            continue
        # 3. reply network
        author_of = {"t3_" + r["id"]: r.get("author") for r in posts}
        author_of.update({"t1_" + r["id"]: r.get("author") for r in comments})
        edges, activity, self_replies = collections.Counter(), collections.Counter(), collections.Counter()
        for r in gc:
            src, dst = r.get("author"), author_of.get(r.get("parent_id"))
            if src in DELETED_AUTHORS:
                continue
            activity[src] += 1
            if dst in DELETED_AUTHORS:
                continue
            edges[(src, dst)] += 1
            if src == dst:
                self_replies[src] += 1
        nodes = {n: ("user_self_replies" if self_replies[n] else "user", activity[n]) for e in edges for n in e}
        write_net(a.out, "reply", ev, win, edges, nodes, True, summary)

        # 4. user <-> subreddit
        edges, nodes = collections.Counter(), {}
        for r in gp + gc:
            u = r.get("author")
            if u in DELETED_AUTHORS:
                continue
            edges[("u/" + u, "r/" + r["subreddit"])] += 1
        for (u, s), w in edges.items():
            nodes[u] = ("user", nodes.get(u, ("", 0))[1] + w)
            nodes[s] = ("subreddit", nodes.get(s, ("", 0))[1] + w)
        write_net(a.out, "user_sub", ev, win, edges, nodes, False, summary)

    write_csv(f"{a.out}/networks_summary.csv", ["network", "event", "window", "nodes", "edges", "total_weight"], summary)


if __name__ == "__main__":
    main()
