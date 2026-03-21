# Keyword Hit Rate Audit

**Goal:** Before pushing the site live, investigate whether the keyword hit rates look correct. We want to understand the actual magnitude of each theme and catch any pipeline issues (under-matching, over-matching, bad normalization).

Run each section below in order and report the results. Do NOT fix anything — just report findings. I'll decide what to change.

---

## 1. Overall hit rates by theme

Run this query against tracker.db:

```sql
SELECT 
    category,
    COUNT(*) as total_hits,
    COUNT(DISTINCT post_id) as unique_posts_with_hits
FROM keyword_hits
GROUP BY category
ORDER BY total_hits DESC;
```

Then get the total post count:

```sql
SELECT COUNT(*) as total_posts FROM posts;
```

For each category, calculate:
- hits per 1,000 posts (total_hits / total_posts * 1000)
- percentage of posts that match at least once (unique_posts_with_hits / total_posts * 100)

Report both numbers. These tell different stories — a theme could have high hits-per-1k because a few posts match many keywords, or because many posts each match once.

---

## 2. Hit rates over time

For each theme, show monthly hit rates to see if the magnitude changes dramatically across the timeline:

```sql
SELECT 
    category,
    strftime('%Y-%m', post_date) as month,
    COUNT(*) as hits,
    (SELECT COUNT(*) FROM posts WHERE strftime('%Y-%m', created_utc) = strftime('%Y-%m', kh.post_date)) as posts_that_month,
    ROUND(COUNT(*) * 1000.0 / (SELECT COUNT(*) FROM posts WHERE strftime('%Y-%m', created_utc) = strftime('%Y-%m', kh.post_date)), 1) as hits_per_1k
FROM keyword_hits kh
GROUP BY category, month
ORDER BY category, month;
```

For each theme, report:
- The minimum monthly hits_per_1k
- The maximum monthly hits_per_1k  
- The most recent 3 months' hits_per_1k
- Flag any theme where the max is more than 20x the min (could indicate a data issue)

---

## 3. Which keywords are actually firing?

For each category, show which specific keywords are generating the most matches:

```sql
SELECT 
    category,
    matched_term,
    COUNT(*) as match_count
FROM keyword_hits
GROUP BY category, matched_term
ORDER BY category, match_count DESC;
```

For each category, report the top 5 keywords by match count and what percentage of that category's total hits they represent. Flag any keyword that accounts for more than 50% of its category's hits — that means the category is essentially measuring one word, not a theme.

---

## 4. Spot-check: are matches real?

For each category, pull 5 random posts that matched and show the title + the first 200 characters of the body + which keyword matched:

```sql
SELECT 
    kh.category,
    kh.matched_term,
    p.title,
    SUBSTR(p.selftext, 1, 200) as body_preview
FROM keyword_hits kh
JOIN posts p ON kh.post_id = p.id
WHERE kh.category = '[CATEGORY_NAME]'
ORDER BY RANDOM()
LIMIT 5;
```

Run this for each of the 6 categories. I want to eyeball whether the matches look like genuine mentions of the theme or if they're false positives (e.g., "addicted to this app" matching the addiction theme when the poster is just expressing enthusiasm, not discussing actual addiction).

---

## 5. Post volume by month

Show total posts per month across the full timeline to understand the denominator:

```sql
SELECT 
    strftime('%Y-%m', created_utc) as month,
    COUNT(*) as post_count
FROM posts
GROUP BY month
ORDER BY month;
```

Flag any months with suspiciously low (< 100) or high volume, and note when coverage starts and ends.

---

## 6. Multi-theme overlap

How many posts hit multiple themes?

```sql
SELECT 
    themes_hit,
    COUNT(*) as post_count
FROM (
    SELECT post_id, COUNT(DISTINCT category) as themes_hit
    FROM keyword_hits
    GROUP BY post_id
)
GROUP BY themes_hit
ORDER BY themes_hit;
```

Also show the most common theme pairs:

```sql
SELECT 
    a.category as theme_1,
    b.category as theme_2,
    COUNT(DISTINCT a.post_id) as shared_posts
FROM keyword_hits a
JOIN keyword_hits b ON a.post_id = b.post_id AND a.category < b.category
GROUP BY a.category, b.category
ORDER BY shared_posts DESC
LIMIT 10;
```

---

## Report format

After running everything above, give me a summary that answers:

1. What are the actual hit rates per theme? Are they in the single digits per 1k, tens, or hundreds?
2. Are there any themes that look suspiciously low (might need more keywords) or suspiciously high (might have false-positive keywords)?
3. Are the spot-check matches actually relevant, or are we catching junk?
4. Is there a denominator problem? (e.g., months with very few posts inflating rates)
5. How much overlap is there between themes? (Matters for whether share-of-voice framing makes sense)

Do NOT make any changes to the database, keywords, or code. Just report.
