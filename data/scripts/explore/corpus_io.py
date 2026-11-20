"""Shared helpers for the corpus exploration scripts (standard library only).

Posts CSV columns expected (as in sample_<Event>.csv):
  event, window, subreddit, id, created_utc, date, title, selftext, score,
  num_comments, url, permalink, AI_uppercase   (author is used if present)

Comments CSV (from fetch_comments.py) columns:
  event, window, subreddit, id, link_id, parent_id, author, created_utc, score, body
"""
import csv, datetime as dt, pathlib, re, sys

csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

EVENT_DATES = {"AlphaGo": "2016-03-09", "ChatGPT": "2022-11-30", "DeepSeek": "2025-01-20"}
WINDOW_ORDER = ["before", "immediate", "long"]
EMPTY_TEXT = {"", "[removed]", "[deleted]"}
DELETED_AUTHORS = {"", "[deleted]", "AutoModerator", None}


def read_rows(paths):
    """Read one or more CSV files (or folders of CSVs) into a list of dicts."""
    rows = []
    for p in paths:
        p = pathlib.Path(p)
        files = sorted(p.glob("*.csv")) if p.is_dir() else [p]
        for f in files:
            with open(f, newline="", encoding="utf-8") as fh:
                rows.extend(csv.DictReader(fh))
    return rows


def utc(row):
    return dt.datetime.fromtimestamp(int(float(row["created_utc"])), dt.timezone.utc)


def days_from_event(row):
    d0 = dt.date.fromisoformat(EVENT_DATES[row["event"]])
    return (utc(row).date() - d0).days


def clean_text(s):
    s = (s or "").strip()
    return "" if s in EMPTY_TEXT else s


def post_text(row):
    return " ".join(t for t in (clean_text(row.get("title")), clean_text(row.get("selftext"))) if t)


def write_csv(path, header, rows):
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(header)
        w.writerows(rows)
    print(f"wrote {path} ({len(rows)} rows)")


def group_keys(row):
    """Each item is counted once per subreddit and once under subreddit 'ALL'."""
    return [(row["event"], row["window"], row["subreddit"]), (row["event"], row["window"], "ALL")]


def sort_key(k):
    ev, win, sub = k[:3]
    return (ev, WINDOW_ORDER.index(win) if win in WINDOW_ORDER else 9, sub != "ALL", sub) + tuple(k[3:])


URL_RE = re.compile(r"https?://\S+|www\.\S+")
TOKEN_RE = re.compile(r"[A-Za-z][A-Za-z0-9'\-]*[A-Za-z0-9]|[A-Za-z]")


def tokenize(text, lower=True):
    text = URL_RE.sub(" ", text)
    toks = [t.strip("'-") for t in TOKEN_RE.findall(text)]
    toks = [t for t in toks if t]
    return [t.lower() for t in toks] if lower else toks
