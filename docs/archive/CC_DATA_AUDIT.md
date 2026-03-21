# FULL DATA INTEGRITY AUDIT
#
# We found 3 contamination issues (excluded subs still tagged,
# relationship_advice in data, JanitorAI/SillyTavern not cleaned).
# This audit checks EVERYTHING before we go further.
#
# Run every check. Report results for ALL checks even if they pass.
# Do not skip checks that seem unlikely to fail.

## REFERENCE: What the data SHOULD look like

### Allowed subreddits (T1-T3 ONLY, 22 subs):
```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

### NOT allowed in post_keyword_tags:
- T0 subs: ChatGPT, OpenAI, singularity, ClaudeAI, claudexplorers
- Removed subs: JanitorAI_Official, SillyTavernAI
- Any sub not in the 22 above (relationship_advice, depression,
  Anxiety, autism, AutismInWomen, etc.)

### Allowed keyword categories (v8, 6 themes):
```
therapy, consciousness, addiction, romance, sexual_erp, rupture
```

---

## AUDIT 1: Subreddit Contamination

### 1a. What subreddits exist in post_keyword_tags?

```sql
SELECT p.subreddit, COUNT(*) as tag_count
FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
GROUP BY p.subreddit
ORDER BY tag_count DESC;
```

Compare this list against the 22 allowed subs. Flag ANY subreddit
that is not in the allowed list. Report the full table.

### 1b. What subreddits exist in the posts table?

```sql
SELECT subreddit, COUNT(*) as post_count
FROM posts
GROUP BY subreddit
ORDER BY post_count DESC;
```

It's fine for the posts table to have extra subs (T0, old backfills).
The issue is only if those posts leak into post_keyword_tags.

### 1c. Explicit check for known problem subs:

```sql
SELECT p.subreddit, COUNT(*) FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
WHERE p.subreddit NOT IN (
  'replika','CharacterAI','MyBoyfriendIsAI','ChatGPTcomplaints',
  'AIRelationships','MySentientAI','BeyondThePromptAI',
  'MyGirlfriendIsAI','AICompanions','SoulmateAI','KindroidAI',
  'NomiAI','SpicyChatAI','ChaiApp','HeavenGF','Paradot',
  'AIGirlfriend','ChatGPTNSFW','Character_AI_Recovery',
  'ChatbotAddiction','AI_Addiction','CharacterAIrunaways'
)
GROUP BY p.subreddit
ORDER BY 2 DESC;
```

This should return ZERO rows. If it returns anything, those are
contamination sources.

---

## AUDIT 2: Category Contamination

### 2a. What categories exist in post_keyword_tags?

```sql
SELECT category, COUNT(*) as tag_count
FROM post_keyword_tags
GROUP BY category
ORDER BY tag_count DESC;
```

Should be exactly 6 categories matching v8. Flag any old categories
(romantic_language, dependency_language, withdrawal_recovery_language,
sentience_consciousness_language, attachment_language, etc.) that
are leftover from prior keyword versions.

### 2b. What keywords are being matched per category?

```sql
SELECT category, matched_term, COUNT(*) as hits
FROM post_keyword_tags
GROUP BY category, matched_term
ORDER BY category, hits DESC;
```

Compare every matched_term against the v8 keyword list. Flag any
keyword that is NOT in v8 — it's a leftover from a prior version.

---

## AUDIT 3: Duplicate Posts

### 3a. Duplicate post IDs in posts table:

```sql
SELECT id, COUNT(*) as dupes
FROM posts
GROUP BY id
HAVING COUNT(*) > 1
ORDER BY dupes DESC
LIMIT 20;
```

### 3b. Duplicate post IDs in post_keyword_tags:

```sql
SELECT post_id, category, matched_term, COUNT(*) as dupes
FROM post_keyword_tags
GROUP BY post_id, category, matched_term
HAVING COUNT(*) > 1
ORDER BY dupes DESC
LIMIT 20;
```

Both should return zero rows.

---

## AUDIT 4: Keyword Accuracy Spot Check

For EACH of the 6 themes, pull 5 random tagged posts and display
the subreddit, title, matched_term, and first 200 chars of selftext.
This is a quick sanity check that keywords are matching real content.

```sql
-- Repeat for each category
SELECT p.subreddit, p.title, t.matched_term,
  SUBSTR(p.selftext, 1, 200) as preview
FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
WHERE t.category = 'CATEGORY_NAME'
ORDER BY RANDOM()
LIMIT 5;
```

Read the results yourself. Do the matches make sense? Flag anything
suspicious.

---

## AUDIT 5: Temporal Sanity Check

### 5a. Date range of tagged posts:

```sql
SELECT
  category,
  MIN(datetime(p.created_utc, 'unixepoch')) as earliest,
  MAX(datetime(p.created_utc, 'unixepoch')) as latest,
  COUNT(DISTINCT t.post_id) as posts
FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
GROUP BY category;
```

All categories should span roughly Jan 2023 to Mar 2026. If any
category has a wildly different range, investigate.

### 5b. Monthly volume check for anomalies:

For each theme, show monthly post counts. Flag any month that is
>3x the median for that theme (potential spike to investigate) or
any month with 0 posts (potential data gap).

```sql
SELECT
  t.category,
  strftime('%Y-%m', datetime(p.created_utc, 'unixepoch')) as month,
  COUNT(DISTINCT t.post_id) as posts
FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
GROUP BY t.category, month
ORDER BY t.category, month;
```

---

## AUDIT 6: Tagger Configuration Check

### 6a. Does the tagger script have a subreddit whitelist?

Read the tagger script (scripts/tag_keywords.py or wherever it is).
Answer: does it filter posts by subreddit before tagging, or does
it tag ALL posts in the database? If it tags all posts, this is the
root cause of the contamination and MUST be fixed.

### 6b. Does the tagger read from config/keywords.yaml?

Or does it have keywords hardcoded? If hardcoded, it could be using
an old keyword list.

### 6c. What keyword file is currently at config/keywords.yaml?

```bash
head -5 config/keywords.yaml
```

Confirm it's v8 (should say "Keywords v8" in the header).

---

## AUDIT 7: Export Pipeline Check

### 7a. Does the export script filter by subreddit?

Read the export script. Does it pull from post_keyword_tags
without subreddit filtering (relying on the tagger to have done it
correctly), or does it independently filter to T1-T3?

### 7b. What does the exported JSON contain?

```bash
python3 -c "
import json
data = json.load(open('web/data/keyword_trends.json'))
for k in sorted(data.keys()):
    if k.startswith('_'): continue
    vals = data[k]
    total = sum(v.get('count',0) for v in vals)
    print(f'{k}: {len(vals)} data points, {total} total hits')
"
```

---

## AUDIT 8: Posts Table — Subreddit Coverage

### 8a. Are all 22 T1-T3 subs represented in the posts table?

```sql
SELECT subreddit, COUNT(*) as posts,
  MIN(datetime(created_utc, 'unixepoch')) as earliest,
  MAX(datetime(created_utc, 'unixepoch')) as latest
FROM posts
WHERE subreddit IN (
  'replika','CharacterAI','MyBoyfriendIsAI','ChatGPTcomplaints',
  'AIRelationships','MySentientAI','BeyondThePromptAI',
  'MyGirlfriendIsAI','AICompanions','SoulmateAI','KindroidAI',
  'NomiAI','SpicyChatAI','ChaiApp','HeavenGF','Paradot',
  'AIGirlfriend','ChatGPTNSFW','Character_AI_Recovery',
  'ChatbotAddiction','AI_Addiction','CharacterAIrunaways'
)
GROUP BY subreddit
ORDER BY posts DESC;
```

Check:
- Are all 22 subs present? If any is missing, flag it.
- Does the date range for each sub span Jan 2023 to ~Mar 2026?
  Flag any sub whose earliest post is after Jun 2023 (partial
  backfill) or whose latest post is before Jan 2026 (stale data).

### 8b. Monthly post volume per sub — look for gaps:

```sql
SELECT subreddit,
  strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as month,
  COUNT(*) as posts
FROM posts
WHERE subreddit IN (/* 22 T1-T3 subs */)
GROUP BY subreddit, month
ORDER BY subreddit, month;
```

For each sub, flag any month with ZERO posts between its earliest
and latest post dates. A gap means the backfill missed that period
or the sub was temporarily private/restricted.

Don't print the entire table (it'll be huge). Instead, summarize:
for each sub, list any gap months. If a sub has no gaps, say CLEAN.

---

## AUDIT 9: Post Content Quality

### 9a. How many posts have empty or removed content?

```sql
SELECT
  CASE
    WHEN selftext IS NULL THEN 'NULL'
    WHEN selftext = '' THEN 'EMPTY'
    WHEN selftext = '[removed]' THEN '[removed]'
    WHEN selftext = '[deleted]' THEN '[deleted]'
    ELSE 'HAS CONTENT'
  END as content_status,
  COUNT(*) as posts
FROM posts
WHERE subreddit IN (/* 22 T1-T3 subs */)
GROUP BY content_status
ORDER BY posts DESC;
```

### 9b. Of the tagged posts, how many have empty/removed content?

```sql
SELECT
  CASE
    WHEN p.selftext IS NULL THEN 'NULL'
    WHEN p.selftext = '' THEN 'EMPTY'
    WHEN p.selftext = '[removed]' THEN '[removed]'
    WHEN p.selftext = '[deleted]' THEN '[deleted]'
    ELSE 'HAS CONTENT'
  END as content_status,
  COUNT(DISTINCT t.post_id) as tagged_posts
