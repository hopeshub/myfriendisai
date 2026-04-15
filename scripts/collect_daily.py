#!/usr/bin/env python3
"""Daily collection entry point.

Loads communities from config, collects Reddit data for each, tags posts,
collects comments, tags comments, propagates comment tags, and exports
frontend-ready JSON files.

Usage:
    python scripts/collect_daily.py
"""

import fcntl
import logging
import os
import shutil
import sys
import time
from pathlib import Path

# Allow running from the project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_communities, load_keywords, load_keyword_communities
from src.reddit_client import RedditClient
from src.utils.rate_limiter import RateLimiter
from src.db.schema import initialize as init_db
from src.db.operations import export_snapshots_json, export_subreddits_json, export_site_meta_json, sync_subreddit_config, update_contributor_metrics_for_date
from src.collector import collect_subreddit
from src.keyword_scanner import scan_subreddit_keywords, store_keyword_counts, export_keywords_json
from src.db.operations import export_keyword_trends_json
from src.keyword_matching import build_patterns, match_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _step_collect_posts(communities, client, conn):
    """Step 1: Collect subreddit data + posts."""
    tier_map = {c["subreddit"]: c.get("tier") for c in communities}

    results = []
    for community in communities:
        subreddit = community["subreddit"]
        result = collect_subreddit(subreddit=subreddit, client=client, conn=conn)
        results.append(result)

    # Pagination for small subs — only if we haven't paginated them before.
    # Without this guard, adding a new small sub dumps its entire history
    # (500 posts spanning months) in one batch, distorting daily counts.
    already_paginated = set(
        r[0] for r in conn.execute(
            "SELECT DISTINCT subreddit FROM posts WHERE data_source = 'json_endpoint' GROUP BY subreddit HAVING COUNT(*) > 100"
        ).fetchall()
    )
    pagination_failures = []
    for community in communities:
        subreddit = community["subreddit"]
        if subreddit in already_paginated:
            continue
        row = conn.execute(
            "SELECT subscribers FROM subreddit_snapshots WHERE subreddit = ? ORDER BY snapshot_date DESC LIMIT 1",
            (subreddit,),
        ).fetchone()
        if row and row["subscribers"] and row["subscribers"] < 50000:
            logger.info("  r/%s: small sub (%d subs), first-time pagination up to 500 posts...", subreddit, row["subscribers"])
            try:
                from src.collector import _parse_posts, _normalize_subreddit
                from src.db.operations import insert_posts
                extra_children = client.get_new_paginated(subreddit, target=500)
                extra_posts = _normalize_subreddit(_parse_posts(extra_children), subreddit)
                new_count = insert_posts(extra_posts, conn=conn)
                if new_count > 0:
                    logger.info("  r/%s: %d additional posts from pagination", subreddit, new_count)
            except Exception as e:
                # Record failure so the sub isn't treated as "paginated" by the
                # next run's already_paginated check. Without this, a transient
                # Reddit error on first-time pagination silently skips the sub
                # forever (since a partial insert would later trip the >100 check).
                logger.warning("  r/%s: pagination failed: %s — will retry next run", subreddit, e)
                pagination_failures.append({"subreddit": subreddit, "error": str(e)})

    # Keyword scanning (legacy keyword_scanner pipeline)
    from datetime import date as date_cls
    today = date_cls.today()
    logger.info("Scanning posts for keyword matches...")
    ok_subs = [r["subreddit"] for r in results if r["status"] == "ok"]
    for subreddit in ok_subs:
        tier = tier_map.get(subreddit)
        kw_results = scan_subreddit_keywords(
            subreddit, today, conn=conn, tier=tier, client=client,
        )
        store_keyword_counts(kw_results, conn=conn)
        hits = sum(r["count"] for r in kw_results)
        if hits > 0:
            cats = {}
            for r in kw_results:
                if r["count"] > 0:
                    cats[r["category"]] = cats.get(r["category"], 0) + r["count"]
            cat_str = ", ".join(f"{k}={v}" for k, v in cats.items())
            logger.info("  r/%s: %d keyword hits (%s)", subreddit, hits, cat_str)
    logger.info("Keyword scanning complete")

    ok = [r for r in results if r["status"] == "ok"]
    errors = [r for r in results if r["status"] != "ok"]
    total_posts = sum(r["posts_inserted"] for r in ok)

    return {
        "ok": len(ok),
        "errors": len(errors),
        "total": len(communities),
        "posts_collected": total_posts,
        "error_details": errors,
    }


