#!/usr/bin/env python3
"""Phase 3: Corpus-driven keyword discovery.

For a given theme, finds words/phrases statistically overrepresented in
posts that match existing theme keywords vs. the general corpus.

Scoring:
  - Document frequency (each post counted once per term, not raw token count)
  - Smoothed lift with pseudocounts (no infinite ratios)
  - Composite ranking: doc_freq × smoothed_lift
  - Concentration filter: reject terms dominated by a single subreddit

Usage:
    python discover_keywords.py --theme rupture
    python discover_keywords.py --theme therapy --min-posts 15 --top-n 30
    python discover_keywords.py --theme rupture --generate-batch --batch-top 10
    python discover_keywords.py --theme sexual_erp --exclude-subreddits SpicyChatAI
    python discover_keywords.py --all-themes --top-n 20
"""

import argparse
import csv
import re
import random
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
RESULTS_DIR = SCRIPT_DIR / "results"

from utils import (
    get_conn, load_all_theme_keywords, count_keyword_hits,
    clean_text, tokenize, extract_ngrams, highlight_snippet,
    STOPWORDS, KW_SUBS, SUB_PLACEHOLDERS,
)

# ── Configuration ─────────────────────────────────────────────────────────

BASELINE_SAMPLE = 100_000
BATCH_SIZE = 5_000

# Smoothing pseudocount — prevents zero-denominator and dampens rare-term noise
PSEUDOCOUNT = 10

# Minimum character length for candidates
MIN_CHAR_LEN = 5

# Subreddit name substrings to filter (lowercased)
SUB_NAME_PARTS = set()
for _sub in KW_SUBS:
    _name = _sub.lower()
    SUB_NAME_PARTS.add(_name)
    for _suffix in ("ai", "app", "nsfw", "recovery", "runaways"):
        if _name.endswith(_suffix) and len(_name) > len(_suffix):
            SUB_NAME_PARTS.add(_name[:-len(_suffix)])


# ── Corpus building ──────────────────────────────────────────────────────

def _build_sub_filter(exclude_subs=None):
    """Build a SQL subreddit IN clause, optionally excluding specific subs."""
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


# ── N-gram counting (document frequency) ─────────────────────────────────

def count_ngrams_docfreq(conn, post_ids, label=""):
    """Count document frequency of unigrams and bigrams with per-subreddit tracking.

    Each n-gram is counted once per post (document frequency), not once per
    occurrence (term frequency). This prevents a single spammy/copypasta post
    from inflating a term's score.

    Also tracks capitalization for proper noun filtering.

    Returns:
        uni_stats: {term: {doc_freq, subs: Counter, cap_count, total_count}}
        bi_stats: {term_str: {doc_freq, subs: Counter}}
        total_posts: int
    """
    uni_stats = defaultdict(lambda: {"doc_freq": 0, "subs": Counter(),
                                      "cap_count": 0, "total_count": 0})
    bi_stats = defaultdict(lambda: {"doc_freq": 0, "subs": Counter()})
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
            subreddit = r["subreddit"]
            raw_text = (r["title"] or "") + " " + (r["selftext"] or "")

            # Track capitalization on raw text before cleaning
            raw_words = re.findall(r'\b[A-Za-z]+\b', raw_text)
            cap_tracker = defaultdict(lambda: [0, 0])  # [capitalized, total]
            for w in raw_words:
                key = w.lower()
                if len(key) >= MIN_CHAR_LEN and key not in STOPWORDS:
                    cap_tracker[key][1] += 1
                    if w[0].isupper():
                        cap_tracker[key][0] += 1

            # Clean, tokenize, deduplicate per post
            text = clean_text(raw_text)
            tokens = tokenize(text)

            post_unis = set()
            for t in tokens:
                if t not in STOPWORDS and len(t) >= MIN_CHAR_LEN:
                    post_unis.add(t)

            post_bis = set()
            for gram in extract_ngrams(tokens, n=2):
                gram_str = " ".join(gram)
                if len(gram_str) >= MIN_CHAR_LEN:
                    post_bis.add(gram_str)

            for t in post_unis:
                uni_stats[t]["doc_freq"] += 1
                uni_stats[t]["subs"][subreddit] += 1
                if t in cap_tracker:
                    uni_stats[t]["cap_count"] += cap_tracker[t][0]
                    uni_stats[t]["total_count"] += cap_tracker[t][1]

            for g in post_bis:
                bi_stats[g]["doc_freq"] += 1
                bi_stats[g]["subs"][subreddit] += 1

        done = min(batch_start + BATCH_SIZE, len(post_ids))
        print(f"  {label} {done:,}/{len(post_ids):,} posts processed")

    return uni_stats, bi_stats, total_posts


