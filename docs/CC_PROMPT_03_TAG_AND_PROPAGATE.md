# CC Prompt 3: Comment Keyword Tagging + Post-Level Propagation

Read `docs/COMMENTS_SYSTEM_SPEC.md` first — it contains the full architecture and methodology. This prompt covers Sections 5 (Comment Tagging Pipeline) and 6 (Post-Level Tag Propagation).

Also review:
- `scripts/tag_keywords.py` — the existing post keyword tagger. The comment tagger must use the same matching logic.
- `scripts/collect_comments.py` — the comment collection script from Prompt 2, so you understand what's in the `comments` table.
- `migrations/001_add_comment_tables.py` — the schema for `comment_keyword_hits` and the updated `post_keyword_tags`.

---

## Goal

Create a new script `scripts/tag_comments.py` that:
1. Runs keyword matching against all untagged comments
2. Writes hits to `comment_keyword_hits`
3. Propagates comment-sourced tags up to `post_keyword_tags` with `source='comment'`

---

## Part 1: Comment Keyword Tagging

### Matching Logic — Reuse, Don't Rewrite

The existing `scripts/tag_keywords.py` uses:
- `src.config.load_keywords()` to load keyword definitions from `keywords_v8.yaml`
- Regex matching: single words use `\b` word boundaries, multi-word phrases use plain substring match, all case-insensitive via `re.IGNORECASE`

**Import and call the same matching functions.** Do not reimplement the regex compilation or matching logic. If the existing code doesn't expose the matching as a cleanly importable function, refactor it minimally to extract the matching logic into a shared utility (e.g., `src/keyword_matching.py`) that both `tag_keywords.py` and `tag_comments.py` can import. If you do this refactoring, verify that `tag_keywords.py` still works identically afterward.

### What Gets Tagged

**All comments in the `comments` table that haven't been tagged yet.** No filters on depth, length, score, or comment type.

To determine "not yet tagged": query for comment IDs in the `comments` table that do NOT have any rows in `comment_keyword_hits`. The simplest approach is to track tagged comment IDs similarly to how `tag_keywords.py` tracks tagged post IDs — load the set of already-tagged comment IDs at the start, skip those.

For each untagged comment, match the `body` text against all keywords across all themes/categories.

### Writing Results

Write matches to `comment_keyword_hits` with:
- `comment_id` — the comment's ID
- `post_id` — the parent post ID (from the `comments` table)
- `subreddit` — from the `comments` table
- `category` — theme name (matching the naming in `post_keyword_tags`)
- `matched_term` — the keyword that matched
- `post_date` — derive from the comment's `created_utc`, formatted to match how `post_date` works in `post_keyword_tags` (inspect the existing data to confirm the format — likely `YYYY-MM-DD`)

Use `INSERT OR IGNORE` to handle the unique constraint on `(comment_id, category, matched_term)`.

---

## Part 2: Post-Level Tag Propagation

After tagging completes, propagate comment-sourced tags up to `post_keyword_tags`.

### Logic

For each distinct `(post_id, category, matched_term)` combination in `comment_keyword_hits`:
- Check if a row already exists in `post_keyword_tags` with that `post_id`, `category`, `matched_term`, and `source='comment'`
- If not, insert one with `source='comment'`
- The `post_date` should be the **post's date** (not the comment's date), since the post is the unit of analysis for trend lines. Look up the post's date from the `posts` table.

Use `INSERT OR IGNORE` with the unique constraint `(post_id, category, matched_term, source)` to handle this cleanly.

### Key Rules

1. Comment-sourced tags do NOT replace post-sourced tags. A post can have both `source='post'` and `source='comment'` rows for different keywords, or even for the same keyword (these are separate rows because the unique constraint includes `source`).
2. If a post already has `source='post'` for a given category+matched_term, the comment propagation adds a `source='comment'` row alongside it. Both exist.
3. Propagation is idempotent — running it multiple times produces the same result.

---

## Part 3: Dual-Metric Export Verification

After propagation, we need to verify that the JSON export handles both metric views correctly. The spec (Section 7) requires:

1. **Post+comment metric** (the new default): counts all distinct post_ids tagged by any source. This is what the frontend should display going forward.
2. **Post-only metric** (the control): counts only post_ids tagged with `source='post'`. This preserves the historical metric for comparison.

**Check how `src/db/operations.py` `export_keyword_trends_json()` queries `post_keyword_tags`.** It currently does `COUNT(DISTINCT post_id)` grouped by `(category, post_date)`. With the new `source` column:

- The existing query (with no WHERE clause on source) will automatically include comment-sourced tags — this becomes the post+comment metric. Verify this is the case.
- Add a second query (or modify the export function) to also produce the post-only numbers: same query but with `WHERE source = 'post'`. 

Both sets of numbers should appear in the exported JSON. The simplest approach: in `keyword_trends.json`, each data point currently has a count — add a second field alongside it for the post-only count. Inspect the current JSON structure and figure out the least disruptive way to add this.

**Important**: The frontend currently reads `keyword_trends.json`. Adding fields to the JSON is safe (the frontend ignores fields it doesn't know about). Removing or renaming existing fields would break the frontend. Only add — don't change existing structure.

---

## Script Interface

`scripts/tag_comments.py` should be:

- **Runnable standalone**: `python scripts/tag_comments.py`
- **Importable**: expose a `tag_comments()` function and a `propagate_to_posts()` function that can be called from the daily pipeline
- **Includes both steps**: running the script does tagging first, then propagation, then reports results

### Logging

At the end of the run, log:

```
Comment tagging complete:
  Comments scanned: X
  Comments with keyword hits: X
  Total keyword hits (comment_keyword_hits rows): X
  
  By category:
    consciousness: X hits across Y comments
    romance: X hits across Y comments
    ... (etc for all categories)

Propagation complete:
  New post-level tags added (source='comment'): X
  Posts newly tagged via comments (had no post-source tag for this category): X
  Posts with both post and comment tags for same category: X
```

The "posts newly tagged via comments" number is especially important — it tells us how many posts the comment expansion is capturing that were invisible before.

---

## Testing

After building the script:

1. **Run the tagger** against whatever comments exist in the database from the Prompt 2 testing. Show me the summary output — how many comments had hits, which categories, how many propagated tags were created.

2. **Spot-check 5 comment hits**: Pick 5 rows from `comment_keyword_hits` across different categories. For each, show me the comment body text and the matched keyword. I want to visually verify the matches make sense.

3. **Verify propagation**: Find at least one post that was tagged via comments but NOT via its own post text. Show me the post title/body, the comment that triggered the tag, and the resulting row in `post_keyword_tags` with `source='comment'`.

4. **Verify export**: Run `scripts/export_json.py` and confirm `keyword_trends.json` now includes both metric views. Show me a sample of the JSON structure so I can see how the dual metrics are represented.

5. **Idempotency**: Run the script a second time. It should report 0 new tags (everything already tagged).

Show me all test results before we move on.
