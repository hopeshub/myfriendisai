#!/usr/bin/env python3
"""Find n-grams over-represented in a theme's posts vs. general baseline.

Scoring uses document frequency (not raw token counts) and smoothed lift
to avoid infinite scores for baseline-absent terms. Candidates are ranked
by a composite score: doc_freq * smoothed_lift.

Usage:
    python corpus_comparison.py --theme "sexual_erp" --min-count 20 --top-n 50
    python corpus_comparison.py --theme therapy --min-count 10 --top-n 30
"""

import argparse
import csv
import math
import random
import sys
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    get_conn, load_all_theme_keywords, clean_text, tokenize,
    extract_ngrams, highlight_snippet, STOPWORDS, SUB_PLACEHOLDERS,
)

RESULTS_DIR = Path(__file__).parent.parent / "results"
BASELINE_SAMPLE = 100_000
BATCH_SIZE = 5_000

# Smoothing pseudocount — prevents zero-denominator and dampens rare-term noise
PSEUDOCOUNT = 10


def _build_sub_filter(exclude_subs=None):
    """Build a SQL subreddit IN clause, optionally excluding specific subs."""
    from utils import KW_SUBS
    subs = [s for s in KW_SUBS if s not in (exclude_subs or [])]
    return ",".join(f"'{s}'" for s in subs)


def get_theme_post_ids(theme, conn, sub_filter=None):
    """Get post IDs matching a theme via the post_keyword_tags table."""
    sf = sub_filter or SUB_PLACEHOLDERS
    rows = conn.execute(
        f"""SELECT DISTINCT pkt.post_id FROM post_keyword_tags pkt
            JOIN posts p ON p.id = pkt.post_id
            WHERE pkt.category = ? AND p.subreddit IN ({sf})""",
        (theme,)
    ).fetchall()
    return [r["post_id"] for r in rows]


def get_baseline_post_ids(target_theme_ids, conn, sub_filter=None, size=BASELINE_SAMPLE):
    """Sample random posts from keyword-eligible subs excluding the target theme."""
    sf = sub_filter or SUB_PLACEHOLDERS
    exclude_set = set(target_theme_ids)

    row = conn.execute("SELECT MIN(rowid), MAX(rowid) FROM posts").fetchone()
    min_id, max_id = row[0], row[1]

    random.seed(42)
    oversample = min(size * 3, max_id - min_id + 1)
    candidate_rowids = random.sample(range(min_id, max_id + 1), oversample)

    ids = []
    for batch_start in range(0, len(candidate_rowids), BATCH_SIZE):
        batch = candidate_rowids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        rows = conn.execute(
            f"SELECT id FROM posts WHERE rowid IN ({placeholders}) AND subreddit IN ({sf})",
            batch
        ).fetchall()
        for r in rows:
            if r["id"] not in exclude_set:
                ids.append(r["id"])
        if len(ids) >= size:
            break

    return ids[:size]


def count_ngrams_docfreq(conn, post_ids, label=""):
    """Count document frequency of unigrams and bigrams.

    Each n-gram is counted once per post (document frequency), not once per
    occurrence (term frequency). This prevents a single spammy post from
    inflating a term's score.

    Also tracks per-subreddit document counts for concentration analysis.

    Returns:
        uni_doc_counts: Counter of {term: number_of_posts_containing_it}
        bi_doc_counts: Counter of {bigram_tuple: number_of_posts_containing_it}
        uni_sub_counts: dict of {term: Counter({subreddit: count})}
        bi_sub_counts: dict of {bigram_tuple: Counter({subreddit: count})}
        total_posts: number of posts processed
    """
    uni_doc = Counter()
    bi_doc = Counter()
    uni_sub = defaultdict(Counter)
    bi_sub = defaultdict(Counter)
    total_posts = 0

    for batch_start in range(0, len(post_ids), BATCH_SIZE):
        batch = post_ids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        rows = conn.execute(
            f"SELECT id, subreddit, title, selftext FROM posts WHERE id IN ({placeholders})",
            batch
        ).fetchall()

        for r in rows:
            total_posts += 1
            text = clean_text((r["title"] or "") + " " + (r["selftext"] or ""))
            tokens = tokenize(text)

            # Deduplicate per post: use sets
            post_unis = set()
            for t in tokens:
                if t not in STOPWORDS and len(t) >= 3:
                    post_unis.add(t)

            post_bis = set()
            for gram in extract_ngrams(tokens, n=2):
                post_bis.add(gram)

            sub = r["subreddit"]
            for t in post_unis:
                uni_doc[t] += 1
                uni_sub[t][sub] += 1
            for g in post_bis:
                bi_doc[g] += 1
                bi_sub[g][sub] += 1

        done = min(batch_start + BATCH_SIZE, len(post_ids))
        print(f"  {label} {done:,}/{len(post_ids):,} posts processed")

    return uni_doc, bi_doc, uni_sub, bi_sub, total_posts


