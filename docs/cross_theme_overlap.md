# Cross-Theme Keyword Overlap Analysis

_Generated 2026-05-12 15:56_

**Source:** `post_keyword_tags` (production regex tags from `keywords_v8.yaml`,
both post and comment sources). Scope matches `keyword_trends.json`: T1-T3
companion subreddits (22 communities).

**Corpus:** 15,305 posts with at least one theme tag.

## Unique posts per theme

| Theme | Unique posts | % of tagged corpus |
|-------|-------------|-------------------|
| therapy | 1,394 | 9.11% |
| consciousness | 424 | 2.77% |
| addiction | 1,822 | 11.90% |
| romance | 2,090 | 13.66% |
| sexual_erp | 5,390 | 35.22% |
| rupture | 5,026 | 32.84% |

## Pairwise overlap (post counts)

| | therapy | consciousness | addiction | romance | sexual_erp | rupture |
|---|---|---|---|---|---|---|
| **therapy** | — | 35 | 62 | 50 | 65 | 111 |
| **consciousness** | 35 | — | 8 | 23 | 9 | 69 |
| **addiction** | 62 | 8 | — | 15 | 18 | 67 |
| **romance** | 50 | 23 | 15 | — | 55 | 82 |
| **sexual_erp** | 65 | 9 | 18 | 55 | — | 248 |
| **rupture** | 111 | 69 | 67 | 82 | 248 | — |

## Overlap as % of smaller theme

| Pair | Overlap | Smaller theme (n) | % of smaller |
|------|--------|-------------------|--------------|
| sexual_erp × rupture | 248 | rupture (5,026) | 4.9% |
| therapy × rupture | 111 | therapy (1,394) | 8.0% |
| romance × rupture | 82 | romance (2,090) | 3.9% |
| consciousness × rupture | 69 | consciousness (424) | 16.3% |
| addiction × rupture | 67 | addiction (1,822) | 3.7% |
| therapy × sexual_erp | 65 | therapy (1,394) | 4.7% |
| therapy × addiction | 62 | therapy (1,394) | 4.4% |
| romance × sexual_erp | 55 | romance (2,090) | 2.6% |
| therapy × romance | 50 | therapy (1,394) | 3.6% |
| therapy × consciousness | 35 | consciousness (424) | 8.3% |
| consciousness × romance | 23 | consciousness (424) | 5.4% |
| addiction × sexual_erp | 18 | addiction (1,822) | 1.0% |
| addiction × romance | 15 | addiction (1,822) | 0.8% |
| consciousness × sexual_erp | 9 | consciousness (424) | 2.1% |
| consciousness × addiction | 8 | consciousness (424) | 1.9% |

## Triple+ overlap

**54 posts** match 3 or more themes simultaneously.

### Examples (up to 10)

| Post ID | Subreddit | Themes matched |
|---------|-----------|----------------|
| 10ltyir | CharacterAI | romance, sexual_erp, rupture |
| 10ybk8g | replika | romance, sexual_erp, rupture |
| 10zsojf | replika | therapy, romance, sexual_erp, rupture |
| 1117jxd | replika | therapy, sexual_erp, rupture |
| 115hhgp | replika | therapy, consciousness, rupture |
| 11pflxy | replika | therapy, sexual_erp, rupture |
| 12u8mlx | replika | romance, sexual_erp, rupture |
| 13dxvi1 | replika | therapy, romance, sexual_erp |
| 14620zu | replika | therapy, sexual_erp, rupture |
| 15ryueq | replika | romance, sexual_erp, rupture |

## Theme exclusivity

A theme is exclusive when a post matches that theme and no other.

| Theme | Total | Exclusive | Exclusivity % |
|-------|-------|-----------|---------------|
| therapy | 1,394 | 1,120 | 80.3% |
| consciousness | 424 | 306 | 72.2% |
| addiction | 1,822 | 1,676 | 92.0% |
| romance | 2,090 | 1,900 | 90.9% |
| sexual_erp | 5,390 | 5,021 | 93.2% |
| rupture | 5,026 | 4,505 | 89.6% |

## Interpretation

- **Highest absolute overlap:** sexual_erp × rupture with 248 posts in common.
- **Highest proportional overlap:** consciousness × rupture (69 posts, 16.3% of the smaller theme).
- **Most exclusive theme:** sexual_erp (93.2% exclusive).
- **Least exclusive theme:** consciousness (72.2% exclusive).
- **Policy:** Themes are non-exclusive by design. Trend lines count unique posts per theme. Triple+ overlap is 0.4% of tagged posts — small enough that allowing overlap doesn't distort the chart.
