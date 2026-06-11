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

from src.config import load_communities, load_keywords, load_keyword_communities, keyword_fingerprint
from src.reddit_client import RedditClient
from src.db.schema import initialize as init_db
from src.db.operations import export_snapshots_json, export_subreddits_json, export_site_meta_json, export_community_activity_json, sync_subreddit_config, update_contributor_metrics_for_date
from src.collector import collect_subreddit
from src.db.operations import export_keyword_trends_json, export_theme_health_json
from src.keyword_matching import build_patterns, match_text

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def _step_collect_posts(communities, client, conn):
    """Step 1: Collect subreddit data + posts."""
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


def _step_collect_posts_arctic(communities, conn):
    """Arctic-mode Step 1: pull recent posts from Arctic Shift.

    Used when Reddit is unavailable — either no OAuth creds (arctic-first) or
    Reddit failed for a majority of subreddits mid-run. Keeps post volume and
    theme trends fresh; comments come from _step_collect_comments_arctic, but
    subreddit snapshots (subscribers/active users) have no archive equivalent
    and stay empty for the day.
    """
    from scripts.backfill_arctic import fetch_posts, parse_arctic_post
    from src.db.operations import insert_posts

    before_epoch = int(time.time())
    # 72h window (not 36h): Arctic Shift is an archive with ingestion lag, so a
    # post created 30h ago may not be archived yet. The overlap on consecutive
    # fallback days is absorbed by INSERT OR IGNORE.
    after_epoch = before_epoch - 72 * 3600

    ok = 0
    errors = []
    total_inserted = 0
    for community in communities:
        subreddit = community["subreddit"]
        try:
            raw, truncated = fetch_posts(subreddit, after_epoch, before_epoch)
            if truncated:
                raise RuntimeError("Arctic Shift window truncated (partial data)")
            parsed = [parse_arctic_post(p) for p in raw]
            # Force canonical casing — Arctic Shift returns e.g. "antiai", which
            # case-sensitive IN(...) filters downstream would silently drop.
            for p in parsed:
                p["subreddit"] = subreddit
            inserted = insert_posts(parsed, conn=conn)
            conn.commit()
            total_inserted += inserted
            ok += 1
            logger.info("  r/%s: %d fetched, %d new inserted (arctic fallback)",
                        subreddit, len(raw), inserted)
        except Exception as e:
            logger.warning("  r/%s: arctic fallback failed: %s", subreddit, e)
            errors.append({"subreddit": subreddit, "status": "arctic_error", "error": str(e)})

    return {
        "ok": ok,
        "errors": len(errors),
        "total": len(communities),
        "posts_collected": total_inserted,
        "error_details": errors,
    }


def _step_collect_comments_arctic(communities, conn):
    """Step 3 (arctic mode): pull recent comments from the Arctic Shift archive.

    The Reddit path snapshots a post's comment tree once, 5-6 days after the
    post. Arctic Shift archives comments within seconds of creation (and its
    copy of each post predates any comments, so posts.num_comments-based
    eligibility can't work). Instead: pull all comments *created* in the last
    72h per sub — same lag rationale as the post fallback — and attach them to
    posts already in the DB. Run daily, this converges on the same corpus with
    no per-post bookkeeping; INSERT OR IGNORE absorbs the window overlap.
    """
    from scripts.backfill_arctic import (
        fetch_comments, parse_arctic_comment, filter_comments,
        insert_comments_for_known_posts,
    )
    from scripts.collect_comments import EXCLUDED_SUBREDDITS

    before_epoch = int(time.time())
    after_epoch = before_epoch - 72 * 3600

    eligible = [c for c in communities if c["subreddit"] not in EXCLUDED_SUBREDDITS]
    ok = 0
    errors = []
    total_inserted = 0
    total_orphans = 0
    for community in eligible:
        subreddit = community["subreddit"]
        try:
            raw, truncated = fetch_comments(subreddit, after_epoch, before_epoch)
            if truncated:
                raise RuntimeError("Arctic Shift comment window truncated (partial data)")
            parsed = [parse_arctic_comment(c) for c in filter_comments(raw)]
            inserted, orphans = insert_comments_for_known_posts(parsed, subreddit, conn)
            total_inserted += inserted
            total_orphans += orphans
            ok += 1
            logger.info("  r/%s: %d comments fetched, %d new inserted, %d orphans (arctic)",
                        subreddit, len(raw), inserted, orphans)
        except Exception as e:
            logger.warning("  r/%s: arctic comment collection failed: %s", subreddit, e)
            errors.append({"subreddit": subreddit, "error": str(e)})

    return {
        "eligible": len(eligible),
        "processed": ok,
        "skipped_errors": len(errors),
        "comments_collected": total_inserted,
        "orphans_dropped": total_orphans,
        "requests": 0,  # no Reddit requests in arctic mode
    }


