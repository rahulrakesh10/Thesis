"""Temporal counts for the event corpora: daily and weekly activity per subreddit.

Descriptive tables only; no interpretation.

Outputs (in --out, default ./exploration/temporal/):
  posts_daily.csv     event, window, subreddit, date, days_from_event, posts,
                      posts_AI_uppercase, sum_num_comments, sum_score
  posts_weekly.csv    same, by ISO week (week_start = Monday)
  comments_daily.csv  only if --comments is given: event, window, subreddit, date,
                      days_from_event, comments, unique_authors
  comments_weekly.csv same, by ISO week
  window_summary.csv  event, window, subreddit, first_date, last_date, active_days,
                      posts, posts_AI_uppercase, sum_num_comments, median_score,
                      comments_collected

subreddit = ALL rows add up all subreddits. days_from_event is relative to the event
date in corpus_io.EVENT_DATES. Days with no posts are written as 0 between the first and
last day seen in each window, so gaps show up in plots.

Example:
  python3 explore_temporal.py ../../sample_AlphaGo.csv ../../sample_ChatGPT.csv ../../sample_DeepSeek.csv
  python3 explore_temporal.py corpus/ --comments comments/ --out exploration/temporal
"""
import argparse, collections, datetime as dt, statistics
from corpus_io import (EVENT_DATES, days_from_event, group_keys, read_rows, sort_key, utc, write_csv)


def week_start(d):
    return d - dt.timedelta(days=d.weekday())


def fill_days(counter_by_key, ncols):
    """counter_by_key: {(ev,win,sub): {date: [vals]}} -> rows with zero-filled days."""
    out = []
    for key in sorted(counter_by_key, key=sort_key):
        days = counter_by_key[key]
        d, end = min(days), max(days)
        d0 = dt.date.fromisoformat(EVENT_DATES[key[0]])
        while d <= end:
            out.append(list(key) + [d.isoformat(), (d - d0).days] + days.get(d, [0] * ncols))
            d += dt.timedelta(days=1)
    return out


def to_weekly(daily_rows, ncols, unique_col=None):
    agg = collections.OrderedDict()
    for r in daily_rows:
        ev, win, sub, day = r[0], r[1], r[2], dt.date.fromisoformat(r[3])
        k = (ev, win, sub, week_start(day))
        if k not in agg:
            agg[k] = [0] * ncols
        for i, v in enumerate(r[5:5 + ncols]):
            agg[k][i] += v
    rows = []
    for (ev, win, sub, ws), vals in agg.items():
        d0 = dt.date.fromisoformat(EVENT_DATES[ev])
        rows.append([ev, win, sub, ws.isoformat(), (ws - d0).days] + vals)
    return rows


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("posts", nargs="+", help="posts CSV files or folders")
    ap.add_argument("--comments", nargs="*", default=[], help="comments CSV files or folders (fetch_comments.py output)")
    ap.add_argument("--out", default="exploration/temporal")
    a = ap.parse_args()

    posts = read_rows(a.posts)
    daily = collections.defaultdict(dict)
    scores = collections.defaultdict(list)
    for r in posts:
        day = utc(r).date()
        upper = str(r.get("AI_uppercase", "")).strip().lower() in ("true", "1")
        for k in group_keys(r):
            v = daily[k].setdefault(day, [0, 0, 0, 0])
            v[0] += 1
            v[1] += upper
            v[2] += int(float(r.get("num_comments") or 0))
            v[3] += int(float(r.get("score") or 0))
            scores[k].append(int(float(r.get("score") or 0)))
    head = ["event", "window", "subreddit", "date", "days_from_event", "posts", "posts_AI_uppercase", "sum_num_comments", "sum_score"]
    pdaily = fill_days(daily, 4)
    write_csv(f"{a.out}/posts_daily.csv", head, pdaily)
    write_csv(f"{a.out}/posts_weekly.csv", ["event", "window", "subreddit", "week_start"] + head[4:], to_weekly(pdaily, 4))

    ccount = collections.Counter()
    if a.comments:
        comments = read_rows(a.comments)
        cdaily = collections.defaultdict(dict)
        authors = collections.defaultdict(set)
        for r in comments:
            day = utc(r).date()
            for k in group_keys(r):
                cdaily[k].setdefault(day, [0, 0])[0] += 1
                authors[k + (day,)].add(r.get("author"))
                ccount[k] += 1
        for k, days in cdaily.items():
            for day, v in days.items():
                v[1] = len(authors[k + (day,)] - {"[deleted]", ""})
        chead = ["event", "window", "subreddit", "date", "days_from_event", "comments", "unique_authors"]
        crows = fill_days(cdaily, 2)
        write_csv(f"{a.out}/comments_daily.csv", chead, crows)
        # unique authors cannot be summed across days; weekly file keeps comment counts only
        wk = [r[:6] for r in to_weekly([r[:6] + [0] for r in crows], 1)]
        write_csv(f"{a.out}/comments_weekly.csv", ["event", "window", "subreddit", "week_start", "days_from_event", "comments"], wk)

    summ = []
    for k in sorted(daily, key=sort_key):
        days = daily[k]
        active = [d for d, v in days.items() if v[0]]
        tot = [sum(v[i] for v in days.values()) for i in range(4)]
        summ.append(list(k) + [min(active).isoformat(), max(active).isoformat(), len(active), tot[0], tot[1], tot[2],
                               statistics.median(scores[k]), ccount.get(k, "") if a.comments else ""])
    write_csv(f"{a.out}/window_summary.csv", ["event", "window", "subreddit", "first_date", "last_date", "active_days", "posts",
                                               "posts_AI_uppercase", "sum_num_comments", "median_score", "comments_collected"], summ)


if __name__ == "__main__":
    main()
