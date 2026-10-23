# Reddit volume estimate for three AI events

As of 2026-10-22 · Rahul

## Summary

Collecting every post and comment in the planned subreddits is too large: each 3-month window holds 54,000 to 109,000 posts and 0.7 to 5.3 million comments. Filtering to posts with "AI" in the title brings each window down to roughly 700 to 14,000 posts, which is workable.

- **Volume grows over time.** AlphaGo windows hold about 0.7 to 0.8M comments, ChatGPT about 2.1 to 2.5M, DeepSeek about 3.7 to 5.3M.
- **r/wallstreetbets dominates DeepSeek.** It alone has 2.0 to 3.1M comments per window, more than half of all DeepSeek comments.
- **"AI" alone misses the event in community subreddits.** In r/baduk after the AlphaGo match, only 29 post titles say "AI", but 383 posts mention "AI" or "AlphaGo" in the title or text. In r/Teachers after ChatGPT, only 70 of about 13,000 posts have "AI" in the title.
- **Proposed scope for discussion:** keyword-matched posts plus all their comments; drop r/wallstreetbets or take a random sample of it; add the event name as a keyword in after windows for every event.

## Volume per event

Posts with "AI" in the title, all planned subreddits combined (\* = some subreddits missing, true value is higher):

| Event | Before | Immediately after | One year after |
| --- | --- | --- | --- |
| AlphaGo | 728 | 1,225 | 1,723 |
| ChatGPT | 2,885 | 9,421 | 7,530\* |
| DeepSeek | 9,156\* | 10,714 | 14,072 |

The filtered post counts rise after each event, and the ChatGPT jump (3.3x) is the largest. Unfiltered totals for the same windows:

| Event | Window | All posts (approx.) | All comments (approx.) |
| --- | --- | --- | --- |
| AlphaGo | Before (Dec 9, 2015 to Mar 8, 2016) | 53,600 | 719,000 |
| AlphaGo | Immediately after (Mar 9 to Jun 8, 2016) | 58,100 | 748,000 |
| AlphaGo | One year after (Mar 9 to Jun 8, 2017) | 58,300 | 791,000 |
| ChatGPT | Before (Aug 30 to Nov 29, 2022) | 68,000 | 2,065,000 |
| ChatGPT | Immediately after (Nov 30, 2022 to Feb 28, 2023) | 108,900 | 2,550,000 |
| ChatGPT | One year after (Nov 30, 2023 to Feb 29, 2024) | 105,300 | 2,351,000 |
| DeepSeek | Before (Oct 20, 2024 to Jan 19, 2025) | 95,600 | 3,747,000 |
| DeepSeek | Immediately after (Jan 20 to Apr 19, 2025) | 93,200 | 5,296,000 |
| DeepSeek | One year after (Jan 20 to Apr 19, 2026) | 80,700 | 4,138,000 |

## Keywords per event

The agreed rule is "AI" in every window, plus the event name in the after windows. Extra terms are candidates only and need a written filtering rule applied the same way to all three events.

| Event | All windows | After windows only | Candidate extra terms (not yet used) |
| --- | --- | --- | --- |
| AlphaGo | AI, artificial intelligence | AlphaGo | DeepMind, Lee Sedol |
| ChatGPT | AI, artificial intelligence | ChatGPT | OpenAI, GPT |
| DeepSeek | AI, artificial intelligence | DeepSeek | R1, Nvidia (stock subreddits only) |

Filtering rules so far:

1. "AI" must match as a whole word, case-sensitive. The archive search cannot do this (it also matches "ai"), so the counts here are upper bounds and the strict match is applied after download.
2. "chatbot" is excluded, because it picks up pre-2022 chatbot discussion.
3. Event names are not used in before windows, since the names did not exist yet.
4. Each added term, the reason for it and its filter are logged in README.md.

## Per subreddit

Each cell lists before / immediately after / one year after. Comments are in thousands. A dash means the subreddit did not exist yet, and ≥ marks a partial count.

**AlphaGo**

