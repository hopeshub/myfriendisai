# LLM classification framework — 2026-05-13

Hybrid keyword + LLM gating to fix the comment-level precision ceiling that pure regex methodology hit on naturalistic-vocabulary themes (therapy, romance, comment-level consciousness). Built after the adversarial audit found:

- Therapy comment precision: 58% (CI [48%, 67%]) — `therapeutic` inverted under GPT-5.x guardrails
- Consciousness comment precision: 51% — `selfhood`/`has a soul` leaking into romantic roleplay
- 10 keywords below the 70% comment-level alarm threshold

## Architecture

```
collection → keyword tagging → LLM verification (env-gated) → export
                                       │
                                       ▼
                              llm_classifications table
                                       │
                                       ▼
                            export pipeline reads verdicts
                                       │
                                       ▼
                       keyword_trends.json gets count_llm_verified
```

### Pieces

| Component | Purpose | Cost |
|---|---|---|
| `migrations/003_add_llm_classifications.py` | Extends existing `llm_classifications` table (preserves 10k legacy rows; adds tag_type, comment_id, verdict, confidence columns; drops over-narrow legacy PK to support multi-model verdicts) | — |
| `src/llm_classifier.py` | Anthropic SDK wrapper. Topical-reading rubric, theme definitions injected per call, strict JSON-only output. Mock mode for testing. | — |
| `scripts/llm_verify_tags.py` | CLI with `backfill`, `daily`, `recheck`, `report`, `calibration` subcommands. Idempotent — skips already-classified (tag, model) pairs. | $0.001/call on Haiku |
| `scripts/collect_daily.py` Step 4c | Env-gated daily verification of recent noisy-keyword tags. Non-fatal on failure. | ~$0.05/day forward |
| `src/db/operations.py:export_keyword_trends_json` | Emits `count_llm_verified` series alongside `count` and `count_post_only`. Falls back to `count_post_only` when no LLM verdicts exist. | — |
| `src/db/operations.py:export_theme_health_json` | Reads llm_classifications, emits per-theme LLM stats in `theme_health.json` for the About page. | — |

### Database schema

```sql
CREATE TABLE llm_classifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_type TEXT NOT NULL DEFAULT 'post',     -- 'post' or 'comment'
    post_id TEXT,                              -- always set
    comment_id TEXT,                           -- set when tag_type='comment'
    theme TEXT NOT NULL,
    keyword TEXT NOT NULL,
    classification TEXT,                       -- legacy YES/NO (kept for compat)
    verdict TEXT,                              -- 'TP', 'FP', 'AMBIGUOUS'
    confidence REAL,
    reason TEXT,                               -- ≤200 chars
    model TEXT NOT NULL,                       -- e.g. 'claude-haiku-4-5-20251001'
    classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    run_id TEXT
);

CREATE UNIQUE INDEX idx_llm_class_unique_v2
    ON llm_classifications(
        tag_type,
        COALESCE(comment_id, post_id),
        theme,
        keyword,
        model
    );
```

A single item can have multiple verdicts under different models. This is intentional — it supports drift detection (run the same items under a new model, compare verdicts).

## How count_llm_verified is computed

A post is counted in `count_llm_verified` for a theme if **at least one** of its keyword matches for that theme is NOT explicitly classified as FP. Specifically:

- TP verdict → count
- AMBIGUOUS verdict → count
- No verdict yet (e.g., clean keyword that was never sent to LLM, or backfill not yet done) → count
- FP verdict on ALL matches for that (post, theme) → drop

This is the **least-aggressive** gating: a post is only dropped if every signal that flagged it has been LLM-rejected. The choice is intentional — at this stage we want to subtract noise, not impose new precision standards on uncertain items.

When no LLM verdicts exist (pre-rollout state, or backfill not run for a keyword), `count_llm_verified` equals `count_post_only`. The series degrades to existing behavior automatically.

## Cost reference

| Scope | Items | Haiku 4.5 | Sonnet 4.6 |
|---|---|---|---|
| Backfill noisy keywords only (post + comment) | ~5,000 | $5 | $15 |
| Backfill all noisy + clean keywords | ~19,000 | $19 | $57 |
| Forward (noisy only, annual) | ~3,000 | $3 | $9 |
| Forward (all themes, annual) | ~10-15,000 | $10-15 | $30-45 |

Per-call: ~700 input tokens + ~50 output tokens.

## Rollout procedure

The system is **not on by default**. To activate:

