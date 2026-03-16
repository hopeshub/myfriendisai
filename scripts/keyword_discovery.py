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

    # Also build a flat set of all terms across all categories
    all_terms = set()
    for terms in existing.values():
        all_terms.update(terms)

    return existing, all_terms


def clean_text(text):
    """Clean a post's text: lowercase, strip URLs, markdown, boilerplate."""
    if not text:
        return ""
    text = text.lower()
    # Strip URLs
    text = re.sub(r'https?://\S+', ' ', text)
    # Strip markdown formatting
    text = re.sub(r'[*_~`#>\[\]()]', ' ', text)
    # Strip Reddit boilerplate
    text = re.sub(r'\b(edit|update|tldr|tl;dr)\s*:?', ' ', text)
    # Collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def tokenize(text):
    """Split into word tokens, removing punctuation-only and number-only tokens."""
    tokens = re.split(r'[\s\-/]+', text)
    # Also split on punctuation boundaries
    refined = []
    for t in tokens:
        # Remove leading/trailing punctuation
        t = re.sub(r'^[^\w]+|[^\w]+$', '', t)
        if t and not re.match(r'^[\d]+$', t) and len(t) > 1:
            refined.append(t)
    return refined


def extract_ngrams(tokens, stop_words):
    """Extract unigrams, bigrams, trigrams from token list."""
    uni = Counter()
    bi = Counter()
    tri = Counter()

    filtered = [t for t in tokens if t not in stop_words]
    uni.update(filtered)

    # Bigrams — at least one non-stopword
    for i in range(len(tokens) - 1):
        if tokens[i] not in stop_words or tokens[i+1] not in stop_words:
            bi[(tokens[i], tokens[i+1])] += 1

    # Trigrams — at least one non-stopword
    for i in range(len(tokens) - 2):
        if (tokens[i] not in stop_words or tokens[i+1] not in stop_words
                or tokens[i+2] not in stop_words):
            tri[(tokens[i], tokens[i+1], tokens[i+2])] += 1

    return uni, bi, tri


def ngram_to_str(ngram):
    """Convert ngram tuple to string."""
    if isinstance(ngram, str):
        return ngram
    return " ".join(ngram)


# ── Main ────────────────────────────────────────────────────────────────

