# Task: Build Keyword Validation System

## Context
We track AI companionship discourse on Reddit across 5 themes (Romance, Sex/ERP, Consciousness, Therapy, Addiction, Rupture) using keyword-based classification. Each theme has a curated list of keyword phrases that we match against posts using FTS5 full-text search. We need a systematic workflow for discovering new candidate keywords, validating them, and monitoring existing ones over time.

Create a new directory `keyword_validation/` in the project root with the structure below. Everything should be simple, maintainable Python scripts — no frameworks, no complex dependencies, no over-engineering.

## Directory Structure

```
keyword_validation/
├── README.md                    # Full methodology doc (see below)
├── discovery/
│   ├── corpus_comparison.py     # Stage 1: algorithmic keyword discovery
│   └── emergence_monitor.py     # Stage 1: detect newly rising terms
├── validation/
│   ├── precision_sampler.py     # Stage 2: pull random sample for a candidate keyword
│   ├── cross_theme_check.py     # Stage 2: test a candidate against all themes
│   └── volume_check.py          # Stage 2: check hit count and threshold
├── monitoring/
│   └── keyword_health_check.py  # Stage 3: re-validate existing keywords
├── results/                     # gitignored, stores output CSVs and scorecards
│   └── .gitkeep
└── candidates.csv               # running log of all candidates and their status
```

---

## README.md

Write a clear methodology doc that covers:

1. **Overview** — what this system does and why it exists (one paragraph)
2. **The Loop** — Discovery → Validation → Integration → Monitoring → repeat. Explain each stage in 2-3 sentences.
3. **Scripts Reference** — for each script, document: what it does, how to run it (exact CLI usage with example args), what it outputs, and when you'd use it.
4. **Validation Criteria** — the specific thresholds for a keyword to pass:
   - Precision score ≥ 70% (at least 14/20 sampled posts are genuinely about the target theme)
   - AI-qualification: note whether the keyword is self-qualifying or requires subreddit context
   - No cross-theme collision > 30% (i.e., no more than 30% of hits better fit a different theme)
   - Volume ≥ 50 hits in the 1Y window
5. **candidates.csv format** — explain the columns and status values

---

## candidates.csv

Initialize with headers:
```
candidate,target_theme,source_method,discovery_date,raw_count,precision_score,ai_qualified,cross_theme_collisions,status,notes
```

Status values: `candidate`, `testing`, `validated`, `rejected`, `active`, `degraded`

---

## Script Details

### discovery/corpus_comparison.py

**Purpose:** Given a theme, find n-grams that are statistically over-represented in posts matching that theme vs. a baseline of unmatched posts.

**Usage:** `python corpus_comparison.py --theme "Sex / ERP" --min-count 20 --top-n 50`

**Logic:**
1. Query the database for all posts matching the target theme's existing keywords (positive corpus). Use the same FTS5 matching approach the main site uses.
2. Query a random sample of posts (10,000-20,000) from the same subreddits that do NOT match any theme's keywords (baseline corpus).
3. Tokenize both corpora. Extract unigrams and bigrams. Lowercase everything. Strip punctuation.
4. Remove standard English stopwords, remove any n-grams that are already in ANY theme's keyword list, remove n-grams shorter than 3 characters (for unigrams).
5. Compute over-representation ratio: `(freq_in_positive / positive_size) / (freq_in_baseline / baseline_size)`. Handle division by zero (if the term never appears in baseline, flag it separately as "positive-only").
6. Sort by over-representation ratio descending. Output the top N candidates.

**Output:** CSV file to `results/` with columns: `rank, ngram, positive_count, baseline_count, ratio, sample_post_ids` (include 3 random post IDs containing the term for quick manual inspection).

Also print a summary table to stdout.

### discovery/emergence_monitor.py

**Purpose:** Detect n-grams that are newly rising in frequency — terms that barely existed 6+ months ago but are gaining traction.

**Usage:** `python emergence_monitor.py --months-back 6 --min-recent-count 20 --top-n 30`

