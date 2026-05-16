#!/usr/bin/env python3
"""Build the 6-layer keyword context spot-check audit (2026-05-15).

This audits the project's core measurement assumption: that production
keywords accurately track their themes. It is a precision + temporal-
comparability audit, not an LLM chart series.

Generates (under spotcheck_2026-05-15/):
  gold_sheet.md          ~72 posts for the HUMAN reviewer to blind-code
  manifest.json          private sample_id -> metadata map (NOT shown to agents)
  batches/batch_*.md      agent-ready dual-rubric classification chunks
  corpus_diagnostics.md   Layer-4 SQL checks (denominator / temporal artifacts)

Each agent codes every post under TWO rubrics in one pass:
  - topical : the project's locked standard ("when in doubt YES")
  - strict  : an adversarial reading ("when in doubt NO")
The gap between them is a primary finding.

After agents produce results/*_results.txt, run spotcheck_v2_score.py.
"""
from __future__ import annotations

import argparse
import json
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from datetime import date, datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import load_keyword_communities, load_keywords  # noqa: E402
from src.db.operations import EXCLUDED_AUTHORS  # noqa: E402

ROOT = Path(__file__).parent.parent.parent
DB = ROOT / "data" / "tracker.db"
OUTDIR = Path(__file__).parent / "spotcheck_2026-05-15"
THEME_DEFS_PATH = Path(__file__).parent / "theme_definitions.yaml"

SEED = 20260515
THEMES = ["therapy", "consciousness", "addiction", "romance", "sexual_erp", "rupture"]
ERAS = ["2023", "2024", "2025", "2026"]
BODY_CHARS = 1100
GOLD_BODY_CHARS = 1600

FP_TAXONOMY = """\
  wrong-referent   keyword is about a HUMAN partner / human experience, no AI
  bot-card         keyword is a character-card trait tag, no first-person framing
  third-party      observer / journalism / research solicitation, no personal stake
  ironic-rejection author explicitly denies the frame ("it is NOT my AI boyfriend")
  non-ai-literal   keyword used in a literal non-AI sense (e.g. "good grief" idiom)
  rp-internal      keyword only appears inside in-character roleplay narration
  theme-mismatch   post is about AI companionship but a DIFFERENT theme, not this one
  thin-removed     body is [removed]/[deleted]/empty and the title alone is too vague
  ambiguous        genuinely cannot tell (use only when nothing else fits)"""


