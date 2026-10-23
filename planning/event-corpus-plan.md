# Event corpus plan: subreddits and time windows

This is a first pick for Rahul to review, not final thesis text. Data availability was reasoned from memory and not yet checked against the Arctic Shift or Pushshift dumps.

## Core subreddits (use for all three events)

These five have existed since before 2016, so all three events can be compared on the same baseline.

| Subreddit | Why |
|---|---|
| r/technology | Large general tech audience |
| r/Futurology | Talk about the future of humanity and tech, good for imaginaries |
| r/singularity | AI enthusiasts and AI-risk talk (founded 2008) |
| r/artificial | General AI discussion |
| r/MachineLearning | Practitioners and researchers, a technical counterweight |

## Event-specific subreddits

| Event | Extra subreddits | Notes |
|---|---|---|
| AlphaGo (Mar 2016) | r/baduk, r/compsci | r/baduk is the Go community, the people whose game was "beaten" |
| ChatGPT (Nov 30, 2022) | r/programming, r/cscareerquestions, r/Teachers, r/ChatGPT* | *r/ChatGPT began Dec 2022, so it has no before window; use it as a supplement only |
| DeepSeek-R1 (Jan 20, 2025) | r/LocalLLaMA, r/stocks, r/wallstreetbets | r/LocalLLaMA (2023) has a before window; the stock subs carry the Nvidia market reaction |

## Time windows

The windows are the same length (3 months) for every event so the counts are comparable.

| Event | Before | Immediately after | Long after |
|---|---|---|---|
| AlphaGo (match Mar 9-15, 2016) | Dec 9, 2015 - Mar 8, 2016 | Mar 9 - Jun 8, 2016 | Mar 9 - Jun 8, 2017 |
| ChatGPT (Nov 30, 2022) | Aug 30 - Nov 29, 2022 | Nov 30, 2022 - Feb 28, 2023 | Nov 30, 2023 - Feb 29, 2024 |
| DeepSeek-R1 (Jan 20, 2025) | Oct 20, 2024 - Jan 19, 2025 | Jan 20 - Apr 19, 2025 | Jan 20 - Apr 19, 2026 |

## Confounds to watch for

- **AlphaGo long after:** AlphaGo Master and the Ke Jie match (May 2017) fall inside the window, so it measures AlphaGo's follow-up as well as the 2016 match.
- **ChatGPT before:** Stable Diffusion and DALL-E 2 (Aug-Sep 2022) fall inside the window, so "before" already carries some generative-AI hype.
- **ChatGPT immediately after:** this window ends just before GPT-4 (Mar 14, 2023). That is deliberate, to keep the two separate.
- **DeepSeek-R1 before:** DeepSeek-V3 came out on Dec 26, 2024, so a small early wave shows up inside the before window.
- **DeepSeek-R1 long after:** this window is also covered by Arctic Shift only, since Pushshift dumps end around 2024.

## Keyword strategy (agreed with Yadira, 2026-10-20)

- **Before windows:** collect with broad terms, "artificial intelligence" and "AI", because the event names did not exist yet. Do not use "chatbot": it picks up years of pre-generative-AI chatbot work.
- **Start narrow:** begin with "AI" alone (plus the core event name for the after windows: AlphaGo, ChatGPT, DeepSeek). Check the volume. Add broader terms (e.g. "OpenAI", "Nvidia stock", "DeepMind") only if the data is too thin.
- **Filtering:** broad terms are allowed only with a written filtering rule, applied the same way to all three events. Keep a log of every term added, why, and how its results were filtered.
- **Matching "AI":** match it as a whole word, case-sensitive, so it does not hit words like "said" or "aim". Check a sample by hand for false hits.

## Scope

- Collect **posts and comments** for every window.
- Then estimate the volume per event, window and subreddit, and narrow the scope with Yadira if it is too large. Bring this estimate to the next supervisor meeting.