**Logic:**
1. Split the corpus into two time windows: "recent" (last N months) and "earlier" (everything before that).
2. Extract unigrams and bigrams from both windows (same tokenization as corpus_comparison.py — share a utility function).
3. Compute growth ratio: `(recent_freq / recent_size) / (earlier_freq / earlier_size)`. Only include terms with at least `--min-recent-count` in the recent window.
4. Filter out terms already in any keyword list and stopwords.
5. Sort by growth ratio descending.

**Output:** CSV file to `results/` with columns: `rank, ngram, recent_count, earlier_count, growth_ratio`.

### validation/precision_sampler.py

**Purpose:** Pull a random sample of posts containing a candidate keyword so you can manually assess precision.

**Usage:** `python precision_sampler.py --keyword "intimate" --theme "Sex / ERP" --sample-size 20`

**Logic:**
1. Query the database for posts from AI companion subreddits that contain the candidate keyword (use FTS5 MATCH).
2. Randomly sample N posts.
3. For each post, display: post title, subreddit, date, a text snippet (first 300 chars of body with the keyword highlighted), and the post's permalink.
4. After displaying each post, prompt the user interactively: "Is this post about [theme]? (y/n/s to skip)" — tally up the results.
5. At the end, print the precision score (y_count / (y_count + n_count)) and total count.

**Output:** Print results to stdout. Also append a line to `results/precision_log.csv` with columns: `keyword, theme, date, sample_size, precision_score, y_count, n_count, skip_count`.

### validation/cross_theme_check.py

**Purpose:** Test whether a candidate keyword collides with other themes — i.e., are the posts it matches actually about a different theme?

**Usage:** `python cross_theme_check.py --keyword "intimate" --sample-size 20`

**Logic:**
1. Pull a random sample of posts containing the keyword (same as precision_sampler).
2. For each post, display the snippet and ask: "Which theme does this post best fit? (romance / sex_erp / consciousness / therapy / addiction / rupture / none)"
3. Tally results. Report the distribution across themes.
4. Flag if any theme OTHER than the target gets > 30% of responses.

**Output:** Print distribution table to stdout. Append to `results/cross_theme_log.csv`.

### validation/volume_check.py

**Purpose:** Quick count of how many posts a candidate keyword matches.

**Usage:** `python volume_check.py --keyword "intimate"` or `python volume_check.py --keyword "intimate" --period 1y`

**Logic:**
1. Count posts matching the keyword in the AI companion subreddits, optionally filtered by time period.
2. Break down by subreddit.
3. Report total count and per-subreddit counts.

**Output:** Print to stdout.

### monitoring/keyword_health_check.py

**Purpose:** Re-validate all active keywords for a theme by sampling recent posts.

**Usage:** `python keyword_health_check.py --theme "Sex / ERP" --sample-per-keyword 10 --recent-months 3`

**Logic:**
1. Load the keyword list for the given theme.
2. For each keyword, pull 10 random RECENT posts (from the last N months) that match it.
3. Display each post and prompt: "Is this post about [theme]? (y/n/s)"
4. Compute precision for each keyword.
5. Flag any keyword scoring below 70% as potentially degraded.

**Output:** Print summary table. Save to `results/health_check_YYYY-MM-DD.csv`.

---

## Shared Utilities

Create a `keyword_validation/utils.py` with:
- Database connection helper (reuse the project's existing DB path/connection pattern — check how the rest of the codebase does it)
- Tokenizer function (lowercase, strip punctuation, split into unigrams and bigrams)
- Stopword list (use a standard English stopword list, plus add common Reddit terms: "http", "https", "www", "com", "removed", "deleted", "edit", "update")
- Function to load all current theme keyword lists from wherever they're stored in the project
- Snippet highlighter (given text and a keyword, return a truncated snippet with the keyword wrapped in asterisks or ANSI color)

---

## Important Implementation Notes

- Look at the existing codebase to understand: where the SQLite database lives, how FTS5 queries are constructed, where theme keyword lists are defined, and what the posts table schema looks like. Match those patterns.
- All scripts should use argparse for CLI arguments.
- All scripts should work from the `keyword_validation/` directory OR the project root.
- Keep it simple. No classes where a function will do. No abstractions for "future flexibility." These are research scripts, not production code.
- Add `results/` to .gitignore if it isn't already covered.
