# Cross-Theme Keyword Overlap Analysis

_Generated 2026-04-20 12:14_

**Source:** `post_keyword_tags` (production regex tags from `keywords_v8.yaml`,
both post and comment sources). Scope matches `keyword_trends.json`: T1-T3
companion subreddits (22 communities).

**Corpus:** 14,786 posts with at least one theme tag.

## Unique posts per theme

| Theme | Unique posts | % of tagged corpus |
|-------|-------------|-------------------|
| therapy | 1,442 | 9.75% |
| consciousness | 1,723 | 11.65% |
| addiction | 1,784 | 12.07% |
| romance | 2,178 | 14.73% |
| sexual_erp | 6,589 | 44.56% |
| rupture | 1,697 | 11.48% |

## Pairwise overlap (post counts)

| | therapy | consciousness | addiction | romance | sexual_erp | rupture |
|---|---|---|---|---|---|---|
| **therapy** | — | 49 | 79 | 50 | 91 | 30 |
| **consciousness** | 49 | — | 19 | 49 | 49 | 38 |
| **addiction** | 79 | 19 | — | 14 | 26 | 13 |
| **romance** | 50 | 49 | 14 | — | 74 | 20 |
| **sexual_erp** | 91 | 49 | 26 | 74 | — | 95 |
| **rupture** | 30 | 38 | 13 | 20 | 95 | — |

## Overlap as % of smaller theme

| Pair | Overlap | Smaller theme (n) | % of smaller |
|------|--------|-------------------|--------------|
| sexual_erp × rupture | 95 | rupture (1,697) | 5.6% |
| therapy × sexual_erp | 91 | therapy (1,442) | 6.3% |
| therapy × addiction | 79 | therapy (1,442) | 5.5% |
| romance × sexual_erp | 74 | romance (2,178) | 3.4% |
| therapy × romance | 50 | therapy (1,442) | 3.5% |
| therapy × consciousness | 49 | therapy (1,442) | 3.4% |
| consciousness × romance | 49 | consciousness (1,723) | 2.8% |
| consciousness × sexual_erp | 49 | consciousness (1,723) | 2.8% |
| consciousness × rupture | 38 | rupture (1,697) | 2.2% |
| therapy × rupture | 30 | therapy (1,442) | 2.1% |
| addiction × sexual_erp | 26 | addiction (1,784) | 1.5% |
| romance × rupture | 20 | rupture (1,697) | 1.2% |
| consciousness × addiction | 19 | consciousness (1,723) | 1.1% |
| addiction × romance | 14 | addiction (1,784) | 0.8% |
| addiction × rupture | 13 | rupture (1,697) | 0.8% |

## Triple+ overlap

**43 posts** match 3 or more themes simultaneously.

### Examples (up to 10)

| Post ID | Subreddit | Themes matched |
|---------|-----------|----------------|
| 101myuo | replika | consciousness, addiction, romance |
| 10ltyir | CharacterAI | consciousness, romance, sexual_erp, rupture |
| 10un1gw | replika | consciousness, sexual_erp, rupture |
| 10ybk8g | replika | consciousness, romance, sexual_erp |
| 10zsojf | replika | therapy, romance, sexual_erp, rupture |
| 1111rgf | replika | therapy, consciousness, sexual_erp |
| 1115upo | replika | consciousness, romance, sexual_erp |
| 115h2y1 | replika | consciousness, sexual_erp, rupture |
| 11o0mfx | CharacterAI | therapy, consciousness, sexual_erp |
| 13dxvi1 | replika | therapy, romance, sexual_erp |

## Theme exclusivity

A theme is exclusive when a post matches that theme and no other.

| Theme | Total | Exclusive | Exclusivity % |
|-------|-------|-----------|---------------|
| therapy | 1,442 | 1,181 | 81.9% |
| consciousness | 1,723 | 1,555 | 90.2% |
| addiction | 1,784 | 1,652 | 92.6% |
| romance | 2,178 | 2,004 | 92.0% |
| sexual_erp | 6,589 | 6,289 | 95.4% |
| rupture | 1,697 | 1,533 | 90.3% |

## Interpretation

- **Highest absolute overlap:** sexual_erp × rupture with 95 posts in common.
- **Highest proportional overlap:** therapy × sexual_erp (91 posts, 6.3% of the smaller theme).
- **Most exclusive theme:** sexual_erp (95.4% exclusive).
- **Least exclusive theme:** therapy (81.9% exclusive).
- **Policy:** Themes are non-exclusive by design. Trend lines count unique posts per theme. Triple+ overlap is 0.3% of tagged posts — small enough that allowing overlap doesn't distort the chart.
