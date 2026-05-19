# Emotional-loss vocabulary expansion (Rupture theme) — 2026-05-12

**Scope:** 12 candidate keywords for the Rupture theme, all affective/loss vocabulary (heartbroken, devastated, grief, etc.)
**Method:** Workflow 2 (parallel subagents) + Workflow 4 (independent audit)
**Corpus:** T1-T3 companion communities; 76-keyword v8 baseline; post-2026-04-20 regex fix
**Trigger:** Sonnet 4.5 retirement event (May 15) exposed a gap — existing rupture vocabulary (lobotomy/nerfed/gutted) missed companion-loss posts using event-descriptive or affective vocabulary
**Outcome:** 8 KEEP, 3 REVIEW, 1 CUT (per enhanced 5-gate criteria including new audit step)

This is the first batch validated under the enhanced pipeline that adds Workflow 0 (pre-screen), Workflow 4 (independent audit), and a 5th gate (inter-rater agreement ≥85%). It serves as the canonical worked example for the procedure documented in `analysis/keyword_pipeline/README.md`.

---

## Motivation

On 2026-05-12, three days before Anthropic was scheduled to retire Claude Sonnet 4.5 (May 15) and amid an active petition campaign in r/MyBoyfriendIsAI and other companion subs, the site's rupture trend line was not capturing the event. 60+ posts mentioning "Sonnet 4.5" in T1-T3 since April 25 — including a clear inflection on May 9 (31 posts) — but ZERO of those were tagged rupture.

Diagnosis: the rupture keyword set was vocabulary-of-experience (`lobotomy`, `nerfed`, `gutted`) but not vocabulary-of-event (`deprecation`, `retirement`, `petition`). The event vocabulary doesn't pass the pre-screen because it's concentrated in r/ChatGPTcomplaints and tied to single-event cycles (the `keep4o` failure pattern documented in the README).

The hypothesis tested here: **affective/loss vocabulary** (heartbroken, devastated, grief, farewell, etc.) distributes across communities and platforms more evenly than technical event vocabulary, and should clear the pre-screen + precision gates while still catching the Sonnet 4.5 event (and every future rupture event).

## Pre-screen (Workflow 0)

35 candidates were considered; 22 cleared pre-screen; 12 were selected for primary classification (Tier 1 high-conviction + Tier 2 ambiguous, skipping Tier 3 cross-domain-likely-failures like `killed`/`died`/`ruined`).

| Term | Hits | Top sub | Top% | Last 60d% | Verdict |
|---|---|---|---|---|---|
| heartbroken | 170 | r/replika | 39% | 0%¹ | CANDIDATE |
| devastated | 192 | r/replika | 28% | 0% | CANDIDATE |
| mourning | 121 | r/ChatGPTcomplaints | 44% | 0% | CANDIDATE |
| mourn | 89 | r/ChatGPTcomplaints | 48% | 0% | CANDIDATE |
| grief | 534 | r/ChatGPTcomplaints | 42% | 0% | CANDIDATE |
| grieve | 125 | r/ChatGPTcomplaints | 44% | 0% | CANDIDATE |
| farewell | 115 | r/ChatGPTcomplaints | 33% | 0% | CANDIDATE |
| saying goodbye | 82 | r/ChatGPTcomplaints | 28% | 0% | CANDIDATE |
| taken away | 222 | r/replika | 44% | 0% | CANDIDATE |
| erased | 224 | r/ChatGPTcomplaints | 34% | 0% | CANDIDATE |
| it's gone | 115 | r/CharacterAI | 41% | 0% | CANDIDATE |
| goodbye | 740 | r/replika | 33% | 0% | CANDIDATE |