# ── Scoring ───────────────────────────────────────────────────────────────

def smoothed_lift(pos_count, base_count, pos_total, base_total):
    """Smoothed lift: (pos + α) / (base + α), normalized by corpus sizes.

    Additive smoothing (pseudocounts) so zero-in-baseline never produces
    infinity. Returns a finite, comparable score.
    """
    pos_rate = (pos_count + PSEUDOCOUNT) / (pos_total + PSEUDOCOUNT)
    base_rate = (base_count + PSEUDOCOUNT) / (base_total + PSEUDOCOUNT)
    return pos_rate / base_rate


def max_concentration(sub_counts):
    """Return the fraction of posts from the most dominant subreddit."""
    if not sub_counts:
        return 0.0
    total = sum(sub_counts.values())
    if total == 0:
        return 0.0
    return max(sub_counts.values()) / total


def is_subreddit_substring(term):
    """Check if term is a substring of any subreddit name in the corpus."""
    term_lower = term.lower()
    for part in SUB_NAME_PARTS:
        if term_lower in part or part in term_lower:
            return True
    return False


def get_sample_snippets(ngram, conn, post_ids, n=3, snippet_len=120):
    """Get short example snippets showing the ngram in context."""
    kw = f"%{ngram}%"
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
        snippet = highlight_snippet(text, ngram, max_len=snippet_len)
        snippets.append(snippet)
    return snippets


# ── Discovery ─────────────────────────────────────────────────────────────

