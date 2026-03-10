"""Core collection logic: fetch Reddit data for a subreddit and store it."""

import json
import logging
from datetime import date, datetime, timezone
from typing import Optional

from src.reddit_client import RedditClient, SubredditNotFound, SubredditForbidden, RedditError
from src.db import schema as db_schema
from src.db import operations as db_ops

logger = logging.getLogger(__name__)


def _parse_posts(raw_children: list[dict]) -> list[dict]:
    """Extract normalized post dicts from a Reddit listing response."""
    posts = []
    for child in raw_children:
        p = child.get("data", {})
        posts.append({
            "id": p.get("id", ""),
            "subreddit": p.get("subreddit", ""),
            "title": p.get("title", ""),
            "author": p.get("author", ""),
            "created_utc": p.get("created_utc"),
            "score": p.get("score"),
            "num_comments": p.get("num_comments"),
            "upvote_ratio": p.get("upvote_ratio"),
            "is_self": bool(p.get("is_self")),
            "selftext": p.get("selftext", ""),
            "url": p.get("url", ""),
            "collected_date": date.today().isoformat(),
            "data_source": "json_endpoint",
            "raw_json": json.dumps(p),
        })
    return posts


def _calc_metrics(about_data: dict, new_children: list[dict]) -> dict:
    """Derive engagement metrics from about.json and new.json responses."""
    posts = [c.get("data", {}) for c in new_children]

    # Posts created in the last 24 hours
    now_utc = datetime.now(timezone.utc).timestamp()
    cutoff = now_utc - 86400
    posts_today = sum(1 for p in posts if (p.get("created_utc") or 0) >= cutoff)

    # Averages across the full sample
    comment_counts = [p["num_comments"] for p in posts if p.get("num_comments") is not None]
    score_values = [p["score"] for p in posts if p.get("score") is not None]
    authors = {p["author"] for p in posts if p.get("author") and p["author"] != "[deleted]"}

    return {
        "subscribers": about_data.get("subscribers"),
        "active_users": about_data.get("active_user_count"),
        "visitors_7d": about_data.get("visitors_7d"),       # May be None (not in current API)
        "contributions_7d": about_data.get("contributions_7d"),  # May be None
        "posts_today": posts_today,
        "avg_comments_per_post": round(sum(comment_counts) / len(comment_counts), 2) if comment_counts else None,
        "avg_score_per_post": round(sum(score_values) / len(score_values), 2) if score_values else None,
        "unique_authors": len(authors) if authors else None,
    }


def collect_subreddit(
    subreddit: str,
    client: RedditClient,
    conn,
    today: Optional[date] = None,
) -> dict:
    """Collect and store one subreddit snapshot. Returns a result summary dict."""
    today = today or date.today()
    result = {"subreddit": subreddit, "status": "ok", "posts_inserted": 0, "error": None}

    logger.info("Collecting r/%s", subreddit)

    try:
        about_data = client.get_about(subreddit)
        raw_about = json.dumps(about_data)

        new_children = client.get_new(subreddit, limit=100)
        raw_listing = json.dumps(new_children)

        metrics = _calc_metrics(about_data, new_children)

        db_ops.insert_snapshot(
            subreddit=subreddit,
            snapshot_date=today,
            metrics=metrics,
            raw_about_json=raw_about,
            raw_listing_json=raw_listing,
            conn=conn,
        )

        posts = _parse_posts(new_children)
        result["posts_inserted"] = db_ops.insert_posts(posts, conn=conn)

        logger.info(
            "  r/%s: %s subscribers, %d posts/day, %d new posts stored",
            subreddit,
            f"{metrics['subscribers']:,}" if metrics["subscribers"] else "N/A",
            metrics["posts_today"] or 0,
            result["posts_inserted"],
        )

    except SubredditNotFound:
        result["status"] = "not_found"
        result["error"] = "Subreddit does not exist"
        logger.warning("  r/%s: not found", subreddit)

    except SubredditForbidden:
        result["status"] = "forbidden"
        result["error"] = "Access forbidden (private or NSFW-blocked)"
        logger.warning("  r/%s: forbidden (private or NSFW)", subreddit)

    except RedditError as e:
        result["status"] = "error"
        result["error"] = str(e)
        logger.error("  r/%s: Reddit error — %s", subreddit, e)

    return result
