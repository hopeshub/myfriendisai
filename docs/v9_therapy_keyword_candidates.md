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

### 3. Drift-cycle precision evidence (2026-08-08 — June + July cycles)

The first two full drift cycles (~11,700 classifications; per-keyword n up to 50 at
each of post/comment level) measured therapy as the weakest theme by a wide margin,
**declining June → July at post level**:

| Level | June | July |
|---|---|---|
| post | 68% (n=358) | **62%** (n=360) |
| comment | 66% (n=171) | 68% (n=195) |

Per-keyword post-level precision, July cycle (June in parens):

| Keyword | July post precision |
|---|---|
| `ai therapy` | **36%** (41%) |
| `emotional support` | **46%** (42%) |
| `therapeutic` | **50%** (60%) |
| `as a therapist` | **52%** (70%) |
| `for therapy` | **60%** (78%) |
| `ai therapist` | 76% (74%) |
| `free therapy` | 86% (90%) |
| `coping mechanism` | 88% (90%) |

Classifier notes attribute much of the June→July decline to **post-4o-sunset
"therapy-speak" discourse**: complaints about models' therapeutic *tone*
("pseudo-therapeutic crap", anti-therapy prompt instructions), pasted AI output, and
prompt-engineering threads — ambient language drifting onto the keywords rather than
theme content changing. This is precisely the meaning-drift the instrument exists to
catch. Four keywords now sit at or below ~52%, well under the 60% CUT threshold the
original validation used.

Also relevant from the same cycles: the **first real comment-level precision
measurement** for therapy (66–68%, n≈366 across both cycles) — better than the old
n=100 estimate (58%) but still the second-weakest comment theme.

**Implication for v9:** the review is no longer only about *adding* recall (census
candidates, plural fix) — it should also weigh whether `ai therapy`, `emotional
support`, `therapeutic`, and `as a therapist` still clear the keep bar under current
discourse, or need researcher-accepted status with documented FP patterns, or removal.
Removals *lower* the therapy line; combined with admissions this makes dating and
changelogging the v9 step doubly important.

Additional cross-theme item surfaced by the same cycles (not therapy, but same v9
housekeeping): r/NomiAI's weekly art-collab boilerplate ("no NSFW content") is a
recurring template-driven FP cluster on `nsfw content` (16 of 22 July post-level FPs) —
a candidate for a targeted exclusion rule rather than keyword removal.

Source: `analysis/keyword_pipeline/drift_history.json` (quarters 2026-06, 2026-07);
per-file classifier summaries in the 2026-08-08 session; sample files under
`analysis/keyword_pipeline/results/drift_2026-0{6,7}_*`.

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
