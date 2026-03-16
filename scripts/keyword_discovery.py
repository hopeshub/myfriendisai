#!/usr/bin/env python3
"""
Keyword Discovery via Co-occurrence Analysis

Surfaces new keyword candidates by analyzing distinctive words/phrases
in posts that match existing keyword categories vs. general corpus.
Outputs a report for manual review — does NOT modify keywords.yaml or any data.
"""

import sqlite3
import re
import random
import sys
import yaml
from collections import Counter, defaultdict
from pathlib import Path
from datetime import datetime

from nltk.corpus import stopwords

# ── Config ──────────────────────────────────────────────────────────────

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"
KEYWORDS_PATH = Path(__file__).parent.parent / "config" / "keywords_v8.yaml"
REPORT_PATH = Path(__file__).parent.parent / "docs" / "keyword_discovery_report.md"

CATEGORIES = ["therapy", "consciousness", "addiction", "romance", "sexual_erp", "rupture"]
GENERAL_SAMPLE_SIZE = 50_000
TOP_N = 50
MIN_MATCHED_POSTS = 5
MIN_RATIO = 5.0
CONTEXT_TOP_N = 20
CONTEXT_EXAMPLES = 3
BATCH_SIZE = 10_000

STOP_WORDS = set(stopwords.words("english"))
# Add Reddit-specific stopwords
STOP_WORDS.update([
    "like", "really", "would", "could", "also", "one", "get", "got", "even",
    "much", "know", "think", "want", "going", "back", "still", "make", "made",
    "im", "ive", "dont", "doesnt", "didnt", "cant", "thats", "youre",
    "deleted", "removed", "http", "https", "www", "com", "reddit",
    "amp", "nbsp", "edit", "update", "tldr", "tl", "dr",
])

# Precompile regexes
RE_URL = re.compile(r'https?://\S+')
RE_MARKDOWN = re.compile(r'[*_~`#>\[\]()]')
RE_BOILERPLATE = re.compile(r'\b(edit|update|tldr|tl;dr)\s*:?')
RE_WHITESPACE = re.compile(r'\s+')
RE_TOKEN_SPLIT = re.compile(r'[\s\-/]+')
RE_PUNCT_STRIP = re.compile(r'^[^\w]+|[^\w]+$')
RE_DIGITS = re.compile(r'^[\d]+$')


# ── Helpers ─────────────────────────────────────────────────────────────

def load_existing_keywords():
    """Load all terms from keywords_v8.yaml so we can exclude them."""
    with open(KEYWORDS_PATH) as f:
        data = yaml.safe_load(f)

    existing = {}
    for cat in data["keyword_categories"]:
        terms = set()
        for term in cat["terms"]:
            t = term.lower().strip('"').strip("'")
            terms.add(t)
        existing[cat["name"]] = terms

    all_terms = set()
    for terms in existing.values():
        all_terms.update(terms)

    return existing, all_terms


def clean_text(text):
    """Clean a post's text: lowercase, strip URLs, markdown, boilerplate."""
    if not text:
        return ""
    text = text.lower()
    text = RE_URL.sub(' ', text)
    text = RE_MARKDOWN.sub(' ', text)
    text = RE_BOILERPLATE.sub(' ', text)
    text = RE_WHITESPACE.sub(' ', text).strip()
    return text


def tokenize(text):
    """Split into word tokens, removing punctuation-only and number-only tokens."""
    tokens = RE_TOKEN_SPLIT.split(text)
    refined = []
    for t in tokens:
        t = RE_PUNCT_STRIP.sub('', t)
        if t and not RE_DIGITS.match(t) and len(t) > 1:
            refined.append(t)
    return refined


def ngram_to_str(ngram):
    if isinstance(ngram, str):
        return ngram
    return " ".join(ngram)


def process_corpus_counts_only(conn, post_ids, label=""):
    """Process a corpus returning only ngram counts (no per-post tracking).
    Processes in batches to limit memory. Used for general corpus."""
    total_uni = Counter()
    total_bi = Counter()
    total_tri = Counter()
    total_tokens = 0
    cur = conn.cursor()

    for batch_start in range(0, len(post_ids), BATCH_SIZE):
        batch = post_ids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        cur.execute(
            f"SELECT title, selftext FROM posts WHERE id IN ({placeholders})",
            batch
        )
        for row in cur.fetchall():
            raw = (row[0] or "") + " " + (row[1] or "")
            text = clean_text(raw)
            tokens = tokenize(text)
            total_tokens += len(tokens)

            # Unigrams
            filtered = [t for t in tokens if t not in STOP_WORDS]
            for t in filtered:
                total_uni[t] += 1

            # Bigrams
            for i in range(len(tokens) - 1):
                if tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS:
                    total_bi[(tokens[i], tokens[i+1])] += 1

            # Trigrams
            for i in range(len(tokens) - 2):
                if (tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS
                        or tokens[i+2] not in STOP_WORDS):
                    total_tri[(tokens[i], tokens[i+1], tokens[i+2])] += 1

        done = min(batch_start + BATCH_SIZE, len(post_ids))
        print(f"  {label} processed {done:,}/{len(post_ids):,} posts, {total_tokens:,} tokens so far")

    return {"uni": total_uni, "bi": total_bi, "tri": total_tri, "total_tokens": total_tokens}


