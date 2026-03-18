#!/usr/bin/env python3
"""Test whether a candidate keyword collides with other themes.

Interactive mode (default): prompts the user to pick the best-fit theme.
Auto mode (--auto): uses Claude Haiku to classify each post.
Dump mode (--dump): writes sampled posts to a file for offline review.

Usage:
    python cross_theme_check.py --keyword "intimate" --target-theme "sexual_erp" --sample-size 20
    python cross_theme_check.py --keyword "maladaptive" --target-theme therapy --auto
    python cross_theme_check.py --keyword "selfhood" --target-theme consciousness --dump
"""

import argparse
import csv
import os
import sys
import time
from collections import Counter
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import (
    get_conn, pull_matching_posts, highlight_snippet, load_all_theme_keywords,
    update_candidate,
)

RESULTS_DIR = Path(__file__).parent.parent / "results"
THEME_NAMES = ["romance", "sexual_erp", "consciousness", "therapy", "addiction", "rupture", "none"]

# Theme descriptions loaded from keywords config
THEME_DESCRIPTIONS = {}


def _load_theme_descriptions():
    global THEME_DESCRIPTIONS
    if THEME_DESCRIPTIONS:
        return
    from utils import PROJECT_ROOT
    import yaml
    kw_path = PROJECT_ROOT / "config" / "keywords_v8.yaml"
    with open(kw_path) as f:
        data = yaml.safe_load(f)
    for cat in data.get("keyword_categories", []):
        THEME_DESCRIPTIONS[cat["name"]] = cat.get("description", cat["name"])


