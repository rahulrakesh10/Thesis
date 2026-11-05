"""Monthly "AI" / "artificial intelligence" frequencies on Reddit, 2010 onwards.

Purpose: a keyword time series that is independent of the three chosen events
(AlphaGo, ChatGPT, DeepSeek), so peaks can be looked for without starting from
the event list. Counts only; no post or comment text is downloaded.

Why it is per subreddit: Arctic Shift's keyword search (title / query / body)
only works together with a `subreddit` (or `author`) filter, so there is no
Reddit-wide keyword count. The script therefore counts keyword hits in a list
of subreddits, and also saves Reddit-wide and per-subreddit unfiltered totals
so counts can later be divided by overall activity.

Subreddit list (column `group` says where each one came from):
  - largest:  the N largest non-NSFW subreddits by subscribers (default 100),
              a selection that does not depend on AI at all
  - corpus:   the 13 subreddits already in planning/event-corpus-plan.md
  - extra:    anything passed with --add (e.g. AI-specific subreddits)

Output files (in --out, default ./ai_keyword_timeseries/):
  subreddits.csv      subreddit, group, subscribers (as of the API's last update)
  keyword_monthly.csv subreddit, kind, field, term, month, count
                      kind = posts | comments; field = title | query (title+selftext) | body
  totals_monthly.csv  scope (global or subreddit name), kind, month, count  (no keyword filter)
  errors.csv          every request that still failed after retries

The run is resumable: rows already in keyword_monthly.csv / totals_monthly.csv
are skipped on restart. Standard library only (Python 3.8+).

Example:
  python3 ai_keyword_timeseries.py --top 100 --add OpenAI ChatGPTPro StableDiffusion
  python3 ai_keyword_timeseries.py --only-subs technology Futurology   # quick test

Caveats (also in data/README.md):
  - Keyword search is word-based and NOT case-sensitive, so "AI" also counts "ai"
    (e.g. Portuguese/Japanese words, names). Counts are upper bounds.
  - '"artificial intelligence"' is sent as a quoted phrase. For comments this is a
    Postgres phrase search; for posts the API docs say only simple keyword search
    is used, so posts may count title/text with both words anywhere.
  - Very large subreddits often time out on keyword searches, comments most of all.
    The script splits failed years into months; months that still fail go to errors.csv
    and are missing from keyword_monthly.csv (missing is NOT zero).
  - Months with no matches are not returned by the API; the script writes them as 0
    only when the request for that period succeeded.
"""
import argparse, csv, datetime as dt, json, os, sys, time, urllib.error, urllib.parse, urllib.request

API = os.environ.get("ARCTIC_SHIFT_API", "https://arctic-shift.photon-reddit.com/api")
UA = "uwo-thesis-keyword-timeseries/0.1"
TERMS = ["AI", '"artificial intelligence"']
# (kind, field): posts by title, posts by title+selftext, comments by body
SEARCHES = [("posts", "title"), ("posts", "query"), ("comments", "body")]
CORPUS = ["technology", "Futurology", "singularity", "artificial", "MachineLearning",
          "baduk", "compsci", "programming", "cscareerquestions", "Teachers", "ChatGPT",
          "LocalLLaMA", "stocks", "wallstreetbets"]


def get(path, params, tries=5, pause=1.0):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=180) as r:
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


def months(start, end):
    """List of 'YYYY-MM' from start (inclusive) to end (exclusive), both dates."""
    out, y, m = [], start.year, start.month
    while dt.date(y, m, 1) < end:
        out.append(f"{y}-{m:02d}")
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return out


def next_month(key):
    y, m = map(int, key.split("-"))
    return dt.date(y + 1, 1, 1) if m == 12 else dt.date(y, m + 1, 1)


def to_month(ts):
    # aggregate buckets come back as epoch seconds or ms, or ISO strings
    if isinstance(ts, (int, float)):
        ts = ts / 1000 if ts > 1e11 else ts
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m")
    return str(ts)[:7]


def keyword_counts(sub, kind, field, term, a, b):
    """{month: count} for [a, b), or (None, error)."""
    data, err = get(f"{kind}/search/aggregate", {
        "aggregate": "created_utc", "frequency": "month", "subreddit": sub,
        field: term, "after": a.isoformat(), "before": b.isoformat(), "limit": ""})
    if data is None or "data" not in data:
        return None, err or json.dumps(data)[:200]
    got = {}
    for row in data["data"]:
        k = to_month(row.get("created_utc", row.get("key", row.get("date"))))
        got[k] = got.get(k, 0) + int(row.get("count", row.get("doc_count", 0)))
    return {m: got.get(m, 0) for m in months(a, b)}, None


def series(key, a, b):
    data, err = get("time_series", {"key": key, "precision": "month",
                                     "after": a.isoformat(), "before": b.isoformat()})
    if data is None or "data" not in data:
        return None, err or json.dumps(data)[:200]
    return {to_month(d["date"]): int(d["value"]) for d in data["data"]}, None


def top_subreddits(n):
    """N largest non-NSFW subreddits by subscribers."""
    data, err = get("subreddits/search", {"sort_type": "subscribers", "sort": "desc",
                                           "limit": min(1000, max(n * 2, 100)), "over18": "false"})
    if data is None:
        sys.exit(f"Could not list subreddits: {err}")
    rows = [r for r in data.get("data", []) if not r.get("over18")]
    return [(r["display_name"], r.get("subscribers")) for r in rows[:n]]


