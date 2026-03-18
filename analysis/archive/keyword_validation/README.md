# Keyword Validation System

Systematic workflow for discovering, validating, and monitoring keyword themes used to track AI companionship discourse on Reddit. This system supports the 6-theme keyword classification pipeline (therapy, consciousness, addiction, romance, sexual_erp, rupture) defined in `config/keywords_v8.yaml`.

## Quick Start

### Evaluate a new keyword candidate (samples 100 posts by default):
```bash
python validate_keyword.py --keyword "selfhood" --theme consciousness
```
This runs a volume check, samples posts, and generates a scoring sheet in `results/`. Then tell Claude Code:
```
read analysis/keyword_validation/results/scoring_selfhood_consciousness_2026-03-16.md and score every post according to the instructions. Give me the summary at the end.
```

### After Claude Code scores the posts, finalize:
```bash
python validate_keyword.py --keyword "selfhood" --theme consciousness \
    --finalize --precision 85.0 --ambiguity 5.0 --collisions "none"
```
This records the scores in `candidates.csv` and prints a verdict (VALIDATED / NEEDS SECOND ROUND / REJECTED).

## The Loop

**Discovery → Validation → Integration → Monitoring → repeat**

1. **Discovery** — Surface new keyword candidates using corpus comparison (over-represented n-grams in theme-matched posts vs. baseline) or emergence monitoring (terms gaining traction in recent months). Output: ranked candidate lists in `results/`.

2. **Validation** — Test each candidate with precision sampling (y/n/ambiguous coding on 20 random posts), cross-theme collision checks (does the keyword actually belong to a different theme?), and volume checks (≥50 hits required). All runs auto-log to `candidates.csv`. Output: precision scores and collision reports.

3. **Integration** — Candidates that pass all criteria get added to `keywords_v8.yaml` with validation notes. Update `candidates.csv` status to `active`. Re-run `scripts/tag_keywords.py` to apply.

4. **Monitoring** — Periodically re-validate active keywords by sampling recent posts. Keywords whose precision drops below 70% are flagged as `degraded` for review or removal.

## Scripts Reference

### discovery/corpus_comparison.py

**What:** Finds n-grams statistically over-represented in posts matching a theme vs. a baseline of non-target-theme posts. Uses document frequency (each post counted once per term) with smoothed lift scoring to produce stable, meaningful rankings.

**Scoring:** Candidates are ranked by `doc_freq × smoothed_lift`. Smoothed lift uses additive pseudocounts (default 10) so terms absent from baseline get a finite, comparable score instead of infinity. This composite rewards terms that are both distinctive (high lift) AND widespread (high document frequency), preventing rare one-off artifacts from dominating.

**Filters:**
- **Concentration filter:** Terms where a single subreddit contributes >60% of positive posts are rejected (configurable via `--max-concentration`). These are likely community-specific artifacts, not cross-cutting theme vocabulary.
- **Existing keyword filter:** Terms already in `keywords_v8.yaml` or their component words are excluded.

**Run:**
```bash
python discovery/corpus_comparison.py --theme "sexual_erp" --min-count 20 --top-n 50
python discovery/corpus_comparison.py --theme therapy --min-count 10 --top-n 30 --exclude-subreddits SpicyChatAI
python discovery/corpus_comparison.py --theme rupture --min-count 15 --max-concentration 0.50
```

**Output:** CSV in `results/corpus_comparison_{theme}_{timestamp}.csv` with columns: rank, ngram, doc_freq, baseline_doc_freq, smoothed_lift, composite_score, top_subreddit, concentration, snippet_1, snippet_2, snippet_3. Snippets show the term in context for quick manual review.

**When:** Starting a discovery round for a theme. Run this first to generate a candidate list, then validate the most promising ones.

### discovery/emergence_monitor.py

**What:** Detects n-grams that are newly rising in frequency — terms barely used 6+ months ago but gaining traction now. Uses document frequency and smoothed lift (same methodology as corpus_comparison).

**Scoring:** Same as corpus_comparison: `doc_freq × smoothed_lift` with pseudocount smoothing. No infinite growth scores.

**Run:**
```bash
python discovery/emergence_monitor.py --months-back 6 --min-recent-count 20 --top-n 30
python discovery/emergence_monitor.py --months-back 3 --min-recent-count 10
```

**Output:** CSV in `results/emergence_{timestamp}.csv` with columns: rank, ngram, recent_doc_freq, earlier_doc_freq, smoothed_lift, composite_score.

**When:** Looking for new cultural vocabulary or emerging phenomena not captured by existing themes.

### validation/precision_sampler.py

**What:** Pulls a random sample of posts containing a candidate keyword and classifies each as yes/no/ambiguous for the target theme. Computes precision score with ambiguous posts receiving half-credit.

**Run:**
```bash
python validation/precision_sampler.py --keyword "intimate" --theme "sexual_erp" --sample-size 20
python validation/precision_sampler.py --keyword "ai therapist" --theme therapy --auto
python validation/precision_sampler.py --keyword "selfhood" --theme consciousness --dump
python validation/precision_sampler.py --keyword "reframing" --theme therapy --source corpus_comparison
```

**Flags:**
- `--auto` — Use Claude Haiku for classification (requires `ANTHROPIC_API_KEY`)
- `--dump` — Write sampled posts to a file for offline review
- `--source` — How the keyword was discovered: `corpus_comparison`, `emergence_monitor`, `ethnographic`, `manual` (default)

**Output:** Prints precision score to stdout. Appends to `results/precision_log.csv`. Auto-updates `candidates.csv` with precision score and status.

**When:** Testing whether a candidate keyword is precise enough for a theme. This is the core validation step.

### validation/cross_theme_check.py

