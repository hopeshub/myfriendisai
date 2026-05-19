# v9 therapy-keyword review — QUEUED

**Status:** queued, not actioned. A keyword change is a versioned v8 → v9 step
requiring researcher sign-off (see CLAUDE.md "Researcher-accepted keywords" and the
frozen-methodology rule). This doc is the **standing input** to that review — append
evidence as it accumulates; do **not** edit `keywords_v8.yaml` on the strength of it.

## Why a review is warranted

The therapy theme's vocabulary is structurally fragmented (CLAUDE.md, 2026-05-12): the
keyword set captures a precision-first slice and misses help-framing carried by ordinary
or near-miss phrasings. Two independent lines of evidence have now accumulated.

### 1. Census-recovered low-volume keywords (2026-05-16)

The therapy/consciousness census validation recovered **15 clean low-volume therapy
keywords** — sub-floor phrasings validated by reading 100% of their matches rather than an
n=100 sample. Available, not admitted.
Source: `docs/therapy_consciousness_quality_program_2026-05-16.md`; artifacts under
`analysis/keyword_pipeline/therapy_census_2026-05-16/`.

### 2. Leak-test misses (2026-05-18)

The therapy↔addiction leak test hand-read 90 addiction-only posts; 4 of the 22 help-frame
"leaks" were explicit therapy vocabulary the keyword set simply does not include:

- **`coping mechanisms` (plural)** — the admitted keyword `coping mechanism` matches the
  singular only; the `\b…\b` regex misses the plural. This is closer to a recall *bug*
  than a vocabulary gap, and is the cheapest, highest-confidence fix on the list.
- **`therapist bot`** — previously a documented LOW-VOLUME reject; re-surfacing.
- **`coping medicine`**
- **`like my therapist`** — the admitted keyword is `as a therapist`.

Source: `docs/therapy_addiction_overlap_finding_2026-05-18.md`; full audit
`analysis/leak_test_problem_only_2026-05-18_audit.md`.

## What a v9 review should decide

- Whether to admit any/all of the 15 census-recovered keywords (each already
  100%-match-validated).
- Whether to broaden `coping mechanism` to also match the plural — trivial, near-pure
  recall gain, lowest risk.
- Whether `therapist bot` / `coping medicine` / `like my therapist` clear the validation
  gate at current corpus volume — they may now exceed the 50-hit floor; re-check.
- Any admission **raises** the therapy line; it must be dated and changelogged so the
  step-change is not read as real-world change (coverage_start + changelog discipline).

## Explicitly out of scope

This is a keyword-set bump only — it does not reopen methodology, and it does **not**
revive the merged therapy↔addiction view. The leak test showed the overlap is dominated by
ordinary-language coping frames no finite keyword list captures (18 of 22 leaks); the
near-miss phrasings here are only 4 of 22. A richer therapy lexicon improves the therapy
line's recall; it does not make the therapy↔addiction overlap measurable by co-occurrence.
See `docs/therapy_addiction_overlap_finding_2026-05-18.md`.
