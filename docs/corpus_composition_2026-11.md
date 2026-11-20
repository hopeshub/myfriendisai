# Corpus composition — quarterly re-run, 2026-11-20

Scheduled quarterly check (due ~2026-11) of `analysis/keyword_pipeline/corpus_composition.py`,
window through `LAST_COMPLETE_MONTH = 2026-10`. Spec: `docs/corpus_composition_plan.md`; prior
run: `docs/corpus_composition_2026-08-27.md` (window through 2026-07). Run read-only
(`mode=ro`) against `data/tracker.db` on the collection host, 2026-11-20 09:30 PT, with the
script as fixed on branch `refresh/2026-11`.

## Correction: the script now counts the site's own population

The 2026-11-19 refresh pass found the script had drifted from the published population a
second time (the first was August's `exclude_from_keywords` leak):

- it kept only `is_active` subs from `subreddit_config`, dropping r/HeavenGF's and
  r/MySentientAI's history, which the site keeps;
- it counted shells (posts stored as `[removed]`/`[deleted]`), which the site has excluded
  from numerator and denominator since 2026-09-08;
- it excluded one of the two excluded authors (`SoulmateAI_Dev`, not `heatherado`), and only
  from the numerator;
- section B1 ignored the window, so the partial current month leaked in.

The script now imports the definitions instead of restating them: the corpus is
`load_keyword_communities()` (24 subs: T1–T3 without `exclude_from_keywords`, deactivated
subs' history included), the population is `measurable_post_where()` with `EXCLUDED_AUTHORS`
dropped on both sides, and every section stops at the last complete UTC month. The window
end and per-theme `coverage_start` are now read at run time (from today's date and
`data/keyword_trends.json`), not hard-coded.

**Verified against the database.** The fixed script reproduces the refresh pass's independent
check exactly, on every figure it gave:

| Top-3 subreddit share | Romance | Sex/ERP | Consc. | Therapy | Addiction | Rupture | r/replika share of sex/ERP |
|---|---|---|---|---|---|---|---|
| Script before the fix (through Nov 19) | 57.5 | 74.5 | 68.1 | 63.9 | 92.9 | 79.7 | 57.8% |
| Independent check, site population, ≤ Oct 2026 | 56.2 | 74.8 | 68.8 | 63.1 | 93.0 | 79.7 | 59.1% |
| **This run (fixed script, ≤ Oct 2026)** | **56.2** | **74.8** | **68.8** | **63.1** | **93.0** | **79.7** | **59.1%** |
| August 2026 run (≤ Jul 2026) | 61.2 | 75.7 | 69.8 | 65.7 | 92.8 | 80.4 | 59.1% |

The live pipeline's own `theme_health.json` gave r/replika 58.9% of sex/ERP all-time on
2026-11-18; the gap to 59.1% is the partial November month, which this run leaves out.

## Headline: disclosures hold

"Two or three subreddits usually account for most of a theme's posts" stands: top-3 share is
56–93% on every theme. "Well over half r/replika alone" for sex/ERP stands at 59.1%.
Romance's top-3 share is five points below August's (61.2 → 56.2). The unfixed script shows
most of that drop too (57.5), so it is mainly the theme spreading across more rooms (r/aipartners
supplied 40 of 196 romance tags in Q3 2026), not the redefinition. Every other theme is within
2.6 points of August.

## Per-theme top-1 / tier mix (coverage window → 2026-10)

| Theme | Posts | Top-1 sub | Top-1 % | Top-3 | Tier mix (T1/T2/T3) |
|---|---|---|---|---|---|
| romance | 2,530 | r/replika | 20.6% | replika, characterai 18.8, myboyfriendisai 16.8 | 80.8 / 18.0 / 1.2 |
| sexual_erp | 5,354 | r/replika | 59.1% | replika, soulmateai 8.6, characterai 7.1 | 81.2 / 15.5 / 3.3 |
| consciousness | 538 | r/beyondthepromptai | 34.4% | beyondthepromptai, chatgptcomplaints 23.6, replika 10.8 | 94.1 / 5.0 / 0.9 |
| therapy | 1,530 | r/characterai | 31.4% | characterai, chatgptcomplaints 16.5, replika 15.2 | 80.7 / 7.9 / 11.4 |
| addiction | 3,608 | r/character_ai_recovery | 50.7% | character_ai_recovery, characterai 32.1, chatbotaddiction 10.2 | 36.0 / 1.6 / 62.4 |
| rupture | 5,385 | r/characterai | 44.9% | characterai, chatgptcomplaints 19.2, replika 15.6 | 92.0 / 5.2 / 2.9 |

Sex/ERP has fewer posts than in August (5,354 vs 5,927) despite three more months: the
population change (shells and `heatherado` out) outweighs the new months.

## Composition drift (tier share of corpus posts)

2024 = 87.6 / 11.9 / 0.5, 2025 = 85.2 / 13.0 / 1.8, 2026 to October = **79.6 / 15.8 / 4.7**.
Not directly comparable with August's figures, which counted shells and dropped inactive subs,
but the trajectory is the same and steeper: T3 (the recovery rooms) is now 4.7% of corpus
posts, against 0.5% in 2024. This is the tier-level face of the refresh pass's main finding
(handoff D1): as r/CharacterAI shrank from 67% of the denominator in Q4 2025 to 47% in October
2026, the communities dense in addiction and romance vocabulary became a larger share of the
count. B4 shows both halves: within T1, addiction rose 1.0 → 3.1 per 1,000 (first half of the
window → second half), and within T3 it rose 128 → 215.

## Leave-one-sub-out (shape fragility)

| Theme | Most shape-fragile to | Corr when removed | Biggest level dependence | Level change |
|---|---|---|---|---|
| romance | r/characterai | 0.731 | r/myboyfriendisai | −17% |
| sexual_erp | r/replika | 0.644 | r/replika | −50% |
| consciousness | r/characterai | 0.691 | r/beyondthepromptai | −37% |
| therapy | r/chatgptcomplaints | 0.868 | r/chatgptcomplaints | −14% |
| addiction | r/character_ai_recovery | 0.944 | r/character_ai_recovery | −55% |
| rupture | r/replika | 0.883 | r/chatgptcomplaints | −17% |

Consistent with August. The one shift: consciousness is now most shape-fragile to
r/characterai (August: r/beyondthepromptai), a consequence of the population change on a
short (19-month) window.

## Normalization comparison (B5)

All six themes remain below 0.9 on at least one reweighting (sub-equal correlation
0.44–0.90, tier-equal 0.49–0.96): the documented reason the published line is
volume-weighted and read direction-only. No change to that posture. Romance (0.55 / 0.49)
and consciousness (0.44 sub-equal) are the least robust to reweighting.

## Changes merged after this run (2026-11-20)

- **PR #4** (exclude `rawunfilteredchaos`, r/MyBoyfriendIsAI's recurring-thread moderator
  account, plus two seeding-ring accounts) removed 12 template sex/ERP tags and ~11
  denominator posts a month from 2025 on. r/myboyfriendisai is not in sex/ERP's top 3, so
  its top-3 share rises by about 0.2 points; nothing above changes materially.
- **Community additions of 2026-11-20** (r/therapyGPT, r/Ai_art_is_not_art, r/cogsuckers) all
  carry `exclude_from_keywords: true` and do not enter this corpus.

## Next re-run

~2027-02. The script now follows the site's definitions by import, so a re-run needs no edit
unless the population definition itself changes.