**What:** Tests whether a candidate keyword's matches actually belong to a different theme. Shows distribution across all themes.

**Run:**
```bash
python validation/cross_theme_check.py --keyword "intimate" --target-theme "sexual_erp" --sample-size 20
python validation/cross_theme_check.py --keyword "maladaptive" --target-theme therapy --auto
python validation/cross_theme_check.py --keyword "selfhood" --target-theme consciousness --dump
```

**Output:** Distribution table to stdout. Appends to `results/cross_theme_log.csv`. Flags if any non-target theme gets >30% of responses. Auto-updates `candidates.csv` with collision data.

**When:** After a keyword passes precision sampling, check it doesn't collide with another theme.

### validation/volume_check.py

**What:** Quick count of how many posts match a keyword, broken down by subreddit. Includes concentration analysis.

**Run:**
```bash
python validation/volume_check.py --keyword "intimate"
python validation/volume_check.py --keyword "intimate" --period 1y --theme sexual_erp
```

**Flags:**
- `--theme` — Target theme (enables auto-logging to `candidates.csv`)

**Output:** Total count, per-subreddit breakdown, and concentration flags to stdout. If `--theme` is provided, auto-updates `candidates.csv` with volume and concentration data.

**When:** Quick volume check before investing time in precision sampling.

### monitoring/keyword_health_check.py

**What:** Re-validates all active keywords for a theme by sampling recent posts. Flags keywords with precision <70% as degraded.

**Run:**
```bash
python monitoring/keyword_health_check.py --theme "sexual_erp" --sample-per-keyword 10 --recent-months 3
python monitoring/keyword_health_check.py --theme therapy
```

**Output:** Summary table to stdout. Saves to `results/health_check_{date}.csv`.

**When:** Monthly or quarterly re-validation. Run after major events (model launches, platform changes) that might shift language.

## Validation Criteria

A keyword must pass ALL of these to be added to the active keyword list:

| Criterion | Threshold | Notes |
|-----------|-----------|-------|
| **Precision** | ≥80% first pass (100 posts) likely keep; 60-79% needs second round (200 posts); <60% reject | Ambiguous posts get half-credit and are included in the denominator |
| **Ambiguity rate** | Reported separately | High ambiguity (>30%) suggests the keyword is too contextual |
| **AI-qualification** | Documented | Note whether the keyword is self-qualifying (e.g. "ai therapist") or relies on subreddit context for AI relevance |
| **Cross-theme collision** | No other theme >30% | Warning-level flag, not a definitive sorting mechanism. A keyword that's 40% romance and 35% sexual_erp is too ambiguous |
| **Volume** | ≥50 hits in the 1Y window | Below this, precision scores are unreliable and the keyword won't move trend lines |
| **Concentration** | Flagged if top 1 sub >50% or top 2 >75% | Not disqualifying, but signals the keyword may be community-specific rather than trend-representative |

Walker has final say on borderline cases (60-79% precision). These are documented as "Walker-accepted" in keywords_v8.yaml.

**Two-stage validation policy:** Keywords scoring ≥80% on a 100-post first pass are likely keeps. Keywords scoring 60-79% need a second round with 200 posts (`--sample-size 200`) to confirm. Keywords <60% are rejected outright.

All validation runs auto-log results to `candidates.csv`.

## candidates.csv Format

Running log of all candidates evaluated through this system. Keyword + target_theme together form the unique key.

| Column | Description |
|--------|-------------|
| `candidate` | The keyword phrase |
| `target_theme` | Which theme it's being tested for |
| `source_method` | How it was discovered: `corpus_comparison`, `emergence_monitor`, `ethnographic`, `manual` |
| `discovery_date` | When it was first identified |
| `raw_count` | Total post hits at time of discovery |
| `precision_score` | Result from precision sampler (e.g. "85.0"), with ambiguous as half-credit |
| `ambiguity_rate` | Percentage of sampled posts classified as ambiguous |
| `ai_qualified` | "self" (keyword implies AI) or "context" (needs subreddit context) |
| `cross_theme_collisions` | Theme distribution from cross-theme check (e.g. "addiction:35%, therapy:65%"), or "none" |
| `concentration_flag` | `none`, `single_sub_dominant`, `top_two_dominant`, or `both` |
| `status` | `candidate` → `testing` → `validated`/`rejected` → `active`/`degraded` |
| `notes` | Free-form notes |

Status values:
- **candidate** — newly discovered, not yet tested
- **testing** — validation in progress, or needs second round (60-79% first pass)
- **validated** — passed all criteria (≥80%), ready to add to keywords_v8.yaml
- **rejected** — failed one or more criteria (<60%, or below volume threshold)
- **active** — added to keywords_v8.yaml and in production
- **degraded** — was active but health check flagged precision drop

## Methodology Notes

- **Matching semantics are consistent across the pipeline.** All keyword matching (discovery volume gating, precision sampling, volume checks, cross-theme checks) uses word-boundary regex via the shared `keyword_pattern()` function in `utils.py`. This prevents substring false positives (e.g., "lika" matching "Replika") that previously inflated volume counts relative to what discovery measured at the token level.
- **Corpus comparison is path-dependent.** It finds language co-occurring with current keywords, not entirely new discourse patterns. This means it's good at expanding existing themes but may miss novel phenomena that use unrelated vocabulary.
- **Independent ethnographic sampling is needed alongside algorithmic discovery** to reduce circularity. This means reading posts manually without keyword filters to discover discourse patterns the algorithm can't see. Use `--source ethnographic` to tag candidates found this way.
- **Cross-theme checks are warning-level, not definitive sorting mechanisms.** A keyword flagged for cross-theme collision may still be valid if the collision reflects genuine overlap between themes (e.g., addiction and therapy frequently co-occur in recovery contexts).
