# CC Prompt 1: Schema Inspection + Migration for Comment Collection

Read `docs/COMMENTS_SYSTEM_SPEC.md` first — it contains the full architecture and methodology for comment collection. This prompt covers the schema migration (Section 3 of that spec).

## This prompt has two steps. Do Step A first, then STOP and show me the results before proceeding to Step B.

---

## Step A: Inspect and Report

Before making any changes, I need you to examine the existing codebase and report back on the following. Do NOT modify anything yet.

### 1. Existing Schema

Run `.schema` on `tracker.db` and show me:
- The full schema of the table that stores post-level keyword/theme hits (whatever it's called — might be `keyword_hits`, `post_keyword_hits`, `theme_hits`, or something else)
- The full schema of the `posts` table
- Any other tables that seem related to the tagging or export pipeline

### 2. Keyword Tagger

Find the Python script that matches keywords against post text and tell me:
- What file is it in?
- How does it load `keywords_v8.yaml`?
- How does it match keywords against text? (exact match, regex, word boundary, case-insensitive?)
- How does it write results to the database? (what table, what columns?)

### 3. Export Pipeline

Find the script that exports data to JSON for the frontend and tell me:
- What file is it in?
- What tables/queries does it read from?
- How does it aggregate theme mention counts?

### 4. Daily Pipeline

Find whatever script orchestrates the daily run and tell me:
- What file is it in?
- What's the execution order?
- How would a new step (comment collection + tagging) be wired in?

**After completing Step A, show me all findings and STOP. I'll review and confirm before you proceed to Step B.**

---

## Step B: Schema Migration (execute only after I confirm Step A findings)

### New Tables

Create these three tables in `tracker.db` exactly as specified in `docs/COMMENTS_SYSTEM_SPEC.md` Section 3:

1. `comments` — stores comment text and metadata
2. `comment_keyword_hits` — stores keyword matches found in comment text
3. `comment_collection_log` — tracks which posts have had comments collected

Include all indexes specified in the spec.

### Modify Existing Post Keyword Hits Table

Based on what you found in Step A, add a `source` column to the existing post-level keyword hits table:
- Type: `TEXT NOT NULL DEFAULT 'post'`
- All existing rows should get `source = 'post'`
- New comment-propagated rows will later get `source = 'comment'`

**Important**: If the existing table structure doesn't cleanly support adding a `source` column (e.g., if it uses a different pattern for storing hits), flag this and suggest an alternative approach rather than forcing it.

### Verify Nothing Broke

After making schema changes:
1. Run the existing daily pipeline (or whatever the normal post collection + tagging flow is)
2. Confirm it completes without errors
3. Confirm the JSON export still produces the same output as before
4. Show me the output of `.schema` for all modified/new tables

### Write a Migration Script

Put the schema changes in a standalone script (e.g., `migrations/001_add_comment_tables.py`) so the migration is repeatable and documented. The script should be idempotent — safe to run multiple times without breaking anything (`CREATE TABLE IF NOT EXISTS`, etc.).