| Subreddit | Posts with "AI" in title | All posts | All comments (thousands) |
| --- | --- | --- | --- |
| r/technology | 188 / 325 / 366 | 39,995 / 42,460 / 40,359 | 459 / 441 / 432 |
| r/Futurology | 216 / 351 / 591 | 8,223 / 9,171 / 11,048 | 219 / 252 / 317 |
| r/MachineLearning | 67 / 117 / 167 | 2,665 / 2,999 / 3,523 | 17 / 21 / 15 |
| r/baduk | 15 / 29 / 20 | 654 / 1,274 / 832 | 9 / 18 / 14 |
| r/compsci | 9 / 24 / 12 | 952 / 974 / 796 | 9 / 8 / 6 |
| r/singularity | 54 / 107 / 143 | 491 / 576 / 716 | 4 / 5 / 4 |
| r/artificial | 179 / 272 / 424 | 617 / 646 / 1,045 | 3 / 3 / 4 |

**ChatGPT**

| Subreddit | Posts with "AI" in title | All posts | All comments (thousands) |
| --- | --- | --- | --- |
| r/technology | 456 / 1,294 / 1,671 | 16,140 / 16,260 / 11,745 | 1,038 / 978 / 668 |
| r/Futurology | 311 / 872 / 647 | 3,965 / 5,919 / 3,428 | 353 / 551 / 237 |
| r/Teachers | 13 / 70 / 117 | 13,894 / 13,175 / 14,912 | 295 / 310 / 419 |
| r/ChatGPT | — / 3,014 / not retrieved | — / 37,235 / 30,955 | — / 286 / 394 |
| r/cscareerquestions | 48 / 141 / 206 | 16,072 / 13,978 / 13,918 | 214 / 195 / 204 |
| r/singularity | 544 / 1,141 / 2,312 | 2,133 / 3,924 / 8,584 | 39 / 96 / 277 |
| r/programming | 99 / 273 / 221 | 7,885 / 7,889 / 7,857 | 100 / 96 / 85 |
| r/MachineLearning | 504 / 907 / 881 | 5,948 / 6,963 / 8,466 | 23 / 27 / 41 |
| r/artificial | 910 / 1,709 / ≥1,475 | 2,010 / 3,547 / 5,423 | 5 / 10 / 27 |

**DeepSeek**

| Subreddit | Posts with "AI" in title | All posts | All comments (thousands) |
| --- | --- | --- | --- |
| r/wallstreetbets | ≥410 / 643 / 425 | 40,289 / 33,817 / 20,577 | 2,051 / 3,121 / 2,365 |
| r/technology | 1,693 / 2,041 / 2,942 | 11,446 / 11,561 / 11,296 | 849 / 976 / 853 |
| r/stocks | 211 / 303 / 489 | 10,109 / 12,706 / 10,281 | 155 / 450 / 285 |
| r/singularity | 2,282 / 1,887 / 1,788 | 8,985 / 7,349 / 5,424 | 330 / 322 / 193 |
| r/LocalLLaMA | 910 / 1,394 / 2,857 | 10,053 / 12,247 / 18,410 | 146 / 192 / 253 |
| r/Futurology | 664 / 842 / 929 | 3,458 / 4,015 / 3,553 | 163 / 174 / 135 |
| r/artificial | 1,938 / 2,038 / 3,599 | 3,579 / 3,703 / 5,997 | 26 / 38 / 34 |
| r/MachineLearning | 1,048 / 1,566 / 1,043 | 7,671 / 7,768 / 5,200 | 26 / 22 / 21 |

## Method, caveats and next steps

All numbers are counts from the public [Arctic Shift](https://arctic-shift.photon-reddit.com) Reddit archive. No post or comment text has been downloaded yet.

- **All posts and comments** are monthly archive totals, pro-rated by day for months that only partly fall in a window. They are approximate. For example, r/baduk after AlphaGo shows about 1,270 posts by this method against an exact 1,420, because the match spike fell early in March.
- **Posts with "AI" in the title** are exact archive counts, but the search ignores case, so they include "ai". Searching the title and body text, or searching comments, kept timing out, so those counts are not available yet.
- **Missing values:** r/ChatGPT one year after ChatGPT (not retrieved); r/artificial one year after ChatGPT covers Nov 30 to Jan 14 only; r/wallstreetbets before DeepSeek covers Oct 20 to Jan 4 only.
- **Gen-AI use:** these counts were gathered and tabled by Claude, and every automated step is logged in ai-use-log.md as the course requires.

Next steps once Yadira agrees the scope:

- [ ] Decide on r/wallstreetbets (drop, sample, or keep)
- [ ] Confirm adding the event names, and any candidate terms, as keywords
- [ ] Download matching posts and their comments, then apply the case-sensitive "AI" filter
