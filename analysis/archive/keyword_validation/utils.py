"""Shared utilities for keyword validation scripts."""

import re
import sqlite3
import yaml
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
KEYWORDS_PATH = PROJECT_ROOT / "config" / "keywords_v8.yaml"

# Import keyword-eligible subs from project config
import sys
sys.path.insert(0, str(PROJECT_ROOT))
from src.config import load_keyword_communities, load_keywords

# Keyword-eligible subreddits (T1-T3, excl JanitorAI/SillyTavern)
KW_SUBS = [c["subreddit"] for c in load_keyword_communities()]
SUB_PLACEHOLDERS = ",".join(f"'{s}'" for s in KW_SUBS)

# Stopwords: standard English + Reddit junk
STOPWORDS = {
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your",
    "yours", "yourself", "yourselves", "he", "him", "his", "himself", "she", "her",
    "hers", "herself", "it", "its", "itself", "they", "them", "their", "theirs",
    "themselves", "what", "which", "who", "whom", "this", "that", "these", "those",
    "am", "is", "are", "was", "were", "be", "been", "being", "have", "has", "had",
    "having", "do", "does", "did", "doing", "a", "an", "the", "and", "but", "if",
    "or", "because", "as", "until", "while", "of", "at", "by", "for", "with",
    "about", "against", "between", "through", "during", "before", "after", "above",
    "below", "to", "from", "up", "down", "in", "out", "on", "off", "over", "under",
    "again", "further", "then", "once", "here", "there", "when", "where", "why",
    "how", "all", "both", "each", "few", "more", "most", "other", "some", "such",
    "no", "nor", "not", "only", "own", "same", "so", "than", "too", "very", "s",
    "t", "can", "will", "just", "don", "should", "now", "d", "ll", "m", "o", "re",
    "ve", "y", "ain", "aren", "couldn", "didn", "doesn", "hadn", "hasn", "haven",
    "isn", "ma", "mightn", "mustn", "needn", "shan", "shouldn", "wasn", "weren",
    "won", "wouldn",
    # Common informal
    "like", "really", "would", "could", "also", "one", "get", "got", "even",
    "much", "know", "think", "want", "going", "back", "still", "make", "made",
    "im", "ive", "dont", "doesnt", "didnt", "cant", "thats", "youre",
    # Reddit-specific
    "http", "https", "www", "com", "removed", "deleted", "edit", "update",
    "reddit", "subreddit", "amp", "nbsp", "tldr",
}

# Precompiled regexes for text cleaning
RE_URL = re.compile(r'https?://\S+')
RE_MARKDOWN = re.compile(r'[*_~`#>\[\]()]')
RE_BOILERPLATE = re.compile(r'\b(edit|update|tldr|tl;dr)\s*:?', re.IGNORECASE)
RE_WHITESPACE = re.compile(r'\s+')
RE_TOKEN_SPLIT = re.compile(r'[\s\-/]+')
RE_PUNCT_STRIP = re.compile(r'^[^\w]+|[^\w]+$')
RE_DIGITS = re.compile(r'^[\d]+$')