def _step_heal_snapshots(communities, conn):
    """Step 1c: self-heal snapshot rows from our own data (trailing 14 days).

    Reddit-sourced snapshot rows stop appearing whenever Reddit access breaks.
    For any day in the trailing window with no row, build one from the posts
    table (posts_today, unique_authors) + the comments table (7d contributor
    metrics; avg comments/post once a day is 6+ days old and its threads have
    finished accruing). subscribers/active_users stay NULL — unobservable
    without Reddit. Idempotent: INSERT OR IGNORE never touches real rows.
    """
    from datetime import date as date_cls, timedelta
    from src.db.operations import (
        create_arctic_snapshot_rows, update_arctic_comment_averages,
    )

    subs = [c["subreddit"] for c in communities]
    today = date_cls.today()
    rows_created = 0
    for offset in range(13, 0, -1):  # past days; today's row + its contributor
        d = today - timedelta(days=offset)  # metrics are handled by Step 4b
        # Cheap existence guard: the aggregation behind create/update does a
        # full posts-table scan per date, so skip dates already fully healed.
        existing = conn.execute(
            "SELECT COUNT(*) FROM subreddit_snapshots WHERE snapshot_date = ?",
            (d.isoformat(),),
        ).fetchone()[0]
        if existing >= len(subs):
            continue
        created = create_arctic_snapshot_rows(d, subs, conn=conn)
        if created:
            update_contributor_metrics_for_date(d, conn=conn)
            rows_created += created
    create_arctic_snapshot_rows(today, subs, conn=conn)

    avgs_updated = 0
    for offset in range(6, 14):  # refresh the maturity boundary + healed days
        d = today - timedelta(days=offset)
        pending = conn.execute(
            "SELECT COUNT(*) FROM subreddit_snapshots "
            "WHERE snapshot_date = ? AND data_source = 'arctic_shift' "
            "AND avg_comments_per_post IS NULL",
            (d.isoformat(),),
        ).fetchone()[0]
        if pending:
            avgs_updated += update_arctic_comment_averages(d, conn=conn)

    return {"rows_created": rows_created, "comment_avgs_updated": avgs_updated}


