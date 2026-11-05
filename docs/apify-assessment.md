# Apify and non-Reddit sources: options and costs

As of 2026-11-05. Prepared for discussion with the supervisor (Yadira Lizama Mue).

## Summary

Apify could add X (Twitter) posts and YouTube comments to the corpus for roughly **$0 to $150 in total**, depending on how much is sampled. It is a marketplace of third-party scrapers ("Actors") billed per result, not a data archive, so what it returns for 2016 and 2022 depends on each scraper and on the platform it scrapes.

- **Cheapest extension:** Hacker News, which is free through its own public search API and needs no Apify at all.
- **Main Apify use cases:** X posts (about $0.15 per 1,000 tweets) and YouTube comments (about $0.50 per 1,000 comments).
- **Hardest gap:** news coverage of AlphaGo in 2016, which neither the Apify Google News scraper nor GDELT's search API reaches.
- **Main risks:** X's terms of use, scraper reliability for old posts, and whether the ethics approval covers non-Reddit platforms.

This doc lays out options and costs only. Whether to expand beyond Reddit is Rahul's call, and keeping the project Reddit-only is also a valid choice.

## Historical coverage is the deciding constraint

The thesis needs data from March 2016, Nov 2022 to Jan 2023, and Jan to Feb 2025, and most scraping tools are built for recent data. Coverage by source:

| Source | 2016 (AlphaGo) | 2022 (ChatGPT) | 2025 (DeepSeek-R1) | Evidence |
| --- | --- | --- | --- | --- |
| Hacker News | Yes | Yes | Yes | Counts pulled from the HN search API (table below) |
| X / Twitter | Claimed | Claimed | Claimed | Scraper supports since/until dates; old-post completeness is the vendor's claim, untested |
| YouTube comments | Partly | Partly | Partly | Comments on old videos stay up, but only those not deleted; you must supply the video URLs |
| Google News (Apify) | No | No | Yes | Scraper only searches the last 1,000 days |
| GDELT DOC API (free) | No | No | No | Rolling 3-month window |