def get_conn():
    """Get a SQLite connection to the tracker database."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def load_all_theme_keywords():
    """Load all theme keyword lists from keywords_v8.yaml.

    Returns:
        dict: {theme_name: [term1, term2, ...]}
        set: all terms across all themes (lowercased)
    """
    categories = load_keywords()
    by_theme = {}
    all_terms = set()
    for cat in categories:
        terms = [t.lower().strip('"').strip("'") for t in cat["terms"]]
        by_theme[cat["name"]] = terms
        all_terms.update(terms)
    return by_theme, all_terms


def clean_text(text):
    """Clean post text: lowercase, strip URLs, markdown, boilerplate."""
    if not text:
        return ""
    text = text.lower()
    text = RE_URL.sub(' ', text)
    text = RE_MARKDOWN.sub(' ', text)
    text = RE_BOILERPLATE.sub(' ', text)
    text = RE_WHITESPACE.sub(' ', text).strip()
    return text


def tokenize(text):
    """Split cleaned text into word tokens, removing punctuation-only and number-only."""
    tokens = RE_TOKEN_SPLIT.split(text)
    refined = []
    for t in tokens:
        t = RE_PUNCT_STRIP.sub('', t)
        if t and not RE_DIGITS.match(t) and len(t) > 1:
            refined.append(t)
    return refined


def extract_ngrams(tokens, n=2, filter_stopwords=True):
    """Extract n-grams from token list. Returns Counter-compatible list of tuples."""
    ngrams = []
    for i in range(len(tokens) - n + 1):
        gram = tuple(tokens[i:i + n])
        if filter_stopwords and all(t in STOPWORDS for t in gram):
            continue
        ngrams.append(gram)
    return ngrams


def highlight_snippet(text, keyword, max_len=300):
    """Return a truncated snippet with the keyword wrapped in **bold** markers."""
    if not text:
        return ""
    # Find keyword position (case-insensitive)
    idx = text.lower().find(keyword.lower())
    if idx == -1:
        return text[:max_len] + ("..." if len(text) > max_len else "")

    # Center the snippet around the keyword
    start = max(0, idx - max_len // 2)
    end = min(len(text), start + max_len)
    snippet = text[start:end]

    # Bold the keyword in the snippet
    pattern = re.compile(re.escape(keyword), re.IGNORECASE)
    snippet = pattern.sub(lambda m: f"**{m.group()}**", snippet)

    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return f"{prefix}{snippet}{suffix}"


def keyword_pattern(keyword):
    """Build a compiled word-boundary regex for a keyword or phrase.

    Single words: \\bword\\b
    Phrases: \\bword1\\s+word2\\b (flexible whitespace between tokens)

    This is the single source of truth for keyword matching semantics.
    All discovery, validation, and volume-checking code should use this.
    """
    tokens = keyword.strip().lower().split()
    if len(tokens) == 1:
        return re.compile(r'\b' + re.escape(tokens[0]) + r'\b', re.IGNORECASE)
    else:
        pattern = r'\b' + r'\s+'.join(re.escape(t) for t in tokens) + r'\b'
        return re.compile(pattern, re.IGNORECASE)


def post_matches_keyword(post, pattern):
    """Check if a post (dict with title/selftext) matches a compiled keyword pattern."""
    return (pattern.search(post.get("title", "") or "")
            or pattern.search(post.get("selftext", "") or ""))


def pull_matching_posts(keyword, conn, limit=100, recent_months=None):
    """Pull random matching posts from keyword-eligible subs.

    Uses LIKE for SQL pre-filtering, then word-boundary regex for precision.

    Args:
        keyword: The keyword/phrase to search for
        conn: SQLite connection
        limit: Max posts to return
        recent_months: If set, only include posts from the last N months
    """
    kw_lower = keyword.lower()
    fetch_limit = limit * 3  # Oversample to account for regex filtering

    query = f"""
        SELECT id, subreddit, title, selftext, collected_date
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (LOWER(title) LIKE ? OR LOWER(selftext) LIKE ?)
    """
    params = [f"%{kw_lower}%", f"%{kw_lower}%"]

    if recent_months:
        query += " AND collected_date >= date('now', ?)"
        params.append(f"-{recent_months} months")

    query += " ORDER BY RANDOM() LIMIT ?"
    params.append(fetch_limit)

    rows = conn.execute(query, params).fetchall()
    posts = [dict(r) for r in rows]

    # Word-boundary filter (all keywords, not just short ones)
    pattern = keyword_pattern(keyword)
    posts = [p for p in posts if post_matches_keyword(p, pattern)]

    return posts[:limit]


def count_keyword_hits(keyword, conn, period=None):
    """Count total posts matching a keyword in keyword-eligible subs.

    Uses LIKE for SQL pre-filtering, then word-boundary regex for precision.

    Args:
        keyword: The keyword/phrase to search for
        conn: SQLite connection
        period: Optional period string like '1y', '6m', '30d'
    """
    kw_lower = keyword.lower()
    query = f"""
        SELECT id, title, selftext
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (LOWER(title) LIKE ? OR LOWER(selftext) LIKE ?)
    """
    params = [f"%{kw_lower}%", f"%{kw_lower}%"]

    if period:
        months = _period_to_months(period)
        query += " AND collected_date >= date('now', ?)"
        params.append(f"-{months} months")

    rows = conn.execute(query, params).fetchall()
    pattern = keyword_pattern(keyword)
    return sum(1 for r in rows if post_matches_keyword(dict(r), pattern))


def count_keyword_hits_by_sub(keyword, conn, period=None):
    """Count keyword hits broken down by subreddit.

    Uses LIKE for SQL pre-filtering, then word-boundary regex for precision.
    """
    kw_lower = keyword.lower()
    query = f"""
        SELECT id, subreddit, title, selftext
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (LOWER(title) LIKE ? OR LOWER(selftext) LIKE ?)
    """
    params = [f"%{kw_lower}%", f"%{kw_lower}%"]

    if period:
        months = _period_to_months(period)
        query += " AND collected_date >= date('now', ?)"
        params.append(f"-{months} months")

    rows = conn.execute(query, params).fetchall()
    pattern = keyword_pattern(keyword)

    from collections import Counter
    counts = Counter()
    for r in rows:
        if post_matches_keyword(dict(r), pattern):
            counts[r["subreddit"]] += 1

    return sorted(counts.items(), key=lambda x: -x[1])


def _period_to_months(period):
    """Convert period string like '1y', '6m', '30d' to months."""
    period = period.strip().lower()
    if period.endswith('y'):
        return int(period[:-1]) * 12
    elif period.endswith('m'):
        return int(period[:-1])
    elif period.endswith('d'):
        return max(1, int(period[:-1]) // 30)
    else:
        raise ValueError(f"Invalid period format: {period}. Use '1y', '6m', '30d', etc.")


# ── candidates.csv helpers ──────────────────────────────────────────────

import csv

CANDIDATES_PATH = Path(__file__).parent / "candidates.csv"
CANDIDATES_FIELDS = [
    "candidate", "target_theme", "source_method", "discovery_date", "raw_count",
    "precision_score", "ambiguity_rate", "ai_qualified", "cross_theme_collisions",
    "concentration_flag", "status", "notes",
]


def _read_candidates():
    """Read candidates.csv, returning list of dicts."""
    if not CANDIDATES_PATH.exists():
        return []
    with open(CANDIDATES_PATH, newline="") as f:
        reader = csv.DictReader(f)
        return list(reader)


def _write_candidates(rows):
    """Write rows back to candidates.csv, preserving header."""
    with open(CANDIDATES_PATH, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=CANDIDATES_FIELDS)
        writer.writeheader()
        for row in rows:
            # Ensure all fields exist
            clean = {k: row.get(k, "") for k in CANDIDATES_FIELDS}
            writer.writerow(clean)


def update_candidate(keyword, theme, updates):
    """Update or create a row in candidates.csv for keyword+theme.

    Args:
        keyword: the candidate keyword
        theme: the target theme
        updates: dict of field->value to set/update
    """
    rows = _read_candidates()
    found = False
    for row in rows:
        if row.get("candidate") == keyword and row.get("target_theme") == theme:
            row.update(updates)
            found = True
            break
    if not found:
        new_row = {"candidate": keyword, "target_theme": theme}
        new_row.update(updates)
        rows.append(new_row)
    _write_candidates(rows)
