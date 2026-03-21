# Keyword Validation Pipeline

A tool for validating keyword candidates for the myfriendisai project. The researcher identifies candidate keywords from reading AI companion subreddits. This pipeline tests them quickly.

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
# "Read analysis/keyword_pipeline/results/classify_soulless_rupture_2026-03-17.md and classify each post"

# Parse CC's output
python3 parse_classifications.py \
  --prompt-file results/classify_soulless_rupture_2026-03-17.md \
  --output-file results/classified_soulless_rupture_2026-03-17.txt
```

### Batch
```bash
# Prepare a batch (edit batch.yaml with keyword/theme pairs first)
python3 prepare_batch.py --batch-file batch.yaml

# CC classifies the combined prompt

# Parse and summarize results
python3 parse_batch.py \
  --prompt-file results/batch_2026-03-17.md \
  --output-file results/classified_batch_2026-03-17.txt
python3 summarize_batch.py
```

## Theme definitions
`theme_definitions.yaml` contains plain-language definitions of each theme, describing what does and does not count. These definitions are what CC classifies against. Edit them if classification quality needs tuning.

## Storage
Classifications are cached in the `llm_classifications` table in tracker.db. Posts are only classified once per theme+keyword combo.

## Acceptance criteria
- 80%+ precision: auto-accept
- 60-79% precision: review band — accept at The researcher's discretion if FP patterns are well-defined and the keyword adds vocabulary diversity (see methodology in CLAUDE.md)
- Below 60%: reject
