# Comment Collection & Tagging System — Reference Spec

> **Purpose**: This document is the single source of truth for extending the myfriendisai.com keyword tracking pipeline to include Reddit comments. It is written for Claude Code (CC) as a persistent reference across multiple implementation sessions. Each CC prompt for this project should begin with: *"Read `docs/COMMENTS_SYSTEM_SPEC.md` first — it contains the full architecture and methodology for comment collection."*

> **Last updated**: 2026-03-18
> **Status**: Forward-looking collection LIVE — schema migration, comment collection, comment tagging, post-level propagation, dual-metric export, and daily pipeline integration all implemented and tested. Historical backfill via PullPush is TBD pending comment keyword precision validation (Section 11).

---

## Table of Contents

1. [Project Context](#1-project-context)
2. [Architecture Overview](#2-architecture-overview)
3. [Schema Changes](#3-schema-changes)
4. [Comment Collection Pipeline](#4-comment-collection-pipeline)
5. [Comment Tagging Pipeline](#5-comment-tagging-pipeline)
6. [Post-Level Tag Propagation](#6-post-level-tag-propagation)
7. [JSON Export Integration](#7-json-export-integration)
8. [Methodology Decisions & Rationale](#8-methodology-decisions--rationale)
9. [Rate Limits & Constraints](#9-rate-limits--constraints)
10. [Future: Historical Backfill via PullPush](#10-future-historical-backfill-via-pullpush)
11. [Testing & Validation Checklist](#11-testing--validation-checklist)
12. [Implementation Sequence](#12-implementation-sequence)

---

## 1. Project Context

**myfriendisai.com** is a research dashboard tracking AI companionship discourse across ~27 Reddit subreddits (r/CharacterAI, r/replika, r/BeyondThePromptAI, r/KindroidAI, etc.) from January 2023 to present.

The system uses **keyword-based theme detection** across six themes:

| Theme         | Mentions/1k posts | Keyword count |
|---------------|-------------------|---------------|
| Romance       | 4.8               | —             |
| Sex/ERP       | 5.2               | —             |
| Consciousness | 4.8               | 13            |
| Therapy       | 5.8               | —             |
| Addiction      | 6.7               | —             |
| Rupture       | 7.3               | —             |

**Current limitation**: Keyword tracking only scans **post titles and body text (selftext)**. It does NOT scan comments/replies. This project extends tracking to comments.

### Existing Technical Stack

- **Database**: SQLite (`tracker.db`)
- **Keyword definitions**: `keywords_v8.yaml`
- **Keyword tagger**: Python script that matches keywords against post text
- **Export**: JSON export pipeline feeds Next.js frontend on Vercel
- **Data ingestion**: Reddit public `.json` endpoints (no API credentials, no OAuth)
- **Daily run**: `~54 requests (27 subs × 2 endpoints), ~6 minutes`
- **Backfill**: `backfill_pullpush.py` for historical post data via PullPush API

### Subreddit Exclusions (apply to comments too)

- **JanitorAI_Official** — excluded (bot card noise)
- **SillyTavernAI** — excluded (bot card noise)
- **SpicyChatAI** — excluded from discovery corpora

### Key Methodology Constants

- **80% precision threshold** for keyword acceptance
- **"Researcher-accepted" category** for borderline keywords with documented rationale
- **Overlap policy**: unique posts counted per theme without deduplication
- **CharacterAI backfill gap**: Sep 2023–Nov 2025 (known data limitation)

---

## 2. Architecture Overview

### Design Principle: Hybrid Approach (Option C)

Store comments and their keyword hits in **their own tables** (preserving granularity), but **propagate tags up to the parent post** so the existing "mentions per 1k posts" metric, trend lines, and frontend all continue to work unchanged.

```
┌─────────────────────────────────────────────────────────┐
│                    DAILY PIPELINE                        │
│                                                         │
│  1. Collect posts        (existing — no changes)        │
│  2. Tag posts            (existing — no changes)        │
│  3. Collect comments     (NEW — this spec)              │
│  4. Tag comments         (NEW — this spec)              │
│  5. Propagate to posts   (NEW — this spec)              │
│  6. Export JSON           (existing — verify only)       │
└─────────────────────────────────────────────────────────┘
```

### Data Flow

```
Reddit .json endpoint (/r/{sub}/comments/{post_id}.json)
    │
    ▼
comments table (all comments stored)
    │
    ▼
comment_keyword_hits table (ALL non-bot/non-deleted comments tagged)
    │
    ▼
Propagation step: post gets tagged if any of its comments matched
    │
    ▼
Existing JSON export picks up expanded post-level tags
    │
    ▼
Frontend (no changes needed)
```

---

## 3. Schema Changes

### New Table: `comments`

```sql
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,              -- Reddit comment ID (e.g., "k5jx2a1")
    post_id TEXT NOT NULL,            -- Reddit post ID this comment belongs to
    subreddit TEXT NOT NULL,          -- Subreddit name (without r/ prefix)
    author TEXT,                      -- Comment author username
    body TEXT,                        -- Raw comment text
    score INTEGER,                    -- Upvotes minus downvotes at collection time
    depth INTEGER NOT NULL DEFAULT 0, -- 0 = top-level, 1 = direct reply, etc.
    parent_id TEXT,                   -- Parent comment ID (NULL for top-level)
    created_utc INTEGER,              -- Unix timestamp of comment creation
    permalink TEXT,                   -- Permalink to comment on Reddit
    collected_at TEXT NOT NULL        -- ISO timestamp of when we collected this
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Index for efficient lookups by post
CREATE INDEX IF NOT EXISTS idx_comments_post_id ON comments(post_id);

-- Index for efficient lookups by subreddit + time (for future backfill dedup)
CREATE INDEX IF NOT EXISTS idx_comments_subreddit_created
    ON comments(subreddit, created_utc);
```

### New Table: `comment_keyword_hits`

This table should mirror the structure of the existing post keyword hits table. Inspect the existing schema and replicate it with `comment_id` instead of `post_id`.

```sql
CREATE TABLE IF NOT EXISTS comment_keyword_hits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    comment_id TEXT NOT NULL,          -- FK to comments.id
    post_id TEXT NOT NULL,             -- Denormalized for fast propagation queries
    subreddit TEXT NOT NULL,           -- Denormalized for fast queries
    theme TEXT NOT NULL,               -- Theme name (e.g., "consciousness")
    keyword TEXT NOT NULL,             -- The keyword that matched
    created_utc INTEGER,               -- Comment's created_utc (denormalized for time queries)

    FOREIGN KEY (comment_id) REFERENCES comments(id),
    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- For propagation: "which posts have comment-sourced hits?"
CREATE INDEX IF NOT EXISTS idx_comment_hits_post_id
    ON comment_keyword_hits(post_id);

-- For validation sampling: "show me all hits for keyword X"
CREATE INDEX IF NOT EXISTS idx_comment_hits_keyword
    ON comment_keyword_hits(theme, keyword);

-- Prevent duplicate tagging
CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_hits_unique
    ON comment_keyword_hits(comment_id, theme, keyword);
```

### Modifications to Existing Tables

Add a tracking column to the posts table (or wherever post-level tags live) to distinguish comment-sourced tags from post-sourced tags. **Before implementing, inspect the existing schema to determine the exact table and column structure for post-level keyword hits.** The goal:

- When a post is tagged via its own title/body text → `source = 'post'`
- When a post is tagged via a comment's keyword hit → `source = 'comment'`
- When both → both rows exist (a post can have both sources)

**CC: Check if the existing post keyword hits table has a `source` column or equivalent. If not, add one with a default of `'post'` so all existing data is correctly labeled.**

### New Tracking Table: `comment_collection_log`

```sql
CREATE TABLE IF NOT EXISTS comment_collection_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    post_id TEXT NOT NULL,
    subreddit TEXT NOT NULL,
    comments_collected INTEGER NOT NULL DEFAULT 0,
    collected_at TEXT NOT NULL
        DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now')),

    FOREIGN KEY (post_id) REFERENCES posts(id)
);

-- Prevents re-collecting comments for the same post
CREATE UNIQUE INDEX IF NOT EXISTS idx_comment_log_post
    ON comment_collection_log(post_id);
```

This prevents duplicate work: before fetching comments for a post, check if `post_id` already exists in this table. Important for both daily runs and future backfill.

---

## 4. Comment Collection Pipeline

### Source: Reddit Public JSON

```
GET https://www.reddit.com/r/{subreddit}/comments/{post_id}.json
```

- Returns a two-element JSON array: `[post_data, comment_tree]`
- Comment tree is nested (replies contain replies)
- Requires flattening via recursive traversal
- Custom User-Agent header required
- No auth needed

### Which Posts Get Comment Collection

1. **Age filter**: Posts that are **5 days old** (120 hours). This ensures the large majority of comments have been posted, including on high-traffic threads that stay active longer. The daily run looks at posts collected 5 days ago.
2. **Comment count filter**: Posts with `num_comments >= 5`. Posts with fewer than 5 comments are unlikely to contain meaningful thematic discussion. The `num_comments` field is already stored from post collection.
3. **Not already collected**: Post does NOT have an entry in `comment_collection_log`.
4. **Subreddit not excluded**: Skip posts from excluded subreddits (JanitorAI_Official, SillyTavernAI).

### What Gets Stored (all comments, minimal filtering)

Store **every comment** from the fetched tree, with these exclusions only:

- **Skip AutoModerator**: `author == "AutoModerator"`
- **Skip deleted/removed**: `body` is `"[deleted]"` or `"[removed]"`
- **Skip known bot accounts**: maintain a list — start with `["AutoModerator", "RemindMeBot", "SaveVideo", "vredditdownloader", "RepostSleuthBot"]`. This list can grow over time.

**Do NOT filter on score, depth, or length during collection.** Store everything.

### Traversal Logic

Reddit's comment JSON is nested. The collection script must recursively traverse the tree:

```python
def flatten_comments(comment_data, post_id, subreddit, depth=0):
    """
    Recursively flatten Reddit's nested comment tree into a flat list.
    
    comment_data: a comment object from Reddit's JSON response
    Returns: list of dicts ready for DB insertion
    """
    results = []
    
    # Skip "more comments" stub objects (handled separately)
    if comment_data.get("kind") != "t1":
        return results
    
    data = comment_data.get("data", {})
    
    comment = {
        "id": data.get("id"),
        "post_id": post_id,
        "subreddit": subreddit,
        "author": data.get("author"),
        "body": data.get("body"),
        "score": data.get("score", 0),
        "depth": depth,
        "parent_id": _extract_parent_id(data.get("parent_id", "")),
        "created_utc": int(data.get("created_utc", 0)),
        "permalink": data.get("permalink", ""),
    }
    
    results.append(comment)
    
    # Recurse into replies
    replies = data.get("replies")
    if replies and isinstance(replies, dict):
        children = replies.get("data", {}).get("children", [])
        for child in children:
            results.extend(
                flatten_comments(child, post_id, subreddit, depth + 1)
            )
    
    return results


def _extract_parent_id(full_id):
    """
    Reddit parent_id is like 't1_k5jx2a1' (comment) or 't3_abc123' (post).
    Strip the prefix and return just the ID.
    Returns None if parent is the post itself (t3_ prefix).
    """
    if not full_id:
        return None
    if full_id.startswith("t3_"):
        return None  # Parent is the post, not a comment
    if full_id.startswith("t1_"):
        return full_id[3:]
    return full_id
```

### "More Comments" Expansion

Reddit's JSON truncates large comment trees with `"kind": "more"` stub objects containing a list of unexpanded comment IDs. These represent real comments that aren't included in the initial response.

**Policy: Expand "more comments" stubs for posts with 50+ comments.** These are the high-traffic posts where truncation is most severe and where the missing comments are most likely to contain thematic discussion.

For posts with fewer than 50 comments, the initial response typically contains the full tree and expansion is unnecessary.

#### Expansion Mechanism

When a `"kind": "more"` object is encountered during traversal:

1. Extract the list of comment IDs from `data.children`
2. Fetch expanded comments via: `GET https://www.reddit.com/api/morechildren.json?api_type=json&link_id=t3_{post_id}&children={comma_separated_ids}`
3. **Important**: This endpoint has a limit on the number of IDs per request. Batch into groups of 100 IDs per request.
4. Each expansion request counts against the 10 req/min rate limit — respect the 6-second sleep.
5. Parse the returned comments and add them to the flat list with correct `depth` and `parent_id`.

**CC: The `/api/morechildren.json` endpoint may require different handling than the standard comment tree endpoint. Test with a real high-comment post first. If this endpoint doesn't work without auth via public JSON, fall back to the alternative approach: fetch `https://www.reddit.com/r/{subreddit}/comments/{post_id}.json?limit=500` with a higher limit parameter to get more comments in the initial response. Test both approaches and use whichever works reliably without auth.**

#### Expansion Budget

To prevent runaway API usage on mega-threads (1000+ comments), cap expansion at **5 additional requests per post**. This means a post can generate at most 6 total requests (1 initial + 5 expansions). Log when the cap is hit so we can monitor whether it's losing significant data.

#### Impact on Daily Pipeline Time

- Posts with 50+ comments: estimated ~30–50 per day across 27 subs
- Average expansions per post: ~2–3 additional requests
- Additional requests: ~60–150/day
- Additional time at 6 sec/request: ~6–15 minutes
- **Revised total daily pipeline: ~37–46 minutes** (6 existing + 25 base comments + 6–15 expansion)

### Rate Limiting

- **10 requests/minute** (unauthenticated Reddit .json)
- Sleep **6 seconds** between requests (matches existing pipeline behavior)
- Estimated daily volume: ~310–400 requests (250 base + 60–150 expansion)
- Total daily pipeline time with comments: ~37–46 minutes
- On 429 errors: back off to 12 seconds, retry up to 3 times

### Error Handling

- **429 Too Many Requests**: Back off to 12-second sleep, retry up to 3 times
- **403 Forbidden**: Log and skip (NSFW or private subreddit)
- **404 Not Found**: Log and skip (post was deleted)
- **Timeout / Connection Error**: Retry up to 3 times with exponential backoff
- **Malformed JSON**: Log and skip (Reddit occasionally returns HTML error pages)
- **"More comments" expansion failure**: Log and continue with already-collected comments (partial data is better than no data)
- All errors should be logged with post_id and subreddit for debugging

---

## 5. Comment Tagging Pipeline

### No Pre-Filters — Tag Everything

**All collected comments are eligible for keyword matching.** There are no filters on depth, character length, or comment type at tagging time.

The rationale: filtering before measurement introduces assumptions about where signal lives. It's better to tag comprehensively, measure precision across the full corpus, and then add filters *if the data shows they're needed*. Since tagging is local computation (keyword matching against text already in SQLite), the cost of being comprehensive is negligible — seconds of processing time and some extra rows in `comment_keyword_hits`.

If precision validation later reveals that specific comment types (very short comments, deeply nested comments, URL-only comments) are degrading keyword precision, filters can be added at that point as a data-driven decision. The `comments` table stores `depth`, `body` length, and `score` so any future filtering can be applied by re-running the tagger with new parameters — no re-scraping needed.

### Keyword Matching Logic

Use the **exact same matching logic** as the existing post keyword tagger. Do not create a separate implementation — import/call the same function.

**CC: Inspect the existing keyword tagger to understand:**
1. How it loads `keywords_v8.yaml`
2. How it matches keywords against text (exact match? regex? word boundary? case-insensitive?)
3. How it handles multi-word keywords (e.g., "more than code", "subjective experience")
4. How it writes results to the post keyword hits table

Then replicate that flow for comments → `comment_keyword_hits` table.

### Tagging Scope

Tag comments against **all themes and all keywords** in `keywords_v8.yaml`. Not just Consciousness — even though Consciousness is the immediate motivation, there's no reason to limit scope. The tagger should process all themes uniformly.

---

## 6. Post-Level Tag Propagation

After comment tagging completes, propagate comment-level hits up to the parent post:

```sql
-- Pseudocode / approach:
-- For each (post_id, theme, keyword) in comment_keyword_hits,
-- ensure a corresponding entry exists in the post-level keyword hits table
-- with source = 'comment'.
--
-- Use INSERT OR IGNORE (or equivalent) to avoid duplicating
-- if the post was already tagged with that theme+keyword from its own text.
```

**Key rules:**
1. A comment-sourced tag does NOT replace or override a post-sourced tag. Both can coexist.
2. If a post already has `theme=consciousness, keyword=sentient` from its own text, and a comment also contains "sentient", the post-sourced tag stays. We do NOT add a duplicate comment-sourced tag for the same theme+keyword.
3. If a post does NOT have a given theme+keyword from its own text, but a comment does → add a new row with `source='comment'`.
4. For the purpose of existing metrics ("mentions per 1k posts"), a post tagged via comments counts the same as a post tagged via its own text. The `source` column is for analytical transparency, not for filtering the primary metric.

**CC: The exact implementation depends on how the existing post keyword hits table is structured. Inspect it first.**

---

## 7. JSON Export Integration

The existing JSON export pipeline that feeds the Next.js frontend should pick up comment-sourced post tags automatically, IF:

- Propagation (Section 6) writes to the same table the export reads from
- The export query doesn't filter on a `source` column that would exclude new rows

**CC: After implementing propagation, verify the export by:**
1. Inspecting the export script to see which tables/queries it uses
2. Confirming that comment-propagated tags appear in the exported JSON
3. Spot-checking: pick a post that SHOULD have been tagged via comments but wasn't tagged via post text — confirm it now shows up in the export

**No frontend changes should be needed for this phase.** The frontend reads the JSON and doesn't know or care whether a tag came from post text or comment text.

### Dual-Metric Tracking (Post-Only vs. Post+Comment)

**Critical requirement**: The export must generate **both** metric views internally from launch, even if the frontend only displays one:

1. **Post-only mentions per 1k posts** — counts only posts tagged via their own title/body text (`source = 'post'`). This is the existing metric and preserves continuity with all historical data.
2. **Post+comment mentions per 1k posts** — counts all posts tagged by any source (`source = 'post'` OR `source = 'comment'`). This is the expanded metric that includes comment-sourced tags.

**Why both**: Adding comments to the tagging pipeline will increase theme mention rates. Without tracking both metrics, it will be impossible to distinguish "discourse about this theme grew" from "we started measuring more text." The post-only metric provides the methodological control.

**CC: The export should produce both numbers per theme per time period.** The simplest approach: the existing metric query stays unchanged (it already only counts post-sourced tags, since that's all that existed before). Add a second query or a modified version that includes comment-sourced tags. Both numbers go into the exported JSON. The frontend can use whichever it wants — but both must be available.

For the first launch, the frontend should continue displaying the **post+comment** metric (the more comprehensive one) as the primary number, since that's the whole point of this expansion. But the post-only metric should be present in the JSON for analytical comparison.

---

## 8. Methodology Decisions & Rationale

This section documents the "why" behind key decisions, for future reference.

### Construct Shift: "Theme Language in Posts" → "Theme Language in Thread Discourse"

**This is the most important methodological note in this document.**

Prior to this expansion, the dashboard measured *theme language in posts* — whether the person who created a post used keywords associated with a given theme in their title or body text. This is a specific, well-defined construct: it tells you how often people *initiate* discussion about a theme.

With comment tagging, the construct shifts toward *theme language in thread discourse* — whether a theme appears anywhere in the conversation around a post, including replies from other users. This is a broader construct. A post tagged via comments might mean:

- The OP's post triggered consciousness discussion in the replies, even though the OP didn't use consciousness language themselves
- A single commenter brought up the theme tangentially in an otherwise unrelated thread
- The community organically steered a conversation toward a theme the OP didn't raise

All of these are legitimate forms of thematic discourse, but they mean different things than "the OP posted about consciousness." This is why dual-metric tracking (Section 7) is essential — the post-only metric preserves the original construct, while the post+comment metric captures the expanded one.

**Historical data coverage note:** All backfilled data (via PullPush, pre-2026-03-18) was tagged against post title and body text only — no comments were collected or tagged for historical posts. Comment tagging applies only to posts collected going forward from 2026-03-18. This means the post+comment metric and the post-only metric will be identical for all historical data; they only diverge from the comment collection start date onward. This should be disclosed on the About page and in any methodology documentation.

**Implications for the About page and methodology documentation:**
- The shift should be explicitly disclosed when comment tagging goes live
- The methodology section should explain that "mentions per 1k posts" now reflects thread-level discourse, not just post-level language
- Historical data (before comment tagging) should be clearly marked as post-only
- The About page should note the comment collection start date (2026-03-18) as a methodological boundary
- Walker: update the About page to reflect this when the feature launches (use "Hopes" as the author name per existing convention)

### Why store all comments and tag all comments?

Separating collection from analysis means we can re-run tagging with different parameters without re-scraping Reddit. Pre-filtering based on depth, length, or score would introduce assumptions about where thematic signal lives in comment threads. Since tagging is cheap local computation (keyword matching in SQLite), there's no meaningful cost to being comprehensive. The data itself should tell us if certain comment types are noisy — that's what precision validation is for.

If future precision analysis shows that specific comment types degrade keyword precision (e.g., comments under 10 characters produce false positives), filters can be added at that point as a data-driven decision. The `comments` table stores `depth`, `body`, and `score` so any filtering can be applied by re-running the tagger — no re-scraping needed.

### Why expand "more comments" for 50+ comment posts?

Reddit's initial JSON response truncates large comment trees. For high-traffic posts (50+ comments), the truncated portion can be substantial — potentially hundreds of comments behind "more" stubs. These are often the most active and thematically rich threads. Skipping expansion would systematically undersample exactly the posts where comment-level tagging adds the most value.

The 50-comment threshold balances comprehensiveness against API cost. Posts under 50 comments typically return the full tree without truncation. The 5-request-per-post expansion cap prevents runaway API usage on mega-threads.

### Why 5-day delay?

Reddit posts accumulate the large majority of their comments within 3–5 days. High-traffic posts on larger subreddits (r/CharacterAI during drama events, new model releases) can stay active longer than typical posts. A 5-day delay ensures we capture a more complete comment thread in a single pass, avoiding the need for repeat visits. The tradeoff is that dashboard data is slightly less current, which is acceptable for a research tool tracking long-term trends.

### Why not filter on comment score?

Score filtering (e.g., only comments with score > 1) would bias toward popular opinions and filter out minority viewpoints. For thematic discourse tracking, a downvoted comment about AI consciousness is still consciousness discourse. We store score for potential future analysis but don't use it as a filter.

### Why the bot exclusion list?

Bot comments (AutoModerator, RemindMeBot, etc.) are pure noise for thematic analysis — they're template text, not human discourse. Unlike depth/length/score filters (which are judgment calls about signal quality), bot exclusion is a clear categorical filter. The list is deliberately conservative (only well-known bots); it should grow over time as community-specific bots are discovered in the data.

### Keyword re-validation in comment context is a launch priority

Existing keywords in `keywords_v8.yaml` were validated against post text. Comment text is structurally different — more conversational, more sarcastic, more contextual, shorter on average. A keyword that hits 80% precision in posts may not hold that threshold in comments. For example, "sentient" used earnestly in a post title is a different signal than "lol so sentient" in a comment.

**This is not a "we'll get to it later" item.** Keyword precision in comment context should be validated within the first two weeks of comment collection, before backfill is considered. The precision validation checklist (Section 11) includes this, but to be explicit: if any keyword drops below 80% precision in comment context, it should be flagged and either excluded from comment tagging or given "researcher-accepted" status with documented rationale.

---

## 9. Rate Limits & Constraints

### Reddit Public JSON

| Parameter                | Value                          |
|--------------------------|--------------------------------|
| Rate limit               | 10 requests/minute             |
| Sleep between requests   | 6 seconds                      |
| Max results per request  | Full comment tree (one post)   |
| Auth required            | No (custom User-Agent only)    |
| Pagination ceiling       | N/A (one request = one post)   |
| NSFW blocking            | 403 for subreddit-level blocks |

### PullPush API (for future backfill)

| Parameter                | Value                              |
|--------------------------|------------------------------------|
| Comment endpoint         | `https://api.pullpush.io/reddit/search/comment/` |
| Soft rate limit          | 15 requests/minute                 |
| Hard rate limit          | 30 requests/minute                 |
| Long-term limit          | 1,000 requests/hour                |
| Max results per request  | 100 comments                       |
| Supports subreddit filter| Yes (`&subreddit=`)                |
| Supports time range      | Yes (`&after=` / `&before=` epoch) |
| Returns `link_id`        | Yes (parent post ID)               |
| Returns `parent_id`      | Yes (parent comment ID)            |
| Returns `body`           | Yes                                |

### Daily Pipeline Budget

| Step                          | Requests   | Time        |
|-------------------------------|------------|-------------|
| Post collection (existing)    | ~54        | ~6 min      |
| Comment collection (base)     | ~250       | ~25 min     |
| "More comments" expansion     | ~60–150    | ~6–15 min   |
| **Total**                     | **~364–454** | **~37–46 min** |

The ~250 base comment request estimate assumes ~250 posts/day across 27 subs have 5+ comments and are 5 days old. The expansion estimate assumes ~30–50 of those posts have 50+ comments and need ~2–3 expansion requests each. These will vary; high-activity periods could push higher. The pipeline should log actual request counts for monitoring.

---

## 10. Future: Historical Backfill via PullPush

**Not in scope for initial implementation.** Documenting here for future planning.

PullPush's comment search endpoint supports bulk retrieval by subreddit + time range, returning up to 100 comments per request. This enables historical backfill without the per-post bottleneck of Reddit's public JSON.

### Estimated Backfill Volume

- 27 subreddits × 2+ years × estimated 5–15 comments per post
- Rough estimate: 1–7 million comments total
- At 15 req/min, 100 comments/request: ~11–33 hours runtime
- Feasible as a one-time job

### Backfill Script Requirements (future)

- Mirror the approach in `backfill_pullpush.py` but target the comment endpoint
- Support `--subreddit` flag for per-subreddit runs (same pattern as the pending TODO for `backfill_pullpush.py`)
- Use `comment_collection_log` to avoid duplicating with already-collected forward-looking data
- PullPush returns `link_id` (post ID) for each comment — use this to link to existing posts in the DB
- Handle the case where PullPush returns comments for posts we don't have in our DB (skip them, or optionally ingest the post too)

### Backfill Decision Criteria

Proceed with backfill ONLY after:
1. Forward-looking collection has been running for ≥2 weeks
2. We've validated that comment-sourced tags meaningfully expand theme coverage
3. We've checked precision of existing keywords against comment text
4. The daily pipeline is stable and debugged

### Future Enhancement: Second-Pass Collection for High-Comment Posts

The current design collects comments once per post, 5 days after posting. For high-traffic posts (100+ comments), meaningful discussion may continue beyond the 5-day window — particularly during community drama events, model releases, or viral threads.

A future enhancement would add a **second-pass fetch** for posts that meet a high-comment threshold (e.g., 100+ comments at initial collection). This second pass would run 14 days after posting to capture late-arriving comments.

**Implementation notes for future:**
- The `comment_collection_log` table would need to support multiple collection events per post (currently it's a unique index on `post_id` — would need to change to allow a second row, or add a `pass` column)
- The second pass should use `INSERT OR IGNORE` on the `comments` table to avoid duplicating comments already collected in the first pass
- Only re-run keyword tagging on newly collected comments (not the full comment set for the post)
- This is a **v2 feature** — do not implement in the initial rollout

---

## 11. Testing & Validation Checklist

### After Schema Migration (Component 1)
- [ ] `comments` table exists with correct columns and indexes
- [ ] `comment_keyword_hits` table exists with correct columns and indexes
- [ ] `comment_collection_log` table exists
- [ ] Existing post keyword hits table has `source` column (defaulting to `'post'`)
- [ ] All existing rows in post keyword hits have `source = 'post'`
- [ ] No existing functionality is broken (run existing pipeline, verify output unchanged)

### After Comment Collection (Component 2)
- [ ] Script correctly identifies posts that are 5 days old with 5+ comments
- [ ] Script skips posts already in `comment_collection_log`
- [ ] Script skips excluded subreddits
- [ ] AutoModerator and bot comments are filtered out
- [ ] Deleted/removed comments are filtered out
- [ ] Comment `depth` values are correct (manually verify against Reddit UI for a few posts)
- [ ] `parent_id` correctly links to parent comment (NULL for top-level)
- [ ] "More comments" expansion triggers for posts with 50+ comments
- [ ] "More comments" expansion respects the 5-request-per-post cap
- [ ] `comment_collection_log` is updated after successful collection
- [ ] Rate limiting works (no 429 errors in logs)
- [ ] Error handling works (script doesn't crash on 404/403/expansion failure)
- [ ] Manual spot-check: pick 3 posts, compare DB comments to Reddit UI
- [ ] Manual spot-check: pick 1 high-comment post (50+), verify expansion fetched additional comments

### After Comment Tagging (Component 3)
- [ ] All non-bot, non-deleted comments are tagged (no depth/length/URL filtering)
- [ ] Keyword matching produces same results as post tagger for identical text
- [ ] `comment_keyword_hits` rows are created correctly
- [ ] No duplicate entries (unique constraint works)
- [ ] Manual spot-check: pick 5 tagged comments, verify the keyword actually appears in context

### After Propagation (Component 4)
- [ ] Posts tagged via comments appear in post-level keyword hits with `source = 'comment'`
- [ ] Posts already tagged via post text are NOT duplicated
- [ ] A post can have both `source = 'post'` and `source = 'comment'` rows (different keywords)
- [ ] JSON export includes comment-propagated tags
- [ ] Frontend displays expanded data correctly (spot-check a few posts)

### Precision Validation (Manual — LAUNCH PRIORITY, complete within 2 weeks)
- [ ] Sample 50 comment-tagged posts per theme
- [ ] Check: does the comment actually discuss the tagged theme?
- [ ] Calculate precision per keyword for comment-sourced hits
- [ ] Compare per-keyword precision in comments vs. existing post-text precision
- [ ] Break out precision by comment depth (do deeper comments have lower precision?)
- [ ] Break out precision by comment length (do short comments have lower precision?)
- [ ] Break out precision by comment score (do low-score comments have lower precision?)
- [ ] Use findings to determine whether any post-hoc filters are warranted
- [ ] Flag any keywords that drop below 80% precision in comment context
- [ ] Document results in validation log
- [ ] **Gate**: Do NOT proceed to backfill until this validation is complete

---

## 12. Implementation Sequence

### CC Prompt 1: Schema Migration ✅ (2026-03-18)

**Goal**: Add new tables and modify existing schema. No new scripts yet.

Implemented in `migrations/001_add_comment_tables.py`:
- Created `comments`, `comment_keyword_hits`, `comment_collection_log` tables
- Added `source` column to `post_keyword_tags` (default `'post'`, unique constraint updated to include source)
- All 15,550 existing rows migrated with `source='post'`
- Existing pipeline verified — no breakage

### CC Prompt 2: Comment Collection Script ✅ (2026-03-18)

**Goal**: New script that fetches comments for eligible posts via Reddit public JSON.

Implemented in `scripts/collect_comments.py`:
- Finds posts 5-6 days old with 5+ comments, not already collected, not in excluded subs
- Fetches and flattens nested comment trees via recursive traversal
- "More comments" expansion via `/api/morechildren.json` works without auth (fallback to `?limit=500` refetch)
- Filters bots (AutoModerator, RemindMeBot, etc.) and deleted/removed comments
- Transaction-per-post with rollback on failure
- Standalone (`--dry-run`, `--post-id`) and importable (`collect_comments()`)
- First run: 272 posts → 8,933 comments, 9 expansions, 281 requests, 28 min

### CC Prompt 3: Comment Tagging + Propagation ✅ (2026-03-18)

**Goal**: Extend keyword tagger to process comments and propagate hits to posts.

Implemented in `scripts/tag_comments.py` and `src/keyword_matching.py`:
- Matching logic extracted to shared `src/keyword_matching.py` (both taggers import it)
- Tags ALL comments from T1-T3 subs — no depth/length/score filtering
- Propagation inserts `source='comment'` rows in `post_keyword_tags` using post's date
- Dual-metric export: `keyword_trends.json` now includes `count_post_only` + `count_post_only_7d_avg` alongside existing fields
- First run: 182 comment keyword hits, 65 propagated post tags, 25 posts newly tagged via comments

### CC Prompt 4: Integration + Daily Pipeline Update ✅ (2026-03-18)

**Goal**: Wire everything into the daily run and verify end-to-end.

Implemented in updated `scripts/collect_daily.py`:
- 5-step pipeline: collect posts → tag posts → collect comments → tag comments → export JSON
- Error isolation: each step wrapped in try/except, failure in one doesn't kill subsequent steps
- Post keyword tagging (previously manual) now automated in the pipeline
- Summary log with per-step timing and request counts
- Full pipeline tested end-to-end; idempotency verified on second run

---

## Appendix A: Bot Author Exclusion List

Maintain this list in a config file (e.g., `config/bot_authors.txt` or within a Python config module). Start with:

```
AutoModerator
RemindMeBot
SaveVideo
vredditdownloader
RepostSleuthBot
```

Add to this list as new bots are discovered in the data.

## Appendix B: Key File Paths (to be confirmed by CC)

These paths are assumed based on project history. CC should verify and update:

| File                                   | Purpose                              |
|----------------------------------------|--------------------------------------|
| `data/tracker.db`                      | SQLite database                      |
| `config/keywords_v8.yaml`              | Keyword definitions per theme        |
| `src/keyword_matching.py`              | Shared regex matching logic          |
| `scripts/collect_comments.py`          | Comment collection script            |
| `scripts/tag_comments.py`              | Comment tagging + propagation        |
| `scripts/tag_keywords.py`              | Post keyword tagger                  |
| `scripts/collect_daily.py`             | Daily pipeline (all 5 steps)         |
| `scripts/backfill_pullpush.py`         | Historical post backfill script      |
| `migrations/001_add_comment_tables.py` | Schema migration for comment system  |
| `docs/COMMENTS_SYSTEM_SPEC.md`         | This document                        |

## Appendix C: PullPush Comment Endpoint Reference

For future backfill implementation:

```
GET https://api.pullpush.io/reddit/search/comment/

Parameters:
  subreddit   — filter by subreddit name (without r/)
  q           — keyword search (optional, not needed for bulk pull)
  after       — epoch timestamp, return comments after this time
  before      — epoch timestamp, return comments before this time
  size        — results per request (max 100)
  sort        — "asc" or "desc" by created_utc

Response fields (relevant):
  id          — comment ID
  link_id     — parent post full ID (e.g., "t3_abc123" → strip prefix for post_id)
  parent_id   — parent comment full ID (e.g., "t1_xyz789") or post ID if top-level
  body        — comment text
  author      — username
  score       — upvotes minus downvotes
  subreddit   — subreddit name
  created_utc — unix timestamp

Rate limits:
  Soft: 15 req/min
  Hard: 30 req/min
  Long-term: 1,000 req/hr
  Recommended sleep: 4 seconds between requests
```