def _step_tag_posts(conn):
    """Step 2: Tag posts with keyword categories (tag_keywords.py logic)."""
    keyword_categories = load_keywords()
    patterns = build_patterns(keyword_categories)
    logger.info("Loaded %d patterns across %d categories", len(patterns), len(keyword_categories))

    # Load post IDs already scanned against post text. source='post' only:
    # a post that gained comment-propagated tags before its own text was ever
    # scanned must not be skipped here.
    tagged_ids = set(
        r[0] for r in conn.execute(
            "SELECT DISTINCT post_id FROM post_keyword_tags WHERE source = 'post'"
        ).fetchall()
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

    # Daily tagging only covers newly collected posts. If the keyword config
    # has changed since the corpus was last fully tagged, historical posts are
    # NOT retagged here — surface that so the gap doesn't go unnoticed.
    current_fp = keyword_fingerprint(keyword_categories)
    row = conn.execute(
        "SELECT value FROM pipeline_meta WHERE key = 'keyword_fingerprint'"
    ).fetchone()
    stored_fp = row[0] if row else None
    keyword_version_stale = stored_fp is not None and stored_fp != current_fp
    if keyword_version_stale:
        logger.warning(
            "Keyword config changed since last full tagging — historical posts "
            "are NOT retagged by daily collection. Run: "
            ".venv/bin/python scripts/tag_keywords.py"
        )

    return {
        "posts_scanned": scanned,
        "tags_added": tagged,
        "keyword_version_stale": keyword_version_stale,
    }


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

    activity_path = export_community_activity_json(output_path=data_dir / "community_activity.json.tmp", conn=conn)
    os.replace(str(activity_path), str(data_dir / "community_activity.json"))
    activity_path = data_dir / "community_activity.json"

    kw_trends_path = export_keyword_trends_json(output_path=data_dir / "keyword_trends.json.tmp", conn=conn)
    os.replace(str(kw_trends_path), str(data_dir / "keyword_trends.json"))
    kw_trends_path = data_dir / "keyword_trends.json"

    # Composition view: the same export with CharacterAI excluded. CharacterAI
    # is 75-90% of post volume and swings on its own platform lifecycle; the
    # ex-CharacterAI series is the dedicated-community signal. Additive — does
    # not alter keyword_trends.json. See docs/characterai_composition_fault_2026-05-16.md.
    comp_path = export_keyword_trends_json(
        output_path=data_dir / "composition_trends.json.tmp", conn=conn,
        exclude_subreddits=["CharacterAI"],
    )
    os.replace(str(comp_path), str(data_dir / "composition_trends.json"))
    comp_path = data_dir / "composition_trends.json"

    meta_path = export_site_meta_json(output_path=data_dir / "site_meta.json.tmp", conn=conn)
    os.replace(str(meta_path), str(data_dir / "site_meta.json"))
    meta_path = data_dir / "site_meta.json"

    health_path = export_theme_health_json(output_path=data_dir / "theme_health.json.tmp", conn=conn)
    os.replace(str(health_path), str(data_dir / "theme_health.json"))
    health_path = data_dir / "theme_health.json"

    logger.info("Exported: %s, %s, %s, %s, %s", snap_path, sub_path, kw_trends_path, meta_path, health_path)

    # Copy to web/data/ atomically.
    web_data_dir = Path(__file__).parent.parent / "web" / "data"
    web_data_dir.mkdir(parents=True, exist_ok=True)
    _atomic_copy(snap_path, web_data_dir / "snapshots.json")
    _atomic_copy(sub_path, web_data_dir / "subreddits.json")
    _atomic_copy(activity_path, web_data_dir / "community_activity.json")
    _atomic_copy(kw_trends_path, web_data_dir / "keyword_trends.json")
    _atomic_copy(comp_path, web_data_dir / "composition_trends.json")
    _atomic_copy(meta_path, web_data_dir / "site_meta.json")
    _atomic_copy(health_path, web_data_dir / "theme_health.json")
    logger.info("Copied JSON to web/data/ for frontend")

    # Export keyword details (transparency panel data)
    import subprocess
    detail_result = subprocess.run(
        [sys.executable, str(Path(__file__).parent / "export_keyword_details.py")],
        capture_output=True, text=True, timeout=600,
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
    # No explicit rate limiter: the client picks 1.5s (OAuth) or 6s (unauth).
    client = RedditClient()

    step_times = {}
    failed_steps = []

    # ── Step 1: Collect posts ───────────────────────────────────────────
    # Arctic-first: with no OAuth credentials, Reddit is guaranteed dead
    # (unauthenticated endpoints disabled 2026-05-30, app creation gated
    # behind an approval ticket since ~2026-03) — skip the 40 doomed requests
    # and go straight to the archive. Installing the creds file flips the
    # pipeline back to Reddit-primary automatically.
    logger.info("=" * 60)
    arctic_mode = not client.is_authenticated
    if arctic_mode:
        logger.warning("STEP 1: No OAuth creds — ARCTIC-FIRST mode (skipping Reddit entirely)")
        t0 = time.time()
        try:
            post_stats = _step_collect_posts_arctic(communities, conn)
        except Exception:
            logger.exception("Step 1 (arctic-first post collection) failed")
            post_stats = {"ok": 0, "errors": len(communities), "total": len(communities), "posts_collected": 0, "error_details": []}
            failed_steps.append("post_collection")
        step_times["post_collection"] = time.time() - t0
    else:
        logger.info("STEP 1: Collecting subreddit data + posts")
        t0 = time.time()
        try:
            post_stats = _step_collect_posts(communities, client, conn)
        except Exception:
            logger.exception("Step 1 (post collection) failed")
            post_stats = {"ok": 0, "errors": len(communities), "total": len(communities), "posts_collected": 0, "error_details": []}
            failed_steps.append("post_collection")
        step_times["post_collection"] = time.time() - t0

        # ── Step 1b: Arctic Shift fallback ──────────────────────────────
        # If Reddit failed for a majority of subs (auth outage, policy
        # change), recover post volume from the Arctic Shift archive so the
        # theme trends stay fresh. Snapshots are not recoverable here.
        if post_stats["errors"] >= (post_stats["total"] or 1) / 2:
            logger.warning("=" * 60)
            logger.warning("STEP 1b: Reddit failed for %d/%d subs — falling back to Arctic Shift",
                           post_stats["errors"], post_stats["total"])
            t0 = time.time()
            try:
                arctic_stats = _step_collect_posts_arctic(communities, conn)
                arctic_mode = True
                post_stats = arctic_stats
                if "post_collection" in failed_steps:
                    failed_steps.remove("post_collection")
            except Exception:
                logger.exception("Step 1b (arctic fallback) failed")
            step_times["arctic_fallback"] = time.time() - t0

    # ── Step 1c: Self-heal snapshot rows ────────────────────────────────
    # Must run AFTER Step 1/1b: real Reddit rows insert first, so the
    # INSERT OR IGNORE here only fills genuinely missing days.
    logger.info("=" * 60)
    logger.info("STEP 1c: Self-healing snapshot rows (trailing 14 days)")
    t0 = time.time()
    try:
        heal_stats = _step_heal_snapshots(communities, conn)
        logger.info("  %d snapshot rows created, %d comment averages filled",
                    heal_stats["rows_created"], heal_stats["comment_avgs_updated"])
    except Exception:
        logger.exception("Step 1c (snapshot self-heal) failed")
        failed_steps.append("snapshot_heal")
    step_times["snapshot_heal"] = time.time() - t0

    # ── Step 2: Tag posts ───────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 2: Tagging posts with keywords")
    t0 = time.time()
    try:
        tag_stats = _step_tag_posts(conn)
    except Exception:
        logger.exception("Step 2 (post tagging) failed")
        tag_stats = {"posts_scanned": 0, "tags_added": 0}
        failed_steps.append("post_tagging")
    step_times["post_tagging"] = time.time() - t0

    # ── Step 3: Collect comments ────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 3: Collecting comments%s",
                " from Arctic Shift (Reddit unavailable)" if arctic_mode else " for eligible posts")
    t0 = time.time()
    try:
        if arctic_mode:
            comment_stats = _step_collect_comments_arctic(communities, conn)
        else:
            comment_stats = _step_collect_comments(conn)
    except Exception:
        logger.exception("Step 3 (comment collection) failed")
        comment_stats = {"comments_collected": 0, "processed": 0, "requests": 0}
        failed_steps.append("comment_collection")
    step_times["comment_collection"] = time.time() - t0

    # ── Step 4: Tag comments + propagate ────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 4: Tagging comments + propagating to posts")
    t0 = time.time()
    try:
        comment_tag_stats = _step_tag_comments(conn)
    except Exception:
        logger.exception("Step 4 (comment tagging) failed")
        comment_tag_stats = {"total_hits": 0, "posts_newly_tagged": 0}
        failed_steps.append("comment_tagging")
    step_times["comment_tagging"] = time.time() - t0

    # ── Step 4b: Compute contributor metrics ────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 4b: Computing rolling-7d contributor metrics")
    t0 = time.time()
    try:
        contrib_stats = _step_compute_contributors(conn)
    except Exception:
        logger.exception("Step 4b (contributor metrics) failed")
        contrib_stats = {"rows_updated": 0}
        failed_steps.append("contributor_metrics")
    step_times["contributor_metrics"] = time.time() - t0

    # ── Step 5: Export JSON ─────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("STEP 5: Exporting JSON files")
    t0 = time.time()
    try:
        _step_export(conn)
    except Exception:
        logger.exception("Step 5 (JSON export) failed")
        failed_steps.append("export")
    step_times["export"] = time.time() - t0

    conn.close()

    # ── Pipeline summary ────────────────────────────────────────────────
    total_duration = time.time() - pipeline_start
    logger.info("=" * 60)
    logger.info("Daily pipeline complete:")
    logger.info(
        "  1. Post collection:      %.1f min (%d posts collected)%s",
        step_times["post_collection"] / 60,
        post_stats.get("posts_collected", 0),
        " [via ARCTIC SHIFT — no snapshots today]" if arctic_mode else "",
    )
    if arctic_mode:
        logger.warning(
            "Arctic Shift served today's posts and comments — Reddit access is unavailable; "
            "subscriber/active-user snapshots did not run (no archive equivalent)."
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

    # Decide exit status. Previously: any per-sub error → exit 1 → push skipped.
    # That made one dead subreddit (e.g., r/HeavenGF on 2026-05-14) block the
    # entire daily deploy for 3+ days. New policy: per-sub errors are NOT fatal
    # unless they affect a majority of subreddits OR a step itself failed.
    # Catastrophic-only fatality keeps the site fresh through normal sub-deletion
    # events while still flagging genuine pipeline breakage.
    n_total = post_stats.get("total", 1) or 1
    n_errors = post_stats.get("errors", 0)
    catastrophic_sub_failure = n_errors > n_total / 2
    if failed_steps or catastrophic_sub_failure:
        return 1
    # Soft warning state: per-sub issues exist but pipeline overall is healthy
    if post_stats.get("error_details"):
        logger.warning(
            "Per-sub errors present (%d/%d) but below catastrophic threshold — pushing anyway.",
            n_errors, n_total,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