def main():
    print("Loading existing keywords...")
    existing_by_cat, all_existing = load_existing_keywords()

    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # ── Step 1: Build corpora ──────────────────────────────────────────

    print("Building matched corpus per category...")

    # Get matched post IDs per category
    matched_posts_per_cat = {}
    all_matched_ids = set()

    for cat in CATEGORIES:
        cur.execute(
            "SELECT DISTINCT post_id FROM post_keyword_tags WHERE category = ?",
            (cat,)
        )
        ids = [r["post_id"] for r in cur.fetchall()]
        matched_posts_per_cat[cat] = ids
        all_matched_ids.update(ids)
        print(f"  {cat}: {len(ids)} matched posts")

    # Get general corpus (posts not matching any category)
    print(f"Sampling {GENERAL_SAMPLE_SIZE} general (non-matching) posts...")
    # Use a deterministic seed for reproducibility
    placeholders = ",".join("?" * len(all_matched_ids)) if all_matched_ids else "'__none__'"

    # Since all_matched_ids could be large, use a subquery instead
    cur.execute("""
        SELECT id FROM posts
        WHERE id NOT IN (SELECT DISTINCT post_id FROM post_keyword_tags)
        ORDER BY RANDOM()
        LIMIT ?
    """, (GENERAL_SAMPLE_SIZE,))
    general_ids = [r["id"] for r in cur.fetchall()]
    print(f"  General corpus: {len(general_ids)} posts")

    # ── Step 2 & 3: Process each category ──────────────────────────────

    def fetch_post_texts(post_ids):
        """Fetch title + selftext for a list of post IDs, in batches."""
        texts = {}
        for i in range(0, len(post_ids), BATCH_SIZE):
            batch = post_ids[i:i+BATCH_SIZE]
            placeholders = ",".join("?" * len(batch))
            cur.execute(
                f"SELECT id, title, selftext FROM posts WHERE id IN ({placeholders})",
                batch
            )
            for r in cur.fetchall():
                raw = (r["title"] or "") + " " + (r["selftext"] or "")
                texts[r["id"]] = clean_text(raw)
        return texts

    def process_corpus(texts_dict):
        """Tokenize and extract ngrams from a dict of {id: text}. Returns ngram counts + per-post sets."""
        total_uni = Counter()
        total_bi = Counter()
        total_tri = Counter()
        total_tokens = 0
        # Track which posts each ngram appears in
        post_sets_uni = defaultdict(set)
        post_sets_bi = defaultdict(set)
        post_sets_tri = defaultdict(set)

        for pid, text in texts_dict.items():
            tokens = tokenize(text)
            total_tokens += len(tokens)

            uni, bi, tri = extract_ngrams(tokens, STOP_WORDS)

            total_uni += uni
            total_bi += bi
            total_tri += tri

            for u in set(t for t in tokens if t not in STOP_WORDS):
                post_sets_uni[u].add(pid)
            for i in range(len(tokens) - 1):
                if tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS:
                    post_sets_bi[(tokens[i], tokens[i+1])].add(pid)
            for i in range(len(tokens) - 2):
                if (tokens[i] not in STOP_WORDS or tokens[i+1] not in STOP_WORDS
                        or tokens[i+2] not in STOP_WORDS):
                    post_sets_tri[(tokens[i], tokens[i+1], tokens[i+2])].add(pid)

        return {
            "uni": total_uni, "bi": total_bi, "tri": total_tri,
            "total_tokens": total_tokens,
            "post_sets_uni": post_sets_uni,
            "post_sets_bi": post_sets_bi,
            "post_sets_tri": post_sets_tri,
        }

    # Process general corpus once
    print("Processing general corpus...")
    general_texts = fetch_post_texts(general_ids)
    general_data = process_corpus(general_texts)
    print(f"  General corpus tokens: {general_data['total_tokens']:,}")

    # Process each category
    category_results = {}

    for cat in CATEGORIES:
        print(f"\nProcessing category: {cat} ({len(matched_posts_per_cat[cat])} posts)...")
        matched_texts = fetch_post_texts(matched_posts_per_cat[cat])
        matched_data = process_corpus(matched_texts)
        print(f"  Matched tokens: {matched_data['total_tokens']:,}")

        # Calculate overrepresentation for all ngram types
        candidates = []
        existing_terms = existing_by_cat.get(cat, set()) | all_existing

        for ngram_type, label in [("uni", "post_sets_uni"), ("bi", "post_sets_bi"), ("tri", "post_sets_tri")]:
            matched_counts = matched_data[ngram_type]
            general_counts = general_data[ngram_type]
            post_sets = matched_data[label]
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

                unique_posts = len(post_sets.get(ngram if isinstance(ngram, tuple) else ngram, set()))

                # Minimum post threshold
                if unique_posts < MIN_MATCHED_POSTS:
                    continue

                freq_matched = count / matched_total if matched_total > 0 else 0
                general_count = general_counts.get(ngram, 0)
                freq_general = general_count / general_total if general_total > 0 else 0

                # Avoid division by zero — if not in general corpus, treat as very high ratio
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

        # Sort by ratio descending, take top 50
        candidates.sort(key=lambda x: x["ratio"], reverse=True)
        candidates = candidates[:TOP_N]
        category_results[cat] = candidates

        print(f"  Found {len(candidates)} candidates")

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

    # ── Step 6: Sample contexts ────────────────────────────────────────

    print("\nFetching sample contexts for top 20 per category...")
    category_contexts = {}

    for cat in CATEGORIES:
        candidates = category_results[cat][:CONTEXT_TOP_N]
        contexts = {}

        for cand in candidates:
            ngram = cand["ngram"]
            # Search for posts containing this ngram in the matched set
            matched_ids = matched_posts_per_cat[cat]

            # Sample from matched posts
            random.seed(42)  # Reproducible
            sample_ids = random.sample(matched_ids, min(len(matched_ids), 500))

            placeholders = ",".join("?" * len(sample_ids))
            cur.execute(
                f"""SELECT id, title, selftext FROM posts
                    WHERE id IN ({placeholders})""",
                sample_ids
            )

            examples = []
            for r in cur.fetchall():
                text = (r["title"] or "") + " " + (r["selftext"] or "")
                if ngram.lower() in text.lower():
                    excerpt = clean_text(text)[:200]
                    examples.append(excerpt)
                    if len(examples) >= CONTEXT_EXAMPLES:
                        break

            # If we didn't find enough in the sample, search more broadly
            if len(examples) < CONTEXT_EXAMPLES:
                # Use FTS to find more
                try:
                    fts_query = ngram.replace('"', '""')
                    cur.execute(
                        f"""SELECT p.id, p.title, p.selftext FROM posts_fts fts
                            JOIN posts p ON p.id = fts.rowid
                            WHERE posts_fts MATCH ?
                            LIMIT 50""",
                        (f'"{fts_query}"',)
                    )
                    for r in cur.fetchall():
                        if r["id"] in set(matched_ids):
                            text = (r["title"] or "") + " " + (r["selftext"] or "")
                            if ngram.lower() in text.lower():
                                excerpt = clean_text(text)[:200]
                                if excerpt not in examples:
                                    examples.append(excerpt)
                                    if len(examples) >= CONTEXT_EXAMPLES:
                                        break
                except Exception:
                    pass  # FTS might not match all ngrams

            contexts[ngram] = examples

        category_contexts[cat] = contexts

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
                        # Escape markdown pipe characters
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
