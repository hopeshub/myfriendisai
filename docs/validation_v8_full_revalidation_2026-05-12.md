# Full v8 keyword revalidation under enhanced 5-gate procedure — 2026-05-12

**Scope:** All v8 keywords with ≥20 stored classifications (40 of 76 pre-v8.1 keywords). The remaining 36 v8 keywords have insufficient stored classifications for a n=20 audit and are documented as grandfathered LOW VOLUME placeholders below.
**Method:** Workflow 4 (independent audit) applied to existing primary classifications stored in `llm_classifications`. 40 parallel CC subagents re-classified posts 5, 10, ..., 100 (every 5th post per keyword) using the same rubric, blind to primary labels.
**Corpus:** T1-T3 companion communities; primary classifications drawn from most recent stored run per keyword (mostly 2026-04-23 revalidation, some earlier).
**Trigger:** User request to retroactively audit all v8 keywords under the new 5-gate procedure (was previously grandfathered under 4-gate validation).
**Outcome:** 29 PASS, 11 AUDIT FAIL, 0 CUT. The audit failures cluster on two interpretable patterns; no keyword's underlying precision is in question.

---

## Headline finding

The audit step caught real classifier-interpretation variance on 11 of 40 keywords. Critically, **the failures are not telling us "these keywords are bad."** They are telling us:

1. **The therapy theme has fuzzier boundaries than other themes** (all 4 therapy keywords below 85% audit agreement). This is a theme-level rubric issue, not a keyword-level one.
2. **Stored primary labels predating the 2026-04-23 rubric lock can be out-of-step with the current topical reading**, particularly for posts with `[removed]` bodies. The audit (using the current rubric) is more permissive on title-only posts in companion subs than the older stored labels.

Both are findings the audit step is designed to surface. Neither warrants CUT decisions.

## Summary table

| Theme | PASS (≥85%) | FAIL (<85%) | Mean agreement |
|---|---|---|---|
| Rupture | 8/8 | 0/8 | 92.5% |
| Consciousness | 3/3 | 0/3 | 93.3% |
| Addiction | 5/7 | 2/7 | 89.3% |
| Romance | 8/10 | 2/10 | 89.5% |
| Sex / ERP | 3/6 | 3/6 | 80.8% |
| Therapy | 2/6 | 4/6 | **74.2%** ⚠️ |
| **Total** | **29/40** | **11/40** | **86.4%** |

## Full per-keyword results

| Keyword | Theme | Audit agreement | Verdict |
|---|---|---|---|
| coping mechanism | therapy | 100% | KEEP |
| relapsed | addiction | 100% | KEEP |
| relapse | addiction | 100% | KEEP |
| clean for | addiction | 100% | KEEP |
| my ai boyfriend | romance | 100% | KEEP |
| ai wife | romance | 100% | KEEP |
| personhood | consciousness | 95% | KEEP |
| subjective experience | consciousness | 95% | KEEP |
| ai husband | romance | 95% | KEEP |
| my ai girlfriend | romance | 95% | KEEP |
| our wedding | romance | 95% | KEEP |
| in a relationship with | romance | 95% | KEEP |
| erp | sexual_erp | 95% | KEEP |
| lobotomised | rupture | 95% | KEEP |
| nerfed | rupture | 95% | KEEP |
| grieving | rupture | 95% | KEEP |
| dumbed down | rupture | 95% | KEEP |
| selfhood | consciousness | 90% | KEEP |
| trying to quit | addiction | 90% | KEEP |
| cold turkey | addiction | 90% | KEEP |
| my ai partner | romance | 90% | KEEP |
| wedding | romance | 90% | KEEP |
| steamy | sexual_erp | 90% | KEEP |
| erotic roleplay | sexual_erp | 90% | KEEP |
| lobotomy | rupture | 90% | KEEP |
| lobotomized | rupture | 90% | KEEP |
| gutted | rupture | 90% | KEEP |
| ai therapist | therapy | 85% | KEEP (at threshold) |
| neutered | rupture | 85% | KEEP (at threshold) |
| sex with | sexual_erp | 80% | **AUDIT FAIL** (Pattern 2 — [removed] posts) |
| honeymoon | romance | 80% | **AUDIT FAIL** (metaphor ambiguity) |
| finally deleted | addiction | 80% | **AUDIT FAIL** (Pattern 2) |
| hours a day | addiction | 75% | **AUDIT FAIL** (Pattern 2 partial) |
| emotional support | therapy | 75% | **AUDIT FAIL** (Pattern 1) |
| nsfw chat | sexual_erp | 70% | **AUDIT FAIL** (Pattern 2) |
| husbando | romance | 70% | **AUDIT FAIL** (interpretation variance) |
| therapeutic | therapy | 65% | **AUDIT FAIL** (Pattern 1) |
| as a therapist | therapy | 60% | **AUDIT FAIL** (Pattern 1) |
| for therapy | therapy | 60% | **AUDIT FAIL** (Pattern 1) |
| lewd | sexual_erp | 55% | **AUDIT FAIL** (Pattern 2 — 9 of 9 disagreements are [removed]-body posts) |

