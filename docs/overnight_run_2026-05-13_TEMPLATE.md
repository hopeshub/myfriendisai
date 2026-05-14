# Overnight run summary — 2026-05-13/14

**This is a template.** When the overnight work finishes, Claude renames
this to `docs/overnight_run_2026-05-13.md` and fills in the brackets.

## What was attempted

The day's adversarial audit produced the LLM classification framework
(Phase 1). The user went to sleep with the backfill mid-run. Overnight
plan: complete backfill, calibrate LLM against an independent agent
classifier, flip the chart's default series to the LLM-verified one
if calibration passes, and ship.

## What actually happened

### Backfill
- Final verdict count under `claude-haiku-4-5-20251001`: **[N]** classifications
- Per-theme breakdown:
  - rupture: [posts=X, comments=Y, precision=Z%]
  - addiction: [posts=X, comments=Y, precision=Z%]
  - romance: [posts=X, comments=Y, precision=Z%]
  - sexual_erp: [posts=X, comments=Y, precision=Z%]
  - consciousness: [posts=X, comments=Y, precision=Z%]
  - therapy: [posts=X, comments=Y, precision=Z%]

### Calibration
- Sample size: [N items] ([N_FP] FP + [N_TP] TP, stratified across themes)
- Independent agent classifier agreement with LLM: **[X%]**
- False-rejection rate (agent says TP where LLM said FP): **[Y%]**
- Threshold: ≥85% agreement + <20% FRR
- **Verdict: [PASS / DEFER / BLOCK]**

### Chart default
- Decision: **[FLIPPED to count_llm_verified / KEPT as count, deferred]**
- Reason: [brief reason]

### Surprises
- [Anything notable about specific keywords or themes]
- [Disagreement zones if any]

## What's outstanding for the morning

- [ ] [item]
- [ ] [item]

## Key file paths

- LLM verdicts: `data/tracker.db` table `llm_classifications`
- Calibration sample: `analysis/keyword_pipeline/results/calibration_2026-05-14.md`
- Calibration agent verdicts: `analysis/keyword_pipeline/results/calibration_2026-05-14_results.txt`
- Calibration decision: `analysis/keyword_pipeline/results/calibration_decision_2026-05-14.json`
- Theme health snapshot: `data/theme_health.json`
- Verification examples (rendered on About page): `data/verification_examples.json`
- Backfill log: `/tmp/llm_backfill_full.log`

## Reproducing the result

```bash
# Re-run report
.venv/bin/python scripts/llm_verify_tags.py report --model claude-haiku-4-5-20251001

# Re-run calibration parse
.venv/bin/python scripts/llm_calibration_check.py parse \
  --results-file analysis/keyword_pipeline/results/calibration_2026-05-14_results.txt

# Inspect a specific theme's flagged keywords
sqlite3 data/tracker.db "SELECT keyword, verdict, COUNT(*) FROM llm_classifications \
  WHERE model='claude-haiku-4-5-20251001' AND theme='therapy' GROUP BY keyword, verdict ORDER BY 3 DESC;"
```
