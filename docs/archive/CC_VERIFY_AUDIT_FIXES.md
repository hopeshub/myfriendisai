# Post-Audit Verification
#
# Run this AFTER applying the audit fixes. Confirms everything is clean.
# Report PASS or FAIL for each check. Do not fix anything — report only.

## CHECK 1: Tag contamination is gone

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
GROUP BY p.subreddit;
```

**PASS** = zero rows returned.

## CHECK 2: Tag counts are reasonable post-cleanup

```sql
SELECT category, COUNT(*) as tags, COUNT(DISTINCT post_id) as posts
FROM post_keyword_tags
GROUP BY category
ORDER BY tags DESC;
```

Compare to the audit's exported JSON counts. These should now be
close to the export numbers (since both filter to T1-T3):
- addiction: ~1,055
- consciousness: ~1,152
- romance: ~1,779
- rupture: ~464
- sexual_erp: ~6,085
- therapy: ~408

If any category is significantly HIGHER than the export count,
contamination may remain. If significantly LOWER, tags may have
been over-deleted.

## CHECK 3: Tagger whitelist is enforced

Read the tagger script. Confirm it filters to the 22 T1-T3 subs
BEFORE tagging. Show the relevant code block.

## CHECK 4: Export still filters independently

Read the export function. Confirm it independently filters to
T1-T3 (not relying on the tags table being clean). Show the
relevant code block.

## CHECK 5: Keywords file is v8

```bash
head -3 config/keywords_v8.yaml
```

Should say "Keywords v8" and "2026-03-14".

## CHECK 6: CharacterAI backfill status

```sql
SELECT
  strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as month,
  COUNT(*) as posts
FROM posts
WHERE subreddit = 'CharacterAI'
GROUP BY month
ORDER BY month;
```

Report whether the Sep 2023–Nov 2025 gap still exists or has been
filled. If still a gap, note it as PENDING.

## CHECK 7: Exported JSON matches clean tags

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

Confirm these numbers match the tag table counts from Check 2.
If the export hasn't been re-run since cleanup, note that.

## CHECK 8: Site is deployed with clean data

```bash
git log --oneline -3
```

Confirm the latest commit includes the tag cleanup and re-export.
If not, note what still needs to be pushed.

## OUTPUT

Write a simple table:

| Check | Status | Notes |
|-------|--------|-------|
| 1. Tag contamination | PASS/FAIL | |
| 2. Tag counts reasonable | PASS/FAIL | |
| 3. Tagger whitelist | PASS/FAIL | |
| 4. Export filter | PASS/FAIL | |
| 5. Keywords v8 | PASS/FAIL | |
| 6. CharacterAI backfill | PASS/PENDING | |
| 7. JSON matches tags | PASS/FAIL | |
| 8. Deployed | PASS/PENDING | |
