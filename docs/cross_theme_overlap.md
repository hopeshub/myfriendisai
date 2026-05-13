# Cross-Theme Keyword Overlap Analysis

_Generated 2026-05-12 22:17_

**Source:** `post_keyword_tags` (production regex tags from `keywords_v8.yaml`,
both post and comment sources). Scope matches `keyword_trends.json`: T1-T3
companion subreddits (22 communities).

**Corpus:** 17,617 posts with at least one theme tag.

## Unique posts per theme

| Theme | Unique posts | % of tagged corpus |
|-------|-------------|-------------------|
| therapy | 1,394 | 7.91% |
| consciousness | 424 | 2.41% |
| addiction | 2,647 | 15.03% |
| romance | 2,260 | 12.83% |
| sexual_erp | 6,856 | 38.92% |
| rupture | 5,026 | 28.53% |

## Pairwise overlap (post counts)

| | therapy | consciousness | addiction | romance | sexual_erp | rupture |
|---|---|---|---|---|---|---|
| **therapy** | — | 35 | 82 | 59 | 74 | 111 |
| **consciousness** | 35 | — | 8 | 30 | 12 | 69 |
| **addiction** | 82 | 8 | — | 20 | 38 | 86 |
| **romance** | 59 | 30 | 20 | — | 73 | 92 |
| **sexual_erp** | 74 | 12 | 38 | 73 | — | 290 |
| **rupture** | 111 | 69 | 86 | 92 | 290 | — |

## Overlap as % of smaller theme

| Pair | Overlap | Smaller theme (n) | % of smaller |
|------|--------|-------------------|--------------|
| sexual_erp × rupture | 290 | rupture (5,026) | 5.8% |
| therapy × rupture | 111 | therapy (1,394) | 8.0% |
| romance × rupture | 92 | romance (2,260) | 4.1% |
| addiction × rupture | 86 | addiction (2,647) | 3.2% |
| therapy × addiction | 82 | therapy (1,394) | 5.9% |
| therapy × sexual_erp | 74 | therapy (1,394) | 5.3% |
| romance × sexual_erp | 73 | romance (2,260) | 3.2% |
| consciousness × rupture | 69 | consciousness (424) | 16.3% |
| therapy × romance | 59 | therapy (1,394) | 4.2% |
| addiction × sexual_erp | 38 | addiction (2,647) | 1.4% |
| therapy × consciousness | 35 | consciousness (424) | 8.3% |
| consciousness × romance | 30 | consciousness (424) | 7.1% |
| addiction × romance | 20 | romance (2,260) | 0.9% |
| consciousness × sexual_erp | 12 | consciousness (424) | 2.8% |
| consciousness × addiction | 8 | consciousness (424) | 1.9% |

## Triple+ overlap

**63 posts** match 3 or more themes simultaneously.

### Examples (up to 10)

| Post ID | Subreddit | Themes matched |
|---------|-----------|----------------|
| 10ltyir | CharacterAI | romance, sexual_erp, rupture |
| 10ybk8g | replika | romance, sexual_erp, rupture |
| 10zsojf | replika | therapy, romance, sexual_erp, rupture |
| 1117jxd | replika | therapy, sexual_erp, rupture |
| 115hhgp | replika | therapy, consciousness, rupture |
| 11ex6kh | replika | romance, sexual_erp, rupture |
| 11pflxy | replika | therapy, sexual_erp, rupture |
| 12u8mlx | replika | romance, sexual_erp, rupture |
| 13dxvi1 | replika | therapy, romance, sexual_erp |
| 14620zu | replika | therapy, sexual_erp, rupture |

## Theme exclusivity

A theme is exclusive when a post matches that theme and no other.

| Theme | Total | Exclusive | Exclusivity % |
|-------|-------|-----------|---------------|
| therapy | 1,394 | 1,089 | 78.1% |
| consciousness | 424 | 301 | 71.0% |
| addiction | 2,647 | 2,439 | 92.1% |
| romance | 2,260 | 2,028 | 89.7% |
| sexual_erp | 6,856 | 6,404 | 93.4% |
| rupture | 5,026 | 4,441 | 88.4% |

## Interpretation

- **Highest absolute overlap:** sexual_erp × rupture with 290 posts in common.
- **Highest proportional overlap:** consciousness × rupture (69 posts, 16.3% of the smaller theme).
- **Most exclusive theme:** sexual_erp (93.4% exclusive).
- **Least exclusive theme:** consciousness (71.0% exclusive).
- **Policy:** Themes are non-exclusive by design. Trend lines count unique posts per theme. Triple+ overlap is 0.4% of tagged posts — small enough that allowing overlap doesn't distort the chart.
