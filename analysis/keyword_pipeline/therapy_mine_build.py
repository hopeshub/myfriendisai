#!/usr/bin/env python3
"""Build therapy keyword-mining batches from the spot-check audit's confirmed
therapy posts.

Anchor set = every post the audit's blind dual-rubric classification coded
topical=YES AND strict=YES for the therapy theme (main precision batches +
the n=100 confirmatory batches). These are unambiguous AI-as-therapy posts;
mining their vocabulary surfaces candidate keywords.

Outputs batch_therapymine_*.md under spotcheck_2026-05-15/therapy_mine/.
"""
from __future__ import annotations

import json
import re
import sqlite3
import sys
from pathlib import Path

THISDIR = Path(__file__).parent
sys.path.insert(0, str(THISDIR.parent.parent))

ROOT = THISDIR.parent.parent
DB = ROOT / "data" / "tracker.db"
SC = THISDIR / "spotcheck_2026-05-15"
OUT = SC / "therapy_mine"
CHUNK = 35


def clean(t):
    return re.sub(r"\s+", " ", t or "").strip()


def both_yes_ids() -> list[str]:
    """post_ids of therapy posts coded topical=YES and strict=YES."""
    # verdicts from all result files
    v = {}
    for f in (SC / "results").glob("*_results.txt"):
        for ln in f.read_text(errors="replace").splitlines():
            m = re.search(r"(ID-\d{4}).*topical=(\w+).*strict=(\w+)", ln)
            if m:
                v[m.group(1)] = (m.group(2)[:3], m.group(3)[:3])
    ids = []
    # main manifest: therapy precision samples
    man = json.loads((SC / "manifest.json").read_text())
    for sid, s in man["samples"].items():
        if s.get("theme") == "therapy" and s.get("kind") in ("precision", "event"):
            if v.get(sid) == ("YES", "YES"):
                ids.append(s["post_id"])
    # confirm manifest: emotional support + therapeutic (all therapy theme)
    cm = json.loads((SC / "confirm_manifest.json").read_text())
    for sid, s in cm["samples"].items():
        if s["theme"] == "therapy" and v.get(sid) == ("YES", "YES"):
            ids.append(s["post_id"])
    return list(dict.fromkeys(ids))


HEADER = """# Therapy keyword mining — batch {BATCH}

Every post below was independently confirmed (blind, dual-rubric) to be about
**a person using an AI for therapy / mental-health support / as a therapist
substitute** — venting, coping, processing anxiety/depression/grief, or
treating the AI as a counsellor.

The current keyword set catches this theme at only ~64% precision because its
two biggest keywords (`emotional support`, `therapeutic`) are generic. We need
**better keywords** — phrases that are specific to AI-as-therapy use.

## Your task

Read all {N} posts. Extract the recurring **vocabulary** a keyword search could
use to find posts like these:

1. Propose candidate phrases — 1–4 words each — that signal AI-as-therapy use.
2. Strongly prefer phrases **specific** to this theme — ones unlikely to fire
   on romance, rupture, addiction, or generic AI-companion chatter. A phrase
   that also matches "the model's therapeutic tone is annoying" or "emotional
   support animal" is a bad candidate; say so if you propose it anyway.
3. For each candidate, give: the phrase, why it signals AI-as-therapy, and
   roughly how many of the posts below contain it.
4. Note any phrasing pattern you see a lot that is hard to turn into a clean
   keyword (this tells us where the theme is structurally hard to catch).

Output a ranked list (most promising first). Write it to:
  analysis/keyword_pipeline/spotcheck_2026-05-15/therapy_mine/{BATCH}_mined.md

---

## Posts

"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    ids = both_yes_ids()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    rows = []
    for pid in ids:
        r = conn.execute(
            "SELECT id, subreddit, title, selftext, date(created_utc,'unixepoch') d "
            "FROM posts WHERE id=?", (pid,)).fetchone()
        if r:
            rows.append(r)
    conn.close()

    chunks = [rows[i:i + CHUNK] for i in range(0, len(rows), CHUNK)]
    for ci, chunk in enumerate(chunks, 1):
        name = f"batch_therapymine_{ci:02d}"
        body = HEADER.replace("{BATCH}", name).replace("{N}", str(len(chunk)))
        for i, r in enumerate(chunk, 1):
            txt = clean(r["selftext"])
            if len(txt) > 1500:
                txt = txt[:1500] + " […]"
            body += (f"### {i}. r/{r['subreddit']} · {r['d']}\n\n"
                     f"**Title:** {clean(r['title']) or '(none)'}\n\n"
                     f"**Body:** {txt or '(no body)'}\n\n---\n\n")
        (OUT / f"{name}.md").write_text(body, encoding="utf-8")
    print(f"anchor posts: {len(rows)}  ->  {len(chunks)} mining batches in {OUT}")


if __name__ == "__main__":
    main()
