"""Export keyword details for the transparency panel.

Generates web/data/keyword_details.json with per-theme keyword lists,
hit counts, subreddit distributions, and sample post titles.
"""

import json
import re
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
KEYWORDS_PATH = PROJECT_ROOT / "config" / "keywords_v8.yaml"
OUTPUT_PATH = PROJECT_ROOT / "web" / "data" / "keyword_details.json"

# Posts to exclude from samples
EXCLUDED_TITLES = {"[deleted]", "[removed]", "", None}

# Prefer samples from the last 12 months
RECENT_CUTOFF_DAYS = 365


def parse_precision(comment_text: str) -> "float | None":
    """Extract precision percentage from a YAML inline comment like '# 92.0%, 27 hits'."""
    match = re.search(r"(\d+\.?\d*)%", comment_text)
    return float(match.group(1)) if match else None


def parse_keywords_yaml(yaml_path: Path) -> dict:
    """Parse keywords YAML and extract terms with precision scores from comments."""
    raw_text = yaml_path.read_text()
    config = yaml.safe_load(raw_text)

    categories = {}
    for cat in config["keyword_categories"]:
        name = cat["name"]
        terms = []
        for term in cat["terms"]:
            # The term itself (strip quotes if present in YAML)
            clean_term = str(term).strip()

            # Find the line in raw text to extract the inline comment
            precision = None
            for line in raw_text.splitlines():
                # Match YAML term definition lines: "- term" or '- "term"'
                term_pattern = re.escape(clean_term)
                if re.search(
                    rf"^\s*-\s*\"?{term_pattern}\"?\s", line, re.IGNORECASE
                ):
                    # Extract precision from comment portion
                    comment_match = re.search(r"#\s*(.+)", line)
                    if comment_match:
                        precision = parse_precision(comment_match.group(1))
                    break

            terms.append({"term": clean_term, "precision": precision})
        categories[name] = terms

    return categories


def build_keyword_details(db: sqlite3.Connection, categories: dict) -> dict:
    """Build the full keyword_details structure from DB and parsed YAML."""
    result = {}
    recent_date = (datetime.now() - timedelta(days=RECENT_CUTOFF_DAYS)).strftime(
        "%Y-%m-%d"
    )

    for cat_name, terms_info in categories.items():
        # --- Per-keyword stats and samples ---
        keywords = []
        for ti in terms_info:
            term = ti["term"]

            # Total hits for this term in this category
            row = db.execute(
                """SELECT COUNT(DISTINCT post_id)
                   FROM post_keyword_tags
                   WHERE category = ? AND matched_term = ?""",
                (cat_name, term),
            ).fetchone()
            hits = row[0] if row else 0

            if hits == 0:
                # Try case-insensitive match
                row = db.execute(
                    """SELECT COUNT(DISTINCT post_id)
                       FROM post_keyword_tags
                       WHERE category = ? AND LOWER(matched_term) = LOWER(?)""",
                    (cat_name, term),
                ).fetchone()
                hits = row[0] if row else 0

            # Sample 3 recent post titles (exclude SpicyChatAI — mostly promotional)
            sample_posts = db.execute(
                """SELECT DISTINCT p.title, pkt.subreddit, pkt.post_date, p.id
                   FROM post_keyword_tags pkt
                   JOIN posts p ON pkt.post_id = p.id
                   WHERE pkt.category = ? AND LOWER(pkt.matched_term) = LOWER(?)
                     AND p.title IS NOT NULL
                     AND p.title NOT IN ('[deleted]', '[removed]', '')
                     AND pkt.subreddit != 'SpicyChatAI'
                     AND pkt.post_date >= ?
                   ORDER BY pkt.post_date DESC
                   LIMIT 3""",
                (cat_name, term, recent_date),
            ).fetchall()

            # Fall back to older posts if not enough recent ones
            if len(sample_posts) < 3:
                older = db.execute(
                    """SELECT DISTINCT p.title, pkt.subreddit, pkt.post_date, p.id
                       FROM post_keyword_tags pkt
                       JOIN posts p ON pkt.post_id = p.id
                       WHERE pkt.category = ? AND LOWER(pkt.matched_term) = LOWER(?)
                         AND p.title IS NOT NULL
                         AND p.title NOT IN ('[deleted]', '[removed]', '')
                         AND pkt.subreddit != 'SpicyChatAI'
                       ORDER BY pkt.post_date DESC
                       LIMIT ?""",
                    (cat_name, term, 3 - len(sample_posts)),
                ).fetchall()
                existing_titles = {sp[0] for sp in sample_posts}
                for o in older:
                    if o[0] not in existing_titles:
                        sample_posts.append(o)
                    if len(sample_posts) >= 3:
                        break

            keywords.append(
                {
                    "term": term,
                    "hits": hits,
                    "precision": ti["precision"],
                    "sample_posts": [
                        {
                            "title": sp[0],
                            "subreddit": sp[1],
                            "date": sp[2],
                            "id": sp[3],
                        }
                        for sp in sample_posts
                    ],
                }
            )

        # Sort keywords by hit count descending
        keywords.sort(key=lambda k: k["hits"], reverse=True)

        # --- Subreddit distribution ---
        sub_rows = db.execute(
            """SELECT subreddit, COUNT(DISTINCT post_id) as hits
               FROM post_keyword_tags
               WHERE category = ?
               GROUP BY subreddit
               ORDER BY hits DESC""",
            (cat_name,),
        ).fetchall()

        total_hits_from_subs = sum(r[1] for r in sub_rows)

        subreddits = []
        for sub_name, sub_hits in sub_rows:
            pct = (sub_hits / total_hits_from_subs * 100) if total_hits_from_subs else 0
            if pct >= 1.0:  # Only include subs with ≥1% of hits
                subreddits.append(
                    {
                        "name": sub_name,
                        "hits": sub_hits,
                        "pct": round(pct, 1),
                    }
                )

        # --- Category totals ---
        total_row = db.execute(
            "SELECT COUNT(*) FROM post_keyword_tags WHERE category = ?",
            (cat_name,),
        ).fetchone()
        total_hits = total_row[0] if total_row else 0

        unique_row = db.execute(
            "SELECT COUNT(DISTINCT post_id) FROM post_keyword_tags WHERE category = ?",
            (cat_name,),
        ).fetchone()
        unique_posts = unique_row[0] if unique_row else 0

        result[cat_name] = {
            "keywords": keywords,
            "subreddits": subreddits,
            "total_hits": total_hits,
            "unique_posts": unique_posts,
        }

    return result


def main():
    print("Parsing keywords from", KEYWORDS_PATH.name)
    categories = parse_keywords_yaml(KEYWORDS_PATH)
    print(f"  Found {len(categories)} categories:")
    for name, terms in categories.items():
        print(f"    {name}: {len(terms)} terms")

    print("Querying database at", DB_PATH)
    db = sqlite3.connect(str(DB_PATH))

    result = build_keyword_details(db, categories)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(result, f, indent=2)

    size_kb = OUTPUT_PATH.stat().st_size / 1024
    print(f"\nWrote {OUTPUT_PATH} ({size_kb:.1f} KB)")
    for cat, data in result.items():
        print(
            f"  {cat}: {len(data['keywords'])} keywords, "
            f"{data['unique_posts']} unique posts, "
            f"{len(data['subreddits'])} subreddits"
        )

    db.close()


if __name__ == "__main__":
    main()
