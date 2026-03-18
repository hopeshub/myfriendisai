#!/usr/bin/env python3
"""Parse Claude Code's classification output and store in SQLite.

Takes the prompt file (to extract post IDs) and CC's classification text,
parses each YES/NO, and stores results in the llm_classifications table.

Usage:
    # Parse from a file containing CC's output
    python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \
        --output-file results/classified_grieving_rupture_2026-03-17.txt

    # Parse from stdin (pipe CC's output)
    python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \
        --from-stdin

    # Parse inline classifications (pass directly as argument)
    python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \
        --classifications "1. YES # rupture grief\\n2. NO # human grief\\n3. YES # platform loss"
"""

import argparse
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
sys.path.insert(0, str(SCRIPT_DIR))
from utils import get_conn


def ensure_classifications_table(conn):
    """Create the llm_classifications table if it doesn't exist."""
    conn.execute("""
        CREATE TABLE IF NOT EXISTS llm_classifications (
            post_id TEXT NOT NULL,
            theme TEXT NOT NULL,
            keyword TEXT NOT NULL,
            run_id TEXT,
            classification TEXT NOT NULL,
            reason TEXT,
            model TEXT NOT NULL,
            classified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (post_id, theme, keyword)
        )
    """)
    columns = {
        row["name"] for row in conn.execute("PRAGMA table_info(llm_classifications)").fetchall()
    }
    if "run_id" not in columns:
        conn.execute("ALTER TABLE llm_classifications ADD COLUMN run_id TEXT")
    conn.commit()


def extract_metadata_from_prompt(filepath):
    """Extract keyword, theme, and post IDs from the prompt file."""
    keyword = None
    theme = None
    post_ids = []

    with open(filepath) as f:
        for line in f:
            if line.startswith("**Keyword:**"):
                keyword = line.split("**Keyword:**")[1].strip()
            elif line.startswith("**Target Theme:**"):
                theme = line.split("**Target Theme:**")[1].strip().lower()
                # Normalize theme names
                theme = theme.replace("sex / erp", "sexual_erp").replace("sex/erp", "sexual_erp")
            elif line.startswith("**ID:**"):
                post_id = line.split("**ID:**")[1].strip()
                post_ids.append(post_id)

    return keyword, theme, post_ids


def parse_classification_lines(text):
    """Parse CC's structured classification output.

    Expected format:
        1. YES  # brief reason
        2. NO   # off-theme
        3. YES  # platform rupture

    Returns list of (classification, reason) tuples.
    """
    results = []
    # Match lines like "1. YES # reason" or "1. YES — reason" or "1. YES - reason"
    pattern = re.compile(
        r'^\s*\d+\.\s*(YES|NO)\s*(?:[#\-—|]\s*(.*))?$',
        re.IGNORECASE | re.MULTILINE
    )

    for match in pattern.finditer(text):
        classification = match.group(1).upper()
        reason = (match.group(2) or "").strip()
        results.append((classification, reason))

    return results


def store_classifications(conn, post_ids, classifications, keyword, theme, run_id, model="claude-code"):
    """Store classification results in SQLite."""
    stored = 0
    for post_id, (classification, reason) in zip(post_ids, classifications):
        conn.execute(
            """INSERT OR REPLACE INTO llm_classifications
               (post_id, theme, keyword, run_id, classification, reason, model)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (post_id, theme, keyword, run_id, classification, reason, model)
        )
        stored += 1
    conn.commit()
    return stored


def main():
    parser = argparse.ArgumentParser(
        description="Parse Claude Code's classification output and store in SQLite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \\
      --output-file results/classified_grieving_rupture_2026-03-17.txt

  python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \\
      --from-stdin

  python parse_classifications.py --prompt-file results/classify_grieving_rupture_2026-03-17.md \\
      --classifications "1. YES # rupture\\n2. NO # human grief"
"""
    )
    parser.add_argument("--prompt-file", required=True, help="Path to the prompt file (to extract post IDs and metadata)")
    parser.add_argument("--output-file", help="Path to a file containing CC's classification output")
    parser.add_argument("--from-stdin", action="store_true", help="Read CC's output from stdin")
    parser.add_argument("--classifications", help="CC's output as a string (newlines as \\n)")
    parser.add_argument("--run-id", help="Optional label for this validation run (defaults to prompt filename stem)")
    parser.add_argument("--force-truncate", action="store_true",
                        help="Store overlapping rows even if the number of classifications does not match the prompt")

    args = parser.parse_args()

    # Get the classification text
    if args.output_file:
        with open(args.output_file) as f:
            text = f.read()
    elif args.from_stdin:
        text = sys.stdin.read()
    elif args.classifications:
        text = args.classifications.replace("\\n", "\n")
    else:
        print("ERROR: Provide --output-file, --from-stdin, or --classifications")
        sys.exit(1)

    # Extract metadata from prompt file
    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"ERROR: Prompt file not found: {prompt_path}")
        sys.exit(1)

    keyword, theme, post_ids = extract_metadata_from_prompt(prompt_path)
    if not keyword or not theme:
        print("ERROR: Could not extract keyword/theme from prompt file")
        sys.exit(1)
    run_id = args.run_id or prompt_path.stem

    print(f"Keyword: {keyword}")
    print(f"Theme: {theme}")
    print(f"Run ID: {run_id}")
    print(f"Post IDs extracted: {len(post_ids)}")

    # Parse classifications
    classifications = parse_classification_lines(text)
    print(f"Classifications parsed: {len(classifications)}")

    if len(classifications) != len(post_ids):
        print(f"\nWARNING: Mismatch — {len(post_ids)} posts but {len(classifications)} classifications.")
        if not args.force_truncate:
            print("Refusing to store partial results. Re-run with --force-truncate if you want to keep the overlap.")
            sys.exit(1)
        if len(classifications) < len(post_ids):
            print(f"Storing only the first {len(classifications)} posts.")
            post_ids = post_ids[:len(classifications)]
        else:
            print(f"Storing only the first {len(post_ids)} classifications.")
            classifications = classifications[:len(post_ids)]

    # Store in SQLite
    conn = get_conn()
    ensure_classifications_table(conn)

    stored = store_classifications(conn, post_ids, classifications, keyword, theme, run_id)
    conn.close()

    # Summary
    yes_count = sum(1 for c, _ in classifications if c == "YES")
    no_count = sum(1 for c, _ in classifications if c == "NO")
    total = yes_count + no_count
    precision = yes_count / total * 100 if total > 0 else 0

    print()
    print("=" * 55)
    print(f"  STORED: {keyword} → {theme}")
    print("=" * 55)
    print(f"  Posts stored:   {stored}")
    print(f"  YES:            {yes_count} ({precision:.1f}%)")
    print(f"  NO:             {no_count} ({100-precision:.1f}%)")
    print(f"  Precision:      {precision:.1f}%")
    print("=" * 55)


if __name__ == "__main__":
    main()
