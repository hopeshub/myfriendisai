# Task: Build Keyword Validation Orchestrator Script

## Context
The keyword validation pipeline in `analysis/keyword_validation/` currently requires running 4-5 separate scripts manually. We want a single orchestrator script that automates as much as possible and minimizes manual steps.

The constraint: we do NOT use the Anthropic API for LLM scoring. Instead, we generate dump files that the user feeds to Claude Code for classification.

## Create: `analysis/keyword_validation/validate_keyword.py`

This is the main entry point for the entire validation pipeline. It runs in two modes.

---

### Mode 1: Evaluate (default)

**Usage:**
```
python validate_keyword.py --keyword "selfhood" --theme "Consciousness"
```

**Optional flags:**
- `--sample-size N` (default 20)
- `--period PERIOD` (default "1y")
- `--source METHOD` (default "manual", accepts: corpus_comparison, emergence_monitor, ethnographic, manual)

**What it does, in order:**

**Step 1: Volume check**
- Run the same logic as `validation/volume_check.py`
- Print the total hits and per-subreddit breakdown
- Print concentration flags

- If hits < 50:
  - Print `❌ REJECTED: Below volume threshold ({N} hits)`
  - Auto-log to candidates.csv with status `rejected` and note "Below volume threshold"
  - Stop here. Do not continue to sampling.

- If hits >= 50:
  - Print `✓ Volume: {N} hits (passes threshold)`
  - Print any concentration warnings
  - Continue to Step 2

**Step 2: Generate scoring dumps**
- Sample `--sample-size` random posts containing the keyword from AI companion subreddits
- Write TWO files to `analysis/keyword_validation/results/`:

**File 1: `results/scoring_{keyword}_{theme}_{date}.md`**

Format this as a markdown file that is designed to be read by an LLM (Claude Code). Include:

```markdown
# Keyword Validation Scoring Sheet
**Keyword:** {keyword}
**Target Theme:** {theme}
**Date:** {date}
**Sample Size:** {N}
**Instructions:** For each post below, provide TWO scores:

1. **Precision:** Is this post genuinely about the theme "{theme}"?
   - YES: The post is clearly about {theme}
   - NO: The post is not about {theme}
   - AMBIGUOUS: Unclear or borderline

2. **Best-fit theme:** Which theme does this post BEST belong to?
   - Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture, or None

After scoring all posts, provide a summary in this exact format:
```
PRECISION: {yes_count}/{total} = {percentage}%
AMBIGUOUS: {count}/{total} = {percentage}%
CROSS-THEME DISTRIBUTION:
  Romance: {count}
  Sex/ERP: {count}
  Consciousness: {count}
  Therapy: {count}
  Addiction: {count}
  Rupture: {count}
  None: {count}
COLLISIONS ABOVE 30%: {list or "none"}
```

---

## Posts to Score

### Post 1 of {N}
**Title:** {title}
**Subreddit:** r/{subreddit}
**Date:** {date}
**Permalink:** https://www.reddit.com{permalink}
**Snippet:**
> {first 500 chars of body with keyword highlighted in **bold**}

---

### Post 2 of {N}
...
```

**File 2: Not needed — combine precision and cross-theme into one scoring sheet as shown above.**

**Step 3: Print next steps**
After generating the file, print:

```
═══════════════════════════════════════════════════
  VALIDATION FILE READY
  
  Volume: {N} hits ✓
  Concentration: {status}
  
  Next step — tell Claude Code:
  
    read analysis/keyword_validation/results/scoring_{keyword}_{theme}_{date}.md and score every post according to the instructions. Give me the summary at the end.
  
  Then run:
  
    python validate_keyword.py --keyword "{keyword}" --theme "{theme}" --finalize --precision {score} --ambiguity {score} --collisions "{collision_string}"
═══════════════════════════════════════════════════
```

Also log the keyword to candidates.csv with status `testing` at this point.

---

### Mode 2: Finalize

**Usage:**
```
python validate_keyword.py --keyword "selfhood" --theme "Consciousness" --finalize --precision 94.7 --ambiguity 5.3 --collisions "none"
```

**Flags:**
- `--finalize` — triggers finalize mode
- `--precision FLOAT` — precision percentage from CC scoring
- `--ambiguity FLOAT` — ambiguity rate percentage from CC scoring  
- `--collisions STRING` — either "none" or a comma-separated list like "Addiction:35%,Therapy:10%"

**What it does:**

1. Parse the scores
2. Apply decision rules:
   - Precision >= 80% AND no collisions above 30% → status `validated`
   - Precision 60-79% OR any collision above 30% → status `testing` with note recommending second-round review at 40-50 posts
   - Precision < 60% → status `rejected`
3. Update the existing row in candidates.csv with all scores and the final status
4. Print a clear verdict:

```
═══════════════════════════════════════════════════
  VERDICT: {keyword} → {theme}
  
  Precision:     {score}% {✓ or ⚠️ or ❌}
  Ambiguity:     {score}%
  Volume:        {N} hits
  Concentration: {status}
  Collisions:    {collision_string}
  
  Status: VALIDATED / NEEDS SECOND ROUND / REJECTED
  
  {If validated: "Ready to add to keyword list. Tell CC:"}
  {  "Add '{keyword}' to the {theme} theme keyword list and backfill historical posts."}
  
  {If needs second round: "Run again with --sample-size 50 for a larger review."}
  
  {If rejected: "Logged as rejected in candidates.csv."}
═══════════════════════════════════════════════════
```

---

## Implementation Notes

- Import and reuse logic from the existing scripts in `validation/` — don't duplicate the database queries, tokenization, or CSV handling
- The orchestrator should call functions from the existing scripts, not shell out to them
- Use the same `utils.py` for DB connection, snippet highlighting, keyword matching
- All file paths should work whether run from `analysis/keyword_validation/` or the project root
- Use argparse with subcommands or flag detection to handle both modes cleanly
- Add a `--help` that clearly explains both modes with examples

---

## Also update README.md

Add a **Quick Start** section at the top of the README that shows the two-command workflow:

```
## Quick Start

### Evaluate a new keyword candidate:
python validate_keyword.py --keyword "selfhood" --theme "Consciousness"

### After CC scores the posts, finalize:
python validate_keyword.py --keyword "selfhood" --theme "Consciousness" --finalize --precision 94.7 --ambiguity 5.3 --collisions "none"
```

## What NOT to change
- Existing individual scripts — they should still work standalone
- Database schema
- candidates.csv format (but rows will now be created/updated by this script)
