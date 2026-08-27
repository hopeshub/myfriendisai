# Corpus composition — quarterly re-run, 2026-08-27

Scheduled quarterly check (due ~2026-08-18) of `analysis/keyword_pipeline/corpus_composition.py`,
window extended to `LAST_COMPLETE_MONTH = 2026-07`. Read-only analysis; full output in the
session scratchpad, key figures recorded here. Spec: `docs/corpus_composition_plan.md`;
prior run: 2026-05-16 (window through 2026-04).

## Headline: disclosures still hold, one copy edit made

- **Concentration is unchanged in kind.** Top-3 subreddit share per theme: romance 56.7%,
  sexual_erp 68.4%, consciousness 68.3%, therapy 62.6%, addiction 92.3%, rupture 77.7%.
  The About-page claim "two or three subreddits usually account for most of a theme's posts"
  remains accurate.
- **One quantitative claim drifted:** r/replika's share of sexual_erp is now **48.7%**
  (was 50% at the May run). The About page said "well over half r/replika alone" — softened
  to "roughly half" (`web/app/about/page.tsx`), 2026-08-27.

## Per-theme top-1 / tier mix (coverage window → 2026-07)

| Theme | Posts | Top-1 sub | Top-1 % | Tier mix |
|---|---|---|---|---|
| romance | 2,662 | r/replika | 22.1% | T1 75.5 / T2 23.5 / T3 1.0 |
| sexual_erp | 7,181 | r/replika | 48.7% | T1 66.9 / T2 30.9 / T3 2.2 |
| consciousness | 498 | r/beyondthepromptai | 34.9% | T1 92.0 / T2 7.2 / T3 0.8 |
| therapy | 1,538 | r/characterai | 31.4% | T1 78.8 / T2 11.8 / T3 9.4 |
| addiction | 3,324 | r/character_ai_recovery | 48.0% | T1 39.0 / T2 2.3 / T3 58.7 |
| rupture | 5,517 | r/characterai | 44.3% | T1 88.8 / T2 8.7 / T3 2.6 |

## Composition drift (tier share of corpus posts)

T1 share continues its slow decline as T2/T3 grow: 2024 = 83.7/15.8/0.5,
2025 = 73.9/24.6/1.5, 2026-to-date = **70.3/26.3/3.3**. Same trajectory as May; no step change.

## Leave-one-sub-out (shape fragility)

Largest single-sub dependences, consistent with May: sexual_erp → r/replika (corr drops to
0.615 removed; level −42%), addiction → r/character_ai_recovery (level −50%), consciousness →
r/beyondthepromptai (corr 0.781; level −40%), romance → r/myboyfriendisai (corr 0.811; −18%).

## Normalization comparison (B5)

All six themes remain below 0.9 on at least one reweighting (sub-equal corr 0.61–0.91) —
the known, documented reason the published line is volume-weighted and read direction-only.
No change to that posture.

## Next re-run

~2026-11 (with the comprehensiveness re-audit window).
