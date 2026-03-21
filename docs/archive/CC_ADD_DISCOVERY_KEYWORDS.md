# Add Validated Discovery Keywords and Re-tag

**Goal:** Add 16 validated keywords to keywords.yaml and re-run the tagger to update keyword_hits. Then re-export the JSON files so the frontend reflects the new data.

---

## Step 1: Add keywords to keywords.yaml

Add the following keywords to their respective categories. Place them under a comment line `# Discovery batch — validated 2026-03-15` within each category section so we know when and why they were added.

### addiction
```
chatbot addiction    # 100.0%, 74 hits
almost relapsed      # 100.0%, 16 hits
finally deleted      # 81.4%, 86 hits
the craving          # 100.0%, 45 hits
so addictive         # 100.0%, 32 hits
```

### consciousness
```
sapience             # 92.3%, 13 hits
tulpa                # 100.0%, 32 hits
lemoine              # 81.8%, 12 hits
soulbonder           # 100.0%, 12 hits
```

### sexual_erp
```
erps                 # 100.0%, 35 hits
erping               # 100.0%, 23 hits
```

### rupture
```
lobotomies           # 100.0%, 21 hits
lobotomizing         # 100.0%, 31 hits
lobotomised          # 100.0%, 52 hits
```

### therapy
```
emotional support    # 100.0%, 505 hits
coping mechanism     # 100.0%, 307 hits
```

Do NOT remove any existing keywords. Only add.

---

## Step 2: Re-run the tagger

Run `scripts/tag_keywords.py` to re-tag all posts with the updated keyword list. The script should be idempotent — it will skip posts already tagged for existing keywords and only process the new ones.

After tagging completes, run this verification query and report the results:

```sql
SELECT 
    category,
    COUNT(*) as total_hits,
    COUNT(DISTINCT post_id) as unique_posts
FROM keyword_hits
GROUP BY category
ORDER BY total_hits DESC;
```

Compare to the pre-update numbers (from the earlier audit):
- sexual_erp: was 6,357
- romance: was 2,077
- consciousness: was 1,365
- addiction: was 1,312
- rupture: was 491
- therapy: was 452

Report the delta for each category.

---

## Step 3: Re-export JSON

Run the export script to regenerate the frontend JSON files with the updated keyword hit data. This should update `web/data/keyword_trends.json` (and any other JSON files the export produces).

---

## Step 4: Verify

After export, spot-check one of the new keywords to make sure it's flowing through correctly:

```sql
SELECT matched_term, COUNT(*) 
FROM keyword_hits 
WHERE matched_term IN ('emotional support', 'coping mechanism', 'chatbot addiction', 'lobotomised', 'tulpa')
GROUP BY matched_term;
```

Report the counts. If any are zero, something went wrong in the tagger.

---

## CC Prompt

```
Read docs/CC_ADD_DISCOVERY_KEYWORDS.md and follow the instructions. Add the 16 new keywords, re-run the tagger, re-export JSON, and report the before/after numbers.
```