class Appender:
    def __init__(self, path, fields, key_fields):
        self.path, self.fields = path, fields
        self.done = set()
        if os.path.exists(path):
            with open(path, newline="") as f:
                for r in csv.DictReader(f):
                    self.done.add(tuple(r[k] for k in key_fields))
        new = not os.path.exists(path)
        self.fh = open(path, "a", newline="")
        self.w = csv.DictWriter(self.fh, fieldnames=fields)
        if new:
            self.w.writeheader()

    def write(self, rows):
        self.w.writerows(rows)
        self.fh.flush()


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="ai_keyword_timeseries")
    p.add_argument("--start", default="2010-01-01")
    p.add_argument("--end", default=None, help="exclusive; default = first day of current month")
    p.add_argument("--top", type=int, default=100, help="number of largest subreddits to include")
    p.add_argument("--add", nargs="*", default=[], help="extra subreddits (group 'extra')")
    p.add_argument("--only-subs", nargs="*", help="use exactly these subreddits (for testing)")
    p.add_argument("--no-comments", action="store_true", help="skip comment searches (much faster)")
    p.add_argument("--pause", type=float, default=1.0, help="seconds between requests")
    args = p.parse_args()

    global get
    _get = get
    get = lambda path, params, tries=5: _get(path, params, tries, args.pause)

    start = dt.date.fromisoformat(args.start)
    end = dt.date.fromisoformat(args.end) if args.end else dt.date.today().replace(day=1)
    os.makedirs(args.out, exist_ok=True)

    # 1. subreddit list
    sub_path = os.path.join(args.out, "subreddits.csv")
    if args.only_subs:
        subs = [(s, "test", "") for s in args.only_subs]
    elif os.path.exists(sub_path):
        with open(sub_path, newline="") as f:
            subs = [(r["subreddit"], r["group"], r["subscribers"]) for r in csv.DictReader(f)]
        have = {s.lower() for s, _, _ in subs}
        subs += [(s, "extra", "") for s in args.add if s.lower() not in have]
    else:
        subs, seen = [], set()
        for s, n in top_subreddits(args.top):
            subs.append((s, "largest", n)); seen.add(s.lower())
        for s in CORPUS:
            if s.lower() not in seen:
                subs.append((s, "corpus", "")); seen.add(s.lower())
        for s in args.add:
            if s.lower() not in seen:
                subs.append((s, "extra", "")); seen.add(s.lower())
    if not args.only_subs:
        with open(sub_path, "w", newline="") as f:
            w = csv.writer(f); w.writerow(["subreddit", "group", "subscribers"]); w.writerows(subs)
    print(f"{len(subs)} subreddits, {start} to {end} (exclusive)", flush=True)

    kw = Appender(os.path.join(args.out, "keyword_monthly.csv"),
                  ["subreddit", "kind", "field", "term", "month", "count"],
                  ["subreddit", "kind", "field", "term", "month"])
    tot = Appender(os.path.join(args.out, "totals_monthly.csv"),
                   ["scope", "kind", "month", "count"], ["scope", "kind", "month"])
    errors = Appender(os.path.join(args.out, "errors.csv"),
                      ["when", "subreddit", "kind", "field", "term", "period", "error"], [])

    def log_err(sub, kind, field, term, period, e):
        errors.write([{"when": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "subreddit": sub,
                       "kind": kind, "field": field, "term": term, "period": period, "error": e}])
        print(f"  ERROR {sub} {kind} {field} {term} {period}: {e}", flush=True)

    all_months = months(start, end)

    # 2. unfiltered totals (Reddit-wide and per subreddit)
    for scope in ["global"] + [s for s, _, _ in subs]:
        key_base = "global" if scope == "global" else f"r/{scope}"
        for kind in ("posts", "comments"):
            if all((scope, kind, m) in tot.done for m in all_months):
                continue
            vals, e = series(f"{key_base}/{kind}/count", start, end)
            if vals is None:
                log_err(scope, kind, "", "", f"{start}..{end}", f"time_series: {e}")
                continue
            tot.write([{"scope": scope, "kind": kind, "month": m, "count": v}
                       for m, v in sorted(vals.items()) if (scope, kind, m) not in tot.done])
        print(f"totals done: {scope}", flush=True)

    # 3. keyword counts, one year per request; failed years are retried month by month
    searches = [s for s in SEARCHES if not (args.no_comments and s[0] == "comments")]
    for sub, _, _ in subs:
        for kind, field in searches:
            for term in TERMS:
                for year in range(start.year, end.year + 1):
                    a = max(start, dt.date(year, 1, 1))
                    b = min(end, dt.date(year + 1, 1, 1))
                    if a >= b:
                        continue
                    todo = [m for m in months(a, b) if (sub, kind, field, term, m) not in kw.done]
                    if not todo:
                        continue
                    vals, e = keyword_counts(sub, kind, field, term, a, b)
                    if vals is None:
                        vals = {}
                        for m in todo:
                            ma = dt.date.fromisoformat(m + "-01")
                            v, e2 = keyword_counts(sub, kind, field, term, ma, min(next_month(m), end))
                            if v is None:
                                log_err(sub, kind, field, term, m, e2)
                            else:
                                vals.update(v)
                    kw.write([{"subreddit": sub, "kind": kind, "field": field, "term": term,
                               "month": m, "count": vals[m]} for m in todo if m in vals])
                print(f"{sub} {kind}/{field} {term}: done", flush=True)
    print("finished", flush=True)


if __name__ == "__main__":
    main()
