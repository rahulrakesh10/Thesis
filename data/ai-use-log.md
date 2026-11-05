# Generative-AI use log (CS4490Z documentation requirement)

| Date | Tool | What was automated | Human check needed |
|---|---|---|---|
| 2026-10-20 | Claude (Claude Code, cloud) | Tested which Reddit archives were reachable; queried Arctic Shift by hand for a few spot-check counts (see README.md) | Rahul to confirm spot checks look plausible |
| 2026-10-20 | Claude | Wrote `scripts/estimate_volume.py` (count-only queries to the Arctic Shift API) and the filtering notes in README.md | Rahul to read the script and the filtering rules before they go into the thesis |
| 2026-10-20 | (not run) | Remote Control run of the script on Rahul's Mac was declined; nothing ran there | none |
| 2026-10-22 | Claude (cloud) | Fetched monthly post/comment totals and "AI"-in-title post counts from Arctic Shift one query at a time; wrote `scripts/window_totals.py`; built `volume_table.csv` and the Claude Doc summary | Rahul to spot-check a few counts on the Arctic Shift site before presenting |
| 2026-11-05 | Claude (cloud) | Wrote `scripts/explore/` (temporal counts, term/n-gram frequencies, keyword in context, Gephi network edge lists, comment downloader) and the README section; ran the three explore scripts on the samples; tested `fetch_comments.py` only against a fake local API. No analysis or interpretation done | Rahul to read the scripts and the choices list (README items 5-9), run `fetch_comments.py` on his Mac, and spot-check a few counts by hand |
