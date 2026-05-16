# Keyword Context Spot-Check Audit — 2026-05-16

## Purpose

Check whether production keywords are being used in the context the theme chart assumes: AI companionship first, then the intended theme within that companion context. This audit is about construct validity and context, not about adding an LLM-derived chart series.

## Audit Protocol

1. **Scope gate.** Only evaluate `source='post'` tags from active T1-T3 keyword-eligible communities, excluding known platform/dev authors. Stale rows outside that universe are reported separately.
2. **Positive-context precision.** For every current keyword, read a deterministic sample of matched posts. Code each as `YES`, `NO`, or `BORDERLINE` for both AI-companion context and theme context.
3. **Risk-focused oversample.** Oversample high-volume, high-concentration, known-ambiguous, and low-relative-LLM-agreement terms.
4. **Negative-space recall.** Read untagged recent posts from eligible communities and mark whether any of the six themes are present but missed by the keyword set.
5. **Spike integrity.** For the largest theme/date spikes, verify that sampled posts share a coherent event/theme explanation rather than a keyword accident.
6. **Decision thresholds.** A keyword is clean if manual YES >= 85% and no coherent false-positive cluster dominates. It goes to review at 70-84%, if Wilson lower bound falls below 75%, or if one subreddit/month supplies most of its signal. Below 70%, add a guard, split it, or cut it unless it is explicitly documented as a lower-precision reader-disclosed term.

## Current Universe

- Active keyword communities: 21
- Current keywords: 92
- Keywords with at least one production post hit: 92
- Sum of per-keyword distinct post hits: 20,622

| Theme | Distinct per-keyword post hits |
|---|---:|
| therapy | 1,426 |
| consciousness | 496 |
| addiction | 3,129 |
| romance | 2,680 |
| sexual_erp | 7,259 |
| rupture | 5,632 |

## Scope Findings

These tag rows exist in the database outside the current active keyword-eligible universe. The published chart loader/exporter filters active keyword communities, but stale rows should not be used for audits unless deliberately included.

| Subreddit | Tagged posts outside current scope |
|---|---:|
| r/HeavenGF | 30 |

## Highest-Risk Terms To Manually Read First