def process_matched_corpus(conn, post_ids):
    """Process matched corpus — returns counts AND per-post sets for unique post counting."""
    total_uni = Counter()
    total_bi = Counter()
    total_tri = Counter()
    total_tokens = 0
    post_sets_uni = defaultdict(set)
    post_sets_bi = defaultdict(set)
    post_sets_tri = defaultdict(set)
    cur = conn.cursor()

    for batch_start in range(0, len(post_ids), BATCH_SIZE):
        batch = post_ids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        cur.execute(
            f"SELECT id, title, selftext FROM posts WHERE id IN ({placeholders})",
            batch
        )
        for row in cur.fetchall():
            pid = row[0]
            raw = (row[1] or "") + " " + (row[2] or "")
            text = clean_text(raw)
            tokens = tokenize(text)
            total_tokens += len(tokens)

            # Unigrams
            seen_uni = set()
            for t in tokens:
                if t not in STOP_WORDS:
                    total_uni[t] += 1
                    if t not in seen_uni:
                        post_sets_uni[t].add(pid)
                        seen_uni.add(t)

            # Bigrams
            seen_bi = set()
            for i in range(len(tokens) - 1):
                if tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS:
                    bg = (tokens[i], tokens[i+1])
                    total_bi[bg] += 1
                    if bg not in seen_bi:
                        post_sets_bi[bg].add(pid)
                        seen_bi.add(bg)

            # Trigrams
            seen_tri = set()
            for i in range(len(tokens) - 2):
                if (tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS
                        or tokens[i+2] not in STOP_WORDS):
                    tg = (tokens[i], tokens[i+1], tokens[i+2])
                    total_tri[tg] += 1
                    if tg not in seen_tri:
                        post_sets_tri[tg].add(pid)
                        seen_tri.add(tg)

    return {
        "uni": total_uni, "bi": total_bi, "tri": total_tri,
        "total_tokens": total_tokens,
        "post_sets_uni": post_sets_uni,
        "post_sets_bi": post_sets_bi,
        "post_sets_tri": post_sets_tri,
    }


