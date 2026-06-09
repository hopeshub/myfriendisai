"""Load and validate config/communities.yaml and config/keywords.yaml."""

import hashlib
from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config"


def _load_all_communities():
    path = CONFIG_DIR / "communities.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)

    communities = data.get("communities", [])
    errors = []

    for i, c in enumerate(communities):
        if not c.get("subreddit"):
            errors.append(f"communities[{i}]: missing 'subreddit'")
        if c.get("tier") not in (0, 1, 2, 3, 4, "adjacent"):
            errors.append(f"r/{c.get('subreddit')}: invalid tier '{c.get('tier')}'")
        if not c.get("category"):
            errors.append(f"r/{c.get('subreddit')}: missing 'category'")

    if errors:
        raise ValueError("communities.yaml validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return communities


def load_communities():
    """Communities to actively collect from (excludes deactivated/banned subs)."""
    return [c for c in _load_all_communities() if c.get("is_active", True)]


def load_keyword_communities():
    """Load communities eligible for keyword trend calculations.

    Filters to T1-T3 subs only (excludes T0 general AI subs and T4 ambient
    discourse-climate subs) and respects the exclude_from_keywords flag
    (e.g. bot-listing-heavy subs). The explicit tier check is defense-in-depth:
    every T4 sub also carries exclude_from_keywords=true, but tightening the
    filter from `tier >= 1` to `tier in (1, 2, 3)` means an accidentally-flagged
    T4 sub still can't slip into the keyword pipeline.

    Deliberately ignores is_active: a deactivated sub (e.g. r/HeavenGF, banned
    by Reddit ~May 2026) stops being COLLECTED, but its historical posts stay
    in the corpus — numerator and denominator — per the documented invariant.
    """
    return [
        c for c in _load_all_communities()
        if c.get("tier") in (1, 2, 3) and not c.get("exclude_from_keywords", False)
    ]


def load_keywords():
    path = CONFIG_DIR / "keywords_v8.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)

    categories = data.get("keyword_categories", [])
    errors = []

    for i, cat in enumerate(categories):
        if not cat.get("name"):
            errors.append(f"keyword_categories[{i}]: missing 'name'")
        if not cat.get("terms"):
            errors.append(f"keyword_categories[{i}] '{cat.get('name')}': missing 'terms'")

    if errors:
        raise ValueError("keywords.yaml validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return categories


def keyword_fingerprint(keyword_categories=None) -> str:
    """A stable hash of the keyword set.

    Used to detect when the keyword config has changed in a way that requires
    re-tagging the historical corpus (otherwise a newly added keyword is only
    ever applied to posts collected after the change). Sensitive to category
    names and the exact set of terms; insensitive to ordering and to YAML
    comments (so a precision-annotation edit does not trigger a re-tag).
    """
    if keyword_categories is None:
        keyword_categories = load_keywords()
    lines = []
    for cat in keyword_categories:
        name = str(cat["name"])
        for term in cat.get("terms", []):
            lines.append(f"{name}|{str(term).strip()}")
    blob = "\n".join(sorted(lines))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    communities = load_communities()
    print(f"Loaded {len(communities)} active communities:")
    for c in communities:
        print(f"  [Tier {c['tier']}] r/{c['subreddit']} — {c['category']}")

    print()

    keywords = load_keywords()
    print(f"Loaded {len(keywords)} keyword categories:")
    for cat in keywords:
        print(f"  {cat['name']}: {', '.join(str(t) for t in cat['terms'])}")
