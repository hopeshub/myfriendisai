# Overnight run summary — 2026-05-13 → 2026-05-14

## TL;DR

The LLM backfill completed across all 92 keywords on both surfaces. The
calibration check against an independent classifier **failed**: the LLM
is over-rejecting — agreement was 61.5% (threshold 85%), and the
false-rejection rate is 57.2% (threshold <20%). The chart default
**was not flipped**; `DEFAULT_SERIES` remains `count`.

When the LLM says **TP**, it's almost always right (89/90 = 99% precision
on those calls). When it says **FP**, the independent agent disagrees
57% of the time. The LLM is correctly identifying obvious problems but
incorrectly gating away genuine theme content.

## What happened

### Backfill
Final Haiku verdict counts:

| Theme | Posts (n) | Post precision | Comments (n) | Comment precision |
|---|---|---|---|---|
| rupture | 5,423 | 52.6% | 713 | 71.9% |
| addiction | 3,092 | 83.6% | 183 | 67.8% |
| romance | 2,437 | 67.5% | 112 | 72.3% |
| sexual_erp | 7,036 | 79.1% | 406 | 84.5% |
| consciousness | 461 | 64.4% | 49 | 51.0% |
| therapy | 1,357 | 56.2% | 125 | 71.2% |

The post-level rupture and therapy numbers are striking — both below
60% under Haiku. This is partly the LLM being too strict (see
calibration), partly real keyword noise the original validation didn't
catch.

### Calibration
- Sample: 270 items, stratified across themes (~60% FP, ~33% TP from each theme)
- Independent CC agent classified each under the same topical-reading rubric
- **Overall agreement: 166/270 = 61.5%**
- **False-rejection rate: 103/180 = 57.2%**
- Confusion matrix:
  - LLM=TP, agent=TP: 89 (LLM correctly kept)
  - LLM=TP, agent=FP: 1 (LLM rare error keeping something)
  - LLM=FP, agent=TP: **103 (LLM incorrectly rejected)**
  - LLM=FP, agent=FP: 77 (LLM correctly rejected)
- Per-theme agreement ranged 53-71%, all below threshold

### Verdict
**BLOCK.** The LLM is too strict. Switching the chart default to
`count_llm_verified` would hide genuine theme content. Need to tune the
prompt before redeploying.

## What this means

The methodology framework is sound. The LLM **can** distinguish theme
content; it's just calibrated too aggressively under the current prompt.
Two interpretations of the disagreement, both probably partially true:

1. **The Haiku prompt's "FP rules" (polysemy, sarcasm, quoted speech,
   metaphorical use) are too broad.** When the LLM sees a structural
   FP pattern, it rejects, even when the post is *thematically* about
   the theme. The independent CC agent under the same rubric reads more
   leniently — preserving topical relevance over surface-level pattern
   matching.

2. **The Haiku model is more conservative than Sonnet/Opus under the
   same prompt.** The original validation was done by Claude Code
   (Sonnet-class). Running Haiku may produce systematically stricter
   verdicts on borderline cases.

Either way: the framework works in principle. The first commit (Phase 1
infrastructure) stands. The next step is prompt iteration:

- Tighten the "when in doubt, YES" guidance more explicitly
- De-emphasize the "FP patterns" enumeration so the LLM doesn't treat
  it as a checklist
- Consider a Sonnet-tier model for the gating decision instead of Haiku
- Re-run calibration on a fresh sample to verify

## What's outstanding

- [ ] Prompt iteration on `src/llm_classifier.py` `SYSTEM_TEMPLATE`
- [ ] Re-run calibration against same 270 items after prompt change to
      directly measure improvement (the `llm_truth.json` file has the
      original LLM verdicts; the agent results are the gold standard)
- [ ] Once calibration passes ≥85%, flip `DEFAULT_SERIES` in
      `web/app/page.tsx` (one-character change)
- [ ] Consider whether to surface count_llm_verified as a user-facing
      toggle even at lower agreement (the LLM correctly identifies
      consensus FPs — that's a real subset, even if it's not the full
      gating story)

## What's still useful from tonight's work

Even with the calibration block, several things shipped successfully and
are worth keeping:

- **Verification examples panel** (`data/verification_examples.json` →
  About page "What Claude catches"). 18 examples across 6 themes
  showcasing the failure modes the LLM caught. Even though the LLM
  over-rejects in aggregate, the consensus-FP examples (LLM=FP,
  agent=FP, 77 items) are real and visible to readers.
- **Methodology disclosure** on About page about hybrid keyword+LLM
  classification.
- **Drift cadence tightened** to monthly (commit `e789c1d`).
- **Sustainability framework** (drift detection, theme health public
  surface, comment-precision tracked separately).
- **All infrastructure** (classifier module, CLI, calibration check,
  orchestrator, examples extractor) is in place and reusable for the
  next iteration.

## Files of note

- LLM verdicts: `data/tracker.db` table `llm_classifications` (~13k Haiku rows)
- Calibration sample: `analysis/keyword_pipeline/results/calibration_2026-05-14.md`
- Calibration agent verdicts: `analysis/keyword_pipeline/results/calibration_2026-05-14_results.txt`
- Calibration decision JSON: `analysis/keyword_pipeline/results/calibration_decision_2026-05-14.json`
- Verification examples: `data/verification_examples.json`
- Theme health snapshot: `data/theme_health.json`
- Updated trend exports: `data/keyword_trends.json` (count + count_post_only + count_llm_verified)

## Cost

Two API runs (initial noisy + comprehensive all-keyword): roughly $15-20
in Haiku calls. Calibration agent: covered by CC subscription, no
additional API cost.

## Reproducing the calibration result

```bash
# Inspect verdicts
.venv/bin/python scripts/llm_verify_tags.py report \
    --model claude-haiku-4-5-20251001

# Re-parse calibration
.venv/bin/python scripts/llm_calibration_check.py parse \
    --results-file analysis/keyword_pipeline/results/calibration_2026-05-14_results.txt

# Run decide command
.venv/bin/python scripts/llm_calibration_check.py decide
```

## Decision for the morning

The post-`therapeutic` audit honestly assumed the LLM gating would be
clean. It isn't yet. The right next step is one iteration on the
prompt, not a methodology pivot. If the prompt iteration doesn't get
agreement to ≥85%, the alternatives are: use Sonnet instead of Haiku
(~3x cost, probably acceptable), or use the LLM as a "high-confidence
TP keeper" only (count_llm_verified excludes only items where LLM is
confidently FP and the keyword is already known noisy).
