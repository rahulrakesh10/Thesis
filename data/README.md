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

## Hacker News (added 2026-11-05)

Decision (Rahul, 2026-11-05): the corpus stays Reddit-focused, plus Hacker News as a free
second source. No paid Apify sources (see `docs/apify-assessment.md`).

- Script: `scripts/collect_hn.py` (stdlib only). Source: the free HN Algolia search API.
  The cloud environment blocks hn.algolia.com, so run it on the Mac from the repo root:
  `python3 data/scripts/collect_hn.py --counts` first, then `python3 data/scripts/collect_hn.py`.
- Same windows as the Reddit corpus. Same terms: "AI" and "artificial intelligence" in all
  windows, plus the event name (AlphaGo, ChatGPT, DeepSeek) in the after windows.
- Algolia matching is case-insensitive, so API hits are an upper bound. The `match` column
  applies the plan's rule (case-sensitive whole-word `AI`, "artificial intelligence", or the
  event name); rows with an empty `match` are false hits to drop.
- Algolia returns at most 1,000 hits per query; the script splits time ranges until each fits.
- Searches look only at the item's own text (comment_text; story title + story_text), not the
  parent story's title or URL. Large counts from Algolia are estimates (`exhaustive` = False in
  `hn/counts.csv`); e.g. the first --counts run (2026-11-05) gave 517k "AI" comments for
  DeepSeek long, out of an estimated 615k comments in total. Use counts from the downloaded CSVs.
- Downloaded CSVs are not committed (`.gitignore`); only `hn/counts.csv` is.
- Output: `hn/<event>_<window>.csv` (stories and comments, with story_id/parent_id for threads)
  and `hn/counts.csv`.
- Test (2026-11-05, AlphaGo immediate window, API hits): "AI" 743 stories / 3,280 comments;
  "artificial intelligence" 166 comments; "AlphaGo" 132 stories / 1,028 comments.

## Corpus exploration scripts (added 2026-11-05)

Supervisor's request (Nov 2026): start exploring the corpus already built: temporal
patterns, language and possible networks. `scripts/explore/` produces descriptive tables
only (counts, frequencies, edge lists). They contain no interpretation; reading them is
Rahul's work. Standard library only (Python 3.8+), run from `data/scripts/explore/`.

| Script | Needs | Writes |
|---|---|---|
| `explore_temporal.py` | posts CSVs (`sample_<Event>.csv`); optional comments | daily / weekly posts, comments, score and `num_comments` per event x window x subreddit, `days_from_event`, `window_summary.csv` |
| `explore_language.py` | same | corpus size, unigram / bigram / trigram frequencies (count, document frequency, per 10k tokens), keyword-in-context lines for `AI` and "artificial intelligence" |
| `explore_networks.py` | same; reply and user networks need comments | Gephi CSVs (nodes + edges) per event x window: term co-occurrence, subreddit-domain, reply (author -> author), user-subreddit |
| `fetch_comments.py` | network access to Arctic Shift (Mac) | `comments.csv` and `posts_with_authors.csv` for the posts in the corpus |

Run on the samples (writes to `./exploration/`, ignored by git; the 2026-11-05 sample-run
output is kept in `data/exploration/`, with a descriptive `SUMMARY.md`):

```
cd data/scripts/explore
python3 explore_temporal.py ~/thesis-data/sample/sample_*.csv
python3 explore_language.py ~/thesis-data/sample/sample_*.csv
python3 explore_networks.py ~/thesis-data/sample/sample_*.csv
```

With comments (the samples have no comments and no authors, so reply and user networks
need this step first; it runs on the Mac because the cloud network blocks Arctic Shift):

```
python3 fetch_comments.py ~/thesis-data/sample/sample_*.csv --out ~/thesis-data/comments
python3 explore_temporal.py ~/thesis-data/sample/sample_*.csv --comments ~/thesis-data/comments/comments.csv
python3 explore_language.py ~/thesis-data/sample/sample_*.csv --comments ~/thesis-data/comments/comments.csv
python3 explore_networks.py ~/thesis-data/sample/sample_*.csv ~/thesis-data/comments/posts_with_authors.csv \
    --comments ~/thesis-data/comments/comments.csv
```

Choices to check before using any table in the thesis (log changes here):

5. Text = title + selftext for posts, body for comments; `[removed]` / `[deleted]` and URLs dropped.
6. Tokens are lowercased, so the language tables merge "AI" and "ai"; the keyword-in-context
   file keeps the case-sensitive `\bAI\b` match. Stopwords: `scripts/explore/stopwords.txt`,
   the same list for every event (`--keep-stopwords` turns it off).
7. Comments are grouped under the window of their post, but dated by their own timestamp,
   so some comment dates fall after the window ends.
8. Networks: deleted authors and AutoModerator are dropped; term co-occurrence uses the 100
   most frequent terms per event x window and drops pairs seen in fewer than 2 documents;
   reddit / imgur hosts are left out of the subreddit-domain network.
9. The sample outputs were run on samples of 207 / 240 / 210 posts (AlphaGo / ChatGPT /
   DeepSeek, r/technology and r/singularity only), so they show the format, not the corpus.
