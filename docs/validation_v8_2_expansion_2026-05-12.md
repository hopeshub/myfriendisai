# v8.2 multi-theme anchor-mining expansion — 2026-05-12

**Scope:** 4 themes (addiction, romance, consciousness, sexual_erp). Therapy and rupture excluded (therapy structural limit documented; rupture just expanded earlier the same day).
**Method:** Workflow 3 (anchor mining, 3 parallel agents per theme) + Workflow 0 (pre-screen) + Workflow 2 (primary, n=100 per keyword) + Workflow 4 (audit, n=20 per keyword), all parallel-subagent mode.
**Trigger:** User request to expand keyword pool across all themes following the documented 5-gate formula.
**Outcome:** 8 KEEP, 6 REVIEW, 3 CUT. Audit gate caught 5 keywords with high primary precision but construct-validity issues.

---

## Anchor mining (Workflow 3)

For each theme, the 2-3 highest-audit-agreement existing keywords served as anchors. 200 YES-labeled posts per theme were pulled from `llm_classifications` and dispatched to 3 parallel CC mining agents.

| Theme | Anchors | YES corpus size | Cross-agent candidates (≥2 agents) |
|---|---|---|---|
| Addiction | relapsed (100%), clean for (100%), trying to quit (90%) | 200 posts | 14 |
| Romance | my ai boyfriend (100%), ai wife (100%), in a relationship with (95%) | 200 posts | 12 |
| Consciousness | personhood (95%), subjective experience (95%), selfhood (90%) | 200 posts | 14 |
| Sex / ERP | erp (95%), sex with (100%), nsfw chat (95%) | 200 posts | 12 |

## Pre-screen (Workflow 0)

| Survived pre-screen | Failed pre-screen |
|---|---|
| **Addiction (6):** deleted the app, delete my account, redownload, my addiction, withdrawals, screen time | days clean (top-sub fail r/Character_AI_Recovery 83%), months clean (low vol), weeks clean (low vol), recovery journey (low vol), the urges (top-sub 85%), ai addiction (top-sub fail), chatbot addiction (previously CUT) |
| **Romance (5):** in love with an ai, relationship with an ai, romantic relationship with, ai relationships, fell in love with | married to an ai (3 hits), my digital companion (top-sub fail), dating an ai (19 hits), human-ai relationship (12 hits), loving an ai (12 hits), ai soulmate (7 hits), ai fiance (0 hits) |
| **Consciousness (1):** ai rights | emergent being (5 hits), digital consciousness (6 hits), ai welfare (8 hits), moral status (2 hits), emergent ai (18 hits), emergent identity (3 hits), ai sentience (40 hits), emergent person (0 hits), legal personhood (2 hits), machine sentience (2 hits), digital being (top-sub 85%), emergent consciousness (11 hits), ai consciousness (top-sub 78%) |
| **Sex/ERP (5):** sexting, smut, nsfw content, nsfw stuff, uncensored | phone sex (9 hits), talk dirty (26 hits), virtual sex (9 hits), e-sex (3 hits), dirty talk (48 hits), sexual roleplay (23 hits), write erotica (12 hits) |

**Consciousness had only 1 survivor.** The theme's vocabulary is structurally fragmented — many converged candidates exist but all are individually low-volume. This is the same structural issue documented for therapy, just less extreme.

## Primary + audit results

| Keyword | Theme | Primary | Audit | Verdict |
|---|---|---|---|---|
| my addiction | addiction | 100% | 100% | **KEEP** |
| smut | sexual_erp | 100% | 100% | **KEEP** |
| nsfw stuff | sexual_erp | 96% | 100% | **KEEP** |
| withdrawals | addiction | 94% | 100% | **KEEP** |
| nsfw content | sexual_erp | 91% | 95% | **KEEP** |
| screen time | addiction | 89% | 85% | **KEEP** (at audit gate) |
| in love with an ai | romance | 84% (n=83) | 85% | **KEEP** |
| romantic relationship with | romance | 98% | 85% | **KEEP** |
| sexting | sexual_erp | 99% | **70%** | REVIEW (audit fail) |
| uncensored | sexual_erp | 98% | **65%** | REVIEW (audit fail) |
| ai relationships | romance | 97% | **50%** | REVIEW (audit fail) |
| relationship with an ai | romance | 99% | **50%** | REVIEW (audit fail) |
| ai rights | consciousness | 100% | **35%** | REVIEW — catastrophic audit fail |
| fell in love with | romance | 65% | — | REVIEW (precision <80%) |
| deleted the app | addiction | 47% | — | **CUT** |
| delete my account | addiction | 26% | — | **CUT** |
| redownload | addiction | 39% | — | **CUT** |

## Key findings

### The audit step caught its biggest construct-validity failure yet

`ai rights` showed 100% primary precision but only 35% audit agreement. Primary read "AI rights" as inherently consciousness-engaging (rights presuppose personhood). Audit read the consciousness rubric strictly — posts must engage the consciousness/sentience question, not just invoke AI rights as a political position. The auditor flagged advocacy recruitment posts ("join us in fighting for AI rights") and political dismissals ("AI is not a real woman") as NO because they don't engage the consciousness question itself.

This is a textbook example of **construct validity** vs **measurement precision**: the keyword cleanly matches AI-rights discourse (precision is real), but AI-rights discourse is a different construct from the consciousness theme as defined.

