# Task: Update Discovery Filtering + README

Two things to do:

## 1. Fix discover_keywords.py filtering

Add these filtering requirements to the discovery script:

1. **Minimum 10 distinct posts** containing the term (not just raw token count — a word appearing 200 times in 3 posts is copypasta, not vocabulary)
2. **Minimum 3 distinct subreddits** — terms concentrated in a single community are likely artifacts
3. **Proper noun filter** — exclude terms that appear capitalized >80% of the time (catches character names, usernames)
4. **Minimum 5 characters** — catches substrings like "lika" from Replika
5. **Subreddit name filter** — exclude terms that are substrings of any subreddit name in the corpus (catches "lika", "nomi", etc.)

After fixing, re-run on ALL SIX themes and show the top 20 candidates per theme.

## 2. Update analysis/keyword_automation/README.md

Update the Phase 3 section (Step 3.2) to reflect these filtering requirements as permanent parts of the pipeline, not one-off fixes. Replace the existing filter list with:

```
- Filter out:
  - Words already in the current keywords yaml
  - Common stopwords
  - Words shorter than 5 characters (catches substrings of platform names)
  - Words with fewer than 10 distinct posts containing the term (raw token count is misleading — copypasta inflates frequency)
  - Words appearing in fewer than 3 distinct subreddits (too concentrated)
  - Proper nouns: words capitalized >80% of the time (character names, usernames)
  - Words that are substrings of subreddit names in the corpus
```

Also add a note under Phase 3 overview:

```
NOTE: Raw TF-IDF on Reddit data produces heavy noise from copypasta, character names,
usernames, and platform-specific artifacts. The filtering requirements below were developed
through trial and error and are essential for usable output.
```
