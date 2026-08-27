# Corpus composition — quarterly re-run, 2026-08-27 (corrected same day)

Scheduled quarterly check (due ~2026-08-18) of `analysis/keyword_pipeline/corpus_composition.py`,
window extended to `LAST_COMPLETE_MONTH = 2026-07`. Spec: `docs/corpus_composition_plan.md`;
prior run: 2026-05-16 (window through 2026-04).

## Correction (2026-08-27, same session)

The first pass of this re-run — and the 2026-05-16 run before it — used an inflated corpus:
the script selected `tier BETWEEN 1 AND 3 AND is_active=1` from `subreddit_config`, which has
**no `exclude_from_keywords` column**, so the three NSFW-scope subs excluded from the published
line since 2026-05-18 (r/AIGirlfriend, r/SpicyChatAI, r/ChatGPTNSFW) leaked their pre-exclusion
historical tags into every B1–B5 figure, despite the docstring's "mirrors the published
methodology" claim. Fixed 2026-08-27: the script now parses the exclusion flags from
`config/communities.yaml` (25 → 22 subs). Consequences of the correction:

- **r/replika is 59.1% of sexual_erp** on the published corpus (uncorrected pass said 48.7%,
  with r/chatgptnsfw absorbing 12.6%). The About-page claim "well over half r/replika alone"
  is **accurate and stands** — an interim copy softening made from the uncorrected number was
  reverted the same day, before any deploy.
- The May run's headline "sexual_erp is 50% r/replika alone" was likewise understated.

All figures below are from the **corrected** corpus (22 subs).

## Headline: disclosures hold

Top-3 subreddit share per theme: romance 61.2%, sexual_erp 75.7%, consciousness 69.8%,
therapy 65.7%, addiction 92.8%, rupture 80.4%. The About-page claim "two or three subreddits
usually account for most of a theme's posts" remains accurate, as does the replika claim above.

## Per-theme top-1 / tier mix (coverage window → 2026-07)

| Theme | Posts | Top-1 sub | Top-1 % | Tier mix (T1/T2/T3) |
|---|---|---|---|---|
| romance | 2,467 | r/replika | 23.8% | 81.5 / 17.4 / 1.1 |
| sexual_erp | 5,927 | r/replika | 59.1% | 81.1 / 16.3 / 2.6 |
| consciousness | 487 | r/beyondthepromptai | 35.7% | 94.0 / 5.1 / 0.8 |
| therapy | 1,465 | r/characterai | 33.0% | 82.7 / 7.4 / 9.9 |
| addiction | 3,306 | r/character_ai_recovery | 48.2% | 39.2 / 1.8 / 59.0 |
| rupture | 5,331 | r/characterai | 45.8% | 91.9 / 5.5 / 2.7 |

## Composition drift (tier share of corpus posts)

T1 share declines slowly as T2/T3 grow: 2024 = 85.9/13.6/0.5, 2025 = 82.1/16.3/1.6,
2026-to-date = **77.6/18.7/3.7**. Same trajectory as May; no step change. (T3's rise from
0.5% → 3.7% in two years is the notable secondary trend — recovery communities are a growing
share of corpus volume.)

## Leave-one-sub-out (shape fragility)

Largest single-sub dependences: sexual_erp → r/replika (corr drops to 0.625 removed; level
−50%), addiction → r/character_ai_recovery (level −51%), consciousness → r/beyondthepromptai
(corr 0.774; level −41%), romance → r/myboyfriendisai (corr 0.748; level −20%).

## Normalization comparison (B5)

All six themes remain below 0.9 on at least one reweighting (sub-equal corr 0.56–0.90) —
the known, documented reason the published line is volume-weighted and read direction-only.
No change to that posture.

## Next re-run

~2026-11 (with the comprehensiveness re-audit window).
