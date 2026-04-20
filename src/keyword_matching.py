"""Shared keyword matching logic used by both post and comment taggers.

Compiles regex patterns from keyword config and matches them against text.
"""

import re

from src.config import load_keywords


def build_patterns(keyword_categories: list[dict] = None) -> list[tuple[str, str, re.Pattern]]:
    """Return list of (category_name, term, compiled_pattern) for all terms.

    If keyword_categories is None, loads from config automatically.
    """
    if keyword_categories is None:
        keyword_categories = load_keywords()

    patterns = []
    for cat in keyword_categories:
        category = cat["name"]
        for term in cat.get("terms", []):
            escaped = re.escape(term)
            pat = re.compile(r"\b" + escaped + r"\b", re.IGNORECASE)
            patterns.append((category, term, pat))
    return patterns


def match_text(text: str, patterns: list[tuple[str, str, re.Pattern]]) -> list[tuple[str, str]]:
    """Return list of (category, matched_term) for all keyword matches in text."""
    if not text:
        return []
    seen = set()
    matches = []
    for category, term, pat in patterns:
        key = (category, term)
        if key not in seen and pat.search(text):
            matches.append(key)
            seen.add(key)
    return matches
