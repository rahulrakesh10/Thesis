"""Estimate Reddit volume per event, window and subreddit from the Arctic Shift API.

Counts only; downloads no post or comment text. Writes volume_counts.csv next to
where it is run. Standard library only (Python 3.8+).

Keyword matching uses Arctic Shift's full-text search (`query` for posts = title +
selftext, `body` for comments). That search is word-based and NOT case-sensitive,
so "AI" also hits "ai"; see notes in data/README.md.
"""
import csv, json, sys, time, urllib.parse, urllib.request

API = "https://arctic-shift.photon-reddit.com/api"

WINDOWS = {
    "AlphaGo":  {"before": ("2015-12-09", "2016-03-09"), "immediate": ("2016-03-09", "2016-06-09"), "long": ("2017-03-09", "2017-06-09")},
    "ChatGPT":  {"before": ("2022-08-30", "2022-11-30"), "immediate": ("2022-11-30", "2023-03-01"), "long": ("2023-11-30", "2024-03-01")},
    "DeepSeek": {"before": ("2024-10-20", "2025-01-20"), "immediate": ("2025-01-20", "2025-04-20"), "long": ("2026-01-20", "2026-04-20")},
}
CORE = ["technology", "Futurology", "singularity", "artificial", "MachineLearning"]
EXTRA = {
    "AlphaGo": ["baduk", "compsci"],
    "ChatGPT": ["programming", "cscareerquestions", "Teachers", "ChatGPT"],
    "DeepSeek": ["LocalLLaMA", "stocks", "wallstreetbets"],
}
NO_BEFORE = {("ChatGPT", "ChatGPT")}  # r/ChatGPT was created Dec 2022


def get(path, params, tries=5):
    url = f"{API}/{path}?{urllib.parse.urlencode(params)}"
    err = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "uwo-thesis-volume-estimate/0.1"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r), None
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}: {e.read()[:200].decode('utf-8', 'replace')}"
        except Exception as e:  # timeouts, resets
            err = repr(e)[:200]
        time.sleep(2 ** i)
    return None, err


def count(kind, sub, after, before, **search):
    """Exact count via the aggregate endpoint; None if the API refused."""
    data, err = get(f"{kind}/search/aggregate",
                    {"aggregate": "subreddit", "subreddit": sub, "after": after, "before": before, "limit": 1, **search})
    if data is None or "data" not in data:
        return None, err or json.dumps(data)[:200]
    rows = data["data"]
    return (int(rows[0]["count"]) if rows else 0), None


def series_total(kind, sub, after, before):
    """Fallback for unfiltered totals: sum of daily time-series values."""
    data, err = get("time_series", {"key": f"r/{sub}/{kind}/count", "precision": "day", "after": after, "before": before})
    if data is None:
        return None, err
    return sum(int(d["value"]) for d in data.get("data", [])), None


def main(out="volume_counts.csv"):
    fields = ["event", "window", "start", "end_exclusive", "subreddit",
              "posts_total", "posts_AI", "posts_AI_or_event",
              "comments_total", "comments_AI", "comments_AI_or_event", "errors"]
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for event, wins in WINDOWS.items():
            for win, (a, b) in wins.items():
                for sub in CORE + EXTRA[event]:
                    if win == "before" and (event, sub) in NO_BEFORE:
                        continue
                    row = {"event": event, "window": win, "start": a, "end_exclusive": b, "subreddit": sub}
                    errs = []
                    union = f"AI OR {event}" if win != "before" else None
                    for kind, key, param in (("posts", "posts", "query"), ("comments", "comments", "body")):
                        n, e = count(kind, sub, a, b)
                        if n is None:
                            n, e2 = series_total(kind, sub, a, b)
                            errs.append(f"{key}_total aggregate failed ({e}); used time_series")
                            if n is None:
                                errs.append(f"{key}_total time_series failed ({e2})")
                        row[f"{key}_total"] = n
                        n, e = count(kind, sub, a, b, **{param: "AI"})
                        row[f"{key}_AI"] = n
                        if e:
                            errs.append(f"{key}_AI: {e}")
                        if union:
                            n, e = count(kind, sub, a, b, **{param: union})
                            row[f"{key}_AI_or_event"] = n
                            if e:
                                errs.append(f"{key}_AI_or_event: {e}")
                    row["errors"] = " | ".join(errs)
                    w.writerow(row)
                    f.flush()
                    print(event, win, sub, {k: row.get(k) for k in fields[5:11]}, flush=True)
                    time.sleep(0.5)


if __name__ == "__main__":
    main(*sys.argv[1:])
