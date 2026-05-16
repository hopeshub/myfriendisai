# All-themes keyword revalidation — 2026-04-23

**Scope:** All 46 high-volume (≥50 hits) keywords across 6 themes
**Method:** 100-post CC classification per keyword
**Corpus:** T1-T3 companion communities; post-April-20 regex fix applied
**Trigger:** Pre-publish pipeline review
**Outcome:** 6 cuts, 6 promotions, 34 stable; theme definitions tightened

---

## Summary

| Action | Count | Keywords |
|---|---|---|
| CUT | 6 | sentient, self-aware, chatbot addiction, kink, fetish, nsfw bot |
| PROMOTED (→ KEEP) | 6 | neutered, grieving, clean for, as a therapist, therapeutic, for therapy |
| Stable (near baseline) | 34 | across all themes |
| Skipped (low volume) | 27 | <50 hits in corpus; annotations retained |

Net keyword count: **82 → 76** (v8 locked).

---

## Two-pass methodology

An initial classification pass produced implausibly low numbers across four themes (therapy, consciousness, romance, sexual_erp) — e.g. "coping mechanism" at 1%, "nsfw chat" at 0%, "sentient" at 20%. Meanwhile rupture and addiction stayed healthy.

Root cause: the agent prompts for the first pass emphasized "the author describes their OWN personal [theme behavior]." This is a stricter **first-person-content reading** than the methodology that established the keyword baselines in March 2026. The discrepancy was amplified by an ambiguity in `analysis/keyword_pipeline/theme_definitions.yaml`, which mixed topical ("Posts about X") and first-person-content ("The poster describes X") language for each theme. The agents latched onto the strict clause.

The v2 rerun used a calibrated **topical reading**: *"does this keyword appear in a thematically-relevant context within an AI companion community?"* A post that references a theme behavior by the author, even without graphic description, counts as YES. Bot-card listings, clearly off-topic matches, ironic rejections, and pure third-party journalism remain NO. This matches how the original baselines were measured.

Rupture and addiction did not need a v2 rerun — their keywords are behavior/event words (lobotomized, relapsed) whose precision is stable under either reading.

The `theme_definitions.yaml` file has been updated to make the topical reading explicit. The updated standard is documented in a comment header at the top of that file.

---

## Full precision table (46 keywords)

Format: keyword — baseline → current (delta) — status

### Rupture — 8/8 KEEP (strongest theme)

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| lobotomy | 91.8% | 86.0% | -6 | KEEP (stable) |
| lobotomized | 86.6% | 95.0% | +8 | KEEP (improved) |
| lobotomised | 100.0% | 98.1% | -2 | KEEP (stable) |
| nerfed | 82.0% | 89.0% | +7 | KEEP (improved) |
| **neutered** | **79.0%** | **93.0%** | **+14** | **PROMOTED to KEEP** |
| **grieving** | **74.0%** | **86.0%** | **+12** | **PROMOTED to KEEP** |
| gutted | 80.2% | 84.0% | +4 | KEEP (stable) |
| dumbed down | 83.0% | 91.0% | +8 | KEEP (improved) |

### Addiction — 7/8 KEEP, 1 CUT

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| trying to quit | 90.5% | 91.0% | 0 | KEEP (stable) |
| relapsed | 90.5% | 96.0% | +6 | KEEP (stable) |
| cold turkey | 85.5% | 93.0% | +8 | KEEP (improved) |
| relapse | 80.0% | 98.0% | +18 | KEEP (improved) |
| **clean for** | **72.7%** | **95.9%** | **+23** | **PROMOTED to KEEP** |
| hours a day | 63.2% | 53.0% | -10 | researcher-accepted (T1-T2 bridge) |
| **chatbot addiction** | **100.0%** | **55.1%** | **-45** | **CUT** (journalist/mod dilution) |
| finally deleted | 81.4% | 76.0% | -5 | KEEP (near-stable) |

