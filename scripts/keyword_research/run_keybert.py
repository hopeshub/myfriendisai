#!/usr/bin/env python3
"""Extract top keyphrases from companion post sample using KeyBERT.

Reads docs/keyword_research_sample.txt, runs KeyBERT with sentence-transformers
to find the most distinctive 2-5 word phrases, and saves ranked results.

Usage:
    python scripts/keyword_research/run_keybert.py
"""

import re
import logging
from collections import Counter
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

SAMPLE_FILE = Path("docs/keyword_research_sample.txt")
OUTPUT_FILE = Path("docs/keybert_results.txt")
TOP_N = 200


def parse_posts(path: Path) -> list[str]:
    """Parse the sample file into individual post texts (title + body)."""
    text = path.read_text()
    # Split on the [NNNN] pattern
    blocks = re.split(r"\n\[\d{4}\] r/\w+\n", text)
    posts = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Remove TITLE: and BODY: prefixes, join into one string
        cleaned = block.replace("TITLE: ", "").replace("BODY:  ", " ").strip()
        if len(cleaned) > 50:
            posts.append(cleaned)
    return posts


def main():
    logger.info("Parsing posts from %s", SAMPLE_FILE)
    posts = parse_posts(SAMPLE_FILE)
    logger.info("Parsed %d posts", len(posts))

    logger.info("Loading KeyBERT model (all-MiniLM-L6-v2)...")
    from keybert import KeyBERT
    kw_model = KeyBERT(model="all-MiniLM-L6-v2")

    # Extract keyphrases per post in batches, then aggregate
    # KeyBERT works best per-document, but 5000 docs is slow one-by-one
    # Strategy: process in chunks of 500, extract top 10 per chunk, aggregate
    CHUNK_SIZE = 500
    all_phrases: Counter = Counter()

    chunks = [posts[i:i + CHUNK_SIZE] for i in range(0, len(posts), CHUNK_SIZE)]
    logger.info("Processing %d chunks of ~%d posts each...", len(chunks), CHUNK_SIZE)

    for i, chunk in enumerate(chunks):
        logger.info("  Chunk %d/%d (%d posts)", i + 1, len(chunks), len(chunk))
        # Join chunk into one document for faster extraction
        combined = "\n\n".join(chunk)
        keywords = kw_model.extract_keywords(
            combined,
            keyphrase_ngram_range=(2, 5),
            stop_words="english",
            top_n=100,
            use_mmr=True,       # Maximal Marginal Relevance for diversity
            diversity=0.5,
        )
        for phrase, score in keywords:
            all_phrases[phrase] += 1
            # Also store max score seen
            score_key = f"_score_{phrase}"
            if score_key not in all_phrases or score > all_phrases[score_key]:
                all_phrases[score_key] = score

    # Also run on individual posts for per-post phrase frequency
    logger.info("Running per-post extraction on %d posts (top 5 per post)...", len(posts))
    post_phrase_counts: Counter = Counter()

    # Process in batches for progress logging
    for i, post in enumerate(posts):
        if i % 500 == 0 and i > 0:
            logger.info("  Post %d/%d", i, len(posts))
        try:
            keywords = kw_model.extract_keywords(
                post,
                keyphrase_ngram_range=(2, 5),
                stop_words="english",
                top_n=5,
                use_mmr=True,
                diversity=0.3,
            )
            for phrase, score in keywords:
                post_phrase_counts[phrase] += 1
        except Exception:
            continue

    # Merge: rank by post_phrase_counts (how many posts surfaced this phrase)
    # Filter to phrases that appeared in at least 3 posts
    ranked = [
        (phrase, count)
        for phrase, count in post_phrase_counts.most_common()
        if count >= 3 and len(phrase.split()) >= 2
    ][:TOP_N]

    # Write output
    lines = []
    lines.append(f"{'=' * 70}")
    lines.append(f"KEYBERT RESULTS — Top {len(ranked)} phrases from {len(posts)} posts")
    lines.append(f"Model: all-MiniLM-L6-v2 | n-gram range: 2-5 | MMR diversity: 0.3")
    lines.append(f"{'=' * 70}")
    lines.append("")
    lines.append(f"{'Rank':<6} {'Posts':<8} {'Phrase'}")
    lines.append(f"{'-'*5:<6} {'-'*5:<8} {'-'*40}")

    for rank, (phrase, count) in enumerate(ranked, 1):
        lines.append(f"{rank:<6} {count:<8} {phrase}")

    OUTPUT_FILE.write_text("\n".join(lines))
    logger.info("Saved %d phrases to %s", len(ranked), OUTPUT_FILE)

    # Print top 30 to stdout
    print(f"\nTop 30 phrases (of {len(ranked)}):\n")
    for phrase, count in ranked[:30]:
        print(f"  {count:>4} posts  {phrase}")


if __name__ == "__main__":
    main()
