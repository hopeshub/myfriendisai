# Sustainability framework — 2026-05-13

Built in response to the adversarial audit's finding that the 5-gate validation procedure is structurally incapable of catching drift, emergent concentration, or comment-level context collapse. Per-keyword validation at admission is necessary but not sufficient.

The framework adds three layers around the existing validation methodology:

1. **Continuous drift detection** — `scripts/drift_check.py` + `analysis/keyword_pipeline/drift_history.json`
2. **Public system-health surface** — `data/theme_health.json` regenerated daily, rendered on About page
3. **Comment-precision tracked separately from post-precision** — at the keyword level in drift_history, at the theme level in theme_health

## What problem each piece solves

### 1. Drift detection
**Problem the May 2026 audit exposed:** `therapeutic` was admitted at 65% audit-agreement in v8. By May 2026, GPT-5.x guardrail tone caused users to use "therapeutic" as an insult about preachy AI, and the comment-level precision had collapsed to 29%. The validation procedure has no eyes on the keyword after admission — it can't catch language drift, meme dilution, or vocabulary capture.

**The fix:** quarterly sampling of every keyword's hits, fresh classification, precision-over-time tracking. If a keyword drops below 70%, the report flags it. The next `therapeutic`-style inversion gets caught in the quarter it happens.

**Cost:** ~50 keywords × 4 quarters × 50 hits/keyword × 2 surfaces (post + comment) = ~20k classifications/year. Cheap on Sonnet.

**Where it lives:**
- CLI: `scripts/drift_check.py {build,record,report}`
- Sample storage: `analysis/keyword_pipeline/results/drift_<quarter>_*.md`
- Tracker: `analysis/keyword_pipeline/drift_history.json`

**Quarterly procedure:**
```bash
# Step 1: build samples (auto-generates ~100 sample files per keyword × surface)
.venv/bin/python scripts/drift_check.py build --quarter 2026-Q3 --n 50

# Step 2: dispatch CC agents to classify each file
#   Each file has its own classification prompt in the header.
#   Agents write per-line "N. TP" or "N. FP" results to a sibling
#   <basename>_results.txt file.

# Step 3: parse results into the tracker
.venv/bin/python scripts/drift_check.py record \
    --files analysis/keyword_pipeline/results/drift_2026-Q3_*_results.txt

# Step 4: inspect current drift status
.venv/bin/python scripts/drift_check.py report
```

The tracker is the source of truth for per-keyword precision over time. New points append; old points stay. Trend visible by replaying the history.

### 2. Public system-health surface
**Problem:** the methodology page tells readers about validation but doesn't tell them that 61% of comment-rupture is one subreddit, 40% of sex/ERP volume is one Feb-2023 event, or that consciousness at the comment level is 51% precise. A reader looking at the chart can't ask the right questions because the concentration data isn't visible.

**The fix:** `data/theme_health.json` is regenerated on every collection. It contains per-theme:
- Total post tags + total comment tags
- Top subreddit (posts) + % share
- Top subreddit (comments) + % share
- Top single day + % share
- Top single month + % share
- Top-5 authors' combined share
- Latest post-level precision + date
- Latest comment-level precision + date
- Currently flagged noisy comment keywords

The About page renders this in a "Theme health snapshot" section. Each theme gets a card; precision values are color-coded (green ≥80%, yellow 60-80%, red <60%). The reader who sees consciousness flagged red understands the chart's comment-level reliability for that theme without reading the docs.

**Where it lives:**
- Export function: `src/db/operations.py:export_theme_health_json`
- Wired into: `scripts/collect_daily.py` (Step 5)
- Data file: `data/theme_health.json` (and `web/data/theme_health.json`)
- Render: `web/app/about/page.tsx` "Theme health snapshot" section