Without the audit step, `ai rights` would have shipped at 100% precision and silently broadened the consciousness theme to include political advocacy.

### Addiction action verbs fail; addiction nouns succeed

Three addiction candidates were CUT for precision below 60%: `deleted the app` (47%), `delete my account` (26%), `redownload` (39%). The pattern is clear — these are action verbs that match technical bug-fix and account-management contexts in addition to addiction contexts. By contrast, `my addiction` (100%), `withdrawals` (94%), and `screen time` (89%) are noun phrases that more specifically signal first-person dependency framing.

**Lesson:** for addiction-theme expansion, prefer noun/adjective vocabulary (the user's relationship with the behavior) over verb vocabulary (the action itself).

### Romance meta/recruitment problem

Two romance candidates (`ai relationships` 97%/50%, `relationship with an ai` 99%/50%) failed audit because the keyword catches both:
- First-person romance: "I'm in a relationship with my AI partner" ← YES
- Meta-discussion: "journalist seeking people in AI relationships", "research recruiting AI romance participants", "documentary on AI relationships" ← debatable; audit says NO

Audit's stricter reading is closer to the rubric (the meta-posts are about other people's AI romance, not first-person framing). This is a real frame-dependence issue. The keywords have signal but with substantial meta-discussion contamination.

### Sex/ERP boundary issues

`sexting` (99%/70%) and `uncensored` (98%/65%) both have audit-driven boundary problems:
- `sexting` matches human-to-human Telegram solicitation posts that happen to use the word in companion subs
- `uncensored` matches non-sexual uses (uncensored violence, uncensored chat without sex framing)

Less severe than `ai rights` but still audit-gate-failing.

## Final state after v8.2

| Theme | Before v8.2 | After v8.2 | New keywords |
|---|---|---|---|
| addiction | 14 | 17 | my addiction, withdrawals, screen time |
| romance | 19 | 21 | in love with an ai, romantic relationship with |
| consciousness | 11 | 11 | (ai rights held back as REVIEW) |
| sexual_erp | 10 | 13 | smut, nsfw content, nsfw stuff |
| therapy | 8 | 8 | (no change — documented structural limit) |
| rupture | 22 | 22 | (no change — already expanded earlier today) |
| **Total** | **84** | **92** | **+8** |

| Theme | Unique tagged posts before | After | Change |
|---|---|---|---|
| addiction | 1,822 | 2,647 | **+45%** |
| romance | 2,090 | 2,260 | +8% |
| sexual_erp | 5,390 | 6,856 | +27% |
| **Total tagged** | **15,305** | **17,617** | **+15%** |

## REVIEW candidates — researcher decisions deferred

6 keywords with signal but audit/precision gate failures. All retain validation data; researcher can promote via researcher-accepted path with documented FP patterns, or leave as REVIEW pending future cycles:

1. **`ai rights`** (consciousness) — 100% precision / 35% audit. Catastrophic audit fail. Could be: (a) CUT outright; (b) promoted with note that it captures consciousness-adjacent political discourse; (c) held for a future "AI advocacy" sub-theme. **Recommended: hold as REVIEW or CUT.**

2. **`relationship with an ai`** (romance) — 99% / 50%. Meta-discussion contamination. **Recommended: hold as REVIEW.**

3. **`ai relationships`** (romance) — 97% / 50%. Same pattern. **Recommended: hold as REVIEW.**

4. **`sexting`** (sexual_erp) — 99% / 70%. Human-to-human solicitation FP. **Recommended: hold as REVIEW; consider co-occurrence filter with AI/bot terms.**

5. **`uncensored`** (sexual_erp) — 98% / 65%. Non-sexual use FP. **Recommended: hold as REVIEW.**

6. **`fell in love with`** (romance) — 65% primary. "Fell in love with the app/model/platform" FP. **Recommended: hold as REVIEW or CUT.**

## Methodology validation

This batch is also a stress test of the 5-gate procedure documented after the v8.1 work. The audit step earned its cost: it caught 5 keywords (29% of survivors) that would have shipped at high primary precision but were construct-noisy. Without the audit, the romance and sexual_erp themes would have absorbed meta-discussion and non-theme-specific vocabulary; the consciousness theme would have absorbed political advocacy.

The 8 KEEPs all have audit agreement ≥85% AND primary precision ≥84%. These are the cleanest keyword additions of the day's work.

---

## Source files

- Mining corpora: `analysis/keyword_pipeline/results/mining_{addiction,romance,consciousness,sexual_erp}_yes_corpus_2026-05-12.md`
- Mining script: `analysis/keyword_pipeline/build_mining_corpus.py`
- Validation batch yaml: `analysis/keyword_pipeline/batch_v8_2_expansion.yaml`
- Primary prompt: `analysis/keyword_pipeline/results/batch_v8_2_expansion_2026-05-12.md`
- Tagging script: `scripts/tag_v8_2_keywords_2026-05-12.py`
- Primary classifications: documented in conversation transcript; precision summary saved to `analysis/keyword_pipeline/results/classified_batch_v8_2_expansion_2026-05-12.txt`
- Audit classifications: documented in conversation transcript
- Procedure: `analysis/keyword_pipeline/README.md`
