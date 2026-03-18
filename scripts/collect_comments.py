#!/usr/bin/env python3
"""Collect comments from Reddit for eligible posts and store in the comments table.

Fetches comments from Reddit's public .json endpoints for posts that are
5-6 days old, have 5+ comments, and haven't been collected yet. Expands
"more comments" stubs for posts with 50+ comments.

Usage:
    python scripts/collect_comments.py
    python scripts/collect_comments.py --dry-run
    python scripts/collect_comments.py --post-id abc123
"""

import argparse
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reddit_client import RedditClient, RedditError, SubredditForbidden, SubredditNotFound
from src.utils.rate_limiter import RateLimiter
from src.db.schema import get_connection, initialize as init_db

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

# Subreddits excluded from comment collection (same as keyword tagging exclusions)
EXCLUDED_SUBREDDITS = {"JanitorAI_Official", "SillyTavernAI"}

# Bot authors whose comments are noise for thematic analysis
BOT_AUTHORS = {
    "AutoModerator",
    "RemindMeBot",
    "SaveVideo",
    "vredditdownloader",
    "RepostSleuthBot",
}

# Posts with this many comments trigger "more comments" expansion
EXPANSION_THRESHOLD = 50

# Max additional requests per post for expanding "more comments" stubs
MAX_EXPANSION_REQUESTS = 5

# Max comment IDs per expansion request
EXPANSION_BATCH_SIZE = 100


def find_eligible_posts(conn, post_id=None):
    """Find posts eligible for comment collection.

    Returns list of dicts with id, subreddit, num_comments.
    """
    if post_id:
        row = conn.execute(
            "SELECT id, subreddit, num_comments FROM posts WHERE id = ?",
            (post_id,),
        ).fetchone()
        if not row:
            logger.error("Post %s not found in database", post_id)
            return []
        # Check if already collected
        already = conn.execute(
            "SELECT 1 FROM comment_collection_log WHERE post_id = ?",
            (post_id,),
        ).fetchone()
        if already:
            logger.info("Post %s already in comment_collection_log, skipping", post_id)
            return []
        return [dict(row)]

    # Posts created 5-6 days ago, 5+ comments, not already collected, not excluded
    excluded_ph = ",".join("?" for _ in EXCLUDED_SUBREDDITS)
    now = int(datetime.now(timezone.utc).timestamp())
    five_days_ago = now - (5 * 24 * 3600)
    six_days_ago = now - (6 * 24 * 3600)

    rows = conn.execute(
        f"""
        SELECT p.id, p.subreddit, p.num_comments
        FROM posts p
        WHERE p.created_utc BETWEEN ? AND ?
          AND p.num_comments >= 5
          AND p.subreddit NOT IN ({excluded_ph})
          AND p.id NOT IN (SELECT post_id FROM comment_collection_log)
        ORDER BY p.created_utc ASC
        """,
        (six_days_ago, five_days_ago, *EXCLUDED_SUBREDDITS),
    ).fetchall()

    return [dict(r) for r in rows]


def _extract_parent_id(full_id):
    """Strip Reddit's type prefix from parent_id.

    Returns None if parent is the post itself (t3_ prefix).
    """
    if not full_id:
        return None
    if full_id.startswith("t3_"):
        return None
    if full_id.startswith("t1_"):
        return full_id[3:]
    return full_id


def flatten_comments(comment_data, post_id, subreddit, depth=0):
    """Recursively flatten Reddit's nested comment tree into a flat list."""
    results = []

    if comment_data.get("kind") != "t1":
        # Return "more" stubs separately so caller can expand them
        if comment_data.get("kind") == "more":
            return results  # handled by caller via _collect_more_stubs
        return results

    data = comment_data.get("data", {})

    author = data.get("author")
    body = data.get("body", "")

    # Filter bots and deleted/removed
    if author in BOT_AUTHORS:
        pass  # skip but still recurse into replies
    elif body in ("[deleted]", "[removed]"):
        pass  # skip but still recurse into replies
    else:
        results.append({
            "id": data.get("id"),
            "post_id": post_id,
            "subreddit": subreddit,
            "author": author,
            "body": body,
            "score": data.get("score", 0),
            "depth": depth,
            "parent_id": _extract_parent_id(data.get("parent_id", "")),
            "created_utc": int(data.get("created_utc", 0)),
            "permalink": data.get("permalink", ""),
        })

    # Recurse into replies
    replies = data.get("replies")
    if replies and isinstance(replies, dict):
        children = replies.get("data", {}).get("children", [])
        for child in children:
            results.extend(flatten_comments(child, post_id, subreddit, depth + 1))

    return results


