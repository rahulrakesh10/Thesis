# Generative-AI use log (CS4490Z documentation requirement)

| Date | Tool | What was automated | Human check needed |
|---|---|---|---|
| 2026-10-20 | Claude (Claude Code, cloud) | Tested which Reddit archives were reachable; queried Arctic Shift by hand for a few spot-check counts (see README.md) | Rahul to confirm spot checks look plausible |
| 2026-10-20 | Claude | Wrote `scripts/estimate_volume.py` (count-only queries to the Arctic Shift API) and the filtering notes in README.md | Rahul to read the script and the filtering rules before they go into the thesis |
| 2026-10-20 | (not run) | Remote Control run of the script on Rahul's Mac was declined; nothing ran there | none |
| 2026-10-22 | Claude (cloud) | Fetched monthly post/comment totals and "AI"-in-title post counts from Arctic Shift one query at a time; wrote `scripts/window_totals.py`; built `volume_table.csv` and the Claude Doc summary | Rahul to spot-check a few counts on the Arctic Shift site before presenting |
| 2026-11-05 | Claude (cloud) | Researched Apify pricing and scrapers, GDELT and the X API from public web pages; pulled Hacker News event-window counts from the HN Algolia API; wrote `docs/apify-assessment.md` | Rahul to check prices on the linked pages before forwarding; no data was scraped |
| 2026-11-05 | Claude (cloud) | Wrote `scripts/collect_hn.py` (HN Algolia API, same windows and "AI" rule as Reddit); tested its logic offline and checked its query settings against the live API for the AlphaGo immediate window | Rahul to run it on the Mac and spot-check the `match` column on a sample |
| 2026-11-05 | Claude (cloud) | Fixed `collect_hn.py` after Rahul's --counts run showed inflated estimates: search restricted to item text, estimate flag added, resume option added; tested with a fake API | Rahul to compare downloaded totals with counts.csv |
