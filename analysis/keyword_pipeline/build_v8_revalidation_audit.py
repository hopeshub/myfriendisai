#!/usr/bin/env python3
"""Build an audit prompt file for the v8 revalidation (40 keywords).

For each auditable keyword (≥20 stored classifications in llm_classifications),
take 20 posts from the most recent run and format them into a section of an
audit prompt file. The audit agent re-classifies these 20 posts independently
and we compare to the stored primary labels.

Outputs:
    results/audit_v8_revalidation_2026-05-12.md   (prompt for agents)
    results/primary_v8_revalidation_2026-05-12.txt (stored labels in our parser format)
"""

import sqlite3
import yaml
from datetime import date
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
THEME_DEFS = Path(__file__).parent / "theme_definitions.yaml"
KEYWORDS_YAML = PROJECT_ROOT / "config" / "keywords_v8.yaml"
RESULTS = Path(__file__).parent / "results"

JUST_ADDED = {
    "saying goodbye", "taken away", "mourning", "mourn",
    "devastated", "grieve", "goodbye", "farewell",
}

def main():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    with open(THEME_DEFS) as f:
        themes = yaml.safe_load(f)
    with open(KEYWORDS_YAML) as f:
        cfg = yaml.safe_load(f)

    # Walk config to get all (theme, keyword) pairs, skip just-added
    keywords = []
    for cat in cfg["keyword_categories"]:
        for term in cat.get("terms", []):
            if term in JUST_ADDED:
                continue
            keywords.append((cat["name"], term))

    audit_path = RESULTS / f"audit_v8_revalidation_{date.today().isoformat()}.md"
    primary_path = RESULTS / f"primary_v8_revalidation_{date.today().isoformat()}.txt"

    audit_sections = []
    primary_lines = []
    line_offsets = {}  # keyword -> (start_line, length) in audit file
    current_line = 0

    audit_header = [
        "# v8 Revalidation Audit Prompt",
        "",
        f"**Date:** {date.today().isoformat()}",
        "**Purpose:** Independent audit of stored v8 classifications. Each keyword section",
        "contains 20 posts from the most recent stored validation run. Audit agents",
        "re-classify these 20 posts under the same rubric WITHOUT seeing the primary labels.",
        "Inter-rater agreement is then computed vs. stored primary labels.",
        "",
        "---",
        "",
    ]
    audit_text = "\n".join(audit_header) + "\n"
    current_line = audit_text.count("\n")

    skipped = []
    included = []

    for theme_key, keyword in keywords:
        n = conn.execute(
            "SELECT COUNT(*) FROM llm_classifications WHERE keyword=?", (keyword,)
        ).fetchone()[0]
        if n < 20:
            skipped.append((theme_key, keyword, n, "insufficient classifications"))
            continue

        # Pull the most recent run's classifications, ordered consistently
        rows = conn.execute(
            """SELECT lc.post_id, lc.classification, lc.reason, lc.run_id, lc.classified_at,
                      p.title, p.selftext, p.subreddit, date(p.created_utc, 'unixepoch') AS post_date
               FROM llm_classifications lc
               JOIN posts p ON p.id = lc.post_id
               WHERE lc.keyword = ?
               ORDER BY lc.classified_at DESC, lc.post_id ASC""",
            (keyword,),
        ).fetchall()

        # Keep only the most recent run
        latest_run = rows[0]["run_id"] if rows else None
        if latest_run is None:
            # group by classified_at
            latest_at = rows[0]["classified_at"]
            run_rows = [r for r in rows if r["classified_at"] == latest_at]
        else:
            run_rows = [r for r in rows if r["run_id"] == latest_run]
        # If we still have >100, take the latest 100 (consistent across runs)
        run_rows = run_rows[:100]

        sample_size = len(run_rows)
        if sample_size < 20:
            skipped.append((theme_key, keyword, sample_size, "insufficient most-recent-run"))
            continue

        # Take every Nth where N = sample_size // 20 (so 20 spread samples)
        step = max(1, sample_size // 20)
        audit_indices = list(range(step - 1, sample_size, step))[:20]
        # Re-number 1-based positional indices (1..sample_size) for the audit prompt
        audit_post_nums = [i + 1 for i in audit_indices]

        theme_def = themes.get(theme_key)
        if not theme_def:
            skipped.append((theme_key, keyword, sample_size, f"unknown theme {theme_key}"))
            continue

        # Build prompt section
        section = []
        section.append("=" * 60)
        section.append("")
        section.append(f"# KEYWORD: {keyword} → {theme_def['name']}")
        section.append("")
        section.append(f"**Keyword:** {keyword}")
        section.append(f"**Target Theme:** {theme_def['name']}")
        section.append(f"**Audit Sample Size:** 20 (drawn from {sample_size}-post stored run)")
        section.append(f"**Audit Post Numbers:** {audit_post_nums}")
        section.append("")
        section.append(f"**{theme_def['name']}** — what COUNTS:")
        section.append(theme_def["definition"].strip())
        section.append("")
        section.append("What does NOT count:")
        section.append(theme_def["excludes"].strip())
        section.append("")
        section.append("---")
        section.append("")

        # Compute section start line
        section_lines = sum(1 for _ in section) + 1  # +1 for trailing newline
        section_start_line = current_line + 1

        # Add 100 posts (we'll include all, but tell agent to only classify the audit subset)
        for i, row in enumerate(run_rows, 1):
            section.append(f"### Post {i} of {sample_size}")
            section.append(f"**ID:** {row['post_id']}")
            section.append(f"**Title:** {row['title'] or ''}")
            section.append(f"**Subreddit:** r/{row['subreddit']}")
            section.append(f"**Date:** {row['post_date']}")
            body = (row['selftext'] or "")[:500]
            section.append("**Snippet:**")
            section.append(f"> {body}")
            section.append("")
            section.append("---")
            section.append("")

        section_text = "\n".join(section) + "\n"
        section_line_count = section_text.count("\n")
        line_offsets[keyword] = (section_start_line, section_line_count)
        audit_text += section_text
        current_line += section_line_count

        included.append((theme_key, keyword, sample_size, audit_post_nums))

        # Build primary file lines for compute_agreement.py
        primary_lines.append(f"## KEYWORD: {keyword} → {theme_def['name']}")
        for i, row in enumerate(run_rows, 1):
            reason = (row["reason"] or "").replace("\n", " ").strip()
            primary_lines.append(f"{i}. {row['classification']}  # {reason}")
        yes = sum(1 for r in run_rows if r["classification"] == "YES")
        primary_lines.append(f"PRECISION: {yes}/{sample_size} = {yes*100/sample_size:.0f}%")
        primary_lines.append("")

    # Write outputs
    audit_path.write_text(audit_text)
    primary_path.write_text("\n".join(primary_lines))

    # Print line offsets for agent dispatch
    print(f"\nWrote audit prompt: {audit_path}")
    print(f"Wrote primary labels: {primary_path}")
    print(f"\n=== Audit section offsets (for agent Read calls) ===")
    print(f"{'theme':<15} {'keyword':<30} {'audit posts (n=20)':<35} offset  limit")
    for theme_key, keyword, sample_size, audit_post_nums in included:
        start, length = line_offsets[keyword]
        post_nums_str = ",".join(str(n) for n in audit_post_nums[:5]) + ",..."
        print(f"  {theme_key:<13} {keyword:<28} {post_nums_str:<32} {start:>6}  {length:>5}")

    if skipped:
        print(f"\n=== Skipped ({len(skipped)}) ===")
        for theme_key, keyword, n, reason in skipped:
            print(f"  {theme_key:<13} {keyword:<28} ({n} class) — {reason}")

    print(f"\nTotal auditable: {len(included)} keywords")


if __name__ == "__main__":
    main()