def clean(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def truncate(text: str, n: int) -> str:
    text = clean(text)
    return text if len(text) <= n else text[:n] + " […]"


def placeholders(items) -> str:
    return ",".join("?" for _ in items)


def load_theme_defs() -> dict:
    with open(THEME_DEFS_PATH) as f:
        return yaml.safe_load(f)


# ----------------------------------------------------------------------
# Rubric text shared by every precision/comment batch header
# ----------------------------------------------------------------------
def rubric_block() -> str:
    return """\
You will code every item under TWO rubrics. Read the post once, then give
both verdicts.

TOPICAL rubric (the project's locked standard):
  A post counts YES if it is thematically about the theme in an AI-companion
  context — even without graphic or first-person detail. A user defending
  their AI relationship from critics still counts. For [removed]/[deleted]
  bodies, judge on the title + subreddit. When genuinely in doubt, code YES.

STRICT rubric (adversarial reading):
  A post counts YES only if it gives positive, directly-stated evidence that
  the post is about THIS theme as a real AI-companion matter — the theme is
  the actual subject, not incidental, and the referent is clearly an AI
  companion. Code NO for: title-only/[removed] posts where the theme is only
  inferable, third-party/observer framing, the theme being a side mention,
  ambiguous cases. When in doubt, code NO.

A verdict can be YES/NO/BORD (borderline). The two rubrics will often agree;
where they differ, that gap is the point of the audit — do not force them to
match.

When EITHER verdict is NO or BORD, give the single best fp= reason code:
""" + FP_TAXONOMY


def precision_header(theme: str, tdef: dict, kind_note: str) -> str:
    d = tdef[theme]
    return f"""# Spot-check classification batch — theme: {theme}

{kind_note}

Each item below is a Reddit post from an AI-companion community. You do NOT
see which keyword matched it or whether it is currently tagged — code it
fresh, on the text alone.

## Theme being tested: {d['name']}

DEFINITION (counts as the theme):
{d['definition'].rstrip()}

EXCLUDES (does NOT count):
{d['excludes'].rstrip()}

## Rubrics

{rubric_block()}

## Output

Write your answers to a file at:
  analysis/keyword_pipeline/spotcheck_2026-05-15/results/{{BATCH}}_results.txt

One line per item, EXACTLY this pipe format, nothing else:
  ID-XXXX | topical=YES | strict=NO | fp=thin-removed
Use fp=- when both verdicts are YES. Keep the IDs in order.

---

## Posts

"""


def negspace_header(tdefs: dict) -> str:
    lines = ["# Spot-check batch — negative-space recall\n"]
    lines.append(
        "These posts are from AI-companion communities and are currently "
        "NOT tagged by any keyword. For each, decide which of the six themes "
        "(if any) the post is genuinely about, under the TOPICAL reading "
        "(thematically about it in an AI-companion context; when in doubt, "
        "lean YES).\n"
    )
    lines.append("## The six themes\n")
    for t in THEMES:
        d = tdefs[t]
        one = clean(d["definition"]).split(". ")[0]
        lines.append(f"- **{t}** ({d['name']}): {one}.")
    lines.append(
        "\n## Output\n\nWrite to "
        "analysis/keyword_pipeline/spotcheck_2026-05-15/results/{BATCH}_results.txt\n"
        "One line per item, EXACTLY:\n"
        "  NS-XXXX | themes=rupture,romance | ai_referent=YES\n"
        "Use themes=none when no theme applies. ai_referent=YES if the post "
        "is about the author's own AI companion/use, else NO.\n\n---\n\n## Posts\n"
    )
    return "\n".join(lines)


def post_entry(sid: str, row, body_chars: int) -> str:
    body = truncate(row["selftext"], body_chars) or "(no body — image/link/removed)"
    return (
        f"### {sid}\n"
        f"r/{row['subreddit']} · {row['post_date']}\n\n"
        f"**Title:** {clean(row['title']) or '(no title)'}\n\n"
        f"**Body:** {body}\n\n---\n\n"
    )


def comment_entry(sid: str, row, body_chars: int) -> str:
    body = truncate(row["body"], body_chars) or "(empty)"
    return (
        f"### {sid}\n"
        f"r/{row['subreddit']} · {row['post_date']} · comment on post: "
        f"\"{clean(row['post_title']) or '(no title)'}\"\n\n"
        f"**Comment:** {body}\n\n---\n\n"
    )


# ----------------------------------------------------------------------
# Sampling
# ----------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-keyword", type=int, default=20)
    ap.add_argument("--comments-per-theme", type=int, default=60)
    ap.add_argument("--negspace-per-era", type=int, default=40)
    ap.add_argument("--event-spikes", type=int, default=8)
    ap.add_argument("--event-per-spike", type=int, default=8)
    ap.add_argument("--gold-per-theme", type=int, default=12)
    ap.add_argument("--chunk", type=int, default=40)
    args = ap.parse_args()

    rng = random.Random(SEED)
    OUTDIR.mkdir(parents=True, exist_ok=True)
    (OUTDIR / "batches").mkdir(exist_ok=True)
    (OUTDIR / "results").mkdir(exist_ok=True)

    tdefs = load_theme_defs()
    kw_map = {c["name"]: list(c.get("terms", [])) for c in load_keywords()}
    eligible = [c["subreddit"] for c in load_keyword_communities()]
    excl = list(EXCLUDED_AUTHORS)

    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row

    manifest: dict[str, dict] = {}
    sid_counter = {"P": 0, "C": 0, "N": 0}

    def new_sid(prefix: str) -> str:
        sid_counter[prefix] += 1
        letter = {"P": "ID", "C": "CM", "N": "NS"}[prefix]
        return f"{letter}-{sid_counter[prefix]:04d}"

    # ---- distinct-keyword count per (post, theme) for the fragility stratum
    frag = {}
    for r in conn.execute(
        f"""SELECT post_id, category, COUNT(DISTINCT matched_term) n
            FROM post_keyword_tags WHERE source='post'
            AND subreddit IN ({placeholders(eligible)})
            GROUP BY post_id, category""",
        eligible,
    ):
        frag[(r["post_id"], r["category"])] = r["n"]

    # ---- per-keyword precision sample -----------------------------------
    # theme -> list of (sid, row) ; row carries selftext/title/etc.
    precision: dict[str, list] = defaultdict(list)
    seen_post: dict[str, set] = defaultdict(set)  # theme -> post_ids already sampled
    zero_hit: list[tuple[str, str]] = []

    for theme in THEMES:
        for term in kw_map.get(theme, []):
            rows = conn.execute(
                f"""SELECT DISTINCT p.id, p.subreddit, p.title, p.selftext, p.author,
                           t.post_date
                    FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                    WHERE t.source='post' AND t.category=? AND t.matched_term=?
                      AND t.subreddit IN ({placeholders(eligible)})
                      AND (p.author IS NULL OR p.author NOT IN ({placeholders(excl)}))""",
                [theme, term, *eligible, *excl],
            ).fetchall()
            if not rows:
                zero_hit.append((theme, term))
                continue
            picked = rows if len(rows) <= args.per_keyword else rng.sample(rows, args.per_keyword)
            for row in picked:
                if row["id"] in seen_post[theme]:
                    # same post already sampled for this theme via another keyword:
                    # record the extra term on its manifest entry, don't double-list
                    for sid, r2 in precision[theme]:
                        if r2["id"] == row["id"]:
                            manifest[sid]["terms"].append(term)
                            break
                    continue
                seen_post[theme].add(row["id"])
                sid = new_sid("P")
                precision[theme].append((sid, row))
                manifest[sid] = {
                    "kind": "precision",
                    "theme": theme,
                    "terms": [term],
                    "post_id": row["id"],
                    "subreddit": row["subreddit"],
                    "year": str(row["post_date"])[:4],
                    "source": "post",
                    "n_kw_theme": frag.get((row["id"], theme), 1),
                    "is_gold": False,
                    "spike_date": None,
                }

    # ---- event-spike sample (merged into precision pool) ----------------
    spikes = conn.execute(
        f"""SELECT t.category, t.post_date, COUNT(DISTINCT t.post_id) n
            FROM post_keyword_tags t
            WHERE t.source='post' AND t.subreddit IN ({placeholders(eligible)})
            GROUP BY t.category, t.post_date HAVING n >= 20
            ORDER BY n DESC LIMIT ?""",
        [*eligible, args.event_spikes],
    ).fetchall()
    for sp in spikes:
        theme = sp["category"]
        rows = conn.execute(
            f"""SELECT DISTINCT p.id, p.subreddit, p.title, p.selftext, p.author,
                       t.post_date
                FROM post_keyword_tags t JOIN posts p ON p.id = t.post_id
                WHERE t.source='post' AND t.category=? AND t.post_date=?
                  AND t.subreddit IN ({placeholders(eligible)})
                  AND (p.author IS NULL OR p.author NOT IN ({placeholders(excl)}))""",
            [theme, sp["post_date"], *eligible, *excl],
        ).fetchall()
        picked = rows if len(rows) <= args.event_per_spike else rng.sample(rows, args.event_per_spike)
        for row in picked:
            if row["id"] in seen_post[theme]:
                for sid, r2 in precision[theme]:
                    if r2["id"] == row["id"]:
                        manifest[sid]["spike_date"] = sp["post_date"]
                        break
                continue
            seen_post[theme].add(row["id"])
            sid = new_sid("P")
            precision[theme].append((sid, row))
            manifest[sid] = {
                "kind": "event", "theme": theme, "terms": ["(event-spike)"],
                "post_id": row["id"], "subreddit": row["subreddit"],
                "year": str(sp["post_date"])[:4], "source": "post",
                "n_kw_theme": frag.get((row["id"], theme), 1),
                "is_gold": False, "spike_date": sp["post_date"],
            }

    # ---- comment-tag sample ---------------------------------------------
    comments: dict[str, list] = defaultdict(list)
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT DISTINCT c.id, c.body, h.subreddit, h.post_date,
                       p.title AS post_title
                FROM comment_keyword_hits h
                JOIN comments c ON c.id = h.comment_id
                LEFT JOIN posts p ON p.id = h.post_id
                WHERE h.category=? AND h.subreddit IN ({placeholders(eligible)})""",
            [theme, *eligible],
        ).fetchall()
        picked = rows if len(rows) <= args.comments_per_theme else rng.sample(rows, args.comments_per_theme)
        for row in picked:
            sid = new_sid("C")
            comments[theme].append((sid, row))
            manifest[sid] = {
                "kind": "comment", "theme": theme, "terms": ["(comment)"],
                "post_id": None, "comment_id": row["id"], "subreddit": row["subreddit"],
                "year": str(row["post_date"])[:4], "source": "comment",
                "n_kw_theme": None, "is_gold": False, "spike_date": None,
            }

    # ---- negative-space recall sample (era-stratified) ------------------
    negspace: list = []
    for era in ERAS:
        rows = conn.execute(
            f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                       date(p.created_utc,'unixepoch') post_date
                FROM posts p
                LEFT JOIN (SELECT DISTINCT post_id FROM post_keyword_tags
                           WHERE source='post') tg ON tg.post_id = p.id
                WHERE tg.post_id IS NULL
                  AND p.subreddit IN ({placeholders(eligible)})
                  AND (p.author IS NULL OR p.author NOT IN ({placeholders(excl)}))
                  AND p.created_utc >= strftime('%s', ?)
                  AND p.created_utc <  strftime('%s', ?)
                ORDER BY RANDOM() LIMIT 4000""",
            [*eligible, *excl, f"{era}-01-01", f"{int(era)+1}-01-01"],
        ).fetchall()
        picked = rows if len(rows) <= args.negspace_per_era else rng.sample(rows, args.negspace_per_era)
        for row in picked:
            sid = new_sid("N")
            negspace.append((sid, row))
            manifest[sid] = {
                "kind": "negspace", "theme": None, "terms": [],
                "post_id": row["id"], "subreddit": row["subreddit"],
                "year": era, "source": "post", "n_kw_theme": None,
                "is_gold": False, "spike_date": None,
            }

    # ---- gold anchor: pick gold-per-theme from the precision pool -------
    gold_ids: list[str] = []
    for theme in THEMES:
        pool = list(precision[theme])
        rng.shuffle(pool)
        chosen, used_terms, used_years = [], set(), Counter()
        # greedy: prefer unseen primary term + spread years
        for sid, row in pool:
            if len(chosen) >= args.gold_per_theme:
                break
            term0 = manifest[sid]["terms"][0]
            yr = manifest[sid]["year"]
            if term0 in used_terms and used_years[yr] >= 4:
                continue
            chosen.append((sid, row))
            used_terms.add(term0)
            used_years[yr] += 1
        for sid, row in pool:
            if len(chosen) >= args.gold_per_theme:
                break
            if (sid, row) not in chosen:
                chosen.append((sid, row))
        for sid, row in chosen[: args.gold_per_theme]:
            manifest[sid]["is_gold"] = True
            gold_ids.append(sid)

    # ------------------------------------------------------------------
    # WRITE batch files
    # ------------------------------------------------------------------
    batches: dict[str, list[str]] = {}

    def write_batches(prefix: str, theme: str | None, items: list, header: str,
                      entry_fn, body_chars: int):
        chunks = [items[i:i + args.chunk] for i in range(0, len(items), args.chunk)]
        for ci, chunk in enumerate(chunks, 1):
            name = f"batch_{prefix}_{ci:02d}" if theme is None else f"batch_{prefix}_{theme}_{ci:02d}"
            body = header.replace("{BATCH}", name)
            for sid, row in chunk:
                body += entry_fn(sid, row, body_chars)
            (OUTDIR / "batches" / f"{name}.md").write_text(body, encoding="utf-8")
            batches[f"{name}.md"] = [sid for sid, _ in chunk]

    for theme in THEMES:
        items = precision[theme]
        rng.shuffle(items)
        note = ("Mixed sample: per-keyword precision posts plus event-spike "
                "posts. Code every item the same way.")
        write_batches("precision", theme, items, precision_header(theme, tdefs, note),
                      post_entry, BODY_CHARS)

    for theme in THEMES:
        items = comments[theme]
        if not items:
            continue
        note = ("These are COMMENTS (not posts) whose text was keyword-matched "
                "and credited to the parent post. Code the comment text.")
        write_batches("comments", theme, items, precision_header(theme, tdefs, note),
                      comment_entry, BODY_CHARS)

    rng.shuffle(negspace)
    write_batches("negspace", None, negspace, negspace_header(tdefs), post_entry, BODY_CHARS)

    # ------------------------------------------------------------------
    # WRITE gold sheet (human)
    # ------------------------------------------------------------------
    gold_lines = [
        "# Gold-anchor coding sheet — keyword spot-check (2026-05-15)\n",
        "You are the human ground truth. For each post below, decide whether it "
        "is **genuinely about the named theme, in an AI-companion context**.\n",
        "Code each as **YES**, **NO**, or **BORD** (borderline). Judge as an "
        "honest reader: is this post really about that theme as it concerns the "
        "author's own AI companion / AI use? For `[removed]`/empty bodies, judge "
        "on the title. Don't overthink — your gut read is the anchor.\n",
        "Write your verdict on the `Verdict:` line. ~72 posts; ~30-40 min.\n",
        "---\n",
    ]
    gold_rows = []
    for theme in THEMES:
        for sid in gold_ids:
            if manifest[sid]["theme"] != theme:
                continue
            row = next(r for s, r in precision[theme] if s == sid)
            gold_rows.append((sid, theme, row))
    for sid, theme, row in gold_rows:
        d = tdefs[theme]
        gold_lines.append(
            f"## {sid} — theme: **{d['name']}**\n\n"
            f"r/{row['subreddit']} · {row['post_date']}\n\n"
            f"_Theme means:_ {clean(d['definition']).split('. ')[0]}.\n\n"
            f"**Title:** {clean(row['title']) or '(no title)'}\n\n"
            f"**Body:** {truncate(row['selftext'], GOLD_BODY_CHARS) or '(no body — image/link/removed)'}\n\n"
            f"Verdict: \n\n---\n"
        )
    (OUTDIR / "gold_sheet.md").write_text("\n".join(gold_lines), encoding="utf-8")

    # ------------------------------------------------------------------
    # WRITE manifest
    # ------------------------------------------------------------------
    manifest_out = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "seed": SEED,
        "params": vars(args),
        "themes": THEMES,
        "eligible_subs": eligible,
        "zero_hit_keywords": [f"{t}:{k}" for t, k in zero_hit],
        "gold_ids": gold_ids,
        "batches": batches,
        "samples": manifest,
    }
    (OUTDIR / "manifest.json").write_text(json.dumps(manifest_out, indent=1), encoding="utf-8")

    conn.close()

    # ------------------------------------------------------------------
    # summary
    # ------------------------------------------------------------------
    n_prec = sum(len(v) for v in precision.values())
    n_com = sum(len(v) for v in comments.values())
    print(f"output dir: {OUTDIR}")
    print(f"precision posts : {n_prec}  (incl. event-spike)")
    print(f"comment items   : {n_com}")
    print(f"negspace posts  : {len(negspace)}")
    print(f"gold posts      : {len(gold_ids)}")
    print(f"batch files     : {len(batches)}")
    print(f"total classified items: {n_prec + n_com + len(negspace)}")
    if zero_hit:
        print(f"zero-hit config keywords: {len(zero_hit)} -> {zero_hit}")


if __name__ == "__main__":
    main()