### Therapy — 6/6 KEEP

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| ai therapist | 92.0% | 100.0% | +8 | KEEP (improved) |
| **as a therapist** | **73.0%** | **86.9%** | **+14** | **PROMOTED to KEEP** |
| **therapeutic** | **69.0%** | **87.0%** | **+18** | **PROMOTED to KEEP** |
| **for therapy** | **63.5%** | **89.0%** | **+26** | **PROMOTED to KEEP** |
| emotional support | 100.0% | 88.0% | -12 | KEEP (stable) |
| coping mechanism | 100.0% | 94.0% | -6 | KEEP (stable) |

### Consciousness — 3/5 KEEP, 2 CUT

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| personhood | 98.0% | 97.0% | -1 | KEEP (stable) |
| subjective experience | 88.0% | 97.1% | +9 | KEEP (improved) |
| selfhood | 82.5% | 98.9% | +16 | KEEP (improved) |
| **sentient** | **83.0%** | **55.0%** | **-28** | **CUT** (meme dilution) |
| **self-aware** | **78.3%** | **54.0%** | **-24** | **CUT** (meme dilution) |

### Romance — 9/10 KEEP, 1 REVIEW

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| my ai partner | 97.9% | 100.0% | +2 | KEEP (stable) |
| husbando | 95.5% | 100.0% | +5 | KEEP (stable) |
| my ai boyfriend | 94.7% | 98.0% | +3 | KEEP (stable) |
| ai husband | 94.2% | 96.9% | +3 | KEEP (stable) |
| my ai girlfriend | 94.1% | 99.0% | +5 | KEEP (stable) |
| ai wife | 92.3% | 100.0% | +8 | KEEP (improved) |
| our wedding | 87.0% | 99.0% | +12 | KEEP (improved) |
| honeymoon | 83.3% | 89.0% | +6 | KEEP (improved) |
| wedding | 80.6% | 84.0% | +3 | KEEP (stable) |
| in a relationship with | 77.4% | 66.0% | -11 | REVIEW (borderline; consider CUT next review) |

### Sex / ERP — 4/9 KEEP, 2 REVIEW, 3 CUT

| Keyword | Baseline | Current | Δ | Status |
|---|---|---|---|---|
| erp | 100.0% | 98.0% | -2 | KEEP (stable) |
| steamy | 98.6% | 96.0% | -3 | KEEP (stable) |
| erotic roleplay | 92.2% | 85.2% | -7 | KEEP (stable) |
| nsfw chat | 100.0% | 78.0% | -22 | REVIEW (mild drift) |
| sex with | 98.0% | 78.0% | -20 | REVIEW (mild drift) |
| lewd | 80.0% | 59.0% | -21 | REVIEW-DRIFT (borderline CUT next review) |
| **kink** | **84.0%** | **55.0%** | **-29** | **CUT** (bot-directory dilution) |
| **fetish** | **92.0%** | **51.0%** | **-41** | **CUT** (genre-tag dilution) |
| **nsfw bot** | **93.0%** | **52.5%** | **-40** | **CUT** (structural: "bot" is bot-type jargon) |

---

## Cut rationale

### `sentient` (consciousness) — 83% → 55%
CharacterAI meme-culture dilution. Title-only posts like "becomes sentient" (joke), RP character traits ("sentient kite" as character descriptor), dismissive comments ("obviously not sentient"), and product marketing like "emotionally sentient forms" now dominate matches. The theme retains strong alternatives: personhood (97%), subjective experience (97%), selfhood (99%), all validated with consciousness framing.

### `self-aware` (consciousness) — 78% → 54%
Same meme-dilution dynamic as sentient. Already was REVIEW in v8 config; drift pushed it into CUT territory.

### `chatbot addiction` (addiction) — 100% → 55%
The recovery subs (ChatbotAddiction, AI_Addiction) now carry substantial meta-content: journalist recruitment posts, researcher solicitation, subreddit moderation announcements, and third-party articles — all of which match the keyword but don't represent first-person dependency. The addiction theme still has robust recovery-language keywords that score 90%+ (relapsed, trying to quit, cold turkey, clean for, relapse).

### `kink` (sexual_erp) — 84% → 55%
Bot-directory promotional content and genre-tag listings ("TW: degradation kink", "cucking kink as trait") dominate matches. The previous March cleanup validation was measured against a corpus with less promotional volume.

