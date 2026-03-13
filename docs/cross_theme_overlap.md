# Cross-Theme Keyword Overlap Analysis

_Generated 2026-03-13 15:09_

**Scope:** T1–T3 subreddits (22 communities), 390,842 total posts

## Step 2: Unique Posts Per Theme

| Theme | Unique Posts | % of corpus |
|-------|-------------|-------------|
| THERAPY | 412 | 0.11% |
| CONSCIOUSNESS | 1,285 | 0.33% |
| ADDICTION | 910 | 0.23% |
| ROMANCE | 1,805 | 0.46% |
| SEXUAL_ERP | 9,335 | 2.39% |
| RUPTURE | 465 | 0.12% |

## Step 3: Pairwise Overlap Matrix (post counts)

| | THERAPY | CONSCIOUSNESS | ADDICTION | ROMANCE | SEXUAL_ERP | RUPTURE |
|---|---|---|---|---|---|---|
| **THERAPY** | — | 26 | 5 | 16 | 90 | 6 |
| **CONSCIOUSNESS** | 26 | — | 6 | 40 | 173 | 9 |
| **ADDICTION** | 5 | 6 | — | 2 | 20 | 1 |
| **ROMANCE** | 16 | 40 | 2 | — | 130 | 6 |
| **SEXUAL_ERP** | 90 | 173 | 20 | 130 | — | 94 |
| **RUPTURE** | 6 | 9 | 1 | 6 | 94 | — |

## Step 4: Overlap as % of Smaller Theme

| Pair | Overlap Posts | Smaller Theme | % of Smaller |
|------|--------------|---------------|-------------|
| CONSCIOUSNESS × SEXUAL_ERP | 173 | CONSCIOUSNESS (1,285) | 13.5% |
| ROMANCE × SEXUAL_ERP | 130 | ROMANCE (1,805) | 7.2% |
| SEXUAL_ERP × RUPTURE | 94 | RUPTURE (465) | 20.2% |
| THERAPY × SEXUAL_ERP | 90 | THERAPY (412) | 21.8% |
| CONSCIOUSNESS × ROMANCE | 40 | CONSCIOUSNESS (1,285) | 3.1% |
| THERAPY × CONSCIOUSNESS | 26 | THERAPY (412) | 6.3% |
| ADDICTION × SEXUAL_ERP | 20 | ADDICTION (910) | 2.2% |
| THERAPY × ROMANCE | 16 | THERAPY (412) | 3.9% |
| CONSCIOUSNESS × RUPTURE | 9 | RUPTURE (465) | 1.9% |
| THERAPY × RUPTURE | 6 | THERAPY (412) | 1.5% |
| CONSCIOUSNESS × ADDICTION | 6 | ADDICTION (910) | 0.7% |
| ROMANCE × RUPTURE | 6 | RUPTURE (465) | 1.3% |
| THERAPY × ADDICTION | 5 | THERAPY (412) | 1.2% |
| ADDICTION × ROMANCE | 2 | ADDICTION (910) | 0.2% |
| ADDICTION × RUPTURE | 1 | RUPTURE (465) | 0.2% |

## Step 5: Triple+ Theme Overlap

**30 posts** match 3 or more themes simultaneously.

### Example Posts (up to 10)

| Post ID | Subreddit | Themes Matched |
|---------|-----------|----------------|
| 1ptvczj | ChatGPTcomplaints | THERAPY, CONSCIOUSNESS, SEXUAL_ERP |
| 1q9otwh | ChatGPTcomplaints | THERAPY, ROMANCE, SEXUAL_ERP |
| 1qer4pc | ChatGPTcomplaints | THERAPY, CONSCIOUSNESS, SEXUAL_ERP |
| 1qimz1e | ChatGPTcomplaints | CONSCIOUSNESS, ROMANCE, SEXUAL_ERP |
| 1rbt7lq | ChatGPTcomplaints | THERAPY, CONSCIOUSNESS, ROMANCE, SEXUAL_ERP |
| 1rc4h1o | ChatGPTcomplaints | THERAPY, CONSCIOUSNESS, ROMANCE, SEXUAL_ERP |
| 1rhexu8 | ChatGPTcomplaints | CONSCIOUSNESS, SEXUAL_ERP, RUPTURE |
| 10ybk8g | replika | CONSCIOUSNESS, ROMANCE, SEXUAL_ERP |
| 1115upo | replika | CONSCIOUSNESS, ROMANCE, SEXUAL_ERP |
| 115h2y1 | replika | CONSCIOUSNESS, SEXUAL_ERP, RUPTURE |

## Step 6: Theme Exclusivity

| Theme | Total Posts | Exclusive Posts | Exclusivity % |
|-------|------------|----------------|---------------|
| THERAPY | 412 | 286 | 69.4% |
| CONSCIOUSNESS | 1,285 | 1,059 | 82.4% |
| ADDICTION | 910 | 877 | 96.4% |
| ROMANCE | 1,805 | 1,631 | 90.4% |
| SEXUAL_ERP | 9,335 | 8,860 | 94.9% |
| RUPTURE | 465 | 356 | 76.6% |

## Interpretation

### Which theme pairs have the most overlap?

**By raw count:** CONSCIOUSNESS × SEXUAL_ERP with 173 posts in common.

**By % of smaller theme:** THERAPY × SEXUAL_ERP with 21.8% overlap (90 posts).

### Are any themes largely redundant?

Pairs with >25% overlap of the smaller theme suggest partial redundancy. See the percentage table above.

### Does overlap suggest keyword movement?

Keywords that cause cross-theme bleeding should be reviewed if their overlap exceeds ~30% of the smaller theme. The raw LIKE matching means short keywords like `erp`, `kink`, `wedding` may match inside longer words — verify manually if needed.

### Recommendation: cross-theme overlap or deduplication?

- **Triple+ posts (30)** are a small fraction of the corpus; if cross-theme overlap is low overall, allowing it is fine.

- The most exclusive theme is **ADDICTION** (96.4% exclusive) — its trend line is cleanest.

- The least exclusive theme is **THERAPY** (69.4% exclusive) — its trend line has the most cross-contamination.

- **Recommendation:** Allow cross-theme overlap in trend lines (count posts per theme independently). The themes capture distinct enough discourses that deduplication would undersell real co-occurrence patterns. Document that trend lines count unique-per-theme, not unique-across-all-themes.