def discover(theme, min_posts=10, min_subs=3, top_n=50, max_conc=0.60,
             exclude_subs=None):
    """Run corpus comparison with document-frequency scoring and filtering.

    Filters applied:
        1. Min distinct posts containing term (document frequency)
        2. Min distinct subreddits
        3. Proper noun filter (capitalized >80%)
        4. Min character length
        5. Subreddit name substring filter
        6. Concentration filter (single sub >max_conc)
        + existing keyword/stopword filters

    Scoring:
        composite = doc_freq × smoothed_lift(pseudocount=10)
    """
    theme_keywords, all_keywords = load_all_theme_keywords()
    if theme not in theme_keywords:
        print(f"Error: theme '{theme}' not found. Available: {', '.join(theme_keywords.keys())}")
        sys.exit(1)

    sub_filter = _build_sub_filter(exclude_subs) if exclude_subs else None
    conn = get_conn()

    if exclude_subs:
        print(f"  Excluding subreddits: {', '.join(exclude_subs)}")

    # Build corpora
    print(f"\n  Building positive corpus for '{theme}'...")
    positive_ids = get_theme_post_ids(theme, conn, sub_filter=sub_filter)
    print(f"  {len(positive_ids):,} posts match theme")

    print(f"\n  Sampling baseline corpus ({BASELINE_SAMPLE:,} posts)...")
    baseline_ids = get_baseline_post_ids(positive_ids, conn, sub_filter=sub_filter)
    print(f"  {len(baseline_ids):,} baseline posts sampled")

    # Count n-grams (document frequency, per-post deduplication)
    print("\n  Counting document frequencies in positive corpus...")
    pos_uni, pos_bi, pos_total = count_ngrams_docfreq(conn, positive_ids, label="positive")

    print("\n  Counting document frequencies in baseline corpus...")
    base_uni, base_bi, base_total = count_ngrams_docfreq(conn, baseline_ids, label="baseline")

    # Build keyword word set for filtering
    keyword_words = set()
    for term in all_keywords:
        for word in term.split():
            keyword_words.add(word)

    # Score and filter candidates
    raw_candidates = []
    filtered_counts = {"concentration": 0, "proper_noun": 0, "subreddit_name": 0}

    # Unigrams
    for ngram, stats in pos_uni.items():
        if len(ngram) < MIN_CHAR_LEN:
            continue
        if ngram in all_keywords or ngram in keyword_words:
            continue
        if stats["doc_freq"] < min_posts:
            continue
        n_subs = len(stats["subs"])
        if n_subs < min_subs:
            continue
        # Proper noun filter
        if stats["total_count"] > 0:
            cap_ratio = stats["cap_count"] / stats["total_count"]
            if cap_ratio > 0.8:
                filtered_counts["proper_noun"] += 1
                continue
        # Subreddit name filter
        if is_subreddit_substring(ngram):
            filtered_counts["subreddit_name"] += 1
            continue
        # Concentration filter
        conc = max_concentration(stats["subs"])
        if conc > max_conc:
            filtered_counts["concentration"] += 1
            continue

        base_count = base_uni.get(ngram, {}).get("doc_freq", 0)
        lift = smoothed_lift(stats["doc_freq"], base_count, pos_total, base_total)
        score = stats["doc_freq"] * lift
        top_sub = stats["subs"].most_common(1)[0] if stats["subs"] else ("?", 0)

        raw_candidates.append({
            "ngram": ngram,
            "doc_freq": stats["doc_freq"],
            "base_doc_freq": base_count,
            "lift": lift,
            "score": score,
            "n_subs": n_subs,
            "concentration": conc,
            "top_sub": top_sub,
        })

    # Bigrams
    for ngram_str, stats in pos_bi.items():
        if ngram_str in all_keywords:
            continue
        words = ngram_str.split()
        if any(w in all_keywords or w in keyword_words for w in words):
            continue
        if stats["doc_freq"] < min_posts:
            continue
        n_subs = len(stats["subs"])
        if n_subs < min_subs:
            continue
        if is_subreddit_substring(ngram_str):
            filtered_counts["subreddit_name"] += 1
            continue
        conc = max_concentration(stats["subs"])
        if conc > max_conc:
            filtered_counts["concentration"] += 1
            continue

        base_count = base_bi.get(ngram_str, {}).get("doc_freq", 0)
        lift = smoothed_lift(stats["doc_freq"], base_count, pos_total, base_total)
        score = stats["doc_freq"] * lift
        top_sub = stats["subs"].most_common(1)[0] if stats["subs"] else ("?", 0)

        raw_candidates.append({
            "ngram": ngram_str,
            "doc_freq": stats["doc_freq"],
            "base_doc_freq": base_count,
            "lift": lift,
            "score": score,
            "n_subs": n_subs,
            "concentration": conc,
            "top_sub": top_sub,
        })

    # Sort by composite score (doc_freq × smoothed_lift)
    raw_candidates.sort(key=lambda x: (-x["score"], -x["doc_freq"]))

    print(f"\n  Filtered: {filtered_counts['concentration']} concentration, "
          f"{filtered_counts['proper_noun']} proper noun, "
          f"{filtered_counts['subreddit_name']} subreddit name")

    # Take top-n and collect sample snippets
    candidates = raw_candidates[:top_n]
    print(f"\n  Collecting sample snippets for top {len(candidates)} candidates...")
    for c in candidates:
        c["snippets"] = get_sample_snippets(c["ngram"], conn, positive_ids)

    conn.close()
    return candidates


# ── Output ────────────────────────────────────────────────────────────────

def print_results(theme, candidates):
    """Print formatted results table."""
    print(f"\n{'='*95}")
    print(f"  Top {len(candidates)} candidates for '{theme}'")
    print(f"  Scoring: doc_freq × smoothed_lift (pseudocount={PSEUDOCOUNT})")
    print(f"{'='*95}")
    print(f"  {'#':<4} {'N-gram':<25} {'DocFreq':<9} {'Base':<8} {'Lift':<7} {'Score':<9} "
          f"{'TopSub':<18} {'Conc':<6}")
    print(f"  {'-'*85}")
    for i, c in enumerate(candidates, 1):
        sub_name, sub_count = c["top_sub"]
        print(f"  {i:<4} {c['ngram']:<25} {c['doc_freq']:<9} {c['base_doc_freq']:<8} "
              f"{c['lift']:<7.1f} {c['score']:<9.0f} "
              f"{sub_name}({sub_count}){'':<{max(0,10-len(sub_name))}} {c['concentration']:<6.0%}")
    print(f"{'='*95}")


