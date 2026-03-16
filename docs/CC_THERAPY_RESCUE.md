# Therapy Category Rescue — Diagnosis and Discovery

**Goal:** The therapy category has 452 total hits across 3.7M posts (0.1 hits/1k) and the keyword discovery report revealed heavy contamination from SpicyChat bot-building guide spam. We need to: (1) understand the scope of the spam problem, (2) clean it from the analysis, and (3) attempt keyword discovery on the clean corpus.

Do NOT modify keywords.yaml, keyword_hits, or the posts table. This is analysis only. Write all findings to `docs/therapy_rescue_report.md`.

---

## Part 1: Diagnose the spam

### 1A: Identify the spam posts

The keyword discovery report showed that therapy-matched posts are dominated by SpicyChat bot-building guides containing phrases like "veritas nexus," "stellar synergy," "carnival's," etc. Find all therapy-matched posts that appear to be bot-building guides or promotional content rather than genuine user discourse.

Run this query to see which posts matched the therapy keywords:

```sql
SELECT 
    p.id,
    p.subreddit,
    p.title,
    p.author,
    kh.matched_term,
    SUBSTR(p.selftext, 1, 300) as body_preview,
    LENGTH(p.selftext) as body_length
FROM keyword_hits kh
JOIN posts p ON kh.post_id = p.id
WHERE kh.category = 'therapy'
ORDER BY LENGTH(p.selftext) DESC;
```

Manually scan through the results and classify each post into one of these buckets:

- **GENUINE** — A real user discussing AI companions in a therapeutic context (e.g., "this app has been therapeutic for me," "I use my AI as a therapist," "better than my real therapist")
- **SPAM/PROMO** — Bot-building guides, SpicyChat tutorials, promotional content that happens to contain the word "therapeutic" or another therapy keyword incidentally
- **AMBIGUOUS** — Can't tell from the preview

Report:
- Total therapy-matched posts
- Count and percentage in each bucket
- The specific authors and post titles of the spam posts (there may be just a few prolific posters)
- Which therapy keyword triggered the match for spam posts (is it all "therapeutic"?)

### 1B: Check if spam affects other categories

Run a quick check — do any of the spam authors/posts identified above also appear in other category matches?

```sql
SELECT 
    kh.category,
    COUNT(*) as hits_from_spam_authors
FROM keyword_hits kh
JOIN posts p ON kh.post_id = p.id
WHERE p.author IN ([LIST OF SPAM AUTHORS FROM 1A])
GROUP BY kh.category;
```

---

## Part 2: Clean discovery

### 2A: Build a clean therapy corpus

Take the therapy-matched posts, EXCLUDE the ones identified as SPAM/PROMO in Part 1, and build a clean corpus of genuine therapy-related posts.

Report:
- How many genuine therapy posts remain after spam removal
- Which keywords generated the genuine matches (breakdown by keyword)

### 2B: Manual review of genuine matches

For each therapy keyword, pull 10 random GENUINE (non-spam) matches and show title + first 200 chars of body. This tells us which keywords are actually working well for therapy vs. catching incidental usage.

Report for each keyword:
- Number of genuine matches
- Estimated true positive rate (of the 10 samples, how many are genuinely about AI-as-therapy?)
- Whether the keyword is worth keeping

### 2C: Re-run co-occurrence discovery on clean corpus

Using ONLY the genuine therapy posts (spam removed), repeat the co-occurrence analysis from the keyword discovery script:

1. Tokenize the genuine therapy posts into unigrams, bigrams, trigrams
2. Compare frequencies against the same 50,000-post general corpus used before
3. Apply the same filters: minimum 3 matched posts (lowered from 5 since we have fewer posts), 5x overrepresentation
4. Rank top 50 candidates
5. For top 20, pull 3 sample contexts

The lower threshold (3 instead of 5) is intentional — therapy is a small category and we want to see what's there even at low volume.

### 2D: Brainstorm from genuine posts

After reviewing the genuine therapy matches, look for common PATTERNS in how people talk about AI-as-therapy that aren't captured by individual keywords. For example:
- Do people say "better than my therapist" or "replaced my therapist"?
- Do they describe specific therapeutic benefits ("helps with my anxiety," "helps me process")?
- Is there a pattern of comparing AI to professional therapy?

List any recurring phrases or patterns you observe, even if they only appear 2-3 times. These are brainstorm candidates, not validated keywords — Walker will decide which to test.

---

## Part 3: Assess viability

Based on everything above, provide an honest assessment:

1. **After spam removal, how many genuine therapy matches remain?** If it's under 50 total posts across 3+ years, the category may not be viable with keyword matching alone.
2. **Did the clean discovery surface any promising candidates?** List the top 5 with your confidence level.
3. **Is "therapeutic" salvageable as a keyword, or is it too noisy?** The audit showed false positives from casual usage ("muffin top is therapeutic"). After spam removal, what's the real precision?
4. **Honest recommendation:** Should therapy remain as its own category, be merged with another theme, or be acknowledged as a valid but extremely low-signal tracker?

---

## Output

Write everything to `docs/therapy_rescue_report.md` with clear section headers matching the parts above.

## CC Prompt

```
Read docs/CC_THERAPY_RESCUE.md and follow the instructions. This is analysis only — do not modify any data. Write the full report to docs/therapy_rescue_report.md.
```
