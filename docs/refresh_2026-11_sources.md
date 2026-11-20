# Sources for the November 2026 copy edits

Every figure the November 2026 copy states, with where it comes from. Most come from a refresh pass that ran on a byte copy of `data/tracker.db`, taken 2026-11-19 at 15:20 PST while the database was idle. That pass rebuilt the site's population independently: the 24 keyword communities, measurable posts only, excluded authors dropped, post-only tags, UTC months. Its monthly totals matched `data/keyword_trends.json`. The full write-up is the handoff in `docs/refresh_2026-11/` (local).

## Community mix (addiction and romance stories, About page, changelog)

| Copy | Figure | Source |
|---|---|---|
| r/CharacterAI "70–85% through most of 2025, under half today" | 70.8–84.1% of measurable keyword-community posts, Jan–Oct 2025; 43.4–48.5%, Jul–Oct 2026 | `_total_posts` in `keyword_trends.json` versus `composition_trends.json` (excluding r/CharacterAI) |
| "about two thirds" in late 2025 | 63–65%, Nov–Dec 2025; 67% for Q4 2025 | same |
| Addiction "held at the late-2025 mix of communities, rose about a quarter into early 2026 and has been level since" | 10.2 (Q4 2025) → 13.2 (Q2 2026) → 11.6 (Q3) → 11.9 (Oct), per 1,000, held at the Q4-2025 mix | Shift-share on the database copy: each community's own monthly rate, weighted by its Q4-2025 share of measurable posts. Renormalising over the communities present moves any value by at most 0.1 |
| "Much of the 2026 rise in the addiction and romance lines comes from a change in which communities are posting" | About 80% of addiction's Q4 2025 → Oct 2026 rise is mix. Romance stays flat at the held mix through Q3 | same |

## Sex/ERP recall (sex/ERP story, changelog)

| Copy | Figure | Source |
|---|---|---|
| "In a hand-checked sample of 600 posts they found 9 of 16 sexual posts from 2023 … and none of 14 from 2025–26" | 9/16 in 2023 against 0/14 in 2025–26 (Fisher exact p ≈ 0.001) | Period-stratified recall audit (CLAUDE.md item 13). 600 measurable posts, 150 per year for 2023–2026 (100 non-Character.AI, 50 r/CharacterAI, weighted back). Hand-coded under the locked topical reading, with coders blind to tags and dates. Each post was coded once, so there is no agreement measure |

## Character.AI bankruptcy marker (themes.ts EVENTS, changelog)

| Copy | Figure | Source |
|---|---|---|
| Filed for bankruptcy on October 12, 2026 | Chapter 11 petition, 2026-10-12 | Press coverage of the filing (TechCrunch, 2026-10-13; Unite.AI) |
| "r/CharacterAI's rupture rate tripled in the week of the filing" | 28.4 per 1,000 (33 of 1,163 measurable posts) in the week of the filing, against a 9.1 average over the six weeks before | Database copy, weekly buckets. The matched words that week were "devastated", "goodbye" and "mourning" |

## Replika (homepage)

| Copy | Figure | Source |
|---|---|---|
| r/replika "from 32,000 posts a year to under 5,000" | 32,049 measurable posts in 2023; 4,024 in 2025 | Per-community volumes in `web/public/dataset/v1/` |
| "part of that conversation moved to Replika's official subreddit, which this tracker doesn't follow" | r/ReplikaOfficial is untracked and posts 300–600 a month in 2026. r/ReplikaLovers (tracked) posts 400–550 a month | Arctic Shift monthly post aggregates, November 2026 |

## About page, composition note

| Copy | Figure | Source |
|---|---|---|
| Romance July 2026 "5.3 per thousand with them and 3.6 without" (the May-2026 additions) | 5.27 (52 of 9,869) and 3.55 | 5.27 is from `keyword_trends.json`. 3.55 is the without-additions figure recorded in CLAUDE.md after the 2026-10-24 July-hole repair. The copy previously said 5.5 and 3.8, figures from before that repair |
