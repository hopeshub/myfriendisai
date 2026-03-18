# Task: Simplify Keyword Automation Pipeline

## Context
We're stripping this down to what we actually use: Phases 1 and 2. Phase 3 (discovery) is being removed from the pipeline. The goal is a clean, simple tool for validating keyword candidates that Walker identifies from reading posts.

## What to do

### 1. Clean up the folder
Remove or archive to a subfolder called `archive/`:
- discover_keywords.py
- Any discovery-related results or CSVs
- Any references to Phase 3 in other scripts

The folder should contain ONLY:
- README.md
- theme_definitions.yaml
- prepare_sample.py (prepares posts for CC classification)
- parse_classifications.py (parses CC output into SQLite + summary)
- prepare_batch.py (prepares multiple keywords at once)
- summarize_batch.py (summary table across a batch)
- utils.py (shared utilities)
- samples/ (generated sample files)
- results/ (output reports)

### 2. Rewrite the README.md
Replace the current three-phase plan with a simple, honest description of what this tool does:

---

# Keyword Validation Pipeline

A tool for validating keyword candidates for the myfriendisai project. Walker identifies candidate keywords from reading AI companion subreddits. This pipeline tests them quickly.

## How it works

1. **Prepare**: `prepare_sample.py` pulls a sample of posts containing the keyword from tracker.db and generates a classification prompt.
2. **Classify**: CC reads the prompt file and classifies each post YES/NO against the theme definition in `theme_definitions.yaml`.
3. **Parse**: `parse_classifications.py` stores CC's output in SQLite and outputs a precision summary.

For multiple keywords at once, use `prepare_batch.py` and `summarize_batch.py`.

## Quick start

### Single keyword
```bash
# Prepare sample
python3 prepare_sample.py --keyword "soulless" --theme rupture

# Tell CC to read and classify
# "Read analysis/keyword_automation/samples/soulless_rupture_prompt.md and classify each post"

# Parse CC's output
python3 parse_classifications.py --keyword "soulless" --theme rupture --input <CC's output>
```

### Batch
```bash
# Prepare a batch (edit batch.yaml with keyword/theme pairs first)
python3 prepare_batch.py --input batch.yaml

# CC classifies the combined prompt

# Summarize results
python3 summarize_batch.py
```

## Theme definitions
`theme_definitions.yaml` contains plain-language definitions of each theme, describing what does and does not count. These definitions are what CC classifies against. Edit them if classification quality needs tuning.

## Storage
Classifications are cached in the `llm_classifications` table in tracker.db. Posts are only classified once per theme+keyword combo.

## Acceptance criteria
- 80%+ precision: auto-accept
- 60-79% precision: review band — accept at Walker's discretion if FP patterns are well-defined and the keyword adds vocabulary diversity (see methodology in CLAUDE.md)
- Below 60%: reject

---

### 3. Rename the folder
Rename `analysis/keyword_automation/` to `analysis/keyword_pipeline/`. "Automation" oversells what it does. "Pipeline" is accurate.

After making changes, show me the final folder structure and README.