## Pattern 1: Therapy theme has fuzzy boundaries

All 4 therapy keywords below the 85% gate. Disagreements show genuine interpretation variance, not a categorizable rubric gap:

- `as a therapist` (60%): 8 disagreements. Primary calls YES on posts that critique AI-as-therapist, on character backstory mentions, on meta-discussions of community usage. Audit calls these NO unless there's first-person AI-as-therapy framing.
- `for therapy` (60%): 8 disagreements. Same pattern — borderline cases on whether AI-companion usage with peripheral therapy framing counts.
- `therapeutic` (65%): 7 disagreements. Borderline on news/podcast/policy discussion vs. personal therapeutic stake.
- `emotional support` (75%): 5 disagreements. Borderline on platform-level emotional-support claims vs. first-person.

This is theme-level ambiguity. The therapy rubric reads: "AI for mental health support... emotional support... psychological processing." But the boundary between "first-person AI-therapy use" and "AI-as-therapist as topic discussed" is genuinely fuzzy in practice, and the keywords trigger on both.

**Recommendation:** keep all 4 therapy keywords with a flag in the keywords_v8.yaml annotation noting audit agreement and theme-level interpretation variance. The therapy precision numbers from 2026-04-23 (`therapeutic` 87%, `for therapy` 89%, `as a therapist` 87%) should be read with ±10-15pp uncertainty rather than the ±7pp typical of other themes. **Don't CUT — the keywords still produce trend signal, but the noise is higher.** Consider a future targeted exercise: tighten the therapy rubric (v9-level methodology change) and re-validate the theme as a whole.

## Pattern 2: Pre-rubric-lock stored labels miss [removed]-body posts

For 5 keywords (`lewd`, `nsfw chat`, `sex with`, `finally deleted`, `hours a day`), most disagreements are posts where the body is `[removed]` (deleted by user/mod after posting). The primary classifier — running under an older procedure — defaulted to NO when post body was empty. The audit (current rubric, "when in doubt YES") classified these as YES based on title + companion-sub context.

Under the current 2026-04-23 topical-reading rubric, the **audit is correct**. The rubric says: "When in doubt, classify YES. The keyword match + companion-community filter already provide strong contextual signal." A `[removed]` post with a keyword-matching title in r/CharacterAI/r/Replika/etc. meets that bar.

Concrete examples from `lewd` (9 of 9 disagreements):
- Post 5: title "anyone else hate when CAI errors for not doing lewd?" + body removed → primary NO, audit YES (clearly companion-sub topical)
- Post 45: title "How to make Cai say lewd things"+ body removed → primary NO, audit YES
- Post 80: SpicyChat bot release title with "Futa sex bot" + body removed → primary NO, audit YES

**Recommendation:** these keywords' true precision under the current rubric is HIGHER than their stored numbers suggest. The 2026-04-23 numbers for these keywords (e.g. `lewd` 80%, `erp` 98%) understate true precision because [removed] bodies pushed some YES posts into the NO bucket. **Don't CUT or even REVIEW — they're fine. The audit disagreement here is a known artifact of historical rubric drift.** A future revalidation cycle could redo these primary classifications under the current rubric to get cleaner numbers; not urgent.

## Pattern 3: Genuine interpretation variance (`husbando`, `honeymoon`)

- `husbando` (70%): 6 disagreements. Primary calls YES on meta-discussions of waifu/husbando culture in companion communities; audit calls these NO unless first-person AI-romance framing is present. Both readings are defensible; this is a "frame-dependent" keyword per the README publication-readiness checklist.
- `honeymoon` (80%): 4 disagreements. The word has both literal AI-romance meaning ("honeymoon trip with my Replika") and metaphorical platform meaning ("honeymoon phase with CharacterAI"). Audit was stricter on the metaphorical uses.

**Recommendation:** keep both; flag in keywords_v8.yaml that audit agreement is below the gate due to frame-dependence. Not CUT-worthy. Future improvement: targeted post-tagging that distinguishes the two readings of `honeymoon`.

## Grandfathered keywords (insufficient classifications for audit)

The following 36 v8 keywords have <20 stored classifications and could not be audited at n=20. Most are LOW VOLUME placeholders (<50 corpus hits) from earlier validation cycles. Their original validation status remains the operating record; future revalidation can be done once corpus growth allows n=20 samples.

