#!/usr/bin/env python3
"""Pull a random sample of posts for a candidate keyword and assess precision.

Interactive mode (default): prompts the user for y/n/s on each post.
Auto mode (--auto): uses Claude Haiku to classify each post.

Usage:
    python precision_sampler.py --keyword "intimate" --theme "sexual_erp" --sample-size 20
    python precision_sampler.py --keyword "ai therapist" --theme therapy --auto
"""

import argparse
import csv
import os
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from utils import get_conn, pull_matching_posts, highlight_snippet, count_keyword_hits, load_all_theme_keywords

RESULTS_DIR = Path(__file__).parent.parent / "results"

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


def auto_classify_precision(post, keyword, theme, client):
    """Use Claude Haiku to classify whether a post matches a theme."""
    _load_theme_descriptions()
    theme_desc = THEME_DESCRIPTIONS.get(theme, theme)

    title = (post.get("title", "") or "")[:500]
    body = (post.get("selftext", "") or "")[:1500]
    sub = post.get("subreddit", "")

    prompt = f"""You are classifying Reddit posts from AI companion communities for a research project.

Theme: "{theme}" — {theme_desc}
Keyword being tested: "{keyword}"

Post from r/{sub}:
Title: {title}
Body: {body}

Is this post genuinely about the theme "{theme}" ({theme_desc})?

Respond with EXACTLY one line in this format:
YES: <one-sentence reason>
or
NO: <one-sentence reason>"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=100,
        messages=[{"role": "user", "content": prompt}],
    )
    text = response.content[0].text.strip()
    return text


def main():
    parser = argparse.ArgumentParser(description="Precision sampler for keyword validation")
    parser.add_argument("--keyword", required=True, help="Candidate keyword to test")
    parser.add_argument("--theme", required=True, help="Target theme this keyword should match")
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

    # Get total hit count
    total_hits = count_keyword_hits(args.keyword, conn)
    mode_label = "auto (Claude Haiku)" if args.auto else "interactive"
    print(f"\nKeyword: '{args.keyword}'")
    print(f"Target theme: {args.theme}")
    print(f"Total hits in T1-T3: {total_hits}")
    print(f"Mode: {mode_label}")
    print(f"Sampling {args.sample_size} posts...\n")

    posts = pull_matching_posts(args.keyword, conn, limit=args.sample_size)
    if not posts:
        print("No matching posts found.")
        conn.close()
        return

    if args.dump:
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        dump_path = RESULTS_DIR / f"dump_precision_{args.keyword.replace(' ', '_')}_{ts}.txt"
        with open(dump_path, "w") as f:
            f.write(f"Precision sample dump: '{args.keyword}' → {args.theme}\n")
            f.write(f"Total hits in T1-T3: {total_hits}\n")
            f.write(f"Sample size: {len(posts)}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
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

    print(f"Got {len(posts)} posts. {'Auto-classifying...' if args.auto else 'Review each one:'}\n")
    print("=" * 60)

    y_count = 0
    n_count = 0
    skip_count = 0

    for i, post in enumerate(posts, 1):
        title = post.get("title", "") or ""
        body = post.get("selftext", "") or ""
        sub = post.get("subreddit", "")
        date = post.get("collected_date", "")

        print(f"\n--- Post {i}/{len(posts)} ---")
        print(f"Subreddit: r/{sub}  |  Date: {date}")
        print(f"Title: {title[:200]}")
        snippet = highlight_snippet(body, args.keyword, max_len=300)
        if snippet:
            print(f"Body: {snippet}")

        if args.auto:
            try:
                result = auto_classify_precision(post, args.keyword, args.theme, client)
                print(f"  → {result}")
                if result.upper().startswith("YES"):
                    y_count += 1
                elif result.upper().startswith("NO"):
                    n_count += 1
                else:
                    skip_count += 1
                    print(f"  (unclear response, counting as skip)")
                time.sleep(0.2)
            except Exception as e:
                print(f"  → ERROR: {e}")
                skip_count += 1
        else:
            print()
            while True:
                response = input(f"Is this post about [{args.theme}]? (y/n/s to skip): ").strip().lower()
                if response in ("y", "n", "s"):
                    break
                print("  Please enter y, n, or s")

            if response == "y":
                y_count += 1
            elif response == "n":
                n_count += 1
            else:
                skip_count += 1

    # Results
    judged = y_count + n_count
    precision = (y_count / judged * 100) if judged > 0 else 0

    print("\n" + "=" * 60)
    print(f"Results for '{args.keyword}' → {args.theme}")
    print(f"  YES: {y_count}  |  NO: {n_count}  |  Skipped: {skip_count}")
    print(f"  Precision: {precision:.1f}% ({y_count}/{judged})")
    print(f"  Total hits: {total_hits}")
    print(f"  Mode: {mode_label}")
    print("=" * 60)

    # Append to precision log
    log_path = RESULTS_DIR / "precision_log.csv"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not log_path.exists()

    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        if write_header:
            writer.writerow(["keyword", "theme", "date", "sample_size", "precision_score",
                             "y_count", "n_count", "skip_count", "total_hits", "mode"])
        writer.writerow([
            args.keyword, args.theme, datetime.now().strftime("%Y-%m-%d"),
            len(posts), f"{precision:.1f}", y_count, n_count, skip_count, total_hits, mode_label
        ])

    print(f"Logged to {log_path}")
    conn.close()


if __name__ == "__main__":
    main()
