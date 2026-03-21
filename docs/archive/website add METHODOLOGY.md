# About

## How this works

We track 27 Reddit communities where people discuss AI companions — from large platforms like r/CharacterAI and r/replika to recovery communities like r/ChatbotAddiction. Our corpus spans January 2023 to present and contains over 3.7 million posts.

For each of the six themes, we maintain a curated list of keywords and phrases — terms like "lobotomized," "chatbot addiction," "emotional support," "sentient." Every keyword went through a validation process: we sampled up to 100 posts matching each term, classified whether the match genuinely reflected the theme in context, and required at least 80% precision before including it. Keywords that didn't clear that threshold were cut, regardless of volume. The full keyword list and precision scores are published in our [GitHub repository](https://github.com/hopeshub/myfriendisai).

The chart shows how often these validated terms appear per 1,000 posts, using a 7-day rolling average to smooth daily noise. Because we normalize to post volume, the trends reflect changes in how people talk — not just growth in the communities themselves.

## What this captures and what it doesn't

This is a frequency tracker, not a sentiment analyzer. When the addiction line rises, it means more people are using addiction-related language — not that more people are addicted. The signal is intentionally narrow: we trade coverage for precision, preferring to undercount rather than pollute the data. Some themes are measured by just a handful of highly specific terms. Every data point traces back to a validated keyword in a real post.

## Data collection

Data from January 2023 through March 12, 2026 was backfilled from PullPush and Arctic Shift Reddit archives. Beginning March 13, 2026, posts are collected daily via Reddit's API. The data format and processing pipeline are identical regardless of source.

## Ongoing updates

This project evolves as the space does. New themes, subreddits, and keywords are validated and added using the same process described above. Every change is logged in the changelog below, and the full validation records, keyword lists, and decision rationale are available in the [GitHub repository](https://github.com/hopeshub/myfriendisai).

---

## Changelog

**March 15, 2026 — Keyword expansion (discovery batch)**
- Added 16 validated keywords across all 6 themes via co-occurrence analysis
- Addiction: chatbot addiction, almost relapsed, finally deleted, the craving, so addictive
- Consciousness: sapience, tulpa, lemoine, soulbonder
- Sexual/ERP: erps, erping
- Rupture: lobotomies, lobotomizing, lobotomised
- Therapy: emotional support, coping mechanism
- All keywords validated at ≥80% precision. Full results: `docs/validation_discovery_batch.md`

**March 15, 2026 — Keyword validation methodology (v8 → v9)**
- Narrowed from 15 overlapping categories to 6 defensible themes
- Rebuilt keyword classification pipeline with FTS5 full-text search
- Conducted co-occurrence discovery analysis to surface data-driven keyword candidates
- Identified and excluded SpicyChat bot-building spam from 2 prolific authors

**March 13, 2026 — Live daily collection begins**
- Automated daily collection via launchd (local) replacing backfill pipeline
- 27 active subreddits collected daily at 6:00 AM PT

**March 2026 — Subreddit corpus finalized at 27 active communities**
- Expanded from 19 to 29 communities, then deactivated 2 (JanitorAI_Official, SillyTavernAI excluded from keyword matching due to bot-card pollution)
- Tier structure: 4 general AI (T0), 6 primary companionship (T1), 11 platform-specific (T2), 6 recovery/dependency (T3)