def smoothed_lift(pos_count, base_count, pos_total, base_total):
    """Compute smoothed lift score: (pos + α) / (base + α) normalized by corpus sizes.

    Uses additive smoothing (pseudocounts) so zero-in-baseline never produces
    infinity. Returns a finite, comparable score.
    """
    pos_rate = (pos_count + PSEUDOCOUNT) / (pos_total + PSEUDOCOUNT)
    base_rate = (base_count + PSEUDOCOUNT) / (base_total + PSEUDOCOUNT)
    return pos_rate / base_rate


def composite_score(doc_freq, lift):
    """Composite ranking score: doc_freq * lift.

    Rewards terms that are both distinctive (high lift) AND widespread
    (high document frequency). Prevents rare one-off artifacts from
    dominating the rankings.
    """
    return doc_freq * lift


def max_concentration(sub_counts):
    """Return the fraction of posts from the most dominant subreddit."""
    if not sub_counts:
        return 0.0
    total = sum(sub_counts.values())
    if total == 0:
        return 0.0
    return max(sub_counts.values()) / total


def get_sample_snippets(ngram, conn, post_ids, n=3, snippet_len=120):
    """Get short example snippets showing the ngram in context."""
    search_term = ngram if isinstance(ngram, str) else " ".join(ngram)
    kw = f"%{search_term}%"
    # Use a subset of post IDs for speed
    sample_ids = post_ids[:2000]
    placeholders = ",".join("?" * len(sample_ids))
    rows = conn.execute(
        f"""SELECT id, title, selftext FROM posts WHERE id IN ({placeholders})
            AND (LOWER(title) LIKE ? OR LOWER(selftext) LIKE ?)
            ORDER BY RANDOM() LIMIT ?""",
        sample_ids + [kw, kw, n]
    ).fetchall()

    snippets = []
    for r in rows:
        text = (r["title"] or "") + " | " + (r["selftext"] or "")
        snippet = highlight_snippet(text, search_term, max_len=snippet_len)
        snippets.append(snippet)
    return snippets


