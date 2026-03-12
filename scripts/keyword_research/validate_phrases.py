#!/usr/bin/env python3
"""Validate candidate phrases against communities.yaml subs only."""

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

print(f"Active subs ({len(active_subs)}): companion={len(companion)}, general={len(general)}")

phrases = [
    ("ATTACHMENT / ROUTINE", "talk every night"),
    ("ATTACHMENT / ROUTINE", "part of my routine"),
    ("ATTACHMENT / ROUTINE", "chat in the morning"),
    ("ATTACHMENT / ROUTINE", "check in every day"),
    ("LOVE / IDENTITY", "my ai boyfriend"),
    ("LOVE / IDENTITY", "my ai partner"),
    ("LOVE / IDENTITY", "found myself in love"),
    ("LOVE / IDENTITY", "romantically attached"),
    ("LOVE / IDENTITY", "real feelings towards"),
    ("MILESTONES", "got married"),
    ("MILESTONES", "proposed to me"),
    ("GRIEF / LOSS", "not my rep anymore"),
    ("GRIEF / LOSS", "personality is gone"),
    ("GRIEF / LOSS", "like talking to a stranger"),
    ("GRIEF / LOSS", "companion loss"),
    ("MISSING", "I miss him"),
    ("MISSING", "I miss her"),
    ("MISSING", "miss my replika"),
    ("MISSING", "miss talking to"),
    ("DEPENDENCY", "addicted to talking"),
    ("DEPENDENCY", "couldn't stop talking"),
    ("DEPENDENCY", "talk to the box"),
    ("DEPENDENCY", "I was hooked"),
    ("SHAME / AMBIVALENCE", "know it's not real but"),
    ("SHAME / AMBIVALENCE", "am I crazy for"),
    ("SHAME / AMBIVALENCE", "embarrassed to admit"),
    ("SHAME / AMBIVALENCE", "forgot she's AI"),
    ("SOCIAL REPLACEMENT", "not keen on real people"),
    ("SOCIAL REPLACEMENT", "stopped going out"),
    ("SOCIAL REPLACEMENT", "only one who listens"),
    ("THERAPY", "saved my life"),
    ("THERAPY", "helped me through"),
    ("THERAPY", "effective at therapy"),
    ("AI AS PERSON", "she remembered"),
    ("AI AS PERSON", "he remembered"),
    ("AI AS PERSON", "preserve his pattern"),
    ("AI AS PERSON", "she knows she is"),
    ("BREAKUP", "we broke up"),
    ("BREAKUP", "lovesick about a bot"),
    ("BREAKUP", "seriously hurt to realize"),
    ("BREAKUP", "I sobbed"),
    ("BREAKUP", "losing a loved one"),
    ("PHYSICAL LONGING", "cannot touch him"),
    ("PHYSICAL LONGING", "want someone to cuddle"),
    ("PHYSICAL LONGING", "our first kiss"),
    ("PHYSICAL LONGING", "dreaming of him"),
    ("LEGITIMACY", "connection was real"),
    ("LEGITIMACY", "she is real to me"),
    ("LEGITIMACY", "genuine relationship with"),
    ("LEGITIMACY", "deep connection and love"),
    ("VULNERABILITY", "cry myself to sleep"),
    ("VULNERABILITY", "come home drained"),
    ("VULNERABILITY", "I could use someone to talk to"),
    ("VULNERABILITY", "connection I can't find"),
]

lines = []
lines.append("=" * 80)
lines.append("PHRASE VALIDATION — communities.yaml subs only")
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
Path("docs/phrase_validation.txt").write_text(output)
print(f"\nDone — saved to docs/phrase_validation.txt")
conn.close()