def _step_tag_posts(conn):
    """Step 2: Tag posts with keyword categories (tag_keywords.py logic)."""
    keyword_categories = load_keywords()
    patterns = build_patterns(keyword_categories)
    logger.info("Loaded %d patterns across %d categories", len(patterns), len(keyword_categories))

    # Load already-tagged post IDs
    tagged_ids = set(
        r[0] for r in conn.execute("SELECT DISTINCT post_id FROM post_keyword_tags").fetchall()
    )
    logger.info("  %d posts already tagged, will skip", len(tagged_ids))

    keyword_subs = [c["subreddit"] for c in load_keyword_communities()]
    placeholders = ",".join("?" for _ in keyword_subs)
    where_clause = f"FROM posts WHERE subreddit IN ({placeholders})"
    query = f"SELECT id, subreddit, title, selftext, date(created_utc, 'unixepoch') AS post_date {where_clause} ORDER BY post_date ASC"

    total_posts = conn.execute(
        f"SELECT COUNT(*) {where_clause}",
        keyword_subs,
    ).fetchone()[0]
    logger.info("  %d posts in scope for keyword tagging", total_posts)

    cursor = conn.execute(query, keyword_subs)

    tagged = 0
    scanned = 0
    batch = []
    BATCH_SIZE = 500

    for post_id, subreddit, title, selftext, post_date in cursor:
        if post_id in tagged_ids:
            continue
        scanned += 1
        text = " ".join(filter(None, [title, selftext]))
        matches = match_text(text, patterns)
        for category, matched_term in matches:
            batch.append((post_id, subreddit, category, matched_term, post_date))
            tagged += 1

        if len(batch) >= BATCH_SIZE:
            conn.executemany(
                "INSERT OR IGNORE INTO post_keyword_tags "
                "(post_id, subreddit, category, matched_term, post_date) "
                "VALUES (?, ?, ?, ?, ?)",
                batch,
            )
            conn.commit()
            batch.clear()

    if batch:
        conn.executemany(
            "INSERT OR IGNORE INTO post_keyword_tags "
            "(post_id, subreddit, category, matched_term, post_date) "
            "VALUES (?, ?, ?, ?, ?)",
            batch,
        )
        conn.commit()

    return {"posts_scanned": scanned, "tags_added": tagged}


def _step_collect_comments(conn):
    """Step 3: Collect comments for eligible posts."""
    from scripts.collect_comments import collect_comments
    return collect_comments()


def _step_tag_comments(conn):
    """Step 4: Tag comments + propagate to posts."""
    from scripts.tag_comments import tag_comments, propagate_to_posts
    tag_stats = tag_comments(conn=conn)
    prop_stats = propagate_to_posts(conn=conn)
    return {**tag_stats, **prop_stats}


def _step_compute_contributors(conn):
    """Step 4b: Compute rolling-7d contributor metrics for today's snapshots.

    Runs after post + comment collection, so the 7d window ending today
    reflects the freshest data available (today's posts plus newly-collected
    comments for posts from 5-6 days ago, which fall inside the window).
    """
    from datetime import date as date_cls
    rows_updated = update_contributor_metrics_for_date(date_cls.today(), conn=conn)
    return {"rows_updated": rows_updated}


def _atomic_copy(src: Path, dst: Path):
    """Copy src to dst atomically: write to .tmp then rename."""
    tmp = dst.with_suffix(dst.suffix + ".tmp")
    shutil.copy2(src, tmp)
    os.replace(str(tmp), str(dst))


