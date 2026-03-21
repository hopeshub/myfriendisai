# Keyword Discovery via Co-occurrence Analysis

**Goal:** Surface new keyword candidates by analyzing what distinctive words and phrases appear in posts that already match our validated keywords, compared to the general corpus. This is a corpus linguistics technique called collocation extraction.

**Important:** This script generates CANDIDATES only. Do not add anything to keywords.yaml. Do not modify any existing data. Output a report that Walker will review manually.

---

## Setup

You'll need the existing database (tracker.db) and the current keyword_hits table (already populated from the tagger).

Create a new Python script: `scripts/keyword_discovery.py`

---

## Step 1: Build a "matched posts" corpus and a "general" corpus per category

For each of the 6 categories (therapy, consciousness, addiction, romance, sexual_erp, rupture):

1. Pull all posts that matched that category from keyword_hits → join to posts table to get title + selftext
2. Pull a random sample of 50,000 posts that did NOT match ANY category (these are your control/general corpus)

Combine title and selftext into a single text field for each post. Lowercase everything. Strip URLs, markdown formatting, and common Reddit boilerplate ("edit:", "update:", "tldr").

---

## Step 2: Tokenize and extract n-grams

For both the matched corpus and the general corpus:

1. Tokenize into words (split on whitespace and punctuation, remove tokens that are purely punctuation or numbers)
2. Remove standard English stopwords (use NLTK's stopword list — `pip install nltk --break-system-packages` if needed)
3. Generate:
   - Unigrams (single words)
   - Bigrams (2-word phrases)
   - Trigrams (3-word phrases)

For bigrams and trigrams, only keep phrases where at least one word is NOT a stopword.

---

## Step 3: Calculate overrepresentation scores

For each n-gram, compute:

```
frequency_in_matched = count in matched posts / total tokens in matched posts
frequency_in_general = count in general posts / total tokens in general posts
overrepresentation_ratio = frequency_in_matched / frequency_in_general
```

Also compute a simple significance filter:
- The n-gram must appear in at least 5 matched posts (absolute minimum — we need enough signal)
- The overrepresentation ratio must be at least 5x (it appears 5 times more often in matched posts than general posts)
- The n-gram must not be one of the existing validated keywords (we already know about those — exclude all terms currently in keywords.yaml)

---

## Step 4: Rank and filter

For each category, produce a ranked list of the top 50 candidate n-grams, sorted by overrepresentation ratio (highest first).

For each candidate, report:
- The n-gram itself
- Count in matched posts
- Count in general corpus
- Overrepresentation ratio
- Number of unique matched posts it appears in

---

## Step 5: Cross-category check

Some candidates may appear across multiple categories. For each candidate that shows up in more than one category's top 50, flag it and show which categories it appears in. These are either:
- Generic companion-talk terms (not useful for theme-specific tracking)
- Bridge terms that connect themes (potentially interesting but not precise enough for one category)

---

## Step 6: Sample contexts

For the top 20 candidates in each category, pull 3 random example post excerpts (first 200 chars of title + selftext) where that candidate appears. This lets Walker quickly eyeball whether the candidate is capturing real thematic signal or noise.

---

## Output

Write the full report to `docs/keyword_discovery_report.md` with this structure:

```
# Keyword Discovery Report — Co-occurrence Analysis

Generated: [date]
Matched corpus: [N] posts across 6 categories
General corpus: [N] randomly sampled non-matching posts

## Category: [name]
### Existing keywords: [list current keywords for reference]
### Top 50 candidates

| Rank | N-gram | Matched posts | General posts | Ratio | Unique matched posts |
|------|--------|--------------|---------------|-------|---------------------|
| 1    | ...    | ...          | ...           | ...   | ...                 |

### Top 20 — sample contexts

#### 1. "[candidate]"
- Post A: "[excerpt]"
- Post B: "[excerpt]"
- Post C: "[excerpt]"

[repeat for top 20]

## Cross-category candidates
[table of n-grams appearing in multiple categories]
```

---

## Performance notes

- The general corpus sample of 50,000 should be enough for stable frequency estimates. If it's too slow, drop to 20,000.
- Trigram extraction on large corpora can be memory-heavy. If memory is an issue, process in batches of 10,000 posts at a time and accumulate counts.
- Expected runtime: 10-30 minutes depending on corpus size and machine.

---

## CC prompt

```
Read docs/CC_KEYWORD_DISCOVERY.md and follow the instructions exactly. Create and run scripts/keyword_discovery.py. Write the full report to docs/keyword_discovery_report.md. Do not modify keywords.yaml or any existing data.
```
