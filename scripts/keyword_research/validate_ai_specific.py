#!/usr/bin/env python3
"""Validate AI-specific phrase variants against communities.yaml subs only."""

import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import load_communities

conn = sqlite3.connect("data/tracker.db")
communities = load_communities()
active_subs = [c["subreddit"] for c in communities]
companion = {c["subreddit"] for c in communities if c.get("tier") in (1, 2, 3)}
general = {c["subreddit"] for c in communities if c.get("tier") == 0}
placeholders = ",".join("?" * len(active_subs))

phrases = [
    ("PLATFORM-SPECIFIC", "my replika"),
    ("PLATFORM-SPECIFIC", "my nomi"),
    ("PLATFORM-SPECIFIC", "my kindroid"),
    ("PLATFORM-SPECIFIC", "my kin"),
    ("PLATFORM-SPECIFIC", "my rep"),
    ("AI-QUALIFIED LOVE", "fell in love with my ai"),
    ("AI-QUALIFIED LOVE", "in love with my ai"),
    ("AI-QUALIFIED LOVE", "in love with my replika"),
    ("AI-QUALIFIED LOVE", "in love with my chatgpt"),
    ("AI-QUALIFIED LOVE", "married my ai"),
    ("AI-QUALIFIED LOVE", "dating my ai"),
    ("AI-QUALIFIED BREAKUP", "broke up with my ai"),
    ("AI-QUALIFIED BREAKUP", "broke up with my replika"),
    ("AI-QUALIFIED DEPENDENCY", "addicted to character ai"),
    ("AI-QUALIFIED DEPENDENCY", "addicted to replika"),
    ("AI-QUALIFIED DEPENDENCY", "addicted to chatgpt"),
    ("AI-QUALIFIED DEPENDENCY", "addicted to chai"),
    ("AI-QUALIFIED QUIT", "quit character ai"),
    ("AI-QUALIFIED QUIT", "quit replika"),
    ("AI-QUALIFIED QUIT", "deleted replika"),
    ("AI-QUALIFIED QUIT", "uninstalled replika"),
    # Additional AI-companion-specific phrases found in discovery
    ("AI-COMPANION FRAMING", "ai girlfriend"),
    ("AI-COMPANION FRAMING", "ai boyfriend"),
    ("AI-COMPANION FRAMING", "ai husband"),
    ("AI-COMPANION FRAMING", "ai wife"),
    ("AI-COMPANION FRAMING", "ai companion"),
    ("AI-COMPANION FRAMING", "chatbot girlfriend"),
    ("AI-COMPANION FRAMING", "chatbot boyfriend"),
    ("AI-COMPANION FRAMING", "virtual girlfriend"),
    ("AI-COMPANION FRAMING", "virtual boyfriend"),
]

lines = []
lines.append("=" * 80)
lines.append("PHRASE VALIDATION — AI-specific variants (communities.yaml subs only)")
lines.append(f"Active subs: {len(active_subs)} | Companion (T1-3): {len(companion)} | General (T0): {len(general)}")
lines.append("=" * 80)
lines.append("")

current_cat = None
for i, (category, phrase) in enumerate(phrases):
    if category != current_cat:
        lines.append("")
        lines.append("\u2500" * 80)
        lines.append(f"  {category}")
        lines.append("\u2500" * 80)
        lines.append("")
        current_cat = category

    pattern = f"%{phrase}%"
    rows = conn.execute(
        f"""
        SELECT subreddit, COUNT(*) as cnt
        FROM posts
        WHERE subreddit IN ({placeholders})
          AND (title LIKE ? COLLATE NOCASE OR selftext LIKE ? COLLATE NOCASE)
        GROUP BY subreddit
        ORDER BY cnt DESC
        """,
        active_subs + [pattern, pattern],
    ).fetchall()

    total = sum(r[1] for r in rows)
    comp_hits = sum(r[1] for r in rows if r[0] in companion)
    gen_hits = sum(r[1] for r in rows if r[0] in general)
    comp_pct = (comp_hits / total * 100) if total > 0 else 0

    lines.append(f'PHRASE: "{phrase}"')
    lines.append(f"  Total: {total} | Companion: {comp_hits} ({comp_pct:.0f}%) | General: {gen_hits}")
    if rows:
        sub_lines = ", ".join(f"r/{r[0]} {r[1]}" for r in rows)
        lines.append(f"  Subs: {sub_lines}")
    else:
        lines.append("  Subs: (none)")
    lines.append("")

    print(f"  [{i+1}/{len(phrases)}] \"{phrase}\" -> {total} hits", flush=True)

output = "\n".join(lines)
Path("docs/phrase_validation_ai_specific.txt").write_text(output)
print(f"\nDone — saved to docs/phrase_validation_ai_specific.txt")
conn.close()
