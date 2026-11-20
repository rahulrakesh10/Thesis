"""Language tables for the event corpora: term frequencies, n-grams, keyword in context.

Descriptive tables only; no interpretation, no sentiment, no keyness scores.

Text used: posts = title + selftext; comments = body (if --comments is given).
"[removed]" / "[deleted]" text and URLs are dropped. Tokens are lowercased; stopwords
come from stopwords.txt (one file, applied the same way to all events). Use
--keep-stopwords to switch that off.

Outputs (in --out, default ./exploration/language/):
  corpus_stats.csv  event, window, subreddit, source, docs, docs_with_text, tokens,
                    types, mean_tokens_per_doc
  unigrams.csv      event, window, subreddit, source, term, count, doc_freq, per_10k_tokens, rank
                    (per_10k_tokens divides by the group's non-stopword token count, for n-grams too)
  bigrams.csv       same columns, term = "w1 w2"
  trigrams.csv      same columns, term = "w1 w2 w3"
  kwic.csv          keyword-in-context lines for the --kwic terms (default: case-sensitive
                    "AI" and "artificial intelligence"): event, window, subreddit, source,
                    id, date, keyword, left, match, right

subreddit = ALL pools all subreddits. Only the --top most frequent terms per group are kept
(default 200; 0 = all). n-grams do not cross sentence punctuation; stopwords are removed
before unigram counts only, and n-grams are kept unless every word is a stopword.

Example:
  python3 explore_language.py ../../sample_*.csv
  python3 explore_language.py corpus/ --comments comments/ --top 500
"""
import argparse, collections, pathlib, re
from corpus_io import (clean_text, group_keys, post_text, read_rows, sort_key, tokenize, utc, write_csv)

HERE = pathlib.Path(__file__).resolve().parent
SENT_SPLIT = re.compile(r"[.!?;:()\[\]\"\n]+")


def load_stopwords(path):
    words = set()
    for line in pathlib.Path(path).read_text(encoding="utf-8").splitlines():
        if not line.startswith("#"):
            words.update(line.split())
    return words


def ngrams(text, n, stop):
    out = []
    for chunk in SENT_SPLIT.split(text):
        toks = tokenize(chunk)
        for i in range(len(toks) - n + 1):
            g = toks[i:i + n]
            if not all(t in stop for t in g):
                out.append(" ".join(g))
    return out


def kwic(text, patterns, width):
    for label, rx in patterns:
        for m in rx.finditer(text):
            left = text[max(0, m.start() - width):m.start()].replace("\n", " ")
            right = text[m.end():m.end() + width].replace("\n", " ")
            yield label, left, m.group(0), right


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("posts", nargs="+")
    ap.add_argument("--comments", nargs="*", default=[])
    ap.add_argument("--out", default="exploration/language")
    ap.add_argument("--top", type=int, default=200)
    ap.add_argument("--stopwords", default=str(HERE / "stopwords.txt"))
    ap.add_argument("--keep-stopwords", action="store_true")
    ap.add_argument("--kwic", nargs="*", default=[r"\bAI\b", r"(?i)\bartificial intelligence\b"],
                    help="regexes for keyword in context (case-sensitive unless (?i) is used)")
    ap.add_argument("--kwic-width", type=int, default=60)
    a = ap.parse_args()

    stop = set() if a.keep_stopwords else load_stopwords(a.stopwords)
    pats = [(p, re.compile(p)) for p in a.kwic]
    docs = [("posts", r, post_text(r)) for r in read_rows(a.posts)]
    docs += [("comments", r, clean_text(r.get("body"))) for r in read_rows(a.comments)]

    counts = {n: collections.defaultdict(collections.Counter) for n in (1, 2, 3)}
    dfreq = {n: collections.defaultdict(collections.Counter) for n in (1, 2, 3)}
    stats = collections.defaultdict(lambda: [0, 0, 0, set()])
    kw_rows = []
    for source, r, text in docs:
        toks = [t for t in tokenize(text) if t not in stop]
        grams = {1: toks, 2: ngrams(text, 2, stop), 3: ngrams(text, 3, stop)}
        for ev, win, sub in group_keys(r):
            k = (ev, win, sub, source)
            s = stats[k]
            s[0] += 1
            s[1] += bool(text)
            s[2] += len(toks)
            s[3].update(toks)
            for n, g in grams.items():
                counts[n][k].update(g)
                dfreq[n][k].update(set(g))
        for label, left, match, right in kwic(text, pats, a.kwic_width):
            kw_rows.append([r["event"], r["window"], r["subreddit"], source, r.get("id"), utc(r).date().isoformat(),
                            label, left, match, right])

    stat_rows = [list(k) + [s[0], s[1], s[2], len(s[3]), round(s[2] / s[0], 2) if s[0] else 0]
                 for k, s in sorted(stats.items(), key=lambda kv: sort_key(kv[0]))]
    write_csv(f"{a.out}/corpus_stats.csv", ["event", "window", "subreddit", "source", "docs", "docs_with_text", "tokens",
                                             "types", "mean_tokens_per_doc"], stat_rows)
    for n, name in ((1, "unigrams"), (2, "bigrams"), (3, "trigrams")):
        rows = []
        for k in sorted(counts[n], key=sort_key):
            total = stats[k][2] or 1
            items = counts[n][k].most_common(a.top or None)
            for rank, (term, c) in enumerate(items, 1):
                rows.append(list(k) + [term, c, dfreq[n][k][term], round(c * 10000 / total, 2), rank])
        write_csv(f"{a.out}/{name}.csv", ["event", "window", "subreddit", "source", "term", "count", "doc_freq",
                                          "per_10k_tokens", "rank"], rows)
    write_csv(f"{a.out}/kwic.csv", ["event", "window", "subreddit", "source", "id", "date", "keyword", "left", "match", "right"],
              sorted(kw_rows, key=sort_key))


if __name__ == "__main__":
    main()
