"""Export keyword details for the transparency panel.

Generates web/data/keyword_details.json with per-theme keyword lists,
hit counts, subreddit distributions, and sample post titles.
"""

import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta
from pathlib import Path

import yaml

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.config import load_keyword_communities

DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
KEYWORDS_PATH = PROJECT_ROOT / "config" / "keywords_v8.yaml"
OUTPUT_PATH = PROJECT_ROOT / "web" / "data" / "keyword_details.json"

# Posts to exclude from samples
EXCLUDED_TITLES = {"[deleted]", "[removed]", "", None}

# Prefer samples from the last 12 months
RECENT_CUTOFF_DAYS = 365

# How many sample posts to export per keyword. Generous so the theme pages can
# show an abundance of real examples.
SAMPLE_LIMIT = 12


def make_excerpt(term: str, selftext, width: int = 150) -> "str | None":
    """A short snippet of the post body around the first occurrence of `term`.

    Returns None when the body is empty or does not contain the term (e.g. the
    keyword matched the post title instead). The theme page shows this excerpt
    so a body-matched example still visibly shows why it was tagged.
    """
    if not selftext:
        return None
    body = str(selftext)
    # Strip markdown links to their text and bare URLs, so an excerpt never
    # lands in the middle of a URL.
    body = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", body)
    body = re.sub(r"https?://\S+", "", body)
    body = re.sub(r"\bwww\.\S+", "", body)
    body = " ".join(body.split())
    if not body:
        return None
    idx = body.lower().find(term.lower())
    if idx == -1:
        return None
    pad = max(0, (width - len(term)) // 2)
    start = max(0, idx - pad)
    end = min(len(body), idx + len(term) + pad)
    snippet = body[start:end].strip()
    if start > 0:
        snippet = "…" + snippet
    if end < len(body):
        snippet = snippet + "…"
    return snippet


def parse_precision(comment_text: str) -> "float | None":
    """Extract the keyword's current precision from a YAML inline comment.

    A comment may chain several figures, e.g.
        "73.0% -> 86.9% (2026-04-23) -> audit 60% (2026-05-12)."
    Two distinct metrics appear: keyword *precision* (the share of matched
    posts that are on-theme) and *audit agreement* (independent second-coder
    agreement on a 20-post subsample) — a lower audit number does not lower
    the precision. The badge shows precision, so audit-agreement figures are
    stripped first; of the remaining precision figures the last one is taken,
    since the comments are written chronologically (oldest -> newest).
    """
    # Drop audit-agreement figures: "audit [agreement] NN%" and "NN% audit ...".
    stripped = re.sub(
        r"audit[- ]?(?:agreement)?\s*\d+\.?\d*%", "", comment_text, flags=re.IGNORECASE
    )
    stripped = re.sub(r"\d+\.?\d*%\s*audit", "", stripped, flags=re.IGNORECASE)
    figures = re.findall(r"(\d+\.?\d*)%", stripped)
    return float(figures[-1]) if figures else None


def detect_status(annotation_block: str) -> "str | None":
    """Classify a keyword from its YAML annotation block into one display
    status, or None for a clean (>=80%, audit-passing) keyword.

    Mirrors the discipline check in
    analysis/keyword_pipeline/audit_keyword_status.py — keep the two in sync.
    """
    lower = annotation_block.lower()
    # "fail\b" so the plural "audit-gate failures" — a batch note about *other*
    # keywords — is not mistaken for this keyword's own status.
    if re.search(r"audit-gate fail\b", lower):
        return "audit-gate-fail"
    if "researcher-accepted" in lower or "researcher accepted" in lower:
        return "researcher-accepted"
    if "LOW VOLUME" in annotation_block or (
        "low volume" in lower and "placeholder" in lower
    ):
        return "low-volume"
    return None


def parse_keyword_annotation(raw_lines: list, clean_term: str) -> tuple:
    """Locate a keyword's YAML definition line and return (precision, status).

    Reads the inline comment on the definition line plus any continuation
    comment lines below it, so a status note on a wrapped comment is still
    seen.
    """
    term_pattern = re.escape(clean_term)
    for i, line in enumerate(raw_lines):
        # Match YAML term definition lines: "- term" or '- "term"'
        if not re.search(
            rf"^\s*-\s*\"?{term_pattern}\"?\s*(#|$)", line, re.IGNORECASE
        ):
            continue
        # Definition line + following continuation comment lines. A genuine
        # continuation is indented deeper than the keyword's "-" (its "#"
        # aligns under the inline comment); a section or batch comment sits at
        # list-item indent, so the indent test keeps those out of the block.
        def_indent = len(line) - len(line.lstrip())
        block = [line]
        for j in range(i + 1, min(i + 12, len(raw_lines))):
            cont = raw_lines[j]
            cont_indent = len(cont) - len(cont.lstrip())
            if cont.lstrip().startswith("#") and cont_indent > def_indent:
                block.append(cont)
            else:
                break
        comment_match = re.search(r"#\s*(.+)", line)
        precision = (
            parse_precision(comment_match.group(1)) if comment_match else None
        )
        return precision, detect_status("\n".join(block))
    return None, None


def parse_keywords_yaml(yaml_path: Path) -> dict:
    """Parse keywords YAML and extract per-term precision and display status."""
    raw_text = yaml_path.read_text()
    config = yaml.safe_load(raw_text)
    raw_lines = raw_text.splitlines()

    categories = {}
    for cat in config["keyword_categories"]:
        name = cat["name"]
        terms = []
        for term in cat["terms"]:
            # The term itself (strip quotes if present in YAML)
            clean_term = str(term).strip()
            precision, status = parse_keyword_annotation(raw_lines, clean_term)
            terms.append(
                {"term": clean_term, "precision": precision, "status": status}
            )
        categories[name] = terms

    return categories


def build_keyword_details(
    db: sqlite3.Connection, categories: dict, included_subs: list
) -> dict:
    """Build the full keyword_details structure from DB and parsed YAML.

    `included_subs` is the keyword-eligible community list (T1-T3 with
    exclude_from_keywords honored). Every count and sample query is filtered
    to these subreddits so the transparency panel matches the theme lines —
    otherwise excluded subs (e.g. r/ChatGPTNSFW) leak into the per-theme totals.
    Counts are also restricted to post-text matches (`source = 'post'`), so the
    panel describes the same post-only metric the published chart shows rather
    than mixing in comment-sourced tags.
    """
    result = {}
    recent_date = (datetime.now() - timedelta(days=RECENT_CUTOFF_DAYS)).strftime(
        "%Y-%m-%d"
    )
    # Case-insensitive subreddit allowlist for the WHERE ... IN clauses.
    sub_params = tuple(s.lower() for s in included_subs)
    sub_ph = ",".join("?" for _ in sub_params)

    for cat_name, terms_info in categories.items():
        # --- Per-keyword stats and samples ---
        keywords = []
        for ti in terms_info:
            term = ti["term"]

            # Total hits for this term in this category (keyword-eligible subs only)
            row = db.execute(
                f"""SELECT COUNT(DISTINCT post_id)
                   FROM post_keyword_tags
                   WHERE category = ? AND matched_term = ?
                     AND source = 'post'
                     AND LOWER(subreddit) IN ({sub_ph})""",
                (cat_name, term, *sub_params),
            ).fetchone()
            hits = row[0] if row else 0

            if hits == 0:
                # Try case-insensitive match
                row = db.execute(
                    f"""SELECT COUNT(DISTINCT post_id)
                       FROM post_keyword_tags
                       WHERE category = ? AND LOWER(matched_term) = LOWER(?)
                         AND source = 'post'
                         AND LOWER(subreddit) IN ({sub_ph})""",
                    (cat_name, term, *sub_params),
                ).fetchone()
                hits = row[0] if row else 0

            # Sample recent posts (keyword-eligible subs only)
            sample_posts = db.execute(
                f"""SELECT DISTINCT p.title, pkt.subreddit, pkt.post_date, p.id,
                          p.selftext
                   FROM post_keyword_tags pkt
                   JOIN posts p ON pkt.post_id = p.id
                   WHERE pkt.category = ? AND LOWER(pkt.matched_term) = LOWER(?)
                     AND pkt.source = 'post'
                     AND p.title IS NOT NULL
                     AND p.title NOT IN ('[deleted]', '[removed]', '')
                     AND LOWER(pkt.subreddit) IN ({sub_ph})
                     AND pkt.post_date >= ?
                   ORDER BY pkt.post_date DESC
                   LIMIT ?""",
                (cat_name, term, *sub_params, recent_date, SAMPLE_LIMIT),
            ).fetchall()

            # Fall back to older posts if not enough recent ones
            if len(sample_posts) < SAMPLE_LIMIT:
                older = db.execute(
                    f"""SELECT DISTINCT p.title, pkt.subreddit, pkt.post_date, p.id,
                              p.selftext
                       FROM post_keyword_tags pkt
                       JOIN posts p ON pkt.post_id = p.id
                       WHERE pkt.category = ? AND LOWER(pkt.matched_term) = LOWER(?)
                         AND pkt.source = 'post'
                         AND p.title IS NOT NULL
                         AND p.title NOT IN ('[deleted]', '[removed]', '')
                         AND LOWER(pkt.subreddit) IN ({sub_ph})
                       ORDER BY pkt.post_date DESC
                       LIMIT ?""",
                    (cat_name, term, *sub_params, SAMPLE_LIMIT - len(sample_posts)),
                ).fetchall()
                existing_titles = {sp[0] for sp in sample_posts}
                for o in older:
                    if o[0] not in existing_titles:
                        sample_posts.append(o)
                    if len(sample_posts) >= SAMPLE_LIMIT:
                        break

            keywords.append(
                {
                    "term": term,
                    "hits": hits,
                    "precision": ti["precision"],
                    "status": ti["status"],
                    "sample_posts": [
                        {
                            "title": sp[0],
                            "subreddit": sp[1],
                            "date": sp[2],
                            "id": sp[3],
                            "excerpt": make_excerpt(term, sp[4]),
                        }
                        for sp in sample_posts
                    ],
                }
            )

        # Sort keywords by hit count descending
        keywords.sort(key=lambda k: k["hits"], reverse=True)

        # --- Subreddit distribution (keyword-eligible subs only) ---
        sub_rows = db.execute(
            f"""SELECT subreddit, COUNT(DISTINCT post_id) as hits
               FROM post_keyword_tags
               WHERE category = ?
                 AND source = 'post'
                 AND LOWER(subreddit) IN ({sub_ph})
               GROUP BY subreddit
               ORDER BY hits DESC""",
            (cat_name, *sub_params),
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

        # --- Category totals (keyword-eligible subs only) ---
        total_row = db.execute(
            f"SELECT COUNT(*) FROM post_keyword_tags "
            f"WHERE category = ? AND source = 'post' "
            f"AND LOWER(subreddit) IN ({sub_ph})",
            (cat_name, *sub_params),
        ).fetchone()
        total_hits = total_row[0] if total_row else 0

        unique_row = db.execute(
            f"SELECT COUNT(DISTINCT post_id) FROM post_keyword_tags "
            f"WHERE category = ? AND source = 'post' "
            f"AND LOWER(subreddit) IN ({sub_ph})",
            (cat_name, *sub_params),
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

    included_subs = [c["subreddit"] for c in load_keyword_communities()]
    print(f"  {len(included_subs)} keyword-eligible subreddits "
          f"(exclude_from_keywords honored)")

    print("Querying database at", DB_PATH)
    db = sqlite3.connect(str(DB_PATH), timeout=60.0)

    result = build_keyword_details(db, categories, included_subs)

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