def main():
    parser = argparse.ArgumentParser(
        description="Corpus-driven keyword discovery with document-frequency scoring.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python discover_keywords.py --theme rupture
  python discover_keywords.py --all-themes --top-n 20
  python discover_keywords.py --theme therapy --generate-batch --batch-top 10
"""
    )
    parser.add_argument("--theme", help="Target theme (or use --all-themes)")
    parser.add_argument("--all-themes", action="store_true", help="Run discovery on all 6 themes")
    parser.add_argument("--min-posts", type=int, default=10, help="Min distinct posts containing term (default: 10)")
    parser.add_argument("--min-subs", type=int, default=3, help="Min distinct subreddits (default: 3)")
    parser.add_argument("--max-concentration", type=float, default=0.60,
                        help="Reject terms where one sub contributes more than this (default: 0.60)")
    parser.add_argument("--top-n", type=int, default=50, help="Candidates per theme (default: 50)")
    parser.add_argument("--exclude-subreddits", default="",
                        help="Comma-separated subreddits to exclude")
    parser.add_argument("--generate-batch", action="store_true",
                        help="Generate batch.yaml for Phase 2 validation")
    parser.add_argument("--batch-top", type=int, default=10,
                        help="Candidates per theme in batch (default: 10)")

    args = parser.parse_args()

    if not args.theme and not args.all_themes:
        parser.error("Provide --theme or --all-themes")

    exclude_subs = [s.strip() for s in args.exclude_subreddits.split(",") if s.strip()] or None

    themes = [args.theme] if args.theme else list(load_all_theme_keywords()[0].keys())

    RESULTS_DIR.mkdir(exist_ok=True)
    all_candidates = {}

    for theme in themes:
        print(f"\n{'#'*100}")
        print(f"  DISCOVERING: {theme}")
        print(f"{'#'*100}")

        candidates = discover(
            theme,
            min_posts=args.min_posts,
            min_subs=args.min_subs,
            top_n=args.top_n,
            max_conc=args.max_concentration,
            exclude_subs=exclude_subs,
        )
        all_candidates[theme] = candidates
        print_results(theme, candidates)

        # Save CSV per theme with snippets
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_path = RESULTS_DIR / f"discovery_{theme}_{timestamp}.csv"
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "rank", "ngram", "doc_freq", "base_doc_freq", "smoothed_lift",
                "composite_score", "n_subs", "top_subreddit", "concentration",
                "snippet_1", "snippet_2", "snippet_3",
            ])
            writer.writeheader()
            for i, c in enumerate(candidates, 1):
                sub_name, sub_count = c["top_sub"]
                snippets = c.get("snippets", [])
                while len(snippets) < 3:
                    snippets.append("")
                writer.writerow({
                    "rank": i,
                    "ngram": c["ngram"],
                    "doc_freq": c["doc_freq"],
                    "base_doc_freq": c["base_doc_freq"],
                    "smoothed_lift": f"{c['lift']:.1f}",
                    "composite_score": f"{c['score']:.0f}",
                    "n_subs": c["n_subs"],
                    "top_subreddit": f"{sub_name}({sub_count})",
                    "concentration": f"{c['concentration']:.0%}",
                    "snippet_1": snippets[0],
                    "snippet_2": snippets[1],
                    "snippet_3": snippets[2],
                })

    # Generate batch YAML if requested (top N candidates per theme)
    if args.generate_batch:
        batch_data = []
        for theme, candidates in all_candidates.items():
            for c in candidates[:args.batch_top]:
                batch_data.append({"keyword": c["ngram"], "theme": theme})

        if batch_data:
            batch_path = RESULTS_DIR / f"discovery_batch_{date.today().isoformat()}.yaml"
            with open(batch_path, "w") as f:
                yaml.dump(batch_data, f, default_flow_style=False)
            print(f"\n  Batch YAML: {batch_path} ({len(batch_data)} candidates)")
            print(f"  Next: python prepare_batch.py --batch-file {batch_path} --sample-size 100")
        else:
            print(f"\n  No candidates for batch.")


if __name__ == "__main__":
    main()
