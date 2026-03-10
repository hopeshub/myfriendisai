"""Load and validate config/communities.yaml and config/keywords.yaml."""

from pathlib import Path
import yaml

CONFIG_DIR = Path(__file__).parent.parent / "config"


def load_communities():
    path = CONFIG_DIR / "communities.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)

    communities = data.get("communities", [])
    errors = []

    for i, c in enumerate(communities):
        if not c.get("subreddit"):
            errors.append(f"communities[{i}]: missing 'subreddit'")
        if c.get("tier") not in (0, 1, 2, 3, "adjacent"):
            errors.append(f"r/{c.get('subreddit')}: invalid tier '{c.get('tier')}'")
        if not c.get("category"):
            errors.append(f"r/{c.get('subreddit')}: missing 'category'")

    if errors:
        raise ValueError("communities.yaml validation errors:\n" + "\n".join(f"  - {e}" for e in errors))

    return [c for c in communities if c.get("is_active", True)]


def load_keywords():
    path = CONFIG_DIR / "keywords.yaml"
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