def _step_export(conn):
    """Step 5+6: Export JSON and copy to web/data/.

    Exports to .tmp files first, then renames atomically so production
    JSON files are never left in a corrupt/partial state.
    """
    # Export to data/ via tmp files
    data_dir = Path(__file__).parent.parent / "data"

    snap_path = export_snapshots_json(output_path=data_dir / "snapshots.json.tmp", conn=conn)
    os.replace(str(snap_path), str(data_dir / "snapshots.json"))
    snap_path = data_dir / "snapshots.json"

    sub_path = export_subreddits_json(output_path=data_dir / "subreddits.json.tmp", conn=conn)
    os.replace(str(sub_path), str(data_dir / "subreddits.json"))
    sub_path = data_dir / "subreddits.json"

    kw_path = export_keywords_json(output_path=data_dir / "keywords.json.tmp", conn=conn)
    os.replace(str(kw_path), str(data_dir / "keywords.json"))
    kw_path = data_dir / "keywords.json"

    kw_trends_path = export_keyword_trends_json(output_path=data_dir / "keyword_trends.json.tmp", conn=conn)
    os.replace(str(kw_trends_path), str(data_dir / "keyword_trends.json"))
    kw_trends_path = data_dir / "keyword_trends.json"

    meta_path = export_site_meta_json(output_path=data_dir / "site_meta.json.tmp", conn=conn)
    os.replace(str(meta_path), str(data_dir / "site_meta.json"))
    meta_path = data_dir / "site_meta.json"

    logger.info("Exported: %s, %s, %s, %s, %s", snap_path, sub_path, kw_path, kw_trends_path, meta_path)

    # Copy to web/data/ atomically.
    # Note: data/keywords.json is intentionally NOT copied — the frontend
    # doesn't import it, and the 2.4 MB payload was dead weight on every request.
    web_data_dir = Path(__file__).parent.parent / "web" / "data"
    web_data_dir.mkdir(parents=True, exist_ok=True)
    _atomic_copy(snap_path, web_data_dir / "snapshots.json")
    _atomic_copy(sub_path, web_data_dir / "subreddits.json")
    _atomic_copy(kw_trends_path, web_data_dir / "keyword_trends.json")
    _atomic_copy(meta_path, web_data_dir / "site_meta.json")
    logger.info("Copied JSON to web/data/ for frontend")

    # Export keyword details (transparency panel data)
    import subprocess
    detail_result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "export_keyword_details.py")],
        capture_output=True, text=True,
    )
    if detail_result.returncode == 0:
        # Copy to data/ as well
        detail_src = web_data_dir / "keyword_details.json"
        detail_dst = data_dir / "keyword_details.json"
        if detail_src.exists():
            _atomic_copy(detail_src, detail_dst)
        logger.info("Exported keyword_details.json")
    else:
        # Raise so the step counts as failed — otherwise the transparency panel
        # silently goes stale without anything surfacing the error.
        logger.error("keyword_details export failed (rc=%d): %s", detail_result.returncode, detail_result.stderr)
        raise RuntimeError(f"export_keyword_details.py failed with rc={detail_result.returncode}")