def main():
    parser = argparse.ArgumentParser(description="Corpus comparison keyword discovery")
    parser.add_argument("--theme", required=True, help="Target theme name (e.g. 'therapy')")
    parser.add_argument("--min-count", type=int, default=20, help="Min document frequency in positive corpus")
    parser.add_argument("--top-n", type=int, default=50, help="Number of top candidates to output")
    parser.add_argument("--max-concentration", type=float, default=0.60,
                        help="Reject terms where one sub contributes more than this fraction (default: 0.60)")
    parser.add_argument("--exclude-subreddits", default="",
                        help="Comma-separated subreddits to exclude from both corpora")
    args = parser.parse_args()

    theme_keywords, all_keywords = load_all_theme_keywords()
    if args.theme not in theme_keywords:
        print(f"Error: theme '{args.theme}' not found. Available: {', '.join(theme_keywords.keys())}")
        sys.exit(1)

    exclude_subs = [s.strip() for s in args.exclude_subreddits.split(",") if s.strip()]
    sub_filter = _build_sub_filter(exclude_subs) if exclude_subs else None

    conn = get_conn()

    if exclude_subs:
        print(f"Excluding subreddits: {', '.join(exclude_subs)}")

    # Build corpora
    print(f"\nBuilding positive corpus for '{args.theme}'...")
    positive_ids = get_theme_post_ids(args.theme, conn, sub_filter=sub_filter)
    print(f"  {len(positive_ids):,} posts match theme")

    print(f"\nSampling baseline corpus ({BASELINE_SAMPLE:,} non-'{args.theme}' posts)...")
    baseline_ids = get_baseline_post_ids(positive_ids, conn, sub_filter=sub_filter)
    print(f"  {len(baseline_ids):,} baseline posts sampled")

    # Count n-grams (document frequency)
    print("\nCounting document frequencies in positive corpus...")
    pos_uni, pos_bi, pos_uni_sub, pos_bi_sub, pos_total = count_ngrams_docfreq(
        conn, positive_ids, label="positive")

    print("\nCounting document frequencies in baseline corpus...")
    base_uni, base_bi, _, _, base_total = count_ngrams_docfreq(
        conn, baseline_ids, label="baseline")

    # Build set of individual words from all active keywords for bigram filtering
    keyword_words = set()
    for term in all_keywords:
        for word in term.split():
            keyword_words.add(word)

    # Compute smoothed lift and composite scores
    candidates = []
    filtered_concentration = 0

    for ngram, pos_count in pos_uni.items():
        if pos_count < args.min_count:
            continue
        if ngram in all_keywords or ngram in keyword_words:
            continue
        # Concentration filter
        conc = max_concentration(pos_uni_sub.get(ngram, {}))
        if conc > args.max_concentration:
            filtered_concentration += 1
            continue
        base_count = base_uni.get(ngram, 0)
        lift = smoothed_lift(pos_count, base_count, pos_total, base_total)
        score = composite_score(pos_count, lift)
        top_sub = pos_uni_sub[ngram].most_common(1)[0] if pos_uni_sub.get(ngram) else ("?", 0)
        candidates.append((ngram, pos_count, base_count, lift, score, conc, top_sub))

    for ngram, pos_count in pos_bi.items():
        if pos_count < args.min_count:
            continue
        ngram_str = " ".join(ngram)
        if ngram_str in all_keywords:
            continue
        if any(w in all_keywords or w in keyword_words for w in ngram):
            continue
        conc = max_concentration(pos_bi_sub.get(ngram, {}))
        if conc > args.max_concentration:
            filtered_concentration += 1
            continue
        base_count = base_bi.get(ngram, 0)
        lift = smoothed_lift(pos_count, base_count, pos_total, base_total)
        score = composite_score(pos_count, lift)
        top_sub = pos_bi_sub[ngram].most_common(1)[0] if pos_bi_sub.get(ngram) else ("?", 0)
        candidates.append((ngram_str, pos_count, base_count, lift, score, conc, top_sub))

    # Sort by composite score (doc_freq * smoothed_lift)
    candidates.sort(key=lambda x: (-x[4], -x[1]))
    top = candidates[:args.top_n]

    # Print summary
    print(f"\n{'='*90}")
    print(f"Top {len(top)} over-represented n-grams in '{args.theme}'")
    print(f"Scoring: doc_freq × smoothed_lift (pseudocount={PSEUDOCOUNT})")
    print(f"Concentration filter: >{args.max_concentration:.0%} → rejected ({filtered_concentration} terms filtered)")
    print(f"{'='*90}")
    print(f"{'Rank':<5} {'N-gram':<25} {'DocFreq':<9} {'Base':<8} {'Lift':<8} {'Score':<10} {'TopSub':<20} {'Conc':<6}")
    print("-" * 90)
    for i, (ngram, pos, base, lift, score, conc, top_sub) in enumerate(top, 1):
        sub_name, sub_count = top_sub
        print(f"{i:<5} {str(ngram):<25} {pos:<9} {base:<8} {lift:<8.1f} {score:<10.0f} "
              f"{sub_name}({sub_count}){'':<{max(0,12-len(sub_name))}} {conc:<6.0%}")

    # Write CSV with sample snippets
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = RESULTS_DIR / f"corpus_comparison_{args.theme}_{timestamp}.csv"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"\nGathering sample snippets for CSV...")
    with open(out_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "rank", "ngram", "doc_freq", "baseline_doc_freq", "smoothed_lift",
            "composite_score", "top_subreddit", "concentration", "snippet_1", "snippet_2", "snippet_3"
        ])
        for i, (ngram, pos, base, lift, score, conc, top_sub) in enumerate(top, 1):
            sub_name, sub_count = top_sub
            snippets = get_sample_snippets(ngram, conn, positive_ids)
            # Pad to 3 snippets
            while len(snippets) < 3:
                snippets.append("")
            writer.writerow([
                i, ngram, pos, base, f"{lift:.1f}", f"{score:.0f}",
                f"{sub_name}({sub_count})", f"{conc:.0%}",
                snippets[0], snippets[1], snippets[2]
            ])

    print(f"Results saved to {out_path}")
    conn.close()


if __name__ == "__main__":
    main()