def collect_more_stubs(comment_data, post_id, subreddit, depth=0):
    """Collect 'more comments' stub objects from the comment tree.

    Returns list of (children_ids, depth) tuples.
    """
    stubs = []

    if comment_data.get("kind") == "more":
        data = comment_data.get("data", {})
        children_ids = data.get("children", [])
        if children_ids:
            stubs.append((children_ids, depth))
        return stubs

    if comment_data.get("kind") == "t1":
        data = comment_data.get("data", {})
        replies = data.get("replies")
        if replies and isinstance(replies, dict):
            children = replies.get("data", {}).get("children", [])
            for child in children:
                stubs.extend(collect_more_stubs(child, post_id, subreddit, depth + 1))

    return stubs


def expand_more_comments(client, subreddit, post_id, stubs, stats):
    """Expand 'more comments' stubs via Reddit API.

    Tries /api/morechildren.json first; falls back to refetching with limit=500.

    Returns list of flattened comment dicts.
    """
    expanded = []

    # Collect all child IDs from all stubs
    all_ids = []
    for children_ids, _depth in stubs:
        all_ids.extend(children_ids)

    if not all_ids:
        return expanded

    # Batch into groups of EXPANSION_BATCH_SIZE
    batches = [
        all_ids[i : i + EXPANSION_BATCH_SIZE]
        for i in range(0, len(all_ids), EXPANSION_BATCH_SIZE)
    ]

    # Cap at MAX_EXPANSION_REQUESTS
    if len(batches) > MAX_EXPANSION_REQUESTS:
        logger.info(
            "    Expansion cap hit: %d batches needed, capping at %d",
            len(batches), MAX_EXPANSION_REQUESTS,
        )
        batches = batches[:MAX_EXPANSION_REQUESTS]
        stats["expansion_caps"] += 1

    for batch_ids in batches:
        stats["requests"] += 1
        stats["expansions_triggered"] += 1

        try:
            # Try /api/morechildren.json
            data = client._get(
                "https://www.reddit.com/api/morechildren.json",
                params={
                    "api_type": "json",
                    "link_id": f"t3_{post_id}",
                    "children": ",".join(batch_ids),
                },
            )

            # Parse the response - morechildren returns a different format
            things = (
                data.get("json", {}).get("data", {}).get("things", [])
            )
            for thing in things:
                if thing.get("kind") == "t1":
                    thing_data = thing.get("data", {})
                    author = thing_data.get("author")
                    body = thing_data.get("body", "")
                    if author in BOT_AUTHORS:
                        continue
                    if body in ("[deleted]", "[removed]"):
                        continue
                    expanded.append({
                        "id": thing_data.get("id"),
                        "post_id": post_id,
                        "subreddit": subreddit,
                        "author": author,
                        "body": body,
                        "score": thing_data.get("score", 0),
                        "depth": thing_data.get("depth", 0),
                        "parent_id": _extract_parent_id(
                            thing_data.get("parent_id", "")
                        ),
                        "created_utc": int(thing_data.get("created_utc", 0)),
                        "permalink": thing_data.get("permalink", ""),
                    })

        except (RedditError, KeyError, TypeError) as e:
            logger.warning(
                "    Expansion failed for post %s batch: %s. "
                "Falling back to limit=500 refetch.",
                post_id, e,
            )
            # Fallback: refetch with higher limit
            try:
                stats["requests"] += 1
                fallback_data = client._get(
                    f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json",
                    params={"limit": 500},
                )
                if isinstance(fallback_data, list) and len(fallback_data) > 1:
                    children = (
                        fallback_data[1].get("data", {}).get("children", [])
                    )
                    for child in children:
                        expanded.extend(
                            flatten_comments(child, post_id, subreddit)
                        )
            except (RedditError, KeyError, TypeError) as e2:
                logger.warning(
                    "    Fallback refetch also failed for post %s: %s",
                    post_id, e2,
                )
            # Only try the fallback once, not per batch
            break

    return expanded


