"""Cross-theme overlap analysis.

Reads production keyword tags from post_keyword_tags (populated by tag_keywords.py
with regex word-boundary matching from keywords_v8.yaml) instead of re-running
SQL LIKE against raw post text. This matches what's actually being counted on
the trend chart.

Scope: T1-T3 companion subreddits only (same as keyword_trends.json export).
Post+comment tags both count — a post with a theme hit from either source is
counted for that theme.

Writes a human-readable markdown summary to docs/cross_theme_overlap.md.
"""
import itertools
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_keyword_communities

DB = "data/tracker.db"
OUT = "docs/cross_theme_overlap.md"

THEME_NAMES = ["therapy", "consciousness", "addiction", "romance", "sexual_erp", "rupture"]


def build_flags_table(conn, active_subs):
    """Build a temp table of per-post theme flags from post_keyword_tags.

    One row per post that has at least one tag in an active sub, with a 0/1
    flag column per theme. Reads from the production tag table so the numbers
    line up 1:1 with the trend chart.
    """
    placeholders = ",".join("?" * len(active_subs))
    flag_cols = ",\n        ".join(
        f"MAX(CASE WHEN category = '{t}' THEN 1 ELSE 0 END) AS {t}"
        for t in THEME_NAMES
    )
    sql = f"""
    CREATE TEMP TABLE post_flags AS
    SELECT
        post_id,
        subreddit,
        {flag_cols}
    FROM post_keyword_tags
    WHERE subreddit IN ({placeholders})
    GROUP BY post_id
    """
    conn.execute(sql, active_subs)
    n = conn.execute("SELECT COUNT(*) FROM post_flags").fetchone()[0]
    return n


def per_theme_counts(conn):
    return {
        t: conn.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t} = 1").fetchone()[0]
        for t in THEME_NAMES
    }


def pairwise_matrix(conn):
    matrix = {}
    for t1, t2 in itertools.combinations(THEME_NAMES, 2):
        n = conn.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t1}=1 AND {t2}=1").fetchone()[0]
        matrix[(t1, t2)] = n
    return matrix


def triple_plus(conn):
    sum_expr = " + ".join(THEME_NAMES)
    total = conn.execute(f"SELECT COUNT(*) FROM post_flags WHERE ({sum_expr}) >= 3").fetchone()[0]
    cols = ", ".join(THEME_NAMES)
    examples = conn.execute(f"""
        SELECT post_id, subreddit, {cols}
        FROM post_flags
        WHERE ({sum_expr}) >= 3
        LIMIT 10
    """).fetchall()
    return total, examples


def exclusivity_counts(conn):
    out = {}
    for t in THEME_NAMES:
        others = [o for o in THEME_NAMES if o != t]
        no_others = " AND ".join(f"{o}=0" for o in others)
        n = conn.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t}=1 AND {no_others}").fetchone()[0]
        out[t] = n
    return out