FROM post_keyword_tags t
JOIN posts p ON t.post_id = p.id
GROUP BY content_status
ORDER BY tagged_posts DESC;
```

If a large percentage of tagged posts have [removed]/[deleted]
bodies, the tagger is matching on titles only, which may be less
reliable. Report the percentage.

### 9c. Are there posts where selftext is suspiciously long or
contains obvious junk (HTML, bot signatures, etc.)?

```sql
SELECT id, subreddit, LENGTH(selftext) as len,
  SUBSTR(selftext, 1, 100) as preview
FROM posts
WHERE LENGTH(selftext) > 50000
ORDER BY len DESC
LIMIT 10;
```

Flag any posts over 50K characters — these may be bot-generated
content dumps or formatting artifacts.

---

## AUDIT 10: Timestamp Integrity

### 10a. Are there posts with obviously wrong timestamps?

```sql
SELECT id, subreddit,
  datetime(created_utc, 'unixepoch') as created,
  created_utc
FROM posts
WHERE created_utc < 1672531200  -- before Jan 1, 2023
   OR created_utc > 1743465600  -- after Apr 1, 2026
ORDER BY created_utc
LIMIT 20;
```

Any posts outside the Jan 2023-Mar 2026 window are suspicious.

### 10b. Are there months with suspiciously high or low TOTAL
post volume across all T1-T3 subs?

```sql
SELECT strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as month,
  COUNT(*) as total_posts
FROM posts
WHERE subreddit IN (/* 22 T1-T3 subs */)
GROUP BY month
ORDER BY month;
```

Look for:
- Months with < 500 total posts (possible data gap)
- Months where volume suddenly doubles or halves (possible scraping
  issue or new sub added mid-stream)
- Any month with 0 posts

---

## AUDIT 11: Crosspost / Duplicate Content

### 11a. Are there posts with identical titles across different subs?

```sql
SELECT title, GROUP_CONCAT(DISTINCT subreddit) as subs,
  COUNT(DISTINCT subreddit) as sub_count, COUNT(*) as total
FROM posts
WHERE subreddit IN (/* 22 T1-T3 subs */)
AND title != '' AND title != '[removed]' AND title != '[deleted]'
GROUP BY title
HAVING COUNT(DISTINCT subreddit) > 1
ORDER BY total DESC
LIMIT 20;
```

This catches crossposts. Report how many crosspost clusters exist
and how many total duplicate posts they represent. Crossposts are
currently counted separately per sub — this is fine as long as
it's documented, but we need to know the scale.

### 11b. Are there exact duplicate posts (same ID) in the posts table?

```sql
SELECT id, COUNT(*) as dupes FROM posts
GROUP BY id HAVING COUNT(*) > 1;
```

Should return zero.

---

## AUDIT 12: Backfill Completeness

### 12a. When was data last collected per subreddit?

```sql
SELECT subreddit,
  MAX(datetime(created_utc, 'unixepoch')) as latest_post,
  ROUND(JULIANDAY('now') - JULIANDAY(MAX(datetime(created_utc, 'unixepoch')))) as days_stale
FROM posts
WHERE subreddit IN (/* 22 T1-T3 subs */)
GROUP BY subreddit
ORDER BY days_stale DESC;
```

Flag any sub where the latest post is more than 14 days old —
it may not be getting collected by the daily script.

### 12b. Total posts per sub — are any suspiciously small?

Using the results from 8a, flag any T1-T3 sub with fewer than 100
total posts. For context, even small subs like MySentientAI or
Paradot should have a few hundred posts over 3 years. If a sub
has < 100 posts, the backfill may have failed or the sub may be
effectively dead.

---

## OUTPUT

Write results to `docs/DATA_AUDIT_RESULTS.md`

For each audit (1-12), report:
- **PASS** — no issues found (show the evidence)
- **FAIL** — issues found (show exactly what's wrong and how many
  records are affected)
- **ACTION NEEDED** — what specific fix is required

At the end, provide a summary:
- Total contaminated records found
- Root causes identified (tagger config, backfill gaps, etc.)
- Fixes to apply (in order of priority)
- Whether a full re-tag from scratch is needed
- Whether any backfills need to be re-run
- Whether any posts need to be deleted from the posts table
- Overall data confidence: HIGH / MEDIUM / LOW for each theme

If multiple issues are found, DO NOT start fixing them yet.
Report everything first so Walker can review before we make changes.

---

## IMPORTANT

Do NOT fix anything during this audit. Report only. Walker will
review the results and decide what to fix and in what order.
