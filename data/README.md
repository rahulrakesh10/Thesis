# Reddit volume estimate (data/)

Status (2026-10-22): volume estimate done via a slower route (see below); no text
downloaded yet. The cloud environment's network blocks Reddit archives, and running
`scripts/estimate_volume.py` on Rahul's Mac was declined, so counts were fetched one
query at a time.

Summary for Yadira: Claude Doc "Reddit volume estimate for three AI events"
(https://claude.ai/artifact/1t5jxx7C361hU9guaVCKfL).

Files:
- `volume_table.csv`: one row per event x window x subreddit (approx. all posts, approx.
  all comments, exact posts with "AI" in title, note on partial/missing)
- `volume_totals_approx.csv`: day-pro-rated totals from `raw_monthly/` via `scripts/window_totals.py`
- `posts_title_AI_counts.csv` + `posts_title_AI_notes.txt`: title-search counts and how gaps were handled
- `scripts/estimate_volume.py`: full count script (incl. comment keyword counts) for when the network allows

## What gets counted

For every event x window x subreddit in planning/event-corpus-plan.md:

| Column | Meaning |
|---|---|
| posts_total / comments_total | All posts / comments in the subreddit in the window (no keyword filter) |
| posts_AI / comments_AI | Posts whose title or selftext, or comments whose body, match "AI" |
| posts_AI_or_event / comments_AI_or_event | After windows only: match "AI" OR the event name (AlphaGo, ChatGPT, DeepSeek) |

Windows are [start, end_exclusive) in UTC. r/ChatGPT has no before window (created Dec 2022).

Source: Arctic Shift API (`/api/{posts,comments}/search/aggregate`, fallback
`/api/time_series` for unfiltered totals). Pushshift is not used; its dumps end ~2024.

## Filtering rules and caveats (log every change here)

1. Keyword = "AI" only (Yadira, 2026-10-20). No broader terms yet.
2. Arctic Shift's full-text search is word-based and **not case-sensitive**, so it
   cannot do the case-sensitive whole-word match the plan asks for. The API counts
   are therefore an upper bound: "ai" (e.g. Portuguese/Japanese text, "Ai" names)
   is included. The case-sensitive `\bAI\b` filter must be applied after download,
   on a hand-checked sample, the same way for all three events.
3. Event-name terms are added only in after windows, because the names did not exist before.
4. Counts include deleted/removed items that the archive captured.

## Early spot checks (fetched by hand 2026-10-20, Arctic Shift)

| Subreddit | Window | Measure | Count |
|---|---|---|---|
| r/artificial | AlphaGo before | posts matching "AI" (title only) | 179 |
| r/artificial | AlphaGo before | posts matching "AI" (title + text) | 204 |
| r/baduk | AlphaGo immediate | all posts | 1,420 |
| r/baduk | AlphaGo immediate | posts matching "AI OR AlphaGo" | 383 |
| r/artificial | Jan / Feb / Mar 2016 | all comments per month | 1,108 / 1,058 / 1,074 |

Comment keyword search failed when tried from the cloud fetcher, so its reliability
is still unknown; the script records any API error in the `errors` column.

## Reddit-wide "AI" keyword time series (added 2026-11-05)

Supervisor's request (Nov 2026): search "AI" / "artificial intelligence" across Reddit and
look for major moments from keyword and post/comment frequencies, separately from the three
chosen events. Script: `scripts/ai_keyword_timeseries.py`. Counts only, no text.

- **Not truly Reddit-wide.** Arctic Shift keyword search only works with a `subreddit`
  filter, so the script counts hits in a list of subreddits: the N largest non-NSFW
  subreddits by current subscribers (default 100; chosen without reference to AI), the 13
  corpus subreddits, and any extras passed with `--add`. The `group` column in
  `subreddits.csv` records which. Reddit-wide unfiltered totals (`global` in
  `totals_monthly.csv`) are saved for normalisation.
- Searches per subreddit, monthly from 2010-01: posts by title, posts by title+selftext,
  comments by body; terms `AI` and `"artificial intelligence"`.
- Same case-insensitivity caveat as above (rule 2): counts are upper bounds.
- Large subreddits often time out on keyword search (comments especially). Failed months
  are listed in `errors.csv` and are missing from the counts; missing is not zero.
- Run on the Mac (cloud network blocks Arctic Shift):
  `python3 ai_keyword_timeseries.py --top 100` (resumable; rerun to fill gaps).
  Quick test: `python3 ai_keyword_timeseries.py --only-subs technology --out test_run`.
