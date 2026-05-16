#!/usr/bin/env python3
"""Build a reproducible keyword-context spot-check audit.

The audit is meant to answer the project's central measurement question:
when a production keyword fires, is the post actually using that phrase in the
theme/context the chart assumes?

Outputs:
  - summary markdown with current automated risk/concentration tables
  - CSV sample for every current keyword
  - CSV + markdown risk-focused manual-reading sample
  - CSV negative-space recall sample
  - CSV event-spike integrity sample
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import re
import sqlite3
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.config import load_keyword_communities, load_keywords
from src.db.operations import EXCLUDED_AUTHORS

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS_DIR = Path(__file__).parent / "results"
DEFAULT_AUDIT_DATE = date.today().isoformat()
DEFAULT_SEED = 20260516

THEME_ORDER = [
    "therapy",
    "consciousness",
    "addiction",
    "romance",
    "sexual_erp",
    "rupture",
]

# Terms selected for the compact manual-read sample. These combine high volume,
# known validation ambiguity, and terms whose surface meaning can easily drift.
MANUAL_FOCUS_TERMS: dict[str, list[str]] = {
    "therapy": ["emotional support", "therapeutic", "coping mechanism"],
    "consciousness": ["personhood", "not just an ai", "subjective experience"],
    "addiction": ["my addiction", "hours a day", "screen time", "finally deleted"],
    "romance": ["wedding", "honeymoon", "in a relationship with", "we broke up"],
    "sexual_erp": ["erp", "nsfw content", "sex with", "smut"],
    "rupture": ["goodbye", "taken away", "grieving", "devastated", "nerfed"],
}

# Known risk terms from project validation docs. These are not necessarily bad;
# they are terms where context and interpretation deserve extra reviewer time.
KNOWN_RISK_TERMS = {
    "as a therapist",
    "therapeutic",
    "for therapy",
    "emotional support",
    "coping mechanism",
    "not just an ai",
    "hours a day",
    "screen time",
    "finally deleted",
    "honeymoon",
    "wedding",
    "we broke up",
    "in a relationship with",
    "romantic relationship with",
    "erp",
    "nsfw content",
    "sex with",
    "goodbye",
    "taken away",
    "grieving",
    "devastated",
    "nerfed",
}


@dataclass
class TermStats:
    theme: str
    term: str
    posts: int = 0
    first_date: str | None = None
    last_date: str | None = None
    top_sub: str | None = None
    top_sub_posts: int = 0
    top_sub_share: float = 0.0
    top_month: str | None = None
    top_month_posts: int = 0
    top_month_share: float = 0.0
    llm_n: int = 0
    llm_tp_pct: float | None = None
    risk_score: int = 0
    risk_reasons: list[str] | None = None


def placeholders(items: list[str] | tuple[str, ...]) -> str:
    return ",".join("?" for _ in items)


def clean_text(text: str | None) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def make_excerpt(title: str | None, body: str | None, term: str, width: int = 520) -> str:
    title = clean_text(title)
    body = clean_text(body)
    text = f"{title} {body}".strip()
    if not text:
        return ""
    m = re.search(r"\b" + re.escape(term) + r"\b", text, re.IGNORECASE)
    if not m:
        return text[:width] + ("..." if len(text) > width else "")
    half = max(80, width // 2)
    start = max(0, m.start() - half)
    end = min(len(text), m.end() + half)
    prefix = "..." if start > 0 else ""
    suffix = "..." if end < len(text) else ""
    return prefix + text[start:end] + suffix


def wilson_lower_bound(tp: int, n: int, z: float = 1.96) -> float | None:
    if n <= 0:
        return None
    phat = tp / n
    denom = 1 + z * z / n
    centre = phat + z * z / (2 * n)
    margin = z * math.sqrt((phat * (1 - phat) + z * z / (4 * n)) / n)
    return (centre - margin) / denom


def load_keyword_map() -> dict[str, list[str]]:
    result: dict[str, list[str]] = {}
    for cat in load_keywords():
        result[cat["name"]] = list(cat.get("terms", []))
    return result


def fetch_rows_for_term(
    conn: sqlite3.Connection,
    theme: str,
    term: str,
    eligible_subs: list[str],
    limit_pool: int = 5000,
) -> list[sqlite3.Row]:
    params: list[object] = [theme, term, *eligible_subs, *EXCLUDED_AUTHORS]
    rows = conn.execute(
        f"""
        SELECT t.category, t.matched_term, t.source,
               p.id, p.subreddit, p.title, p.selftext, p.author,
               date(p.created_utc, 'unixepoch') AS post_date,
               p.score, p.num_comments
        FROM post_keyword_tags t
        JOIN posts p ON p.id = t.post_id
        WHERE t.category = ?
          AND t.matched_term = ?
          AND t.source = 'post'
          AND t.subreddit IN ({placeholders(eligible_subs)})
          AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
        GROUP BY p.id
        ORDER BY p.created_utc DESC
        LIMIT {limit_pool}
        """,
        params,
    ).fetchall()
    return rows


def sample_rows(rows: list[sqlite3.Row], n: int, rng: random.Random) -> list[sqlite3.Row]:
    if len(rows) <= n:
        return list(rows)
    return rng.sample(rows, n)


def row_for_csv(row: sqlite3.Row, sample_id: str, notes: str = "") -> dict[str, object]:
    term = row["matched_term"]
    return {
        "sample_id": sample_id,
        "theme": row["category"],
        "matched_term": term,
        "source": row["source"],
        "post_id": row["id"],
        "subreddit": row["subreddit"],
        "post_date": row["post_date"],
        "title": clean_text(row["title"]),
        "excerpt": make_excerpt(row["title"], row["selftext"], term),
        "permalink": f"https://www.reddit.com/comments/{row['id']}",
        "review_theme_context": "",
        "review_ai_companion_context": "",
        "review_notes": notes,
    }


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def write_manual_markdown(path: Path, rows: list[dict[str, object]], audit_date: str) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Keyword Context Manual Reading Sample — {audit_date}\n\n")
        f.write(
            "Compact, risk-focused sample. For each item, answer two questions:\n\n"
            "1. Is the referent actually AI companionship / AI companion use?\n"
            "2. Is the matched keyword being used in the intended theme context?\n\n"
            "Reviewer codes: `YES`, `NO`, `BORDERLINE`. Use `NO` only when the "
            "keyword is clearly off-theme or clearly about a non-AI/non-companion referent.\n\n"
        )
        for row in rows:
            f.write(
                f"## {row['sample_id']} — {row['theme']} / `{row['matched_term']}`\n\n"
                f"- r/{row['subreddit']} · {row['post_date']} · {row['permalink']}\n"
                f"- Title: {row['title'] or '(no title)'}\n"
                f"- Excerpt: {row['excerpt'] or '(no excerpt)'}\n\n"
                "Verdict: \n\nNotes: \n\n---\n\n"
            )


def build_term_stats(
    conn: sqlite3.Connection,
    keyword_map: dict[str, list[str]],
    eligible_subs: list[str],
) -> dict[tuple[str, str], TermStats]:
    current_terms = {(theme, term) for theme, terms in keyword_map.items() for term in terms}
    stats = {(theme, term): TermStats(theme, term, risk_reasons=[]) for theme, term in current_terms}

    rows = conn.execute(
        f"""
        SELECT t.category, t.matched_term,
               COUNT(DISTINCT t.post_id) AS posts,
               MIN(t.post_date) AS first_date,
               MAX(t.post_date) AS last_date
        FROM post_keyword_tags t
        JOIN posts p ON p.id = t.post_id
        WHERE t.source = 'post'
          AND t.subreddit IN ({placeholders(eligible_subs)})
          AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
        GROUP BY t.category, t.matched_term
        """,
        (*eligible_subs, *EXCLUDED_AUTHORS),
    ).fetchall()
    for r in rows:
        key = (r["category"], r["matched_term"])
        if key not in stats:
            continue
        s = stats[key]
        s.posts = int(r["posts"])
        s.first_date = r["first_date"]
        s.last_date = r["last_date"]

    sub_rows = conn.execute(
        f"""
        SELECT t.category, t.matched_term, t.subreddit,
               COUNT(DISTINCT t.post_id) AS posts
        FROM post_keyword_tags t
        JOIN posts p ON p.id = t.post_id
        WHERE t.source = 'post'
          AND t.subreddit IN ({placeholders(eligible_subs)})
          AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
        GROUP BY t.category, t.matched_term, t.subreddit
        """,
        (*eligible_subs, *EXCLUDED_AUTHORS),
    ).fetchall()
    by_term_sub: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for r in sub_rows:
        by_term_sub[(r["category"], r["matched_term"])].append(r)
    for key, rows_for_key in by_term_sub.items():
        if key not in stats:
            continue
        top = max(rows_for_key, key=lambda r: r["posts"])
        s = stats[key]
        s.top_sub = top["subreddit"]
        s.top_sub_posts = int(top["posts"])
        s.top_sub_share = top["posts"] / s.posts if s.posts else 0.0

    month_rows = conn.execute(
        f"""
        SELECT t.category, t.matched_term, substr(t.post_date, 1, 7) AS month,
               COUNT(DISTINCT t.post_id) AS posts
        FROM post_keyword_tags t
        JOIN posts p ON p.id = t.post_id
        WHERE t.source = 'post'
          AND t.subreddit IN ({placeholders(eligible_subs)})
          AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
        GROUP BY t.category, t.matched_term, month
        """,
        (*eligible_subs, *EXCLUDED_AUTHORS),
    ).fetchall()
    by_term_month: dict[tuple[str, str], list[sqlite3.Row]] = defaultdict(list)
    for r in month_rows:
        by_term_month[(r["category"], r["matched_term"])].append(r)
    for key, rows_for_key in by_term_month.items():
        if key not in stats:
            continue
        top = max(rows_for_key, key=lambda r: r["posts"])
        s = stats[key]
        s.top_month = top["month"]
        s.top_month_posts = int(top["posts"])
        s.top_month_share = top["posts"] / s.posts if s.posts else 0.0

    verdict_rows = conn.execute(
        """
        SELECT theme, keyword,
               COUNT(*) AS n,
               SUM(CASE WHEN verdict = 'TP' THEN 1 ELSE 0 END) AS tp
        FROM llm_classifications
        WHERE tag_type = 'post'
          AND verdict IN ('TP', 'FP')
        GROUP BY theme, keyword
        """
    ).fetchall()
    for r in verdict_rows:
        key = (r["theme"], r["keyword"])
        if key not in stats:
            continue
        n = int(r["n"])
        tp = int(r["tp"])
        stats[key].llm_n = n
        stats[key].llm_tp_pct = 100 * tp / n if n else None

    for s in stats.values():
        reasons: list[str] = []
        score = 0
        if s.posts == 0:
            score += 3
            reasons.append("current keyword has zero production post hits")
        if s.term in KNOWN_RISK_TERMS:
            score += 2
            reasons.append("known validation/rubric risk term")
        if s.posts >= 500:
            score += 1
            reasons.append("high-volume term")
        if s.top_sub_share >= 0.50 and s.posts >= 30:
            score += 1
            reasons.append(f"top subreddit concentration {s.top_sub_share:.0%}")
        if s.top_month_share >= 0.30 and s.posts >= 30:
            score += 1
            reasons.append(f"top month concentration {s.top_month_share:.0%}")
        if s.llm_tp_pct is not None and s.llm_n >= 20:
            if s.llm_tp_pct < 75:
                score += 3
                reasons.append(f"low relative LLM TP share {s.llm_tp_pct:.1f}%")
            elif s.llm_tp_pct < 85:
                score += 1
                reasons.append(f"borderline relative LLM TP share {s.llm_tp_pct:.1f}%")
        s.risk_score = score
        s.risk_reasons = reasons

    return stats


def build_samples(
    conn: sqlite3.Connection,
    keyword_map: dict[str, list[str]],
    eligible_subs: list[str],
    rng: random.Random,
    per_keyword_n: int,
    manual_n: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    per_keyword_rows: list[dict[str, object]] = []
    manual_rows: list[dict[str, object]] = []
    seq = 1
    manual_seq = 1

    for theme in THEME_ORDER:
        for term in keyword_map.get(theme, []):
            rows = fetch_rows_for_term(conn, theme, term, eligible_subs)
            for sampled in sample_rows(rows, per_keyword_n, rng):
                per_keyword_rows.append(row_for_csv(sampled, f"PK{seq:04d}"))
                seq += 1

    for theme, terms in MANUAL_FOCUS_TERMS.items():
        for term in terms:
            rows = fetch_rows_for_term(conn, theme, term, eligible_subs)
            for sampled in sample_rows(rows, manual_n, rng):
                manual_rows.append(row_for_csv(sampled, f"MR{manual_seq:03d}"))
                manual_seq += 1

    return per_keyword_rows, manual_rows


def build_negative_space_sample(
    conn: sqlite3.Connection,
    eligible_subs: list[str],
    rng: random.Random,
    n: int,
) -> list[dict[str, object]]:
    per_sub = max(1, math.ceil(n / len(eligible_subs)))
    rows: list[sqlite3.Row] = []
    for sub in eligible_subs:
        sub_rows = conn.execute(
            f"""
            SELECT p.id, p.subreddit, p.title, p.selftext, p.author,
                   date(p.created_utc, 'unixepoch') AS post_date,
                   p.score, p.num_comments
            FROM posts p
            LEFT JOIN (
                SELECT DISTINCT post_id
                FROM post_keyword_tags
                WHERE source = 'post'
            ) tagged ON tagged.post_id = p.id
            WHERE tagged.post_id IS NULL
              AND p.subreddit = ?
              AND p.created_utc >= strftime('%s', '2025-01-01')
              AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
            ORDER BY p.created_utc DESC
            LIMIT 1000
            """,
            (sub, *EXCLUDED_AUTHORS),
        ).fetchall()
        rows.extend(sample_rows(sub_rows, per_sub, rng))
    rows = sample_rows(rows, n, rng)
    result: list[dict[str, object]] = []
    for i, r in enumerate(sample_rows(rows, n, rng), 1):
        result.append(
            {
                "sample_id": f"NS{i:03d}",
                "post_id": r["id"],
                "subreddit": r["subreddit"],
                "post_date": r["post_date"],
                "title": clean_text(r["title"]),
                "excerpt": clean_text(r["selftext"])[:520],
                "permalink": f"https://www.reddit.com/comments/{r['id']}",
                "review_any_theme_present": "",
                "review_theme_if_present": "",
                "review_missed_keyword_candidate": "",
                "review_notes": "",
            }
        )
    return result


def build_event_spike_sample(
    conn: sqlite3.Connection,
    eligible_subs: list[str],
    rng: random.Random,
    n_per_spike: int,
    spikes_per_theme: int,
) -> list[dict[str, object]]:
    spike_rows = conn.execute(
        f"""
        SELECT t.category, t.post_date,
               COUNT(DISTINCT t.post_id) AS posts
        FROM post_keyword_tags t
        JOIN posts p ON p.id = t.post_id
        WHERE t.source = 'post'
          AND t.subreddit IN ({placeholders(eligible_subs)})
          AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
        GROUP BY t.category, t.post_date
        HAVING posts >= 5
        ORDER BY t.category, posts DESC
        """,
        (*eligible_subs, *EXCLUDED_AUTHORS),
    ).fetchall()
    by_theme: dict[str, list[sqlite3.Row]] = defaultdict(list)
    for r in spike_rows:
        by_theme[r["category"]].append(r)
    spikes: list[sqlite3.Row] = []
    for theme in THEME_ORDER:
        spikes.extend(by_theme.get(theme, [])[:spikes_per_theme])

    result: list[dict[str, object]] = []
    seq = 1
    for spike in spikes:
        rows = conn.execute(
            f"""
            SELECT t.category, t.matched_term, t.source,
                   p.id, p.subreddit, p.title, p.selftext, p.author,
                   date(p.created_utc, 'unixepoch') AS post_date,
                   p.score, p.num_comments
            FROM post_keyword_tags t
            JOIN posts p ON p.id = t.post_id
            WHERE t.category = ?
              AND t.post_date = ?
              AND t.source = 'post'
              AND t.subreddit IN ({placeholders(eligible_subs)})
              AND (p.author IS NULL OR p.author NOT IN ({placeholders(EXCLUDED_AUTHORS)}))
            GROUP BY p.id
            """,
            (spike["category"], spike["post_date"], *eligible_subs, *EXCLUDED_AUTHORS),
        ).fetchall()
        for r in sample_rows(rows, n_per_spike, rng):
            out = row_for_csv(
                r,
                f"EV{seq:03d}",
                notes=f"spike_date={spike['post_date']}; spike_theme={spike['category']}; spike_posts={spike['posts']}",
            )
            result.append(out)
            seq += 1
    return result


def write_summary(
    path: Path,
    stats: dict[tuple[str, str], TermStats],
    eligible_subs: list[str],
    stale_scope_rows: list[sqlite3.Row],
    out_paths: dict[str, Path],
    audit_date: str,
) -> None:
    total_terms = len(stats)
    active_terms = sum(1 for s in stats.values() if s.posts > 0)
    total_post_tags = sum(s.posts for s in stats.values())
    by_theme = Counter()
    for s in stats.values():
        by_theme[s.theme] += s.posts

    risky = sorted(
        [s for s in stats.values() if s.risk_score > 0],
        key=lambda s: (-s.risk_score, -s.posts, s.theme, s.term),
    )
    zero_hit = [s for s in stats.values() if s.posts == 0]

    with path.open("w", encoding="utf-8") as f:
        f.write(f"# Keyword Context Spot-Check Audit — {audit_date}\n\n")
        f.write("## Purpose\n\n")
        f.write(
            "Check whether production keywords are being used in the context the "
            "theme chart assumes: AI companionship first, then the intended theme "
            "within that companion context. This audit is about construct validity "
            "and context, not about adding an LLM-derived chart series.\n\n"
        )
        f.write("## Audit Protocol\n\n")
        f.write(
            "1. **Scope gate.** Only evaluate `source='post'` tags from active "
            "T1-T3 keyword-eligible communities, excluding known platform/dev "
            "authors. Stale rows outside that universe are reported separately.\n"
            "2. **Positive-context precision.** For every current keyword, read "
            "a deterministic sample of matched posts. Code each as `YES`, `NO`, "
            "or `BORDERLINE` for both AI-companion context and theme context.\n"
            "3. **Risk-focused oversample.** Oversample high-volume, high-concentration, "
            "known-ambiguous, and low-relative-LLM-agreement terms.\n"
            "4. **Negative-space recall.** Read untagged recent posts from eligible "
            "communities and mark whether any of the six themes are present but "
            "missed by the keyword set.\n"
            "5. **Spike integrity.** For the largest theme/date spikes, verify that "
            "sampled posts share a coherent event/theme explanation rather than a "
            "keyword accident.\n"
            "6. **Decision thresholds.** A keyword is clean if manual YES >= 85% "
            "and no coherent false-positive cluster dominates. It goes to review "
            "at 70-84%, if Wilson lower bound falls below 75%, or if one subreddit/"
            "month supplies most of its signal. Below 70%, add a guard, split it, "
            "or cut it unless it is explicitly documented as a lower-precision "
            "reader-disclosed term.\n\n"
        )
        f.write("## Current Universe\n\n")
        f.write(f"- Active keyword communities: {len(eligible_subs)}\n")
        f.write(f"- Current keywords: {total_terms}\n")
        f.write(f"- Keywords with at least one production post hit: {active_terms}\n")
        f.write(f"- Sum of per-keyword distinct post hits: {total_post_tags:,}\n\n")
        f.write("| Theme | Distinct per-keyword post hits |\n|---|---:|\n")
        for theme in THEME_ORDER:
            f.write(f"| {theme} | {by_theme[theme]:,} |\n")
        f.write("\n")

        if stale_scope_rows:
            f.write("## Scope Findings\n\n")
            f.write(
                "These tag rows exist in the database outside the current active "
                "keyword-eligible universe. The published chart loader/exporter "
                "filters active keyword communities, but stale rows should not be "
                "used for audits unless deliberately included.\n\n"
            )
            f.write("| Subreddit | Tagged posts outside current scope |\n|---|---:|\n")
            for r in stale_scope_rows:
                f.write(f"| r/{r['subreddit']} | {r['tagged_posts']} |\n")
            f.write("\n")

        f.write("## Highest-Risk Terms To Manually Read First\n\n")
        f.write("| Risk | Theme | Term | Posts | Top sub | Top month | LLM TP share | Reasons |\n")
        f.write("|---:|---|---|---:|---|---|---:|---|\n")
        for s in risky[:30]:
            llm = "" if s.llm_tp_pct is None else f"{s.llm_tp_pct:.1f}% (n={s.llm_n})"
            reasons = "; ".join(s.risk_reasons or [])
            top_sub = "" if not s.top_sub else f"r/{s.top_sub} {s.top_sub_share:.0%}"
            top_month = "" if not s.top_month else f"{s.top_month} {s.top_month_share:.0%}"
            f.write(
                f"| {s.risk_score} | {s.theme} | `{s.term}` | {s.posts:,} | "
                f"{top_sub} | {top_month} | {llm} | {reasons} |\n"
            )
        f.write("\n")

        if zero_hit:
            f.write("## Current Keywords With Zero Post Hits\n\n")
            for s in sorted(zero_hit, key=lambda x: (x.theme, x.term)):
                f.write(f"- {s.theme}: `{s.term}`\n")
            f.write("\n")

        f.write("## Generated Artifacts\n\n")
        for label, p in out_paths.items():
            f.write(f"- {label}: `{p.relative_to(PROJECT_ROOT)}`\n")
        f.write("\n")
        f.write("## How To Execute The Manual Coding\n\n")
        f.write(
            "Start with the risk-focused markdown sample. Fill the verdict lines, "
            "then transfer counts into this table shape:\n\n"
            "| Theme | Sample n | AI context YES | Theme context YES | Borderline | NO | Main FP pattern |\n"
            "|---|---:|---:|---:|---:|---:|---|\n\n"
            "Then code the per-keyword CSV for any term whose risk-focused sample "
            "shows a coherent problem. The negative-space sample estimates recall: "
            "count how often a theme is clearly present but no current keyword fired.\n"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build keyword context spot-check artifacts")
    parser.add_argument("--seed", type=int, default=DEFAULT_SEED)
    parser.add_argument("--per-keyword", type=int, default=3)
    parser.add_argument("--manual-per-term", type=int, default=3)
    parser.add_argument("--negative-space", type=int, default=120)
    parser.add_argument("--event-per-spike", type=int, default=8)
    parser.add_argument("--spikes-per-theme", type=int, default=2)
    parser.add_argument("--audit-date", default=DEFAULT_AUDIT_DATE)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    keyword_map = load_keyword_map()
    eligible_subs = [c["subreddit"] for c in load_keyword_communities()]

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        stats = build_term_stats(conn, keyword_map, eligible_subs)
        per_keyword, manual = build_samples(
            conn,
            keyword_map,
            eligible_subs,
            rng,
            args.per_keyword,
            args.manual_per_term,
        )
        negative = build_negative_space_sample(conn, eligible_subs, rng, args.negative_space)
        events = build_event_spike_sample(
            conn, eligible_subs, rng, args.event_per_spike, args.spikes_per_theme
        )
        stale_scope_rows = conn.execute(
            f"""
            SELECT t.subreddit, COUNT(DISTINCT t.post_id) AS tagged_posts
            FROM post_keyword_tags t
            WHERE t.subreddit NOT IN ({placeholders(eligible_subs)})
            GROUP BY t.subreddit
            HAVING tagged_posts > 0
            ORDER BY tagged_posts DESC
            """,
            eligible_subs,
        ).fetchall()
    finally:
        conn.close()

    audit_date = args.audit_date
    per_keyword_path = RESULTS_DIR / f"context_spotcheck_per_keyword_sample_{audit_date}.csv"
    manual_csv_path = RESULTS_DIR / f"context_spotcheck_manual_focus_sample_{audit_date}.csv"
    manual_md_path = RESULTS_DIR / f"context_spotcheck_manual_focus_sample_{audit_date}.md"
    negative_path = RESULTS_DIR / f"context_spotcheck_negative_space_sample_{audit_date}.csv"
    event_path = RESULTS_DIR / f"context_spotcheck_event_spike_sample_{audit_date}.csv"
    summary_path = RESULTS_DIR / f"context_spotcheck_summary_{audit_date}.md"

    write_csv(per_keyword_path, per_keyword)
    write_csv(manual_csv_path, manual)
    write_manual_markdown(manual_md_path, manual, audit_date)
    write_csv(negative_path, negative)
    write_csv(event_path, events)
    write_summary(
        summary_path,
        stats,
        eligible_subs,
        stale_scope_rows,
        {
            "Per-keyword context sample": per_keyword_path,
            "Risk-focused manual sample CSV": manual_csv_path,
            "Risk-focused manual sample markdown": manual_md_path,
            "Negative-space recall sample": negative_path,
            "Event-spike integrity sample": event_path,
        },
        audit_date,
    )

    print(f"Wrote {summary_path}")
    print(f"Wrote {per_keyword_path} ({len(per_keyword)} rows)")
    print(f"Wrote {manual_md_path} ({len(manual)} rows)")
    print(f"Wrote {negative_path} ({len(negative)} rows)")
    print(f"Wrote {event_path} ({len(events)} rows)")


if __name__ == "__main__":
    main()