### `fetish` (sexual_erp) — 92% → 51%
Same dynamic as kink, plus real-world human fetish references unrelated to AI.

### `nsfw bot` (sexual_erp) — 93% → 53%
Structural problem: "nsfw bot" is literally bot-type terminology. Matches are overwhelmingly promotional listings ("Looking for NSFW bot recs") and policy/feature complaints. The keyword's genre-identifier nature means it will continue drifting toward meta-content as the corpus grows.

---

## Promotion rationale

All 6 promoted keywords were previously annotated as "researcher-accepted" (60-79% precision band) with documented rationales. They now clear 80% convincingly under the calibrated measurement:

- **neutered** (79 → 93%): animal-context FPs decreased; platform-degradation framing dominant.
- **grieving** (74 → 86%): Sewell-Setzer noise decreased; platform-loss grief framing dominant.
- **clean for** (73 → 96%): recovery-language precision remains strong in T3 subs.
- **as a therapist** (73 → 87%): intentional-use framing reads clearly under topical reading.
- **therapeutic** (69 → 87%): the volume anchor of therapy theme; healthy under calibrated reading.
- **for therapy** (64 → 89%): the historical negation-pattern FP ("not for therapy") appears less common in current corpus.

---

## Low-volume keywords not revalidated

27 keywords have <50 hits in the current corpus and were skipped by the batch pipeline's volume floor. They remain in the config with their original annotations:

- **therapy** (2): ai therapy, free therapy
- **consciousness** (8): more than code, has a soul, inner life, not just an ai, sapience, tulpa, lemoine, soulbonder
- **addiction** (5): neglecting my, addicted to talking, almost relapsed, the craving, so addictive
- **romance** (3): our first kiss, engagement ring, we broke up
- **sexual_erp** (4): intimate scene, ai sex, erps, erping
- **rupture** (5): personality is gone, personality changed, memory reset, lobotomies, lobotomizing

These are either niche/event-specific or plural/gerund variants of high-volume keywords. Low volume means they contribute little to theme-level trend lines either way. A future pass could run with a relaxed volume floor (e.g. ≥20 hits) if we want to validate them.

---

## Methodology update applied

`analysis/keyword_pipeline/theme_definitions.yaml` was updated to make the topical reading explicit for every theme. The ambiguity that caused the first-pass failure has been removed.

**Before (ambiguous — two readings in each definition):**
> "Posts about sexual or erotic roleplay interactions with AI. The poster describes sexual acts, NSFW content, erotic scenarios, sexting, or intimate physical encounters with an AI companion."

**After (topical, explicit):**
> "Posts thematically about sexual or erotic interactions with AI — ERP, NSFW chat, kink or fetish exploration, erotic roleplay, sexting, or the AI-sexual features of a platform. First-person references to doing, wanting, or losing access to sexual AI interactions count, even without graphic or detailed content."

A header comment at the top of the file documents the classification standard and notes the 2026-04-23 calibration.

---

## Pipeline health summary

| Theme | Before | After | Status |
|---|---|---|---|
| Rupture | 14 KW | 14 KW (all ≥84%) | Strongest theme |
| Romance | 19 KW | 19 KW | No cuts; 1 REVIEW drift |
| Therapy | 8 KW | 8 KW (all ≥87%) | All cleared KEEP |
| Addiction | 15 KW | 14 KW | Core solid; 1 cut |
| Consciousness | 13 KW | 11 KW | 2 cuts; core remains strong |
| Sex / ERP | 13 KW | 10 KW | 3 cuts; narrowed to high-precision core |
| **Total** | **82** | **76** | |

---

## Files changed

- `config/keywords_v8.yaml` — 6 keyword cuts, 6 precision promotions, header changelog entry
- `analysis/keyword_pipeline/theme_definitions.yaml` — topical reading made explicit; header comment added
- `web/app/about/page.tsx` — frontend changelog entry
- `data/post_keyword_tags` — stale tags for cut keywords will be removed; tags re-exported

## Related docs

- `docs/validation_romance_revalidation_2026-04-20.md` — prior romance-only drift audit
- `docs/precision_audit_2026-04-20.md` — original smoke test that surfaced romance drift
