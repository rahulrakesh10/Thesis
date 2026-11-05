"""Download the comments (and post authors) for posts already in the corpus, from Arctic Shift.

Run this on a machine that can reach arctic-shift.photon-reddit.com (Rahul's Mac; the
cloud environment blocks it). It adds what explore_networks.py needs for reply networks
and what explore_temporal.py / explore_language.py can use for comments.

Input: the corpus posts CSV(s), e.g. sample_AlphaGo.csv (column `id` = post id).
Output (in --out, default ./comments/):
  posts_with_authors.csv  event, window, subreddit, id, author, created_utc, num_comments
  comments.csv            event, window, subreddit, id, link_id, parent_id, author,
                          created_utc, score, body
  errors.csv              post id, step, error  (missing is NOT zero comments)

Resumable: posts whose comments are already in comments.csv are skipped. Comments are
paged by created_utc in ascending order, 100 per request (the API maximum). Use
--max-per-post to cap very large threads (0 = no cap). Standard library only.

Example:
  python3 fetch_comments.py ~/thesis-data/sample/sample_*.csv --out ~/thesis-data/comments
"""
import argparse, csv, json, os, pathlib, sys, time, urllib.error, urllib.parse, urllib.request
from corpus_io import read_rows

API = os.environ.get("ARCTIC_SHIFT_API", "https://arctic-shift.photon-reddit.com/api")
UA = "uwo-thesis-fetch-comments/0.1"
C_HEAD = ["event", "window", "subreddit", "id", "link_id", "parent_id", "author", "created_utc", "score", "body"]
P_HEAD = ["event", "window", "subreddit", "id", "author", "created_utc", "num_comments"]


def get(path, params, tries=5, pause=1.0):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.load(r)
            if isinstance(data, dict) and data.get("error"):
                err = str(data["error"])[:200]
            else:
                time.sleep(pause)
                return data, None
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"
            if e.code == 429:
                wait = int(e.headers.get("X-RateLimit-Reset", "60") or 60)
                print(f"  rate limited, waiting {wait}s", flush=True)
                time.sleep(wait + 1)
                continue
        except Exception as e:  # timeouts, resets
            err = repr(e)[:200]
        time.sleep(2 ** i)
    return None, err


def appender(path, header):
    new = not path.exists() or path.stat().st_size == 0
    fh = open(path, "a", newline="", encoding="utf-8")
    w = csv.writer(fh)
    if new:
        w.writerow(header)
    return fh, w


def done_ids(path, col):
    if not path.exists():
        return set()
    with open(path, newline="", encoding="utf-8") as fh:
        return {r[col] for r in csv.DictReader(fh)}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--out", default="comments")
    ap.add_argument("--max-per-post", type=int, default=0)
    ap.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    a = ap.parse_args()

    out = pathlib.Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    posts = {r["id"]: r for r in read_rows(a.posts)}
    print(f"{len(posts)} posts")

    # 1. post authors, 100 ids per request
    have = done_ids(out / "posts_with_authors.csv", "id")
    todo = [i for i in posts if i not in have]
    pf, pw = appender(out / "posts_with_authors.csv", P_HEAD)
    ef, ew = appender(out / "errors.csv", ["post_id", "step", "error"])
    for i in range(0, len(todo), 100):
        chunk = todo[i:i + 100]
        data, err = get("posts/ids", {"ids": ",".join(chunk), "fields": "id,author,created_utc,num_comments"}, pause=a.pause)
        if err:
            for pid in chunk:
                ew.writerow([pid, "post_author", err])
            continue
        for d in data.get("data", []):
            p = posts.get(d.get("id"))
            if p:
                pw.writerow([p["event"], p["window"], p["subreddit"], d["id"], d.get("author"), d.get("created_utc"), d.get("num_comments")])
        pf.flush()
    print("post authors done")

    # 2. comments per post
    have = done_ids(out / "comments.csv", "link_id")
    cf, cw = appender(out / "comments.csv", C_HEAD)
    for n, (pid, p) in enumerate(posts.items(), 1):
        if "t3_" + pid in have or int(float(p.get("num_comments") or 0)) == 0:
            continue
        after, got, rows = None, 0, []
        while True:
            params = {"link_id": pid, "limit": 100, "sort": "asc",
                      "fields": "id,link_id,parent_id,author,created_utc,score,body"}
            if after is not None:
                params["after"] = after
            data, err = get("comments/search", params, pause=a.pause)
            if err:
                ew.writerow([pid, "comments", err]); ef.flush()
                rows = None
                break
            batch = data.get("data", [])
            for c in batch:
                rows.append([p["event"], p["window"], p["subreddit"], c.get("id"), c.get("link_id") or "t3_" + pid,
                             c.get("parent_id"), c.get("author"), c.get("created_utc"), c.get("score"), c.get("body")])
            got += len(batch)
            if len(batch) < 100 or (a.max_per_post and got >= a.max_per_post):
                break
            last = batch[-1].get("created_utc")
            if last is None or last == after:
                break
            after = last  # 'after' is exclusive; ties at the same second may be missed (rare)
        if rows is not None:  # write a post's comments only when every page succeeded
            cw.writerows(rows); cf.flush()
        if n % 25 == 0:
            print(f"  {n}/{len(posts)} posts", flush=True)
    for fh in (pf, ef, cf):
        fh.close()
    print("done")


if __name__ == "__main__":
    sys.exit(main())
