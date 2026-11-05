"""Collect Hacker News stories and comments for the three event windows.

Source: the free HN Algolia search API (https://hn.algolia.com/api). No key needed.
Uses the same windows and keyword rules as the Reddit corpus
(planning/event-corpus-plan.md, data/README.md):

  - all windows: "AI" and "artificial intelligence"
  - after windows ("immediate", "long") also: the event name

Algolia returns at most 1,000 hits per query, so any time range with more
hits is split in half until each piece fits.

Algolia's matching is case-insensitive, so the API results are an upper
bound, just like Arctic Shift. Each row gets a `match` column from the plan's
filtering rule: case-sensitive whole-word "AI", "artificial intelligence"
(any case), or the event name (any case). Rows with an empty `match` are
false hits and should be dropped before analysis.

Usage (stdlib only, run from the repo root):
    python3 data/scripts/collect_hn.py --counts            # hit counts only, fast
    python3 data/scripts/collect_hn.py                     # full download
    python3 data/scripts/collect_hn.py --event AlphaGo --window immediate

Output: data/hn/<event>_<window>.csv (one row per story or comment)
and data/hn/counts.csv.
"""
import argparse, csv, datetime as dt, html, json, pathlib, re, sys, time, urllib.parse, urllib.request

API = "https://hn.algolia.com/api/v1/search_by_date"
WINDOWS = {
    "AlphaGo":  {"before": ("2015-12-09", "2016-03-09"), "immediate": ("2016-03-09", "2016-06-09"), "long": ("2017-03-09", "2017-06-09")},
    "ChatGPT":  {"before": ("2022-08-30", "2022-11-30"), "immediate": ("2022-11-30", "2023-03-01"), "long": ("2023-11-30", "2024-03-01")},
    "DeepSeek": {"before": ("2024-10-20", "2025-01-20"), "immediate": ("2025-01-20", "2025-04-20"), "long": ("2026-01-20", "2026-04-20")},
}
BASE_TERMS = ["AI", "artificial intelligence"]
MAX_HITS = 1000
PAUSE = 0.4  # seconds between requests; Algolia's public limit is ~10,000/hour
FIELDS = ["objectID", "type", "created_at", "author", "points", "num_comments",
          "story_id", "parent_id", "title", "url", "text", "terms_queried", "match"]


def epoch(day):
    return int(dt.datetime.fromisoformat(day).replace(tzinfo=dt.timezone.utc).timestamp())


def terms_for(event, window):
    return BASE_TERMS + ([event] if window != "before" else [])


def fetch(params, tries=4):
    url = API + "?" + urllib.parse.urlencode(params)
    for i in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                time.sleep(PAUSE)
                return json.load(r)
        except Exception as e:  # network hiccup or rate limit: back off and retry
            if i == tries - 1:
                raise
            print(f"  retry after error: {e}", file=sys.stderr)
            time.sleep(2 ** (i + 1))


def params(term, tag, a, b, page=0, per_page=0):
    return {
        "query": f'"{term}"' if " " in term else term,
        "tags": tag,
        "numericFilters": f"created_at_i>={a},created_at_i<{b}",
        "typoTolerance": "false",
        "queryType": "prefixNone",   # stop "AI" matching "aim", "air", ...
        "hitsPerPage": per_page,
        "page": page,
    }


def count(term, tag, a, b):
    return fetch(params(term, tag, a, b))["nbHits"]


def collect_range(term, tag, a, b):
    """Yield every hit in [a, b), splitting the range while it has > MAX_HITS."""
    n = count(term, tag, a, b)
    if n == 0:
        return
    if n > MAX_HITS and b - a > 60:
        mid = (a + b) // 2
        yield from collect_range(term, tag, a, mid)
        yield from collect_range(term, tag, mid, b)
        return
    page = 0
    while True:
        res = fetch(params(term, tag, a, b, page=page, per_page=MAX_HITS))
        yield from res["hits"]
        page += 1
        if page >= res.get("nbPages", 0):
            break


def clean(s):
    s = html.unescape(re.sub(r"<[^>]+>", " ", s or ""))
    return re.sub(r"\s+", " ", s).strip()


def match_rule(text, event, window):
    found = []
    if re.search(r"\bAI\b", text):
        found.append("AI")
    if re.search(r"artificial intelligence", text, re.I):
        found.append("artificial intelligence")
    if window != "before" and re.search(re.escape(event), text, re.I):
        found.append(event)
    return ";".join(found)


def row(hit, terms, event, window):
    is_story = "story" in hit.get("_tags", [])
    title = clean(hit.get("title") or hit.get("story_title")) if is_story else ""
    text = clean(hit.get("story_text") if is_story else hit.get("comment_text"))
    return {
        "objectID": hit["objectID"],
        "type": "story" if is_story else "comment",
        "created_at": hit.get("created_at"),
        "author": hit.get("author"),
        "points": hit.get("points"),
        "num_comments": hit.get("num_comments"),
        "story_id": hit.get("story_id"),
        "parent_id": hit.get("parent_id"),
        "title": title,
        "url": hit.get("url") or "",
        "text": text,
        "terms_queried": ";".join(sorted(terms)),
        "match": match_rule(f"{title} {text}", event, window),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", action="store_true", help="only report hit counts")
    ap.add_argument("--event", choices=WINDOWS)
    ap.add_argument("--window", choices=["before", "immediate", "long"])
    ap.add_argument("--out", default="data/hn")
    args = ap.parse_args()
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    counts = []
    for event, wins in WINDOWS.items():
        if args.event and event != args.event:
            continue
        for window, (start, end) in wins.items():
            if args.window and window != args.window:
                continue
            a, b = epoch(start), epoch(end)
            print(f"{event} {window} {start}..{end}", file=sys.stderr)
            rows = {}
            for tag in ("story", "comment"):
                for term in terms_for(event, window):
                    n = count(term, tag, a, b)
                    counts.append({"event": event, "window": window, "start": start, "end_exclusive": end,
                                   "type": tag, "term": term, "api_hits": n})
                    print(f"  {tag:7} {term!r}: {n}", file=sys.stderr)
                    if args.counts:
                        continue
                    for hit in collect_range(term, tag, a, b):
                        r = rows.get(hit["objectID"])
                        if r:  # same item found by another term
                            r["terms_queried"] = ";".join(sorted(set(r["terms_queried"].split(";")) | {term}))
                        else:
                            rows[hit["objectID"]] = row(hit, [term], event, window)
            if not args.counts:
                path = out / f"{event}_{window}.csv"
                with path.open("w", newline="", encoding="utf-8") as f:
                    w = csv.DictWriter(f, fieldnames=FIELDS)
                    w.writeheader()
                    w.writerows(sorted(rows.values(), key=lambda r: r["created_at"] or ""))
                kept = sum(1 for r in rows.values() if r["match"])
                print(f"  wrote {len(rows)} items ({kept} pass the filter) to {path}", file=sys.stderr)

    with (out / "counts.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event", "window", "start", "end_exclusive", "type", "term", "api_hits"])
        w.writeheader()
        w.writerows(counts)


if __name__ == "__main__":
    main()
