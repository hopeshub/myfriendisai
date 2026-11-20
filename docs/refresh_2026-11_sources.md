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

## Added 2026-11-20 (merges #4 and #8, and the review fixes)

| Copy | Figure | Source |
|---|---|---|
| Romance story: "held at the late-2025 mix of communities, the rate was roughly flat through September 2026 and rose only in October, on thin data" | Held-mix romance per 1,000: 4.3 (Q4 2025), 4.7 (Q1 2026), 3.8 (Q2), 4.9 (Q3), 6.6 (Oct). Pooled: 4.3 → 7.0 (Q3) → 8.2 (Oct). Mix is 78% of the Q4→Q3 rise and 42% of the Q4→Oct rise | Shift-share on the database, read-only, 2026-11-20, weights = each community's Q4-2025 share of measurable posts (the method in the first section) |
| Changelog: sex/ERP "about 3–9% from May 2026 on" (the excluded moderator account) | −6.6% (May), −4.0% (Jul), −2.6% (Aug), −8.2% (Sep), −6.0% (Oct, with the seeding ring); June untouched | Real-database before/after posted on PR #4; confirmed by the published export after the merge |
| Homepage §5: cluster post volume "rose 350% in 2025 alone" | 17,440 measurable posts (2024) → 78,393 (2025) across the 11 T4 communities; 319% across the original nine | Trial export on a `VACUUM INTO` copy after the backfill, identical to the real backfill's counts |
| §5: "more than 10,000 posts a month" | 16,732 / 17,417 / 15,552 (Aug–Oct 2026) | same |
| §5: r/antiAI "topped every other community in the cluster, and it has stayed there" | Largest every month from Aug 2025 to Oct 2026, including the two new communities | same |
| §5: "AI bros" in titles "well over ten times more often than 'AI girlfriend'" | 3,754 vs 140 titles (26.8×) across the 11 communities; 27.4× across the nine | same, case-insensitive substring match on titles |
| §5: r/cogsuckers "a few dozen posts a month" | 29–69 measurable posts a month, Jun–Oct 2026 (peak 307, Nov 2025) | same |
| r/ChaiApp page note: "about three in four from 2024 to early 2026, and more than 80% every month since May 2026 (90% in October)"; "about 2,000" submitted a month | Share stored as removed/deleted: 61–85% Jan 2024–Apr 2026; 83–90% May–Oct 2026 (97% in partial November). All posts: 1,750–2,939 a month, May–Oct 2026 | Database, read-only, 2026-11-20 |
| r/therapyGPT page note and About page: "under 2% of the posts … about 40% of the therapy line" | 40% of therapy tags since April 2025 from under 2% of the denominator, had it been included | Refresh pass (handoff D2), full archive pull of r/therapyGPT |
