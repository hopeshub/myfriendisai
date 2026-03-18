# Task: Keyword Validation Pipeline — Methodology Improvements

## Context
We received a methodological review of the keyword validation pipeline in `analysis/keyword_validation/`. Three improvements need to be implemented now. These are small changes but they matter for research rigor.

---

## Fix 1: Replace "skip" with "ambiguous" in precision scoring

### What to change
In `validation/precision_sampler.py` and `validation/cross_theme_check.py` and `monitoring/keyword_health_check.py`:

**Interactive mode:**
- Change the prompt from `(y/n/s to skip)` to `(y/n/a for ambiguous)`
- Rename "Skipped" to "Ambiguous" in all output and logging

**Scoring:**
- Ambiguous posts should be counted in the denominator, NOT excluded
- Count ambiguous as **half-credit** in the precision score
- Formula: `precision = (yes_count + (ambiguous_count * 0.5)) / (yes_count + no_count + ambiguous_count)`
- Display the ambiguity rate separately: `Ambiguity rate: X/N (XX%)`

**Dump mode (--dump flag):**
- Include a note in the dump file header explaining the ambiguous option

**Logging:**
- Update all CSV log outputs to include an `ambiguous_count` and `ambiguity_rate` column

---

## Fix 2: Add subreddit concentration flag to volume_check.py

### What to change
In `validation/volume_check.py`:

After displaying the per-subreddit breakdown, add a concentration analysis:

1. Calculate what percentage of total hits come from the **top 1 subreddit** and the **top 2 subreddits combined**.
2. Apply these flags and print them clearly:
   - If top 1 subreddit > 50% of hits → print `⚠️  CONCENTRATION WARNING: {subreddit} accounts for {X}% of all hits`
   - If top 2 subreddits combined > 75% of hits → print `⚠️  CONCENTRATION WARNING: Top 2 subreddits account for {X}% of all hits`
   - If neither condition is met → print `✓ Distribution: No concentration issues detected`
3. Add a `concentration_flag` field to any CSV output (values: `none`, `single_sub_dominant`, `top_two_dominant`, `both`)

Also update the stdout summary to include a one-line concentration verdict.

---

## Fix 3: Auto-log to candidates.csv after every validation run

### What to change

Every validation script should automatically append or update a row in `analysis/keyword_validation/candidates.csv` after completing a run.

**precision_sampler.py** — after scoring is complete:
- Check if a row for this keyword + target_theme already exists in candidates.csv
- If yes: update the `precision_score` and `status` fields
- If no: append a new row with:
  - `candidate`: the keyword
  - `target_theme`: the theme
  - `source_method`: "manual" (default, can be overridden with a `--source` flag accepting values: `corpus_comparison`, `emergence_monitor`, `ethnographic`, `manual`)
  - `discovery_date`: today's date
  - `precision_score`: the computed score
  - `ambiguity_rate`: from the run
  - `status`: auto-set based on score:
    - `>= 80%` → `validated`
    - `60-79%` → `testing` (needs second round)
    - `< 60%` → `rejected`
  - `notes`: empty (user can fill in later)

**cross_theme_check.py** — after scoring:
- Find the existing row for this keyword in candidates.csv (if any)
- Update or add a `cross_theme_collisions` field with the collision distribution (e.g., "Addiction:35%, Therapy:65%")
- If any non-target theme exceeds 30%, update `status` to `testing` and add a note: "Cross-theme collision with {theme} at {X}%"

**volume_check.py** — after running:
- Find or create the row for this keyword
- Update `raw_count` with the total hits
- Update `concentration_flag` with the result from Fix 2
- If volume < 50, set status to `rejected` with note: "Below volume threshold ({N} hits)"

**General rules:**
- Use a simple CSV read/write approach — no pandas dependency
- When updating an existing row, preserve all fields that aren't being updated
- Keyword + target_theme together form the unique key (same keyword can be tested against different themes)
- Always write the CSV back with the header row intact

---

## Fix 4: Update README.md

Update the README in `analysis/keyword_validation/README.md` to reflect:

1. **Validation Criteria** section — update to include:
   - Ambiguous scoring methodology (half-credit, reported separately)
   - Subreddit concentration flags (>50% single sub, >75% top two)
   - Two-stage validation policy: >=80% first pass likely keep, 60-79% needs second round at 40-50 posts, <60% reject
   - Note that all validation runs auto-log to candidates.csv

2. **candidates.csv format** section — update column list to include `ambiguity_rate` and `concentration_flag`

3. Add a short **Methodology Notes** section at the bottom that acknowledges:
   - Corpus comparison discovery is path-dependent (finds language near current keywords, not entirely new discourse patterns)
   - Independent ethnographic sampling is needed alongside algorithmic discovery to reduce circularity
   - Cross-theme checks are warning-level, not definitive sorting mechanisms

---

## What NOT to change
- Discovery scripts (corpus_comparison.py, emergence_monitor.py) — no changes needed
- Database schema or data layer
- The fundamental validation workflow — these are refinements, not redesigns