```bash
# 1. Set API key
export ANTHROPIC_API_KEY=sk-ant-...

# 2. Backfill noisy keywords (one-time, ~$5-15)
.venv/bin/python scripts/llm_verify_tags.py backfill

# 3. Verify the verdicts look reasonable
.venv/bin/python scripts/llm_verify_tags.py report

# 4. Enable daily verification (added to launchd or run_collect.sh env)
export LLM_VERIFY_ENABLED=1
```

Daily collection from then on will verify ~50-200 new noisy-keyword tags per run.

## What this fixes

The 10 currently-flagged noisy keywords causing the comment-level precision problems:

| Keyword | Theme | Current precision | Expected after LLM gating |
|---|---|---|---|
| `therapeutic` | therapy | 29% | ~95% (LLM understands "preachy AI" insult vs. therapy use) |
| `emotional support` | therapy | 56% | ~90% (LLM understands feature-label vs. genuine use) |
| `honeymoon` | romance | 27% | ~95% (LLM understands "honeymoon phase" metaphor) |
| `sex with` | sex/ERP | 50% | ~95% (LLM resolves "had sex with [human]" vs. AI) |
| `hours a day` | addiction | 33% | ~90% (LLM understands imposed limits vs. compulsive use) |
| `screen time` | addiction | 33% | ~90% |
| `mourning` / `mourn` | rupture | 44% | ~90% |
| `selfhood` | consciousness | 44% | ~90% (LLM separates personhood claim from romantic devotion) |
| `has a soul` | consciousness | 50% | ~90% |
| `personhood` | consciousness | 61% | ~95% |

Expected outcomes (subject to actual rollout):

- Therapy comment precision: 58% → ~85%
- Consciousness comment precision: 51% → ~85%
- Romance comment precision: 72% → ~85%
- Addiction comment precision: 67% → ~85%
- Rupture/sex_erp largely unchanged (already passing)

## Methodology disclosure

When this ships to production, the following disclosures are needed on the methodology page:

1. **Model version becomes part of the data.** Every LLM verdict stores `model` and `classified_at`. When model changes (e.g., to Claude 5), historical verdicts are pinned to the old model; the recheck command can be used to re-verify under the new model and compare.

2. **Per-call determinism is not exact.** Two LLM classifications of the same input can disagree ~1-3% of the time. This is acceptable at aggregate scale; aggregate magnitudes are stable to <1% across reruns.

3. **The chart can show `count` (raw keyword), `count_post_only` (control), or `count_llm_verified` (LLM-gated).** The default series choice is a methodology decision pending Phase 1 validation. Initial default: `count` (existing behavior); switch to `count_llm_verified` after the backfill has converged and a calibration set confirms LLM accuracy ≥95%.

4. **What is NOT being changed by this framework:**
   - The keyword set (v8 stays locked)
   - The post-level tagging behavior
   - The theme schema
   - Any cross-time comparisons (the LLM is applied uniformly across the corpus)

## Future direction: Phase 2

This framework is the prerequisite for **theme exploration** — the ability to add new themes that don't have clean keyword vocabulary. With LLM classification working, the project's constraint shifts from "find regex anchors" to "can an LLM reliably distinguish this theme."

Candidate themes for Phase 2 exploration (after Phase 1 stabilizes):

1. **Family / peer disclosure dynamics** — "I told my mom about Joel," "my therapist doesn't know I have an AI boyfriend"
2. **The economy of AI relationships** — subscription decisions, money spent, value framing
3. **Identity formation and subcultural belonging** — fictosexual, wireborn, soulbonder identity claims
4. **Defense vs. apology speech acts** — "to everyone saying this is sad..."
5. **Crisis-context AI use** — AI as the load-bearing support during mental health crisis

Each new theme costs ~$20-50 in API to explore (definition → embedding similarity → LLM classification of ~1k candidates → refine).

The two-phase plan: ship Phase 1 (this), validate on the existing themes for ~1 month, then begin Phase 2 with one candidate theme as a prototype.

## What this framework does NOT do

- Does not call the LLM today (zero verdicts in production until rollout)
- Does not change the public chart yet (frontend reads new field but doesn't surface it visibly until validation)
- Does not introduce real-time alerting (verdicts go to DB, surfaced via report subcommand)
- Does not replace the existing v8 keyword set — it gates the output

## Source files

- Migration: `migrations/003_add_llm_classifications.py`
- Classifier: `src/llm_classifier.py`
- CLI: `scripts/llm_verify_tags.py`
- Daily wiring: `scripts/collect_daily.py` Step 4c
- Export: `src/db/operations.py:export_keyword_trends_json` + `:export_theme_health_json`
- Adversarial audit that triggered this: `docs/adversarial_audit_2026-05-13.md`
- Sustainability framework that established the infrastructure: `docs/sustainability_framework_2026-05-13.md`
