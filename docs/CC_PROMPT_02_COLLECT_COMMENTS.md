# CC Prompt 2: Comment Collection Script

Read `docs/COMMENTS_SYSTEM_SPEC.md` first — it contains the full architecture and methodology for comment collection. This prompt covers Section 4 (Comment Collection Pipeline).

Also review the migration at `migrations/001_add_comment_tables.py` to confirm you understand the schema for `comments`, `comment_collection_log`, and the existing `posts` table structure.

---

## Goal

Create a new script `scripts/collect_comments.py` that fetches comments from Reddit's public JSON endpoints for eligible posts and stores them in the `comments` table.

---

## What the Script Does

### 1. Find Eligible Posts

Query the `posts` table for posts that meet ALL of these criteria:

- **Age**: `created_utc` is between 5 and 6 days ago (120–144 hours). This window ensures we catch posts from 5 days ago without re-processing older ones on subsequent runs. If this windowing approach doesn't work cleanly with how `created_utc` is stored, use whatever logic ensures "posts that turned 5 days old since the last run" — the key is: each post should be picked up exactly once.
- **Comment count**: `num_comments >= 5`
- **Not already collected**: `post_id` does NOT exist in `comment_collection_log`
- **Not excluded subreddit**: subreddit is NOT in `["JanitorAI_Official", "SillyTavernAI"]`

Log how many eligible posts were found at the start of the run.

### 2. Fetch Comments for Each Post

For each eligible post, fetch comments from:

```
GET https://www.reddit.com/r/{subreddit}/comments/{post_id}.json
```

Use the same User-Agent header and request patterns as the existing collection scripts in this project. Look at `scripts/collect_daily.py` or wherever Reddit requests are made to match the existing approach (headers, session setup, error handling patterns).

**Rate limiting**: Sleep 6 seconds between requests, matching the existing pipeline's approach to Reddit's 10 req/min unauthenticated limit.

### 3. Flatten the Comment Tree

Reddit returns comments as a nested tree. Recursively traverse it to produce a flat list. See `docs/COMMENTS_SYSTEM_SPEC.md` Section 4 "Traversal Logic" for the flattening approach and `_extract_parent_id` helper.

For each comment, extract:
- `id` — Reddit comment ID
- `post_id` — the parent post ID
- `subreddit` — subreddit name
- `author` — comment author
- `body` — comment text
- `score` — upvotes minus downvotes
- `depth` — nesting level (0 = top-level)
- `parent_id` — parent comment ID (NULL if top-level, i.e., parent is the post)
- `created_utc` — unix timestamp
- `permalink` — link to the comment

### 4. Filter Out Noise (at collection time)

Before inserting into the database, skip comments where:

- `author` is in the bot exclusion list: `["AutoModerator", "RemindMeBot", "SaveVideo", "vredditdownloader", "RepostSleuthBot"]`
- `body` is `"[deleted]"` or `"[removed]"`

Store the bot list as a constant at the top of the script (or in a shared config) so it's easy to extend later.

Do NOT filter on score, depth, or comment length. Store everything that passes the above filters.

### 5. "More Comments" Expansion

For posts where `num_comments >= 50`, attempt to expand "more comments" stubs (Reddit's `"kind": "more"` objects in the comment tree).

**First, test whether this works without auth:**

Try fetching: `GET https://www.reddit.com/api/morechildren.json?api_type=json&link_id=t3_{post_id}&children={comma_separated_ids}`

If that endpoint doesn't work without auth (returns 403 or requires cookies), fall back to: refetch the comment tree with a higher limit parameter: `GET https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=500`

**Expansion rules:**
- Only attempt expansion for posts with `num_comments >= 50`
- Cap at 5 additional requests per post (so max 6 total requests per post: 1 initial + 5 expansions)
- If expansion fails for any reason, log a warning and continue with the comments already collected — partial data is fine
- Batch comment IDs into groups of 100 per expansion request
- Respect the same 6-second sleep between expansion requests

Log when expansion is triggered and when the 5-request cap is hit.

### 6. Insert into Database

Insert collected comments into the `comments` table using `INSERT OR IGNORE` (to handle any edge cases with duplicate comment IDs).

After successfully collecting comments for a post, insert a row into `comment_collection_log` with the `post_id`, `subreddit`, and `comments_collected` count.

Use a transaction per post — if insertion fails partway through a post's comments, roll back that post and log the error, then continue to the next post.

### 7. Error Handling

For each Reddit request:
- **429 Too Many Requests**: Back off to 12-second sleep, retry up to 3 times
- **403 Forbidden**: Log warning with post_id, skip this post
- **404 Not Found**: Log warning (post was probably deleted), skip this post
- **Timeout / Connection Error**: Retry up to 3 times with exponential backoff (6s, 12s, 24s)
- **Malformed JSON / KeyError**: Log warning, skip this post
- **Any other unexpected error**: Log the full exception, skip this post, continue to next

The script should NEVER crash on a single post's failure. Log the error and move on.

### 8. Logging

Use Python's `logging` module. At the end of the run, log a summary:

```
Comment collection complete:
  Eligible posts found: X
  Posts processed: X
  Posts skipped (errors): X
  Total comments collected: X
  "More comments" expansions triggered: X
  Expansion cap (5 req) hit: X times
  Total Reddit requests made: X
  Run duration: X minutes
```

### 9. Script Interface

The script should be:

- **Runnable standalone**: `python scripts/collect_comments.py`
- **Importable**: expose a `collect_comments()` function that can be called from the daily pipeline later
- **Dry-run mode**: accept a `--dry-run` flag that finds eligible posts and logs what it would do, but doesn't make any Reddit requests or database writes. This is essential for testing.
- **Single-post mode**: accept a `--post-id {id}` flag for testing against a specific post. This skips the eligibility query and just fetches comments for that one post. Useful for debugging.

---

## Testing

After building the script:

1. Run `--dry-run` first and show me how many eligible posts it finds and from which subreddits.
2. Run `--post-id` against a single known post that has a decent number of comments (20+). Show me how many comments were collected, a few sample rows from the `comments` table, and confirm the `comment_collection_log` entry was created.
3. Run `--post-id` against a high-comment post (50+) to test "more comments" expansion. Report whether expansion worked or if the fallback was needed.
4. Run it again for the same post to confirm idempotency — it should skip the post because it's already in `comment_collection_log`.

Show me the test results before doing a full run.