### 3. Comment-precision as its own object
**Problem:** the published 80% precision gate was established for post-level validation. Comments are systematically noisier (shorter, reactive, idiomatic, embedded in thread context that primes interpretation). The adversarial audit showed comment-level precision runs 5-25 points below post-level, with two themes (therapy 58%, consciousness 51%) below any defensible gate. Treating post+comment as one corpus hides this.

**The fix:** `drift_history.json` tracks `level: post` and `level: comment` separately per keyword. `theme_health.json` reports both numbers separately. The About page renders both. There is no longer a single corpus-wide precision number to point at; readers get the truth per-surface.

**What this doesn't do:** it doesn't prune noisy comment keywords from production. That's a v9 keyword-set change which should follow the methodology-stability rule (frozen v8; new minor version for any methodology change). Pruning candidates are surfaced in the noisy_keywords_comment list on the about page so the work is visible; the cleanup itself is a future bump.

## Re-validation cadence

Established schedule (manual; document here so it persists across Claude sessions):

| Cadence | Action |
|---|---|
| Daily | Theme health export regenerates with current concentration metrics |
| **Monthly** (was quarterly, tightened 2026-05-13) | Run `drift_check.py build` + classify (via LLM or agents) + `drift_check.py record` for every keyword |
| Annual | Sample-based comprehensiveness audit (recall floor) — last run 2026-05-13 |
| Ad hoc | Adversarial audit when a major model release lands (drift catalyst events) |

Next monthly drift check due: **2026-06-13**. Adversarial re-audit due: **after the next GPT or Claude major release**, whichever lands first.

Cadence rationale: quarterly was the initial setting because manual agent dispatch was expensive. With the LLM classifier (`scripts/llm_verify_tags.py`) now available, drift checks can be fully automated at ~$5/month, catching `therapeutic`-style inversions 2-3 months earlier than the quarterly cadence would.

## What survives Claude turnover

If a future Claude session opens this project a year from now, the framework should be self-explanatory:

- `analysis/keyword_pipeline/drift_history.json` — every measurement we've ever taken, with sources
- `data/theme_health.json` — current-state snapshot
- `scripts/drift_check.py --help` — the procedure
- This doc — the why
- `docs/adversarial_audit_2026-05-13.md` — what went wrong and what to look for

The system should *degrade gracefully* without active intervention. If quarterly drift checks lapse, the report still tells you which keywords were last seen at what precision and when. If theme health stops updating, the JSON sitting in data/ remains the latest known state. If a future audit needs to be run, the CLI builds the samples from current data without human guidance beyond `--quarter`.

## What this framework does NOT do

- It does not prune keywords. v8 stays locked.
- It does not change how trend lines are computed.
- It does not introduce real-time alerting (no Slack, no email).
- It does not validate against external sources (no comparison to academic studies, press, community wikis).
- It does not catch corpus-side issues outside keywords — if collection breaks, if a sub goes private, those are caught by `validate_deploy.py` separately.

These are deliberate. The framework adds the smallest possible immune system that catches the failure modes the May 2026 adversarial audit exposed. Further hardening is appropriate when those failure modes recur in a way the current system can't handle.

## Open questions for future sessions

1. **Should noisy comment keywords be excluded from comment-tagging in production?** Today: no — they're flagged but still tagged. The v9 boundary is the right place to make that call after seeing one more quarter of drift data.
2. **Should there be a per-theme reliability badge on the front page chart (not just About)?** Probably yes for themes flagged red. Not implemented yet.
3. **Drift check is currently human-driven (Claude session dispatches agents).** Should it be fully automated via a scheduled `claude` CLI invocation? Possible, but the human-in-the-loop step doubles as a "did anything look weird?" review. Not converting yet.
4. **The 0.70 alarm threshold in `drift_check.py` is arbitrary.** Could be 0.75 (matches Wilson LB gate) or 0.80 (matches admission gate). Picked 0.70 because comments are noisier than posts and we don't want false alarms in the first quarters. Reconsider after Q3 data.