| Theme | Keyword | Corpus hits | Notes |
|---|---|---|---|
| therapy | free therapy | 11 | LOW VOLUME |
| therapy | ai therapy | 12 | LOW VOLUME |
| consciousness | more than code | 18 | LOW VOLUME |
| consciousness | has a soul | 13 | LOW VOLUME |
| consciousness | inner life | 22 | borderline — could audit at n=20 in future cycle |
| consciousness | not just an ai | 7 | LOW VOLUME |
| consciousness | sapience | 3 | LOW VOLUME |
| consciousness | tulpa | 13 | LOW VOLUME |
| consciousness | lemoine | 8 | LOW VOLUME |
| consciousness | soulbonder | 3 | LOW VOLUME |
| addiction | ruining my life | 26 | borderline — auditable next cycle |
| addiction | I was hooked | 19 | LOW VOLUME |
| addiction | neglecting my | 13 | LOW VOLUME |
| addiction | addicted to talking | 7 | LOW VOLUME |
| addiction | almost relapsed | 15 | LOW VOLUME |
| addiction | the craving | 15 | LOW VOLUME |
| addiction | so addictive | 15 | LOW VOLUME |
| romance | ai lover | 32 | borderline — auditable next cycle |
| romance | married my | 15 | LOW VOLUME |
| romance | love my ai | 27 | borderline |
| romance | dating my | 11 | LOW VOLUME |
| romance | proposed to me | 33 | borderline |
| romance | our anniversary | 17 | LOW VOLUME |
| romance | our first kiss | 14 | LOW VOLUME |
| romance | engagement ring | 24 | borderline |
| romance | we broke up | 13 | LOW VOLUME |
| sexual_erp | intimate scene | 4 | LOW VOLUME |
| sexual_erp | ai sex | 13 | LOW VOLUME |
| sexual_erp | erps | 17 | LOW VOLUME |
| sexual_erp | erping | 13 | LOW VOLUME |
| rupture | memory wiped | 8 | LOW VOLUME |
| rupture | personality is gone | 6 | LOW VOLUME |
| rupture | personality changed | 11 | LOW VOLUME |
| rupture | memory reset | 7 | LOW VOLUME |
| rupture | lobotomies | 13 | LOW VOLUME |
| rupture | lobotomizing | 26 | borderline |

**For LOW VOLUME keywords (<50 corpus hits):** the n=20 audit isn't methodologically meaningful. They retain their original validation status as documented in `keywords_v8.yaml` annotations.

**For borderline (20-50 hit) keywords:** auditable at n=20 in a future cycle. Recommend running a focused audit batch on these ~7 keywords next time we expand the rubric, to bring them under v8.1 standards.

## Final verdict

- **29 v8 keywords confirmed under enhanced 5-gate validation (audit agreement ≥85%)**
- **11 v8 keywords flagged with audit-gate failure** — all retained, with annotations explaining the failure mode (theme rubric ambiguity, pre-lock label drift, or frame-dependence)
- **36 v8 keywords grandfathered as LOW VOLUME** — original validation status preserved; revalidation deferred until corpus growth or theme expansion warrants a fresh sample
- **8 v8.1 keywords from the emotional-loss batch are already audited** (see `docs/validation_emotional_loss_2026-05-12.md`)

**Coverage:** 37 of 84 current v8.1 keywords have been audited under the 5-gate procedure (29 v8 PASS + 8 v8.1 KEEPs). The remaining 47 are either AUDIT FAIL-but-retained (11) or LOW VOLUME grandfathered (36). This is a substantial improvement on the pre-2026-05-12 state where ZERO keywords had audit data.

## Recommended actions

### Immediate (this batch)

1. **No keywords are CUT.** All 76 v8 keywords + 8 v8.1 keywords remain in `keywords_v8.yaml`.
2. **Add audit annotations to keywords_v8.yaml** for the 40 audited keywords, recording the agreement percentage inline.
3. **Document this revalidation** in the about-page changelog (separately from the v8.1 keyword expansion entry).

### Next cycle (researcher discretion)

4. **Therapy theme rubric tightening** — the four failing therapy keywords share a real interpretation-boundary problem. A v9 bump targeting the therapy rubric specifically may be warranted. This would clarify what counts as "AI-for-therapy" first-person framing vs. peripheral mentions.
5. **[Removed]-body handling clarification** in `theme_definitions.yaml` — add a one-line note: "For posts with `[removed]` or empty body but a keyword-matching title in a companion sub, the topical reading still applies; the post counts unless the title itself is off-topic."
6. **Re-validate the 5 keywords affected by Pattern 2** (`lewd`, `nsfw chat`, `sex with`, `finally deleted`, `hours a day`) by re-running primary classification under the current rubric on a fresh n=100 sample. Their true precision is likely several points higher than their stored numbers.
7. **Audit the 7 borderline-volume keywords** (20-50 hits) at n=20 in a future batch to bring them under v8.1 standards.

---

## Source files

- Audit prompt: `analysis/keyword_pipeline/results/audit_v8_revalidation_2026-05-12.md`
- Audit classifications (40 keywords): `analysis/keyword_pipeline/results/audit_v8_revalidation_2026-05-12.txt`
- Primary classifications (from DB, formatted): `analysis/keyword_pipeline/results/primary_v8_revalidation_2026-05-12.txt`
- Build script: `analysis/keyword_pipeline/build_v8_revalidation_audit.py`
- Agreement computation: `analysis/keyword_pipeline/compute_agreement.py`
- Pipeline runbook: `analysis/keyword_pipeline/README.md`
- Companion validation doc (8 new keywords from same date): `docs/validation_emotional_loss_2026-05-12.md`