def main():
    active_subs = [c["subreddit"] for c in load_keyword_communities()]
    print(f"Scope: {len(active_subs)} T1-T3 subreddits")

    conn = sqlite3.connect(DB)

    total_tagged_posts = build_flags_table(conn, active_subs)
    print(f"Posts with ≥1 theme tag: {total_tagged_posts:,}")

    theme_counts = per_theme_counts(conn)
    print("Per-theme counts:")
    for t, n in theme_counts.items():
        print(f"  {t}: {n:,}")

    matrix = pairwise_matrix(conn)
    triple_total, triple_examples = triple_plus(conn)
    exclusivity = exclusivity_counts(conn)

    conn.close()

    lines = []
    lines.append("# Cross-Theme Keyword Overlap Analysis")
    lines.append(f"\n_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")
    lines.append("**Source:** `post_keyword_tags` (production regex tags from `keywords_v8.yaml`,")
    lines.append("both post and comment sources). Scope matches `keyword_trends.json`: T1-T3")
    lines.append(f"companion subreddits ({len(active_subs)} communities).\n")
    lines.append(f"**Corpus:** {total_tagged_posts:,} posts with at least one theme tag.\n")

    lines.append("## Unique posts per theme\n")
    lines.append("| Theme | Unique posts | % of tagged corpus |")
    lines.append("|-------|-------------|-------------------|")
    for t in THEME_NAMES:
        pct = theme_counts[t] / total_tagged_posts * 100 if total_tagged_posts else 0
        lines.append(f"| {t} | {theme_counts[t]:,} | {pct:.2f}% |")

    lines.append("\n## Pairwise overlap (post counts)\n")
    header = "| | " + " | ".join(THEME_NAMES) + " |"
    sep = "|---|" + "---|" * len(THEME_NAMES)
    lines.append(header)
    lines.append(sep)
    for t1 in THEME_NAMES:
        row = [f"**{t1}**"]
        for t2 in THEME_NAMES:
            if t1 == t2:
                row.append("—")
            else:
                key = (t1, t2) if (t1, t2) in matrix else (t2, t1)
                row.append(str(matrix[key]))
        lines.append("| " + " | ".join(row) + " |")

    lines.append("\n## Overlap as % of smaller theme\n")
    lines.append("| Pair | Overlap | Smaller theme (n) | % of smaller |")
    lines.append("|------|--------|-------------------|--------------|")
    for (t1, t2), overlap in sorted(matrix.items(), key=lambda x: -x[1]):
        if overlap == 0:
            continue
        smaller_t = t1 if theme_counts[t1] <= theme_counts[t2] else t2
        smaller_n = min(theme_counts[t1], theme_counts[t2])
        pct = overlap / smaller_n * 100 if smaller_n else 0
        lines.append(f"| {t1} × {t2} | {overlap:,} | {smaller_t} ({smaller_n:,}) | {pct:.1f}% |")

    lines.append(f"\n## Triple+ overlap\n")
    lines.append(f"**{triple_total:,} posts** match 3 or more themes simultaneously.\n")
    if triple_examples:
        lines.append("### Examples (up to 10)\n")
        lines.append("| Post ID | Subreddit | Themes matched |")
        lines.append("|---------|-----------|----------------|")
        for row in triple_examples:
            post_id, subreddit = row[0], row[1]
            flags = row[2:]
            matched = [THEME_NAMES[i] for i, f in enumerate(flags) if f == 1]
            lines.append(f"| {post_id} | {subreddit} | {', '.join(matched)} |")

    lines.append("\n## Theme exclusivity\n")
    lines.append("A theme is exclusive when a post matches that theme and no other.\n")
    lines.append("| Theme | Total | Exclusive | Exclusivity % |")
    lines.append("|-------|-------|-----------|---------------|")
    for t in THEME_NAMES:
        total = theme_counts[t]
        excl = exclusivity[t]
        pct = excl / total * 100 if total else 0
        lines.append(f"| {t} | {total:,} | {excl:,} | {pct:.1f}% |")

    lines.append("\n## Interpretation\n")
    if matrix:
        top_pair = max(matrix.items(), key=lambda x: x[1])
        top_pair_name = f"{top_pair[0][0]} × {top_pair[0][1]}"

        top_pct_pair = None
        top_pct = 0
        for (t1, t2), overlap in matrix.items():
            if overlap == 0:
                continue
            smaller_n = min(theme_counts[t1], theme_counts[t2])
            pct = overlap / smaller_n * 100 if smaller_n else 0
            if pct > top_pct:
                top_pct = pct
                top_pct_pair = (t1, t2, overlap, pct)

        most_exclusive = max(
            THEME_NAMES,
            key=lambda t: exclusivity[t] / theme_counts[t] if theme_counts[t] else 0,
        )
        least_exclusive = min(
            THEME_NAMES,
            key=lambda t: exclusivity[t] / theme_counts[t] if theme_counts[t] else 1,
        )

        lines.append(f"- **Highest absolute overlap:** {top_pair_name} with {top_pair[1]:,} posts in common.")
        if top_pct_pair:
            lines.append(
                f"- **Highest proportional overlap:** {top_pct_pair[0]} × {top_pct_pair[1]} "
                f"({top_pct_pair[2]:,} posts, {top_pct_pair[3]:.1f}% of the smaller theme)."
            )
        lines.append(
            f"- **Most exclusive theme:** {most_exclusive} "
            f"({exclusivity[most_exclusive] / theme_counts[most_exclusive] * 100:.1f}% exclusive)."
        )
        lines.append(
            f"- **Least exclusive theme:** {least_exclusive} "
            f"({exclusivity[least_exclusive] / theme_counts[least_exclusive] * 100:.1f}% exclusive)."
        )
        lines.append(
            f"- **Policy:** Themes are non-exclusive by design. Trend lines count unique posts "
            f"per theme. Triple+ overlap is {triple_total / total_tagged_posts * 100:.1f}% of "
            f"tagged posts — small enough that allowing overlap doesn't distort the chart."
        )

    Path(OUT).parent.mkdir(parents=True, exist_ok=True)
    Path(OUT).write_text("\n".join(lines) + "\n")
    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
