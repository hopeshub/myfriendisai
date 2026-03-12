#!/usr/bin/env python3
"""Discover high-precision keywords for AI companionship tracking.

Two-step pipeline:
  1. MINE — Sample posts from companion subs, send to Claude, collect candidate phrases
  2. TEST — For each phrase, check hit distribution and precision across all subreddits

Usage:
    # Full pipeline (mine + test)
    python scripts/keyword_research/discover_keywords.py

    # Mine only (skip precision testing — cheaper, faster)
    python scripts/keyword_research/discover_keywords.py --mine-only

    # Test precision on an existing candidates file
    python scripts/keyword_research/discover_keywords.py --test-only data/keyword_discoveries/candidates_2026-03-11.json

    # Customize
    python scripts/keyword_research/discover_keywords.py --sample-size 1000 --batch-size 25 --model claude-haiku-4-5-20251001

Requires ANTHROPIC_API_KEY environment variable.
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import anthropic

from src.config import load_keywords
from src.db.schema import initialize as init_db
from src.keyword_discovery import (
    deduplicate_phrases,
    format_results_text,
    get_companion_subs,
    get_general_subs,
    mine_candidates,
    sample_posts,
    test_all_phrases,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path("data/keyword_discoveries")


def main():
    parser = argparse.ArgumentParser(description="Discover high-precision companion keywords")
    parser.add_argument("--sample-size", type=int, default=2000, help="Posts to sample (default: 2000)")
    parser.add_argument("--batch-size", type=int, default=50, help="Posts per Claude batch (default: 50)")
    parser.add_argument("--model", default="claude-haiku-4-5-20251001", help="Claude model for mining")
    parser.add_argument("--max-phrases", type=int, default=200, help="Max phrases to precision-test (default: 200)")
    parser.add_argument("--mine-only", action="store_true", help="Only mine candidates, skip precision testing")
    parser.add_argument("--test-only", type=str, help="Path to existing candidates JSON — skip mining, test precision only")
    args = parser.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        logger.error("Set ANTHROPIC_API_KEY environment variable")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    conn = init_db()
    companion_subs = get_companion_subs()
    general_subs = get_general_subs()
    timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # ── Step 1: Mine candidates ──────────────────────────────────────────

    if args.test_only:
        logger.info("Loading existing candidates from %s", args.test_only)
        with open(args.test_only) as f:
            saved = json.load(f)
        candidates = saved.get("candidates", saved.get("phrases", []))
        logger.info("Loaded %d candidates", len(candidates))
    else:
        logger.info("=" * 60)
        logger.info("STEP 1: Mining candidate phrases")
        logger.info("  Sample size: %d | Batch size: %d | Model: %s", args.sample_size, args.batch_size, args.model)
        logger.info("  Companion subs: %s", ", ".join(sorted(companion_subs)))
        logger.info("=" * 60)

        posts = sample_posts(conn, list(companion_subs), n=args.sample_size)
        logger.info("Sampled %d posts", len(posts))

        if not posts:
            logger.error("No posts found — check your database")
            sys.exit(1)

        raw_phrases = mine_candidates(posts, client, args.model, batch_size=args.batch_size)
        logger.info("Raw phrases collected: %d", len(raw_phrases))

        candidates = deduplicate_phrases(raw_phrases)
        logger.info("After deduplication: %d unique phrases", len(candidates))

        # Save candidates
        candidates_file = OUTPUT_DIR / f"candidates_{timestamp}.json"
        with open(candidates_file, "w") as f:
            json.dump({
                "meta": {
                    "timestamp": timestamp,
                    "model": args.model,
                    "sample_size": args.sample_size,
                    "batch_size": args.batch_size,
                    "num_batches": len(posts) // args.batch_size + (1 if len(posts) % args.batch_size else 0),
                    "raw_phrase_count": len(raw_phrases),
                    "unique_phrase_count": len(candidates),
                },
                "candidates": candidates,
            }, f, indent=2)
        logger.info("Saved candidates to %s", candidates_file)

        if args.mine_only:
            # Print top candidates and exit
            print(f"\n{'=' * 60}")
            print(f"TOP CANDIDATES ({len(candidates)} unique phrases)")
            print(f"{'=' * 60}\n")
            for c in candidates[:50]:
                print(f'  [{c["batch_count"]}x] "{c["text"]}"')
                if c.get("reasoning"):
                    print(f'       {c["reasoning"]}')
            print(f"\nFull list saved to {candidates_file}")
            print(f"Run with --test-only {candidates_file} to check precision")
            return

    # ── Step 2: Test precision ───────────────────────────────────────────

    logger.info("")
    logger.info("=" * 60)
    logger.info("STEP 2: Testing precision (%d phrases, max %d)", len(candidates), args.max_phrases)
    logger.info("=" * 60)

    results = test_all_phrases(
        candidates,
        conn,
        client,
        args.model,
        companion_subs,
        general_subs,
        max_phrases=args.max_phrases,
    )

    # Save full results as JSON
    results_file = OUTPUT_DIR / f"results_{timestamp}.json"
    with open(results_file, "w") as f:
        json.dump({
            "meta": {
                "timestamp": timestamp,
                "model": args.model,
                "phrases_tested": len(results),
                "companion_subs": sorted(companion_subs),
                "general_subs": sorted(general_subs),
            },
            "results": results,
        }, f, indent=2)
    logger.info("Saved full results to %s", results_file)

    # Save human-readable summary
    summary_file = OUTPUT_DIR / f"summary_{timestamp}.txt"
    summary_text = format_results_text(results)
    with open(summary_file, "w") as f:
        f.write(summary_text)
    logger.info("Saved summary to %s", summary_file)

    # Print summary to stdout
    print(summary_text)

    # Quick stats
    high = [r for r in results if r["verdict"] == "HIGH"]
    existing = load_keywords()
    existing_terms = set()
    for cat in existing:
        for term in cat.get("terms", []):
            existing_terms.add(term.lower())

    novel = [r for r in high if r["phrase"].lower() not in existing_terms]
    print(f"\n{'=' * 60}")
    print(f"  {len(novel)} HIGH-PRECISION phrases not in keywords.yaml")
    print(f"{'=' * 60}")
    for r in novel[:30]:
        print(f'  "{r["phrase"]}" — {r["total_hits"]} hits, {r["companion_ratio"]:.0%} companion')

    conn.close()


if __name__ == "__main__":
    main()