def auto_classify_theme(post, keyword, client):
    """Use Claude Haiku to pick the best-fit theme for a post."""
    _load_theme_descriptions()

    theme_list = "\n".join(
        f"- {t}: {THEME_DESCRIPTIONS.get(t, t)}" if t != "none"
        else "- none: Post is not about any of the above themes"
        for t in THEME_NAMES
    )

    title = (post.get("title", "") or "")[:500]
    body = (post.get("selftext", "") or "")[:1500]
    sub = post.get("subreddit", "")

    prompt = f"""You are classifying Reddit posts from AI companion communities for a research project.

The keyword "{keyword}" was found in this post. Determine which theme it BEST fits.

Themes:
{theme_list}

Post from r/{sub}:
Title: {title}
Body: {body}

Which single theme best fits this post? Respond with EXACTLY one line in this format:
THEME_NAME: <one-sentence reason>

Use one of: {', '.join(THEME_NAMES)}"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    # Parse theme from response
    for theme in THEME_NAMES:
        if text.lower().startswith(theme):
            return theme, text
    return "none", text


def main():
    parser = argparse.ArgumentParser(description="Cross-theme collision check")
    parser.add_argument("--keyword", required=True, help="Candidate keyword to test")
    parser.add_argument("--target-theme", required=True, help="Expected primary theme")
    parser.add_argument("--sample-size", type=int, default=20, help="Number of posts to sample")
    parser.add_argument("--auto", action="store_true", help="Use Claude Haiku for classification instead of interactive prompts")
    parser.add_argument("--dump", action="store_true", help="Dump sampled posts to a file in results/ instead of prompting")
    args = parser.parse_args()

    client = None
    if args.auto:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("Error: --auto requires ANTHROPIC_API_KEY environment variable")
            sys.exit(1)
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)

    conn = get_conn()
    posts = pull_matching_posts(args.keyword, conn, limit=args.sample_size)

    if not posts:
        print("No matching posts found.")
        conn.close()
        return

    # Build abbreviation map for interactive mode
    theme_abbrevs = {}
    for t in THEME_NAMES:
        key = t[0]
        if key in theme_abbrevs:
            theme_abbrevs[t[:2]] = t
        else:
            theme_abbrevs[key] = t

    if args.dump:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_path = RESULTS_DIR / f"dump_crosstheme_{args.keyword.replace(' ', '_')}_{ts}.txt"
        with open(dump_path, "w") as f:
            f.write(f"Cross-theme sample dump: '{args.keyword}' → target: {args.target_theme}\n")
            f.write(f"Sample size: {len(posts)}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
            f.write(f"Themes: {', '.join(THEME_NAMES)}\n")
            f.write("=" * 70 + "\n")
            for i, post in enumerate(posts, 1):
                title = post.get("title", "") or "(no title)"
                body = post.get("selftext", "") or ""
                sub = post.get("subreddit", "")
                date = post.get("collected_date", "")
                post_id = post.get("id", "")
                permalink = f"https://www.reddit.com/comments/{post_id}" if post_id else ""
                snippet = highlight_snippet(body, args.keyword, max_len=400)
                f.write(f"\n--- Post {i}/{len(posts)} ---\n")
                f.write(f"Subreddit: r/{sub}  |  Date: {date}\n")
                f.write(f"Title: {title}\n")
                if snippet:
                    f.write(f"Snippet: {snippet}\n")
                if permalink:
                    f.write(f"Link: {permalink}\n")
                f.write("\n")
        print(f"Dumped {len(posts)} posts to {dump_path}")
        conn.close()
        return

    mode_label = "auto (Claude Haiku)" if args.auto else "interactive"
    print(f"\nKeyword: '{args.keyword}'  |  Target: {args.target_theme}")
    print(f"Mode: {mode_label}")
    print(f"Sampling {len(posts)} posts. {'Auto-classifying...' if args.auto else 'For each, pick the BEST-FIT theme.'}\n")
    if not args.auto:
        print(f"Themes: {' / '.join(THEME_NAMES)}")
    print("=" * 60)

    tally = Counter()

    for i, post in enumerate(posts, 1):
        title = post.get("title", "") or ""
        body = post.get("selftext", "") or ""
        sub = post.get("subreddit", "")

        print(f"\n--- Post {i}/{len(posts)} ---")
        print(f"r/{sub}: {title[:200]}")
        snippet = highlight_snippet(body, args.keyword, max_len=300)
        if snippet:
            print(f"Body: {snippet}")

        if args.auto:
            try:
                choice, raw = auto_classify_theme(post, args.keyword, client)
                print(f"  → {raw}")
                tally[choice] += 1
                time.sleep(0.2)
            except Exception as e:
                print(f"  → ERROR: {e}")
                tally["none"] += 1
        else:
            print()
            while True:
                response = input(
                    "Best-fit theme? (romance/sexual_erp/consciousness/therapy/addiction/rupture/none): "
                ).strip().lower()
                if response in THEME_NAMES:
                    choice = response
                    break
                if response in theme_abbrevs:
                    choice = theme_abbrevs[response]
                    break
                print(f"  Enter one of: {', '.join(THEME_NAMES)}")

            tally[choice] += 1

    # Results
    total = sum(tally.values())
    print("\n" + "=" * 60)
    print(f"Cross-theme distribution for '{args.keyword}' (target: {args.target_theme})")
    print(f"Mode: {mode_label}")
    print("-" * 40)
    for theme in THEME_NAMES:
        count = tally.get(theme, 0)
        pct = (count / total * 100) if total > 0 else 0
        flag = " ⚠ COLLISION" if theme != args.target_theme and pct > 30 else ""
        bar = "█" * int(pct / 2)
        print(f"  {theme:<16} {count:>3}  ({pct:5.1f}%) {bar}{flag}")

    # Check for collisions
    collisions = []
    collision_details = []
    for theme in THEME_NAMES:
        if theme == args.target_theme or theme == "none":
            continue
        count = tally.get(theme, 0)
        pct = (count / total * 100) if total > 0 else 0
        if pct > 30:
            collisions.append(f"{theme} ({pct:.1f}%)")
        if count > 0:
            collision_details.append(f"{theme}:{pct:.0f}%")

    if collisions:
        print(f"\n⚠  COLLISION WARNING: {', '.join(collisions)}")
    else:
        print(f"\n✓  No cross-theme collisions (all non-target themes <30%)")
    print("=" * 60)

    # Append to log
    log_path = RESULTS_DIR / "cross_theme_log.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            header = ["keyword", "target_theme", "date", "sample_size"] + THEME_NAMES + ["collision_flag", "mode"]
            writer.writerow(header)
        row = [args.keyword, args.target_theme, datetime.now().strftime("%Y-%m-%d"), total]
        row += [tally.get(t, 0) for t in THEME_NAMES]
        row.append("YES" if collisions else "NO")
        row.append(mode_label)
        writer.writerow(row)

    print(f"Logged to {log_path}")

    # Auto-log to candidates.csv
    collision_str = ", ".join(collision_details) if collision_details else "none"
    candidate_updates = {"cross_theme_collisions": collision_str}
    if collisions:
        candidate_updates["status"] = "testing"
        candidate_updates["notes"] = f"Cross-theme collision with {', '.join(collisions)}"
    update_candidate(args.keyword, args.target_theme, candidate_updates)
    print(f"Updated candidates.csv → collisions: {collision_str}")

    conn.close()


if __name__ == "__main__":
    main()
