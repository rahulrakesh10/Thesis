"""Approximate window totals from Arctic Shift monthly counts (raw_monthly/*.txt).

Each window is [start, end) in UTC. Months only partly inside a window are
pro-rated by days, which assumes activity is spread evenly across the month.
That under- or over-counts when a spike falls in a partial month (e.g. r/baduk
in March 2016). Output: volume_totals_approx.csv.
"""
import calendar, csv, datetime as dt, pathlib, sys

WINDOWS = {
    "AlphaGo":  {"before": ("2015-12-09", "2016-03-09"), "immediate": ("2016-03-09", "2016-06-09"), "long": ("2017-03-09", "2017-06-09")},
    "ChatGPT":  {"before": ("2022-08-30", "2022-11-30"), "immediate": ("2022-11-30", "2023-03-01"), "long": ("2023-11-30", "2024-03-01")},
    "DeepSeek": {"before": ("2024-10-20", "2025-01-20"), "immediate": ("2025-01-20", "2025-04-20"), "long": ("2026-01-20", "2026-04-20")},
}
d = lambda s: dt.date.fromisoformat(s)


def window_total(monthly, a, b):
    total, missing = 0.0, []
    y, m = a.year, a.month
    while dt.date(y, m, 1) < b:
        ndays = calendar.monthrange(y, m)[1]
        lo, hi = max(a, dt.date(y, m, 1)), min(b, dt.date(y, m, ndays) + dt.timedelta(days=1))
        key = f"{y}-{m:02d}"
        if key in monthly:
            total += monthly[key] * (hi - lo).days / ndays
        else:
            missing.append(key)
        y, m = (y + 1, 1) if m == 12 else (y, m + 1)
    return round(total), missing


def main(raw_dir, out):
    rows = []
    for f in sorted(pathlib.Path(raw_dir).glob("*.txt")):
        sub, event, kind = f.stem.rsplit("_", 2)
        monthly = {k: int(v) for k, v in (l.split() for l in f.read_text().split("\n") if l.strip())}
        for win, (a, b) in WINDOWS[event].items():
            if sub == "ChatGPT" and win == "before":
                continue
            n, missing = window_total(monthly, d(a), d(b))
            rows.append({"event": event, "window": win, "subreddit": sub, "kind": kind, "approx_count": n,
                         "missing_months": " ".join(missing)})
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main(*sys.argv[1:])