# ── Main ────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("Keyword Discovery — Co-occurrence Analysis")
    print("=" * 60)
    sys.stdout.flush()

    print("\nLoading existing keywords...")
    existing_by_cat, all_existing = load_existing_keywords()
    print(f"  {len(all_existing)} existing keywords across {len(existing_by_cat)} categories")

    conn = sqlite3.connect(str(DB_PATH))
    cur = conn.cursor()

    # ── Step 1: Build corpora ──────────────────────────────────────────

    print("\nBuilding matched corpus per category...")
    sys.stdout.flush()

    matched_posts_per_cat = {}
    all_matched_ids = set()

    for cat in CATEGORIES:
        cur.execute(
            "SELECT DISTINCT post_id FROM post_keyword_tags WHERE category = ?",
            (cat,)
        )
        ids = [r[0] for r in cur.fetchall()]
        matched_posts_per_cat[cat] = ids
        all_matched_ids.update(ids)
        print(f"  {cat}: {len(ids)} matched posts")

    # Sample general corpus efficiently — use rowid sampling instead of ORDER BY RANDOM()
    print(f"\nSampling {GENERAL_SAMPLE_SIZE:,} general (non-matching) posts...")
    sys.stdout.flush()

    # Get total post count and min/max rowid for efficient sampling
    cur.execute("SELECT MIN(rowid), MAX(rowid), COUNT(*) FROM posts")
    min_rowid, max_rowid, total_posts = cur.fetchone()
    print(f"  Total posts: {total_posts:,}, rowid range: {min_rowid}-{max_rowid}")

    # Generate random rowids, oversample to account for gaps and matched-post exclusions
    random.seed(42)
    oversample = int(GENERAL_SAMPLE_SIZE * 1.5)
    candidate_rowids = random.sample(range(min_rowid, max_rowid + 1), min(oversample, max_rowid - min_rowid + 1))

    # Fetch IDs for these rowids, excluding matched posts
    general_ids = []
    for batch_start in range(0, len(candidate_rowids), BATCH_SIZE):
        batch = candidate_rowids[batch_start:batch_start + BATCH_SIZE]
        placeholders = ",".join("?" * len(batch))
        cur.execute(
            f"SELECT id FROM posts WHERE rowid IN ({placeholders})",
            batch
        )
        for r in cur.fetchall():
            if r[0] not in all_matched_ids:
                general_ids.append(r[0])
                if len(general_ids) >= GENERAL_SAMPLE_SIZE:
                    break
        if len(general_ids) >= GENERAL_SAMPLE_SIZE:
            break

    general_ids = general_ids[:GENERAL_SAMPLE_SIZE]
    print(f"  General corpus: {len(general_ids):,} posts")
    sys.stdout.flush()

    # ── Step 2 & 3: Process corpora ────────────────────────────────────

    print("\nProcessing general corpus...")
    sys.stdout.flush()
    general_data = process_corpus_counts_only(conn, general_ids, label="General")
    print(f"  General corpus: {general_data['total_tokens']:,} tokens")
    sys.stdout.flush()

    # Process each category
    category_results = {}

    for cat in CATEGORIES:
        n_posts = len(matched_posts_per_cat[cat])
        print(f"\nProcessing category: {cat} ({n_posts} posts)...")
        sys.stdout.flush()
        matched_data = process_matched_corpus(conn, matched_posts_per_cat[cat])
        print(f"  Matched tokens: {matched_data['total_tokens']:,}")

        # Calculate overrepresentation for all ngram types
        candidates = []
        existing_terms = existing_by_cat.get(cat, set()) | all_existing

        for ngram_type, ps_key in [("uni", "post_sets_uni"), ("bi", "post_sets_bi"), ("tri", "post_sets_tri")]:
            matched_counts = matched_data[ngram_type]
            general_counts = general_data[ngram_type]
            post_sets = matched_data[ps_key]
            matched_total = matched_data["total_tokens"]
            general_total = general_data["total_tokens"]

            for ngram, count in matched_counts.items():
                ngram_str = ngram_to_str(ngram)

                # Skip existing keywords
                if ngram_str in existing_terms:
                    continue

                # Skip very short unigrams
                if isinstance(ngram, str) and len(ngram) <= 2:
                    continue

                unique_posts = len(post_sets.get(ngram, set()))

                if unique_posts < MIN_MATCHED_POSTS:
                    continue

                freq_matched = count / matched_total if matched_total > 0 else 0
                general_count = general_counts.get(ngram, 0)
                freq_general = general_count / general_total if general_total > 0 else 0

                if freq_general == 0:
                    if count >= MIN_MATCHED_POSTS:
                        ratio = 999.0
                    else:
                        continue
                else:
                    ratio = freq_matched / freq_general

                if ratio < MIN_RATIO:
                    continue

                candidates.append({
                    "ngram": ngram_str,
                    "matched_count": count,
                    "general_count": general_count,
                    "ratio": ratio,
                    "unique_posts": unique_posts,
                })

        candidates.sort(key=lambda x: x["ratio"], reverse=True)
        candidates = candidates[:TOP_N]
        category_results[cat] = candidates
        print(f"  Found {len(candidates)} candidates")
        sys.stdout.flush()

    # ── Step 5: Cross-category check ───────────────────────────────────

    print("\nCross-category analysis...")
    ngram_categories = defaultdict(set)
    for cat, candidates in category_results.items():
        for c in candidates:
            ngram_categories[c["ngram"]].add(cat)

    cross_category = {
        ngram: cats for ngram, cats in ngram_categories.items() if len(cats) > 1
    }
    print(f"  {len(cross_category)} n-grams appear in multiple categories")
    sys.stdout.flush()

    # ── Step 6: Sample contexts ────────────────────────────────────────

    print("\nFetching sample contexts for top 20 per category...")
    sys.stdout.flush()
    category_contexts = {}

    for cat in CATEGORIES:
        candidates = category_results[cat][:CONTEXT_TOP_N]
        contexts = {}

        # Pre-fetch a sample of matched post texts for this category
        matched_ids = matched_posts_per_cat[cat]
        random.seed(42)
        sample_size = min(len(matched_ids), 2000)
        sample_ids = random.sample(matched_ids, sample_size)

        # Fetch texts for sample
        sample_texts = {}
        for batch_start in range(0, len(sample_ids), BATCH_SIZE):
            batch = sample_ids[batch_start:batch_start + BATCH_SIZE]
            placeholders = ",".join("?" * len(batch))
            cur.execute(
                f"SELECT id, title, selftext FROM posts WHERE id IN ({placeholders})",
                batch
            )
            for r in cur.fetchall():
                raw = (r[1] or "") + " " + (r[2] or "")
                sample_texts[r[0]] = raw

        for cand in candidates:
            ngram = cand["ngram"]
            examples = []

            # Search in pre-fetched sample
            for pid, text in sample_texts.items():
                if ngram.lower() in text.lower():
                    excerpt = clean_text(text)[:200]
                    examples.append(excerpt)
                    if len(examples) >= CONTEXT_EXAMPLES:
                        break

            # If not enough, try FTS
            if len(examples) < CONTEXT_EXAMPLES:
                try:
                    matched_set = set(matched_ids)
                    fts_query = ngram.replace('"', '""')
                    cur.execute(
                        """SELECT p.id, p.title, p.selftext FROM posts_fts fts
                           JOIN posts p ON p.rowid = fts.rowid
                           WHERE posts_fts MATCH ?
                           LIMIT 100""",
                        (f'"{fts_query}"',)
                    )
                    for r in cur.fetchall():
                        if r[0] in matched_set:
                            text = (r[1] or "") + " " + (r[2] or "")
                            if ngram.lower() in text.lower():
                                excerpt = clean_text(text)[:200]
                                if excerpt not in examples:
                                    examples.append(excerpt)
                                    if len(examples) >= CONTEXT_EXAMPLES:
                                        break
                except Exception:
                    pass

            contexts[ngram] = examples

        category_contexts[cat] = contexts
        print(f"  {cat}: contexts fetched for {len(contexts)} candidates")
        sys.stdout.flush()

    # ── Output report ──────────────────────────────────────────────────

    print("\nWriting report...")

    total_matched = sum(len(ids) for ids in matched_posts_per_cat.values())

    lines = []
    lines.append("# Keyword Discovery Report — Co-occurrence Analysis\n")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"Matched corpus: {total_matched:,} posts across 6 categories")
    lines.append(f"General corpus: {len(general_ids):,} randomly sampled non-matching posts")
    lines.append(f"Minimum thresholds: {MIN_MATCHED_POSTS} matched posts, {MIN_RATIO}x overrepresentation ratio")
    lines.append("")

    for cat in CATEGORIES:
        existing_terms = sorted(existing_by_cat.get(cat, []))
        candidates = category_results[cat]

        lines.append(f"## Category: {cat}\n")
        lines.append(f"### Existing keywords: {', '.join(existing_terms)}\n")
        lines.append(f"Matched posts in category: {len(matched_posts_per_cat[cat]):,}\n")
        lines.append("### Top 50 candidates\n")

        if not candidates:
            lines.append("*No candidates met the threshold criteria.*\n")
        else:
            lines.append("| Rank | N-gram | Matched posts | General posts | Ratio | Unique matched posts |")
            lines.append("|------|--------|--------------|---------------|-------|---------------------|")
            for i, c in enumerate(candidates, 1):
                ratio_str = f"{c['ratio']:.1f}x" if c['ratio'] < 999 else "∞ (0 in general)"
                lines.append(
                    f"| {i} | {c['ngram']} | {c['matched_count']} | "
                    f"{c['general_count']} | {ratio_str} | {c['unique_posts']} |"
                )
            lines.append("")

        # Sample contexts for top 20
        contexts = category_contexts.get(cat, {})
        if contexts:
            lines.append("### Top 20 — sample contexts\n")
            for i, cand in enumerate(candidates[:CONTEXT_TOP_N], 1):
                ngram = cand["ngram"]
                examples = contexts.get(ngram, [])
                lines.append(f'#### {i}. "{ngram}"\n')
                if examples:
                    for ex in examples:
                        ex_clean = ex.replace("|", "\\|")
                        lines.append(f'- "{ex_clean}"')
                else:
                    lines.append("- *(no context examples found in sample)*")
                lines.append("")

    # Cross-category section
    lines.append("## Cross-category candidates\n")
    if cross_category:
        lines.append("N-grams appearing in multiple categories' top 50 lists:\n")
        lines.append("| N-gram | Categories |")
        lines.append("|--------|-----------|")
        for ngram, cats in sorted(cross_category.items(), key=lambda x: len(x[1]), reverse=True):
            lines.append(f"| {ngram} | {', '.join(sorted(cats))} |")
    else:
        lines.append("*No n-grams appeared in multiple categories' top 50 lists.*")
    lines.append("")

    report = "\n".join(lines)
    REPORT_PATH.write_text(report)
    print(f"\nReport written to {REPORT_PATH}")
    print(f"Total candidates across all categories: {sum(len(v) for v in category_results.values())}")

    conn.close()


if __name__ == "__main__":
    main()