Hacker News items mentioning each event, in the 30 days around it ([HN Algolia search API](https://hn.algolia.com/api), queried 2026-11-05):

| Event | Window | Stories | Comments |
| --- | --- | --- | --- |
| AlphaGo | 2016-03-06 to 2016-04-05 | 198 | 981 |
| ChatGPT | 2022-11-29 to 2022-12-29 | 992 | 4,261 |
| DeepSeek | 2025-01-17 to 2025-02-15 | 816 | 3,022 |

These are case-insensitive keyword matches on the event name only, so they are upper bounds for relevance and lower bounds for broader "AI" talk.

## Options by source

X and YouTube are where Apify adds something the free tools cannot; Hacker News and news are better served elsewhere.

| Source | How to collect | Price | Fit for the thesis | Main caveat |
| --- | --- | --- | --- | --- |
| Hacker News | Free HN search API directly (no Apify) | $0 | Tech-literate discussion, threaded like Reddit, so the same methods apply | Small volume, narrow audience |
| X / Twitter | Apify [X Tweet Scraper (xquik)](https://apify.com/xquik/x-tweet-scraper) with since/until dates | $0.15 per 1,000 tweets plus platform usage | Largest public reaction to all three events | X terms, unofficial access, sampling is not random |
| YouTube comments | Apify [YouTube Comments Scraper (apidojo)](https://apify.com/apidojo/youtube-comments-scraper) on a hand-picked video list | $0.50 per 1,000 comments | General-public reactions to news and explainer videos | Gives relative dates ("5 months ago"); you choose the videos, which shapes the sample |
| News articles | Apify [Google News Scraper](https://apify.com/lhotanova/google-news-scraper) | From $1.30 per 1,000 results | Media framing to compare with Reddit | Only the last 1,000 days, so 2025 only |
| X via official API | [X API](https://developer.x.com/en/products/twitter-api) | $5,000 per month for the tier that includes search; archive access is enterprise only | Cleanest legal route | Far beyond a student budget |

A second YouTube scraper ([datascrapers](https://apify.com/datascrapers/youtube-comment-scraper)) returns exact ISO dates but costs $1.70 to $2.50 per 1,000 and has no user ratings yet. A second X scraper ([kaitoeasyapi](https://apify.com/kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest)) warns that its date filters "may return incomplete or empty results", which rules it out for historical windows.

## What it would cost

A realistic expansion (X plus YouTube samples for all three events) comes to about **$70 in scraper fees, so budget $100 to $150** to allow for test runs and re-runs.

**How Apify bills** ([pricing](https://apify.com/pricing)): each plan is a monthly fee that is also prepaid usage credit, and usage beyond it is pay-as-you-go. Unused credit does not roll over.

| Plan | Monthly fee | Usage credit included | Note |
| --- | --- | --- | --- |
| Free | $0 | $5 | No card needed; blocked until next month once used |
| Starter | $19 | $19 | Students get 50% off for up to 4 months ([universities page](https://apify.com/resources/universities)) |
| Scale | $199 | $199 | Not needed at thesis scale |

The student discount needs a university email and a short application, takes up to 2 weeks, and is for academic use only. The page does not say whether the usage credit is also halved.

**Scenarios** (sample sizes are illustrative, not recommendations):

| Scenario | What is added | Scraper fees | Likely plan |
| --- | --- | --- | --- |
| A. Reddit only, or Reddit + HN | Nothing, or HN via its free API | $0 | None |
| B. + YouTube | 30 videos per event, about 1,000 comments each (90,000 comments) | about $45 | Free for a pilot, then 1 to 2 months of Starter |
| C. + YouTube + X | B plus 50,000 tweets per event (150,000 tweets) | about $70 | 1 to 3 months of Starter |

The X figure uses the vendor's own benchmark of $0.000155 per tweet including platform usage. The free $5 monthly credit covers about 30,000 tweets or 10,000 comments, which is enough to test whether 2016 data actually comes back before paying anything.

## Other considerations

The non-cost risks matter more than the dollars, especially for X.

- **Platform terms.** X's terms of service prohibit crawling or scraping without prior written consent (not quoted: x.com blocks automated fetching, so the page could not be opened). Apify scrapers for X are third-party and unofficial. YouTube's terms also restrict automated collection. This is worth raising with Yadira before collecting anything.
- **Ethics approval.** If the current research-ethics plan names Reddit only, adding X or YouTube may need an amendment. Open question: what does the existing approval cover?
- **Reproducibility.** Unofficial scrapers change or break without notice, and keyword search on X is not a random sample. A methods chapter would need to state exactly which Actor version, query and date filters were used.
- **Comparability.** Reddit, HN and YouTube are threaded comments under posts; X is short standalone posts. Mixing them changes what "subreddit-post-comment frequency" means.
- **Gen-AI documentation.** Apify is a scraping tool, not generative AI, but the research for this note was gathered with AI assistance and is logged in `data/ai-use-log.md`.

## Decisions for Rahul

Three choices, none made here:

1. Stay Reddit-only, or expand? Yadira said either is fine.
2. If expanding, which sources: free HN only, or also YouTube and X through Apify?
3. If using Apify, run a free-plan pilot first to check that 2016 tweets and comments actually come back, then decide on a paid month.

## Sources

All opened 2026-11-05.

- [Apify pricing](https://apify.com/pricing)
- [Apify for universities](https://apify.com/resources/universities)
- [X Tweet Scraper (xquik)](https://apify.com/xquik/x-tweet-scraper)
- [X scraper (kaitoeasyapi)](https://apify.com/kaitoeasyapi/twitter-x-data-tweet-scraper-pay-per-result-cheapest)
- [YouTube Comments Scraper (apidojo)](https://apify.com/apidojo/youtube-comments-scraper)
- [YouTube Comment Scraper (datascrapers)](https://apify.com/datascrapers/youtube-comment-scraper)
- [Google News Scraper](https://apify.com/lhotanova/google-news-scraper)
- [HN Algolia search API](https://hn.algolia.com/api)
- [GDELT data](https://www.gdeltproject.org/data.html) and [GDELT DOC 2.0 API](https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/)
- [X API tiers](https://developer.x.com/en/products/twitter-api)
