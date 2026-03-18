#!/usr/bin/env python3
"""Detect n-grams that are newly rising in frequency.

Compares recent posts (last N months) against the earlier corpus to find
terms gaining traction. Uses document frequency (not raw token counts) and
smoothed lift to avoid infinite scores for terms absent in the earlier window.

Usage:
    python emergence_monitor.py --months-back 6 --min-recent-count 20 --top-n 30
    python emergence_monitor.py --months-back 3 --min-recent-count 10
"""

import argparse
import csv
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    get_conn, load_all_theme_keywords, clean_text, tokenize,
    extract_ngrams, STOPWORDS, SUB_PLACEHOLDERS,
)

RESULTS_DIR = Path(__file__).parent.parent / "results"
BATCH_SIZE = 5_000
PSEUDOCOUNT = 10


def get_post_ids_by_window(conn, cutoff_date):
    """Split keyword-eligible posts into recent and earlier windows."""
    recent = conn.execute(
        f"SELECT id FROM posts WHERE subreddit IN ({SUB_PLACEHOLDERS}) AND collected_date >= ?",
        (cutoff_date,)
    ).fetchall()
    earlier = conn.execute(
        f"SELECT id FROM posts WHERE subreddit IN ({SUB_PLACEHOLDERS}) AND collected_date < ?",
        (cutoff_date,)
    ).fetchall()
    return [r["id"] for r in recent], [r["id"] for r in earlier]


def count_ngrams_docfreq(conn, post_ids, label=""):
    """Count document frequency of unigrams and bigrams.

    Each n-gram is counted once per post, preventing a single spammy post
    from inflating a term's score.
    """
    uni_doc = Counter()
    bi_doc = Counter()
    total_posts = 0

    for batch_start in range(0, len(post_ids), BATCH_SIZE):
        batch = post_ids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        rows = conn.execute(
            f"SELECT title, selftext FROM posts WHERE id IN ({placeholders})",
            batch
        ).fetchall()

        for r in rows:
            total_posts += 1
            text = clean_text((r["title"] or "") + " " + (r["selftext"] or ""))
            tokens = tokenize(text)

            # Deduplicate per post
            post_unis = set()
            for t in tokens:
                if t not in STOPWORDS and len(t) >= 3:
                    post_unis.add(t)

            post_bis = set()
            for gram in extract_ngrams(tokens, n=2):
                post_bis.add(gram)

            for t in post_unis:
                uni_doc[t] += 1
            for g in post_bis:
                bi_doc[g] += 1

        done = min(batch_start + BATCH_SIZE, len(post_ids))
        print(f"  {label} {done:,}/{len(post_ids):,} posts processed")

    return uni_doc, bi_doc, total_posts


def smoothed_lift(recent_count, earlier_count, recent_total, earlier_total):
    """Smoothed lift with pseudocounts — no infinities."""
    rec_rate = (recent_count + PSEUDOCOUNT) / (recent_total + PSEUDOCOUNT)
    ear_rate = (earlier_count + PSEUDOCOUNT) / (earlier_total + PSEUDOCOUNT)
    return rec_rate / ear_rate


def composite_score(doc_freq, lift):
    """Composite: doc_freq * lift. Rewards widespread AND distinctive terms."""
    return doc_freq * lift


def main():
    parser = argparse.ArgumentParser(description="Detect emerging n-grams")
    parser.add_argument("--months-back", type=int, default=6, help="Recent window size in months")
    parser.add_argument("--min-recent-count", type=int, default=20, help="Min document frequency in recent window")
    parser.add_argument("--top-n", type=int, default=30, help="Number of top candidates to output")
    args = parser.parse_args()

    _, all_keywords = load_all_theme_keywords()
    conn = get_conn()

    # Compute cutoff date
    cutoff = conn.execute(
        f"SELECT date('now', '-{args.months_back} months')"
    ).fetchone()[0]
    print(f"Cutoff date: {cutoff} (recent = after this)")

    # Split corpus
    print("\nSplitting corpus into time windows...")
    recent_ids, earlier_ids = get_post_ids_by_window(conn, cutoff)
    print(f"  Recent: {len(recent_ids):,} posts")
    print(f"  Earlier: {len(earlier_ids):,} posts")

    if not recent_ids or not earlier_ids:
        print("Error: one of the windows is empty. Adjust --months-back.")
        sys.exit(1)

    # Count n-grams (document frequency)
    print("\nCounting document frequencies in recent window...")
    rec_uni, rec_bi, rec_total = count_ngrams_docfreq(conn, recent_ids, label="recent")

    print("\nCounting document frequencies in earlier window...")
    ear_uni, ear_bi, ear_total = count_ngrams_docfreq(conn, earlier_ids, label="earlier")

    # Compute smoothed growth scores
    candidates = []

    for ngram, rec_count in rec_uni.items():
        if rec_count < args.min_recent_count:
            continue
        if ngram in all_keywords:
            continue
        ear_count = ear_uni.get(ngram, 0)
        lift = smoothed_lift(rec_count, ear_count, rec_total, ear_total)
        score = composite_score(rec_count, lift)
        candidates.append((ngram, rec_count, ear_count, lift, score))

    for ngram, rec_count in rec_bi.items():
        if rec_count < args.min_recent_count:
            continue
        ngram_str = " ".join(ngram)
        if ngram_str in all_keywords:
            continue
        ear_count = ear_bi.get(ngram, 0)
        lift = smoothed_lift(rec_count, ear_count, rec_total, ear_total)
        score = composite_score(rec_count, lift)
        candidates.append((ngram_str, rec_count, ear_count, lift, score))

    candidates.sort(key=lambda x: (-x[4], -x[1]))
    top = candidates[:args.top_n]

    # Print
    print(f"\n{'='*80}")
    print(f"Top {len(top)} emerging n-grams (last {args.months_back} months)")
    print(f"Scoring: doc_freq × smoothed_lift (pseudocount={PSEUDOCOUNT})")
    print(f"{'='*80}")
    print(f"{'Rank':<5} {'N-gram':<30} {'Recent':<10} {'Earlier':<10} {'Lift':<10} {'Score':<10}")
    print("-" * 80)
    for i, (ngram, rec, ear, lift, score) in enumerate(top, 1):
        print(f"{i:<5} {str(ngram):<30} {rec:<10} {ear:<10} {lift:<10.1f} {score:<10.0f}")

    # Write CSV
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"emergence_{timestamp}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["rank", "ngram", "recent_doc_freq", "earlier_doc_freq",
                         "smoothed_lift", "composite_score"])
        for i, (ngram, rec, ear, lift, score) in enumerate(top, 1):
            writer.writerow([i, ngram, rec, ear, f"{lift:.1f}", f"{score:.0f}"])

    print(f"\nResults saved to {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