def collect_comments_for_post(client, conn, post_id, subreddit, num_comments, stats):
    """Fetch and store comments for a single post.

    Returns number of comments inserted.
    """
    stats["requests"] += 1

    # Fetch comment tree
    url = f"https://www.reddit.com/r/{subreddit}/comments/{post_id}.json"
    data = client._get(url)

    if not isinstance(data, list) or len(data) < 2:
        logger.warning("    Unexpected response format for post %s", post_id)
        return 0

    comment_listing = data[1].get("data", {}).get("children", [])

    # Flatten the tree
    comments = []
    more_stubs = []
    for child in comment_listing:
        comments.extend(flatten_comments(child, post_id, subreddit))
        more_stubs.extend(collect_more_stubs(child, post_id, subreddit))

    # Expand "more comments" for high-comment posts
    if num_comments >= EXPANSION_THRESHOLD and more_stubs:
        total_stub_ids = sum(len(ids) for ids, _ in more_stubs)
        logger.info(
            "    Expanding %d 'more' stubs (%d comment IDs) for post %s (%d comments)",
            len(more_stubs), total_stub_ids, post_id, num_comments,
        )
        expanded = expand_more_comments(client, subreddit, post_id, more_stubs, stats)
        # Deduplicate by comment ID (expansion may return comments we already have)
        existing_ids = {c["id"] for c in comments}
        for c in expanded:
            if c["id"] not in existing_ids:
                comments.append(c)
                existing_ids.add(c["id"])
        logger.info(
            "    Expansion added %d new comments (total: %d)",
            len(expanded), len(comments),
        )

    if not comments:
        return 0

    # Insert into database using a transaction per post
    try:
        conn.execute("BEGIN")
        conn.executemany(
            """
            INSERT OR IGNORE INTO comments
                (id, post_id, subreddit, author, body, score, depth,
                 parent_id, created_utc, permalink)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    c["id"], c["post_id"], c["subreddit"], c["author"],
                    c["body"], c["score"], c["depth"], c["parent_id"],
                    c["created_utc"], c["permalink"],
                )
                for c in comments
            ],
        )
        conn.execute(
            """
            INSERT OR IGNORE INTO comment_collection_log
                (post_id, subreddit, comments_collected)
            VALUES (?, ?, ?)
            """,
            (post_id, subreddit, len(comments)),
        )
        conn.commit()
        return len(comments)
    except Exception as e:
        conn.rollback()
        raise e


def collect_comments(post_id=None, dry_run=False):
    """Main entry point for comment collection.

    Args:
        post_id: If set, collect comments for this specific post only.
        dry_run: If True, find eligible posts but don't fetch or store anything.

    Returns:
        dict with summary stats.
    """
    conn = init_db()
    eligible = find_eligible_posts(conn, post_id=post_id)

    logger.info("Eligible posts found: %d", len(eligible))

    if dry_run:
        # Summarize by subreddit
        by_sub = {}
        for p in eligible:
            sub = p["subreddit"]
            by_sub[sub] = by_sub.get(sub, 0) + 1
        for sub in sorted(by_sub, key=by_sub.get, reverse=True):
            logger.info("  r/%-25s %d posts", sub, by_sub[sub])
        high_comment = sum(
            1 for p in eligible if (p["num_comments"] or 0) >= EXPANSION_THRESHOLD
        )
        logger.info(
            "  Posts with %d+ comments (expansion candidates): %d",
            EXPANSION_THRESHOLD, high_comment,
        )
        conn.close()
        return {"eligible": len(eligible), "dry_run": True}

    client = RedditClient(rate_limiter=RateLimiter(min_interval=6.0))

    stats = {
        "eligible": len(eligible),
        "processed": 0,
        "skipped_errors": 0,
        "comments_collected": 0,
        "expansions_triggered": 0,
        "expansion_caps": 0,
        "requests": 0,
    }
    start_time = time.time()

    for i, post in enumerate(eligible, 1):
        pid = post["id"]
        sub = post["subreddit"]
        nc = post["num_comments"] or 0

        logger.info(
            "  [%d/%d] r/%s post %s (%d comments)",
            i, len(eligible), sub, pid, nc,
        )

        try:
            count = collect_comments_for_post(
                client, conn, pid, sub, nc, stats,
            )
            stats["processed"] += 1
            stats["comments_collected"] += count
            logger.info("    Collected %d comments", count)

        except SubredditNotFound:
            stats["skipped_errors"] += 1
            logger.warning("    Skipped: subreddit not found")

        except SubredditForbidden:
            stats["skipped_errors"] += 1
            logger.warning("    Skipped: access forbidden (private/NSFW)")

        except RedditError as e:
            stats["skipped_errors"] += 1
            logger.warning("    Skipped: Reddit error — %s", e)

        except (KeyError, TypeError, ValueError) as e:
            stats["skipped_errors"] += 1
            logger.warning("    Skipped: malformed data — %s", e)

        except Exception as e:
            stats["skipped_errors"] += 1
            logger.error("    Skipped: unexpected error — %s: %s", type(e).__name__, e)

    conn.close()

    duration = time.time() - start_time
    stats["duration_minutes"] = round(duration / 60, 1)

    logger.info("=" * 60)
    logger.info("Comment collection complete:")
    logger.info("  Eligible posts found:              %d", stats["eligible"])
    logger.info("  Posts processed:                    %d", stats["processed"])
    logger.info("  Posts skipped (errors):             %d", stats["skipped_errors"])
    logger.info("  Total comments collected:           %d", stats["comments_collected"])
    logger.info("  'More comments' expansions triggered: %d", stats["expansions_triggered"])
    logger.info("  Expansion cap (5 req) hit:          %d times", stats["expansion_caps"])
    logger.info("  Total Reddit requests made:         %d", stats["requests"])
    logger.info("  Run duration:                       %.1f minutes", stats["duration_minutes"])
    logger.info("=" * 60)

    return stats


def main():
    parser = argparse.ArgumentParser(description="Collect comments for eligible posts")
    parser.add_argument("--dry-run", action="store_true", help="Show eligible posts without fetching")
    parser.add_argument("--post-id", help="Collect comments for a specific post ID")
    args = parser.parse_args()

    collect_comments(post_id=args.post_id, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