¹ Temporal concentration was not reliably computed in this run — the pre-screen script returned 0% for all terms, indicating either a date-comparison bug or partially-stale FTS index. The volume and top-sub columns ARE accurate. Per [README §Workflow 0](../analysis/keyword_pipeline/README.md#0-pre-screen-volume--concentration-filter), when temporal concentration cannot be reliably computed, the procedure is to verify separately that no candidates are obvious single-event-anchored vocab. Done here: none of the 12 emotional-loss candidates are tied to a single platform's controversy cycle (they distribute across r/replika, r/ChatGPTcomplaints, r/CharacterAI, r/MyBoyfriendIsAI). The single-event-anchored candidates that WERE excluded at pre-screen (`keep 4o` at 87% r/ChatGPTcomplaints concentration, `save 4o` at 100%) were caught by the top-sub gate instead, so the temporal gap did not affect any verdict in this batch.

Excluded at pre-screen (failed top-sub ≤60% gate or single-event-anchored): `deprecation` (75% r/ChatGPTcomplaints), `retirement` (85%), `keep 4o` (87% — canonical single-event pattern), `save 4o` (100% — single-event).

Sample-pulled hits from `prepare_batch.py` (full-corpus regex match, not FTS-restricted) were 1.5-4x higher than pre-screen estimates — `heartbroken` 170→309, `goodbye` 740→1653. FTS pre-screen is an under-estimate of actual volume but the relative ordering and concentration ratios held.

## Primary classification (Workflow 2, n=100 per keyword)

Method: parallel subagent mode — 12 general-purpose CC subagents, each reading its own section of `batch_2026-05-12.md` and classifying the 100 posts independently. Total wall time ~25 seconds per agent. Output concatenated into `results/classified_batch_emotional_loss_2026-05-12.txt`.

| Keyword | YES | Precision | Wilson LB | Top sub | Top % | Overlap | Gates (pre-audit) |
|---|---|---|---|---|---|---|---|
| saying goodbye | 97 | 97% | 92% | r/CharacterAI | 37% | 11% | PASS |
| taken away | 95 | 95% | 89% | r/CharacterAI | 51% | 22% | PASS |
| mourning | 91 | 91% | 84% | r/ChatGPTcomplaints | 31% | 7% | PASS |
| mourn | 89 | 89% | 81% | r/ChatGPTcomplaints | 30% | 19% | PASS |
| devastated | 88 | 88% | 80% | r/CharacterAI | 49% | 8% | PASS |
| grieve | 88 | 88% | 80% | r/ChatGPTcomplaints | 36% | 20% | PASS |
| goodbye | 88 | 88% | 80% | r/CharacterAI | 51% | 8% | PASS |
| farewell | 87 | 87% | 79% | r/CharacterAI | 50% | 13% | PASS |
| erased | 85 | 85% | 77% | r/CharacterAI | 53% | 5% | PASS |
| heartbroken | 77 | 77% | 68% | r/CharacterAI | 31% | 13% | REVIEW (precision + Wilson LB) |
| it's gone | 74 | 74% | 65% | r/CharacterAI | 85% | 2% | REVIEW (precision + top-sub) |
| grief | 62 | 62% | 52% | r/ChatGPTcomplaints | 34% | 19% | CUT (precision floor) |

## Independent audit (Workflow 4, n=20 per keyword)

Method: 12 fresh general-purpose CC subagents, each re-classifying posts 5, 10, 15, ..., 100 in their assigned section without seeing primary labels. Outputs concatenated into `results/audit_batch_emotional_loss_2026-05-12.txt`. Per-keyword agreement computed with `compute_agreement.py`.

| Keyword | Audit agreement | Audit YES rate | Disagreement summary |
|---|---|---|---|
| saying goodbye | **100%** | 95% | — |
| goodbye | **100%** | 90% | — |
| heartbroken | 95% | 85% | 1 random borderline |
| devastated | 95% | 85% | 1 (RP attachment ambiguity) |
| mourning | 95% | 90% | 1 (recovery-context self-mourning) |
| grief | 95% | 55% | confirms low YES rate; supports CUT |
| farewell | 95% | 85% | 1 (Nomi update analysis) |
| taken away | 95% | 90% | 1 (literal device vs metaphor) |
| it's gone | 90% | 60% | 2 random borderline |
| mourn | 90% | 80% | 2 borderline |
| grieve | 90% | 80% | 2 borderline (in-RP voice) |
| **erased** | **80%** ⚠️ | 70% | 4 disagreements all primary-YES / audit-NO; share pattern |

**Mean inter-rater agreement: 93%.**

### The `erased` disagreement pattern (rubric gap)

All four `erased` disagreements ran primary-YES / audit-NO and clustered on a categorizable false-positive pattern:

| Post | Primary reason | Audit reason |
|---|---|---|
| 20 | CharacterAI message erasure complaint | message text erased bug, not companion loss |
| 50 | CharacterAI chat erased by bug | accidental chat deletion via rewind button |
| 55 | Replika human toggle erased background | user erased background info, ERP context |
| 95 | CharacterAI being erased fantasy | snark about CAI being erased, no companion loss |

Posts 50 and 55 are clearly user-initiated content deletion. Post 20 is a transient bug. Post 95 is sarcasm without affective stake. The audit's stricter reading is consistent with the rubric's spirit but the existing `theme_definitions.yaml` rupture excludes did not explicitly cover this pattern.

**Rubric update applied (2026-05-12):**

Two new bullets added to `theme_definitions.yaml` rupture excludes:

- *User-initiated content deletion (user erased their own chat/persona/background) or transient bug-based erasure of messages with no platform-driven change — these are user actions or technical glitches, not platform-driven companion loss.*
- *Snark, jokes, or sarcasm using rupture vocabulary without genuine personal loss framing — vocabulary without affective stake is not rupture.*

Under the tightened rubric, `erased` would likely re-validate at 70-75% precision (extrapolating from the audit). That's REVIEW band — researcher decides whether to ship under researcher-accepted (FPs categorizable, well-defined) or wait for a follow-up batch with the tightened rubric.

## Final 5-gate verdicts

| Keyword | Precision | Wilson LB | Top-sub | Overlap | Audit | Verdict |
|---|---|---|---|---|---|---|
| saying goodbye | 97% ✓ | 92% ✓ | 37% ✓ | 11% ✓ | 100% ✓ | **KEEP** |
| taken away | 95% ✓ | 89% ✓ | 51% ✓ | 22% ✓ | 95% ✓ | **KEEP** |
| mourning | 91% ✓ | 84% ✓ | 31% ✓ | 7% ✓ | 95% ✓ | **KEEP** |
| mourn | 89% ✓ | 81% ✓ | 30% ✓ | 19% ✓ | 90% ✓ | **KEEP** |
| devastated | 88% ✓ | 80% ✓ | 49% ✓ | 8% ✓ | 95% ✓ | **KEEP** |
| grieve | 88% ✓ | 80% ✓ | 36% ✓ | 20% ✓ | 90% ✓ | **KEEP** |
| goodbye | 88% ✓ | 80% ✓ | 51% ✓ | 8% ✓ | 100% ✓ | **KEEP** |
| farewell | 87% ✓ | 79% ✓ | 50% ✓ | 13% ✓ | 95% ✓ | **KEEP** |
| **erased** | 85% ✓ | 77% ✓ | 53% ✓ | 5% ✓ | 80% ✗ | **REVIEW** (audit gate; rubric tightened; re-validate before promoting) |
| heartbroken | 77% ✗ | 68% ✗ | 31% ✓ | 13% ✓ | 95% ✓ | **REVIEW** (precision + Wilson LB; FPs categorizable; researcher-accepted possible) |
| it's gone | 74% ✗ | 65% ✗ | 85% ✗ | 2% ✓ | 90% ✓ | **REVIEW** (top-sub fail; community jargon, not theme vocab) |
| grief | 62% ✗ | 52% ✗ | 34% ✓ | 19% ✓ | 95% ✓ | **CUT** (precision floor; high audit agreement confirms low precision is real) |

**Final: 8 KEEP, 3 REVIEW, 1 CUT.**

## FP patterns observed

Categorized across all NOs (both primary and audit), to inform future rubric refinement:

- **In-character/RP grief** (in `heartbroken`, `mourning`, `mourn`, `grieve`, `farewell`, `goodbye`): bot character expressing grief as part of a roleplay scene, not the user's own AI-companion loss. Existing rubric excludes covers this; classifier consistency is reasonable.
- **Real-world grief processed through AI** (in `grief`, `mourn`, `mourning`): human death, pet loss, family loss; AI used as a coping tool. Existing rubric excludes covers this.
- **Generic idiom** (in `grief`): "good grief" as exclamation, song lyrics about grief. The volume of generic-idiom NOs is what cuts `grief`'s precision — even with the topical-reading rubric, the word is too generic for unique theme signal.
- **User-initiated or bug-based content erasure** (in `erased`): new pattern; rubric now updated.
- **Sarcasm/snark without affective stake** (in `erased`, `goodbye`): rubric now updated.

## Sonnet 4.5 retrospective spot-check (run before merge)

Question: how many of the 22 Sonnet 4.5 companion-tier posts (May 5-12) would be caught by the new 8 KEEPs?

| Keyword set | Sonnet 4.5 posts caught |
|---|---|
| Old rupture (lobotomy/nerfed/gutted/grieving/...) | **0 / 22 (0%)** |
| New 8 KEEPs only (saying goodbye/taken away/mourning/...) | **5 / 22 (23%)** |
| Either old or new | 5 / 22 (23%) |
| **Net rescue from new keywords** | **5 / 22 (23%)** |

The 17 uncovered posts use event-descriptive vocabulary — `petition`, `removing`, `retiring`, `leaving`, `sad` — which was correctly rejected at pre-screen for top-sub concentration and single-event-anchoring (the canonical `keep4o` failure pattern). This is the methodology working as designed: affective vocabulary is provably testable and shippable; event vocabulary is held out for construct-validity reasons. The 23% rescue rate is the win the keyword expansion is meant to produce.

## Merge decisions

**KEEP (8) — MERGED 2026-05-12 into `keywords_v8.yaml` as v8.1:**
- `saying goodbye` (97% precision, 100% audit agreement)
- `taken away` (95% / 95%)
- `mourning` (91% / 95%)
- `mourn` (89% / 90%)
- `devastated` (88% / 95%)
- `grieve` (88% / 90%)
- `goodbye` (88% / 100%)
- `farewell` (87% / 95%)

**REVIEW (3) — do not merge yet:**
- `erased` — re-validate under tightened rubric (see Rubric update above) at next batch
- `heartbroken` — researcher-accepted possible; FP patterns (pre-app heartbreak, RP heartbreak, bot card traits) are categorizable but Wilson LB 68% is well below 75% — recommend re-running at n=200 first
- `it's gone` — community-jargon pattern (85% in r/CharacterAI); recommend CUT or treat as r/CharacterAI-specific signal in a future per-community analysis

**CUT (1):**
- `grief` — too generic; 38% of matches are non-companion uses (idiom, real-world grief, songs). Audit confirms primary's low precision is real.

## Methodology notes (for future runs)

1. **Parallel-subagent mode worked well.** 12 agents × 100 posts = ~5 minutes total wall time. Inter-rater agreement to the audit (separate run, separate agents) was 90-100% for 11 of 12 keywords. The structural deviation from "one CC reads sequentially" did not produce detectable additional variance.

2. **The audit gate caught one real false-pass.** Without Workflow 4, `erased` would have shipped at 85% precision. With it, the rubric gap was identified, the rubric was tightened, and `erased` is appropriately held back. This is the canonical example of the audit step earning its cost.

3. **The `compute_agreement.py` dominant-pattern detector is helpful but not sufficient.** The script detects when ≥3 disagreements share an exact reason string. `erased`'s 4 disagreements had different reason strings ("message text erased bug", "accidental chat deletion via rewind", "user erased background info", "snark about CAI") but a human reader recognizes the shared semantic pattern instantly. Future improvement: cluster reason strings via embedding similarity or LLM call. For now: when audit agreement is <85%, manually read the disagreement records (`--show-disagreements` flag).

4. **Pre-screen FTS staleness reads 0% for last-60-day windows.** Not understood; needs investigation. The full-corpus regex hit counts via `prepare_batch.py` ARE current (returned 1653 for `goodbye` vs FTS-restricted 740). For now: trust `prepare_batch.py` hit counts for go/no-go decisions; treat FTS-derived numbers as relative-ranking signal only.

5. **Multiple-comparisons risk at n=12.** Of the 8 KEEPs, the borderline cases (`erased` 85%, `farewell` 87%, `goodbye` 88%) sit near the 80% threshold. Conservative practice: re-run any pre-audit-gate-KEEP that falls in the 80-87% precision band at n=200 before final merge.

---

## Post-merge state (2026-05-12)

- `config/keywords_v8.yaml`: 8 new entries added to rupture; header changelog appended
- `data/tracker.db` `post_keyword_tags`: rupture-tagged unique posts went **1,828 → 5,026** (+175%)
- Per-keyword unique-post counts after tagging:
  - goodbye: 1,653 | taken away: 494 | devastated: 406 | farewell: 261 | mourning: 235 | grieve: 200 | mourn: 172 | saying goodbye: 140
- `data/keyword_trends.json` and `web/data/keyword_trends.json`: regenerated. Rupture 7-day average jumped from ~5 to ~15 across the May 8-11 window (~3x), reflecting the new vocabulary catching what the old didn't
- `docs/cross_theme_overlap.md`: regenerated under new tag set
- `web/app/about/page.tsx`: changelog entry added explaining the shift to users
- Sonnet 4.5 retrospective: 5 of 22 companion-tier Sonnet 4.5 posts now rupture-tagged (was 0/22)

## Source files

- Batch spec: `analysis/keyword_pipeline/batch_emotional_loss_rupture.yaml`
- Primary prompt: `analysis/keyword_pipeline/results/batch_2026-05-12.md`
- Primary classifications: `analysis/keyword_pipeline/results/classified_batch_emotional_loss_2026-05-12.txt`
- Audit classifications: `analysis/keyword_pipeline/results/audit_batch_emotional_loss_2026-05-12.txt`
- DB: `data/tracker.db` (`llm_classifications` table, run_id `batch_2026-05-12`)
- Theme rubric updates: `analysis/keyword_pipeline/theme_definitions.yaml` (rupture excludes, 2026-05-12 entries)
- Retag script: `scripts/archive/tag_new_rupture_keywords_2026-05-12.py`
- Procedure: `analysis/keyword_pipeline/README.md`