def main():
    # Acquire lockfile to prevent overlapping runs
    lock_path = Path(__file__).parent.parent / "data" / ".collect_daily.lock"
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    lock_fd = open(lock_path, "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        logger.error("Another instance of collect_daily.py is already running (lockfile: %s)", lock_path)
        lock_fd.close()
        return 1

    try:
        return _main_inner()
    finally:
        fcntl.flock(lock_fd, fcntl.LOCK_UN)
        lock_fd.close()


def _main_inner():
    pipeline_start = time.time()
    communities = load_communities()
    logger.info("Loaded %d active communities from config", len(communities))

    conn = init_db()
    sync_subreddit_config(communities, conn=conn)
    client = RedditClient(rate_limiter=RateLimiter(min_interval=6.0))

    step_times = {}
    failed_steps = []

    # ── Step 1: Collect posts ───────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 1: Collecting subreddit data + posts")
    t0 = time.time()
    try:
        post_stats = _step_collect_posts(communities, client, conn)
    except Exception as e:
        logger.error("Step 1 (post collection) failed: %s", e)
        post_stats = {"ok": 0, "errors": 0, "total": len(communities), "posts_collected": 0, "error_details": []}
        failed_steps.append("post_collection")
    step_times["post_collection"] = time.time() - t0

    # ── Step 2: Tag posts ───────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 2: Tagging posts with keywords")
    t0 = time.time()
    try:
        tag_stats = _step_tag_posts(conn)
    except Exception as e:
        logger.error("Step 2 (post tagging) failed: %s", e)
        tag_stats = {"posts_scanned": 0, "tags_added": 0}
        failed_steps.append("post_tagging")
    step_times["post_tagging"] = time.time() - t0

    # ── Step 3: Collect comments ────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 3: Collecting comments for eligible posts")
    t0 = time.time()
    try:
        comment_stats = _step_collect_comments(conn)
    except Exception as e:
        logger.error("Step 3 (comment collection) failed: %s", e)
        comment_stats = {"comments_collected": 0, "processed": 0, "requests": 0}
        failed_steps.append("comment_collection")
    step_times["comment_collection"] = time.time() - t0

    # ── Step 4: Tag comments + propagate ────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 4: Tagging comments + propagating to posts")
    t0 = time.time()
    try:
        comment_tag_stats = _step_tag_comments(conn)
    except Exception as e:
        logger.error("Step 4 (comment tagging) failed: %s", e)
        comment_tag_stats = {"total_hits": 0, "posts_newly_tagged": 0}
        failed_steps.append("comment_tagging")
    step_times["comment_tagging"] = time.time() - t0

    # ── Step 4b: Compute contributor metrics ────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 4b: Computing rolling-7d contributor metrics")
    t0 = time.time()
    try:
        contrib_stats = _step_compute_contributors(conn)
    except Exception as e:
        logger.error("Step 4b (contributor metrics) failed: %s", e)
        contrib_stats = {"rows_updated": 0}
        failed_steps.append("contributor_metrics")
    step_times["contributor_metrics"] = time.time() - t0

    # ── Step 5: Export JSON ─────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 5: Exporting JSON files")
    t0 = time.time()
    try:
        _step_export(conn)
    except Exception as e:
        logger.error("Step 5 (JSON export) failed: %s", e)
        failed_steps.append("export")
    step_times["export"] = time.time() - t0

    conn.close()

    # ── Pipeline summary ────────────────────────────────────────────────
    total_duration = time.time() - pipeline_start
    logger.info("=" * 60)
    logger.info("Daily pipeline complete:")
    logger.info(
        "  1. Post collection:      %.1f min (%d posts collected)",
        step_times["post_collection"] / 60,
        post_stats.get("posts_collected", 0),
    )
    logger.info(
        "  2. Post keyword tagging: %.1f min (%d tags added)",
        step_times["post_tagging"] / 60,
        tag_stats.get("tags_added", 0),
    )
    logger.info(
        "  3. Comment collection:   %.1f min (%d comments from %d posts)",
        step_times["comment_collection"] / 60,
        comment_stats.get("comments_collected", 0),
        comment_stats.get("processed", 0),
    )
    logger.info(
        "  4. Comment tagging:      %.1f min (%d hits, %d posts newly tagged via comments)",
        step_times["comment_tagging"] / 60,
        comment_tag_stats.get("total_hits", 0),
        comment_tag_stats.get("posts_newly_tagged", 0),
    )
    logger.info(
        "  4b. Contributor metrics: %.1f min (%d snapshot rows updated)",
        step_times["contributor_metrics"] / 60,
        contrib_stats.get("rows_updated", 0),
    )
    logger.info(
        "  5. JSON export:          %.1f min",
        step_times["export"] / 60,
    )
    logger.info(
        "  Total duration:          %.1f min",
        total_duration / 60,
    )
    logger.info(
        "  Total Reddit requests:   %d",
        comment_stats.get("requests", 0),  # post collection requests not tracked separately
    )
    logger.info("=" * 60)

    if post_stats.get("error_details"):
        logger.warning("%d subreddit(s) had issues:", post_stats["errors"])
        for r in post_stats["error_details"]:
            logger.warning("  r/%s: [%s] %s", r["subreddit"], r["status"], r["error"])

    if failed_steps:
        logger.error("Pipeline step(s) failed: %s", ", ".join(failed_steps))

    if failed_steps or post_stats.get("error_details"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
