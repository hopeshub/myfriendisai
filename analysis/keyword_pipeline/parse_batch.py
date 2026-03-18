#!/usr/bin/env python3
"""Parse CC's batch classification output and store in SQLite.

Takes the batch prompt file (to extract post IDs per keyword section) and
CC's classification text, parses YES/NO per section, stores all results.

Usage:
    python parse_batch.py --prompt-file results/batch_2026-03-17.md \
        --output-file results/classified_batch_2026-03-17.txt
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


def normalize_theme(theme):
    """Normalize human-readable theme labels into internal keys."""
    return theme.strip().lower().replace("sex / erp", "sexual_erp").replace("sex/erp", "sexual_erp")


def extract_sections_from_prompt(filepath):
    """Extract keyword sections from a batch prompt file.

    Returns list of dicts: [{keyword, theme, post_ids}, ...]
    """
    sections = []
    current = None

    with open(filepath) as f:
        for line in f:
            # Detect section headers like "# KEYWORD: grieving → Rupture"
            m = re.match(r'^# KEYWORD:\s*(.+?)\s*→\s*(.+?)\s*$', line)
            if m:
                if current:
                    sections.append(current)
                keyword = m.group(1).strip()
                theme = normalize_theme(m.group(2))
                current = {"keyword": keyword, "theme": theme, "post_ids": []}
                continue

            # Collect post IDs within current section
            if current and line.startswith("**ID:**"):
                post_id = line.split("**ID:**")[1].strip()
                current["post_ids"].append(post_id)

    if current:
        sections.append(current)

    return sections


def parse_classification_sections(text):
    """Parse CC's batch classification output into per-keyword sections.

    Expected format:
        ## KEYWORD: grieving → Rupture
        1. YES  # reason
        2. NO   # reason
        ...
        PRECISION: 74/100 = 74.0%

        ## KEYWORD: soulless → Rupture
        1. YES  # reason
        ...

    Returns list of dicts: [{keyword, theme, classifications}, ...]
    """
    header_pattern = re.compile(r'^##\s*KEYWORD:\s*(.+?)\s*→\s*(.+?)\s*$', re.MULTILINE)
    line_pattern = re.compile(
        r'^\s*\d+\.\s*(YES|NO)\s*(?:[#\-—|]\s*(.*))?$',
        re.IGNORECASE | re.MULTILINE
    )

    headers = list(header_pattern.finditer(text))
    all_sections = []
    for i, header in enumerate(headers):
        start = header.end()
        end = headers[i + 1].start() if i + 1 < len(headers) else len(text)
        section_text = text[start:end]
        results = []
        for match in line_pattern.finditer(section_text):
            classification = match.group(1).upper()
            reason = (match.group(2) or "").strip()
            results.append((classification, reason))
        all_sections.append({
            "keyword": header.group(1).strip(),
            "theme": normalize_theme(header.group(2)),
            "classifications": results,
        })

    return all_sections


def main():
    parser = argparse.ArgumentParser(
        description="Parse CC's batch classification output and store in SQLite.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Example:
  python parse_batch.py --prompt-file results/batch_2026-03-17.md \\
      --output-file results/classified_batch_2026-03-17.txt
"""
    )
    parser.add_argument("--prompt-file", required=True, help="Path to the batch prompt file")
    parser.add_argument("--output-file", help="Path to file containing CC's output")
    parser.add_argument("--from-stdin", action="store_true", help="Read CC's output from stdin")
    parser.add_argument("--run-id", help="Optional label for this validation run (defaults to prompt filename stem)")
    parser.add_argument("--force-truncate", action="store_true",
                        help="Store overlapping rows even if a section has fewer classifications than posts")

    args = parser.parse_args()

    if args.output_file:
        with open(args.output_file) as f:
            text = f.read()
    elif args.from_stdin:
        text = sys.stdin.read()
    else:
        print("ERROR: Provide --output-file or --from-stdin")
        sys.exit(1)

    prompt_path = Path(args.prompt_file)
    if not prompt_path.exists():
        print(f"ERROR: Prompt file not found: {prompt_path}")
        sys.exit(1)

    # Extract sections from prompt
    prompt_sections = extract_sections_from_prompt(prompt_path)
    run_id = args.run_id or prompt_path.stem
    print(f"Prompt sections: {len(prompt_sections)}")
    print(f"Run ID: {run_id}")
    for s in prompt_sections:
        print(f"  {s['keyword']} → {s['theme']} ({len(s['post_ids'])} posts)")

    # Parse classification sections from CC's output
    classification_sections = parse_classification_sections(text)
    print(f"\nClassification sections parsed: {len(classification_sections)}")
    prompt_map = {(s["keyword"], s["theme"]): s for s in prompt_sections}
    classification_map = {(s["keyword"], s["theme"]): s for s in classification_sections}

    missing = [key for key in prompt_map if key not in classification_map]
    extra = [key for key in classification_map if key not in prompt_map]
    if missing or extra:
        if missing:
            print("\nMissing classification sections:")
            for keyword, theme in missing:
                print(f"  {keyword} → {theme}")
        if extra:
            print("\nUnexpected classification sections:")
            for keyword, theme in extra:
                print(f"  {keyword} → {theme}")
        print("\nRefusing to store mismatched batch results.")
        sys.exit(1)

    # Store all classifications
    conn = get_conn()
    ensure_classifications_table(conn)

    print()
    print("=" * 65)
    print(f"  {'Keyword':<20s} {'Theme':<15s} {'YES':>5s} {'NO':>5s} {'Prec':>7s}")
    print("-" * 65)

    for prompt_sec in prompt_sections:
        keyword = prompt_sec["keyword"]
        theme = prompt_sec["theme"]
        post_ids = prompt_sec["post_ids"]
        classifications = classification_map[(keyword, theme)]["classifications"]

        # Handle length mismatch within a section
        n = min(len(post_ids), len(classifications))
        if len(post_ids) != len(classifications):
            print(f"  WARNING: {keyword} — {len(post_ids)} posts but {len(classifications)} classifications.")
            if not args.force_truncate:
                conn.close()
                print("  Refusing to store partial section results. Re-run with --force-truncate to keep the overlap.")
                sys.exit(1)
            print(f"  Storing first {n} overlapping rows.")

        for post_id, (classification, reason) in zip(post_ids[:n], classifications[:n]):
            conn.execute(
                """INSERT OR REPLACE INTO llm_classifications
                   (post_id, theme, keyword, run_id, classification, reason, model)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (post_id, theme, keyword, run_id, classification, reason, "claude-code")
            )

        conn.commit()

        yes = sum(1 for c, _ in classifications[:n] if c == "YES")
        no = sum(1 for c, _ in classifications[:n] if c == "NO")
        total = yes + no
        pct = yes / total * 100 if total > 0 else 0
        print(f"  {keyword:<20s} {theme:<15s} {yes:>5d} {no:>5d} {pct:>6.1f}%")

    conn.close()
    print("=" * 65)


if __name__ == "__main__":
    main()
