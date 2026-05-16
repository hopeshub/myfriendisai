# Spot-check scored summary

Coverage: precision 1820/1821, comments 349/349, negspace 160/160, gold 1/72


## Per-theme precision band (volume-weighted)

| Theme | topical | strict | pooled n |
|---|--:|--:|--:|
| therapy | 55.1% | 40.1% | 159 |
| consciousness | 68.0% | 48.7% | 191 |
| addiction | 90.4% | 78.0% | 334 |
| romance | 75.4% | 53.3% | 411 |
| sexual_erp | 92.8% | 74.3% | 298 |
| rupture | 70.2% | 58.4% | 427 |

## Precision x year (temporal comparability)

| Theme | 2023 | 2024 | 2025 | 2026 |
|---|--:|--:|--:|--:|
| therapy | 73.7% (n38) | 80.0% (n40) | 66.7% (n51) | 59.1% (n22) |
| consciousness | 66.7% (n15) | 66.7% (n9) | 58.5% (n94) | 60.8% (n51) |
| addiction | 76.7% (n30) | 74.6% (n59) | 88.9% (n153) | 94.2% (n86) |
| romance | 74.5% (n106) | 71.9% (n64) | 78.0% (n164) | 74.2% (n31) |
| sexual_erp | 93.4% (n152) | 88.6% (n44) | 75.0% (n64) | 62.5% (n16) |
| rupture | 87.6% (n105) | 68.8% (n77) | 67.0% (n94) | 82.0% (n128) |

## Lowest per-keyword topical precision (n>=8)

| Theme | keyword | n | topical | strict | Wilson LB | prod vol |
|---|---|--:|--:|--:|--:|--:|
| consciousness | `not just an ai` | 17 | 23.5% | 23.5% | 9.6% | 18 |
| romance | `husbando` | 20 | 35.0% | 10.0% | 18.1% | 68 |
| therapy | `emotional support` | 20 | 40.0% | 35.0% | 21.9% | 571 |
| consciousness | `more than code` | 20 | 45.0% | 30.0% | 25.8% | 34 |
| consciousness | `tulpa` | 20 | 45.0% | 30.0% | 25.8% | 29 |
| romance | `in a relationship with` | 20 | 45.0% | 20.0% | 25.8% | 238 |
| therapy | `therapeutic` | 20 | 45.0% | 35.0% | 25.8% | 328 |
| consciousness | `soulbonder` | 14 | 50.0% | 35.7% | 26.8% | 14 |
| rupture | `memory reset` | 11 | 54.5% | 9.1% | 28.0% | 11 |
| addiction | `I was hooked` | 20 | 55.0% | 45.0% | 34.2% | 47 |
| rupture | `goodbye` | 20 | 55.0% | 45.0% | 34.2% | 1754 |
| rupture | `lobotomies` | 20 | 55.0% | 40.0% | 34.2% | 21 |
| romance | `romantic relationship with` | 20 | 60.0% | 40.0% | 38.7% | 141 |
| rupture | `devastated` | 20 | 60.0% | 60.0% | 38.7% | 419 |
| rupture | `grieving` | 20 | 60.0% | 60.0% | 38.7% | 423 |
| consciousness | `sapience` | 14 | 64.3% | 50.0% | 38.8% | 14 |
| romance | `ai lover` | 20 | 65.0% | 30.0% | 43.3% | 51 |
| romance | `dating my` | 20 | 65.0% | 50.0% | 43.3% | 30 |
| romance | `we broke up` | 20 | 65.0% | 40.0% | 43.3% | 33 |
| rupture | `farewell` | 20 | 65.0% | 50.0% | 43.3% | 265 |

## Single-keyword fragility

| Theme | single-kw topical | multi-kw topical |
|---|--:|--:|
| therapy | 70.5% (n149) | 80.0% (n10) |
| consciousness | 58.8% (n160) | 71.0% (n31) |
| addiction | 81.2% (n229) | 97.1% (n105) |
| romance | 74.6% (n343) | 89.7% (n68) |
| sexual_erp | 84.9% (n212) | 87.5% (n40) |
| rupture | 76.1% (n326) | 77.6% (n85) |

## Comment precision
| Theme | topical | strict | n |
|---|--:|--:|--:|
| therapy | 76.7% | 65.0% | 60 |
| consciousness | 75.5% | 53.1% | 49 |
| addiction | 85.0% | 66.7% | 60 |
| romance | 68.3% | 48.3% | 60 |
| sexual_erp | 95.0% | 83.3% | 60 |
| rupture | 85.0% | 61.7% | 60 |

## Negative-space recall-miss rate
| Year | n | has-a-theme | miss rate |
|---|--:|--:|--:|
| 2023 | 40 | 10 | 25.0% |
| 2024 | 40 | 9 | 22.5% |
| 2025 | 40 | 17 | 42.5% |
| 2026 | 40 | 13 | 32.5% |

## Gold-anchor calibration

- Human coded: 1, overlap with fleet: 1
- Human YES rate: 0.0%
- Topical rubric: 100.0% YES, agrees with human 0.0%
- Strict rubric: 100.0% YES, agrees with human 0.0%
- Disagreement cases: 1
