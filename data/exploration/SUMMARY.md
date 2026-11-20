# What the exploration tables show (sample run, 2026-11-05)

This summary describes the tables only. Reading what they mean for the thesis is Rahul's job.
Source: the three sample files (AlphaGo 207 posts, ChatGPT 240, DeepSeek 210), r/technology and
r/singularity only, posts only (no comments yet). Tables: `temporal/`, `language/`, `networks/`.

## Read this first: what the sample can and cannot show

- The samples hold a capped number of posts per day (up to 10, on 9 to 37 days per window). So
  **post counts per day or week show how the sample was drawn, not how active Reddit was.**
  Do not read peaks in `posts` as real peaks.
- 96% of posts match case-sensitive "AI" (`posts_AI_uppercase`), as the sample was drawn on that keyword.
- Many top terms come from one or two long posts. Check `doc_freq` (how many posts use the term)
  before treating a term as common. For example, "war" (39 uses) is in 2 posts.

## Temporal (`temporal/`)

`num_comments` (the comment count Reddit reports on each post) is not capped by the sampling, so it is the more useful activity column here.

| Event | before | immediate | long |
|---|---|---|---|
| AlphaGo, comments on sampled posts | 452 | 821 | 1,157 |
| ChatGPT | 2,607 | 4,693 | 3,045 |
| DeepSeek | 1,091 | 1,325 | 1,945 |

Days with the most comments on sampled posts:
- ChatGPT immediate: 2023-01-14 (1,574), 2022-12-18 (1,340) and 2022-12-09 (779)
- ChatGPT long: 2024-01-15 (878)
- AlphaGo long: 2017-03-27 (828, from 6 posts, mostly r/technology)

Median post score is highest in the ChatGPT before and immediate windows (17 and 13). It is 1 in most DeepSeek windows.

## Language (`language/`)

Text size per window (non-stopword tokens): AlphaGo 2,646 / 2,116 / 772; ChatGPT 1,498 / 1,919 / 1,738;
DeepSeek 1,564 / 2,016 / 3,682 (before / immediate / long). "ai" is the top term in every window.

Next most frequent terms. The number in brackets is how many posts use the term; a (1) or (2) means a single long post:
- **AlphaGo** before: human (8), war (2), virtual (4), consciousness (2), simulation (2). Immediate: human (12), assistant (11), schedules and meetings (8, one repeated post). Long: google (9), learning (10), machine (6), brain (5).
- **ChatGPT** before: people (4), art (6), general ai (2), ai generated (5). Immediate: art (3), artists (3), create (9), chatgpt (8), the singularity (4). Long: new (18), data (5), google (6), gemini (3).
- **DeepSeek** before: system (4), agi (4), nvidia (6), model (4). Immediate: agi (3), grok (4), reasoning (6), research (5), deep research (1). Long: people (12), model/models (9/11), ai tools (3), i built (3).

`kwic.csv` has 913 lines showing each "AI" / "artificial intelligence" match with its context, for close reading.

Noise to filter later: image-link fragments ("width format png auto webp" in DeepSeek before),
"m re's law" (Moore's law with a broken apostrophe), "org wiki". These suggest the stopword list
and URL cleaning need another pass.

## Networks (`networks/`)

- Term co-occurrence (top 100 terms per window, pairs in 2 or more posts): the most edges are in AlphaGo before (1,272) and DeepSeek long (1,511), the fewest in AlphaGo long (154) and ChatGPT before (222). Edge counts follow text size, so compare them only alongside the token counts above.
- Subreddit-domain: 30 to 48 domains per window, mostly linked once each. Most-linked domains in the immediate windows: AlphaGo x.ai (6, r/technology); ChatGPT businessinsider.com and techcrunch.com (2 each); DeepSeek techcrunch.com and youtu.be (5 each).
- Reply and user networks are empty until comments are fetched (`fetch_comments.py`).