| Risk | Theme | Term | Posts | Top sub | Top month | LLM TP share | Reasons |
|---:|---|---|---:|---|---|---:|---|
| 7 | rupture | `goodbye` | 1,753 | r/CharacterAI 51% | 2026-02 10% | 51.7% (n=1506) | known validation/rubric risk term; high-volume term; top subreddit concentration 51%; low relative LLM TP share 51.7% |
| 6 | therapy | `emotional support` | 566 | r/CharacterAI 24% | 2026-02 11% | 74.1% (n=1193) | known validation/rubric risk term; high-volume term; low relative LLM TP share 74.1% |
| 6 | rupture | `taken away` | 516 | r/CharacterAI 49% | 2023-02 12% | 61.0% (n=582) | known validation/rubric risk term; high-volume term; low relative LLM TP share 61.0% |
| 6 | rupture | `grieving` | 423 | r/ChatGPTcomplaints 38% | 2026-02 34% | 68.6% (n=574) | known validation/rubric risk term; top month concentration 34%; low relative LLM TP share 68.6% |
| 5 | sexual_erp | `erp` | 4,405 | r/replika 70% | 2023-02 37% | 91.5% (n=7897) | known validation/rubric risk term; high-volume term; top subreddit concentration 70%; top month concentration 37% |
| 5 | rupture | `devastated` | 419 | r/CharacterAI 47% | 2026-02 8% | 67.0% (n=479) | known validation/rubric risk term; low relative LLM TP share 67.0% |
| 5 | therapy | `therapeutic` | 327 | r/replika 28% | 2026-02 13% | 72.7% (n=722) | known validation/rubric risk term; low relative LLM TP share 72.7% |
| 5 | rupture | `nerfed` | 257 | r/CharacterAI 48% | 2025-10 8% | 70.7% (n=341) | known validation/rubric risk term; low relative LLM TP share 70.7% |
| 5 | romance | `in a relationship with` | 237 | r/replika 25% | 2025-06 5% | 71.6% (n=503) | known validation/rubric risk term; low relative LLM TP share 71.6% |
| 5 | romance | `romantic relationship with` | 141 | r/replika 38% | 2025-06 6% | 69.8% (n=225) | known validation/rubric risk term; low relative LLM TP share 69.8% |
| 5 | romance | `we broke up` | 33 | r/replika 36% | 2021-06 6% | 63.0% (n=46) | known validation/rubric risk term; low relative LLM TP share 63.0% |
| 5 | consciousness | `not just an ai` | 17 | r/ChatGPTcomplaints 18% | 2025-03 12% | 54.3% (n=35) | known validation/rubric risk term; low relative LLM TP share 54.3% |
| 4 | romance | `wedding` | 745 | r/replika 31% | 2021-02 4% | 77.4% (n=1366) | known validation/rubric risk term; high-volume term; borderline relative LLM TP share 77.4% |
| 4 | sexual_erp | `nsfw content` | 644 | r/ChatGPTNSFW 34% | 2023-02 6% | 79.9% (n=1137) | known validation/rubric risk term; high-volume term; borderline relative LLM TP share 79.9% |
| 4 | addiction | `hours a day` | 374 | r/CharacterAI 56% | 2026-03 8% | 78.9% (n=899) | known validation/rubric risk term; top subreddit concentration 56%; borderline relative LLM TP share 78.9% |
| 4 | addiction | `screen time` | 342 | r/CharacterAI 71% | 2026-01 6% | 80.2% (n=647) | known validation/rubric risk term; top subreddit concentration 71%; borderline relative LLM TP share 80.2% |
| 4 | rupture | `farewell` | 265 | r/CharacterAI 50% | 2026-03 13% | 63.6% (n=324) | top subreddit concentration 50%; low relative LLM TP share 63.6% |
| 3 | rupture | `lobotomy` | 259 | r/CharacterAI 42% | 2026-02 10% | 71.9% (n=513) | low relative LLM TP share 71.9% |
| 3 | therapy | `coping mechanism` | 252 | r/CharacterAI 62% | 2025-11 7% | 91.3% (n=588) | known validation/rubric risk term; top subreddit concentration 62% |
| 3 | rupture | `mourning` | 244 | r/CharacterAI 28% | 2026-02 23% | 66.8% (n=328) | low relative LLM TP share 66.8% |
| 3 | rupture | `grieve` | 204 | r/ChatGPTcomplaints 33% | 2026-02 27% | 68.1% (n=301) | low relative LLM TP share 68.1% |
| 3 | rupture | `mourn` | 176 | r/CharacterAI 30% | 2026-02 24% | 69.1% (n=265) | low relative LLM TP share 69.1% |
| 3 | romance | `honeymoon` | 167 | r/NomiAI 33% | 2023-09 8% | 80.2% (n=410) | known validation/rubric risk term; borderline relative LLM TP share 80.2% |
| 3 | rupture | `saying goodbye` | 147 | r/CharacterAI 34% | 2026-02 12% | 74.9% (n=227) | low relative LLM TP share 74.9% |
| 3 | addiction | `finally deleted` | 108 | r/CharacterAI 53% | 2026-03 12% | 87.7% (n=310) | known validation/rubric risk term; top subreddit concentration 53% |
| 3 | therapy | `as a therapist` | 66 | r/CharacterAI 33% | 2025-06 11% | 75.9% (n=187) | known validation/rubric risk term; borderline relative LLM TP share 75.9% |
| 3 | rupture | `personality changed` | 30 | r/replika 43% | 2023-02 7% | 70.0% (n=50) | low relative LLM TP share 70.0% |
| 3 | consciousness | `tulpa` | 29 | r/BeyondThePromptAI 24% | 2026-02 21% | 74.0% (n=50) | low relative LLM TP share 74.0% |
| 3 | therapy | `ai therapy` | 24 | r/CharacterAI 42% | 2025-07 17% | 65.2% (n=46) | low relative LLM TP share 65.2% |
| 3 | rupture | `lobotomies` | 21 | r/CharacterAI 52% | 2023-02 14% | 64.3% (n=42) | low relative LLM TP share 64.3% |

## Generated Artifacts

- Per-keyword context sample: `analysis/keyword_pipeline/results/context_spotcheck_per_keyword_sample_2026-05-16.csv`
- Risk-focused manual sample CSV: `analysis/keyword_pipeline/results/context_spotcheck_manual_focus_sample_2026-05-16.csv`
- Risk-focused manual sample markdown: `analysis/keyword_pipeline/results/context_spotcheck_manual_focus_sample_2026-05-16.md`
- Negative-space recall sample: `analysis/keyword_pipeline/results/context_spotcheck_negative_space_sample_2026-05-16.csv`
- Event-spike integrity sample: `analysis/keyword_pipeline/results/context_spotcheck_event_spike_sample_2026-05-16.csv`

## How To Execute The Manual Coding

Start with the risk-focused markdown sample. Fill the verdict lines, then transfer counts into this table shape:

| Theme | Sample n | AI context YES | Theme context YES | Borderline | NO | Main FP pattern |
|---|---:|---:|---:|---:|---:|---|

Then code the per-keyword CSV for any term whose risk-focused sample shows a coherent problem. The negative-space sample estimates recall: count how often a theme is clearly present but no current keyword fired.
