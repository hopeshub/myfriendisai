#!/usr/bin/env python3
"""Build samples for the adversarial audit (2026-05-13 evening).

Focused on comment-level evidence per the prompt. Produces:
1. 100 random tagged comments per theme (precision audit)
2. 100 random untagged comments from companion subs (recall floor)
3. SQL stat tables (concentration, overlap, temporal artifacts)
"""

import json
import random
import sqlite3
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import load_keyword_communities
from src.keyword_matching import build_patterns, match_text

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = Path(__file__).parent / "results"
SEED = 20260513_3
THEMES = ['rupture', 'addiction', 'romance', 'sexual_erp', 'consciousness', 'therapy']


def truncate(s, n):
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def build_tagged_comment_samples(conn, T1_T3):
    """100 random tagged comments per theme."""
    print("\n=== Tagged comment samples (100 per theme) ===")
    sub_ph = ",".join("?" * len(T1_T3))
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT h.matched_term, h.subreddit, h.post_date,
                      c.id AS cid, c.body AS comment_body, c.score AS c_score, c.author AS c_author,
                      p.id AS pid, p.title, p.selftext, p.author AS p_author
               FROM comment_keyword_hits h
               JOIN comments c ON c.id = h.comment_id
               JOIN posts p ON p.id = h.post_id
               WHERE h.category = ? AND h.subreddit IN ({sub_ph})
               GROUP BY h.comment_id, h.matched_term
               ORDER BY RANDOM()
               LIMIT 100""",
            (theme, *T1_T3)
        ).fetchall()
        out = RESULTS / f"adv_tagged_comments_{theme}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Adversarial — Tagged comments: {theme}\n\n")
            f.write(f"{len(rows)} random comments where comment_keyword_hits.category='{theme}'. ")
            f.write("Each entry includes the parent post for context.\n\n")
            f.write("**Task:** classify each comment as TP or FP for the theme under the topical reading. ")
            f.write("Be strict. A comment is FP if any of these apply:\n")
            f.write("- Keyword matches but the comment is off-theme (e.g., `addicted to coffee`)\n")
            f.write("- Negation: \"I am NOT in a relationship with it\"\n")
            f.write("- Sarcasm/irony: \"my addiction is cured, the site is so bad now\"\n")
            f.write("- Quoted speech: comment quotes someone else's post\n")
            f.write("- Off-topic comment in on-topic thread\n")
            f.write("- Keyword used metaphorically without theme content\n\n")
            f.write("Then identify the 2-3 keywords driving the most FPs in your sample, with example IDs.\n\n")
            f.write("Output format:\n\n```\n## Per-comment verdicts\n")
            f.write("1. TP/FP  matched=<keyword>  reason if FP\n2. ...\n\n")
            f.write("## Worst-offending keywords\n- `<keyword>`: X FPs out of Y matches. Pattern: ...  Examples: COMMENT 3, 17, 42.\n\n")
            f.write("## Precision\nTP / 100 = X% (Wilson 95% CI: [a, b])\n\n")
            f.write("## Embarrassment candidate\nThe single worst miscoding you found, with verbatim text.\n```\n\n")
            f.write("---\n\n## Comments\n\n")
            for i, r in enumerate(rows, 1):
                comment_body = truncate(r['comment_body'], 500) or "(empty)"
                parent_title = r['title'] or '(no title)'
                parent_body = truncate(r['selftext'], 250) or "(image/empty)"
                f.write(f"### COMMENT {i}\n")
                f.write(f"**Matched term:** `{r['matched_term']}`  **r/{r['subreddit']}**  ")
                f.write(f"**Date:** {r['post_date']}  **Comment score:** {r['c_score']}  ")
                f.write(f"**Comment by:** u/{r['c_author'] or '[deleted]'}\n\n")
                f.write(f"**Parent post (u/{r['p_author'] or '[deleted]'}):** {parent_title}\n\n")
                f.write(f"  > {parent_body}\n\n")
                f.write(f"**Comment text:** {comment_body}\n\n---\n\n")
        print(f"  wrote {out.name} ({len(rows)})")


def build_untagged_comment_recall(conn, T1_T3):
    """100 random untagged comments from companion subs."""
    print("\n=== Untagged-comment recall sample ===")
    sub_ph = ",".join("?" * len(T1_T3))
    rows = conn.execute(
        f"""SELECT c.id, c.body, c.subreddit, c.score, c.author,
                  date(c.created_utc,'unixepoch') AS comment_date,
                  p.id AS pid, p.title, p.selftext
           FROM comments c
           JOIN posts p ON p.id = c.post_id
           LEFT JOIN (SELECT DISTINCT comment_id FROM comment_keyword_hits) h
             ON h.comment_id = c.id
           WHERE c.subreddit IN ({sub_ph})
             AND h.comment_id IS NULL
             AND LENGTH(COALESCE(c.body,'')) > 100
             AND c.body NOT IN ('[deleted]', '[removed]', '')
           ORDER BY RANDOM()
           LIMIT 100""",
        T1_T3
    ).fetchall()
    out = RESULTS / "adv_untagged_comments_recall_2026-05-13.md"
    with open(out, "w") as f:
        f.write("# Adversarial — Untagged-comment recall floor\n\n")
        f.write(f"{len(rows)} random comments from T1-T3 companion subs that DID NOT match any theme keyword.\n\n")
        f.write("**Task:** for each comment, decide whether it SHOULD have been tagged under any of the six themes:\n")
        f.write("rupture, addiction, romance, sexual_erp, consciousness, therapy.\n\n")
        f.write("Use the topical reading. Be biased toward YES — if the comment is clearly about a theme in a ")
        f.write("companion-sub context, even with naturalistic language, it counts as a missed tag.\n\n")
        f.write("Output format:\n\n```\nCOMMENT N: themes=[X,Y] OR themes=[NONE]\n```\n\n")
        f.write("Then summarize:\n")
        f.write("- Recall floor per theme (count of missed comments / 100)\n")
        f.write("- The 2-3 dominant patterns of missed content (vocabulary the keyword set doesn't catch)\n")
        f.write("- Whether any specific theme is so under-captured in comments that the trend lines mislead\n\n")
        f.write("---\n\n## Comments\n\n")
        for i, r in enumerate(rows, 1):
            body = truncate(r['body'], 500) or "(empty)"
            parent = truncate(r['title'], 150)
            f.write(f"### COMMENT {i}\n")
            f.write(f"**r/{r['subreddit']}**  **Date:** {r['comment_date']}  ")
            f.write(f"**Score:** {r['score']}\n\n")
            f.write(f"**Parent post title:** {parent or '(no title)'}\n\n")
            f.write(f"**Comment:** {body}\n\n---\n\n")
    print(f"  wrote {out.name} ({len(rows)})")


def compute_stats(conn, T1_T3):
    """Concentration, overlap, temporal stats."""
    print("\n=== Stat tables ===")
    sub_ph = ",".join("?" * len(T1_T3))
    stats = {}

    # 1. Subreddit concentration per theme (posts and comments)
    sub_conc_post = {}
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT subreddit, COUNT(DISTINCT post_id) as n
               FROM post_keyword_tags
               WHERE category = ? AND source='post' AND subreddit IN ({sub_ph})
               GROUP BY subreddit
               ORDER BY n DESC""",
            (theme, *T1_T3)
        ).fetchall()
        total = sum(r['n'] for r in rows)
        top = rows[:5]
        sub_conc_post[theme] = {
            'total': total,
            'top5': [(r['subreddit'], r['n'], 100*r['n']/total if total else 0) for r in top]
        }
    stats['sub_concentration_posts'] = sub_conc_post

    sub_conc_comment = {}
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT subreddit, COUNT(DISTINCT comment_id) as n
               FROM comment_keyword_hits
               WHERE category = ? AND subreddit IN ({sub_ph})
               GROUP BY subreddit
               ORDER BY n DESC""",
            (theme, *T1_T3)
        ).fetchall()
        total = sum(r['n'] for r in rows)
        top = rows[:5]
        sub_conc_comment[theme] = {
            'total': total,
            'top5': [(r['subreddit'], r['n'], 100*r['n']/total if total else 0) for r in top]
        }
    stats['sub_concentration_comments'] = sub_conc_comment

    # 2. Author concentration per theme (top author share)
    author_conc = {}
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT p.author, COUNT(DISTINCT t.post_id) as n
               FROM post_keyword_tags t
               JOIN posts p ON p.id = t.post_id
               WHERE t.category = ? AND t.source='post' AND p.subreddit IN ({sub_ph})
                 AND p.author NOT IN ('[deleted]', 'AutoModerator')
                 AND p.author IS NOT NULL
               GROUP BY p.author
               ORDER BY n DESC""",
            (theme, *T1_T3)
        ).fetchall()
        total = sum(r['n'] for r in rows)
        n_authors = len(rows)
        if n_authors == 0:
            continue
        top1pct = max(1, n_authors // 100)
        top1pct_share = sum(r['n'] for r in rows[:top1pct]) / total if total else 0
        author_conc[theme] = {
            'total_posts': total,
            'total_authors': n_authors,
            'top1pct_authors': top1pct,
            'top1pct_share': 100*top1pct_share,
            'top10': [(r['author'], r['n']) for r in rows[:10]],
        }
    stats['author_concentration'] = author_conc

    # 3. Co-occurrence matrix (posts tagged in N themes simultaneously)
    coocc = defaultdict(int)
    rows = conn.execute(
        f"""SELECT post_id, GROUP_CONCAT(DISTINCT category) as themes
           FROM post_keyword_tags
           WHERE source='post' AND subreddit IN ({sub_ph})
           GROUP BY post_id""",
        T1_T3
    ).fetchall()
    theme_counts = defaultdict(int)
    pair_counts = defaultdict(int)
    triple_plus = 0
    for r in rows:
        themes = sorted(r['themes'].split(','))
        for t in themes:
            theme_counts[t] += 1
        for i in range(len(themes)):
            for j in range(i+1, len(themes)):
                pair_counts[(themes[i], themes[j])] += 1
        if len(themes) >= 3:
            triple_plus += 1
    stats['cooccurrence'] = {
        'theme_totals': dict(theme_counts),
        'pair_counts': {f"{a}|{b}": n for (a, b), n in pair_counts.items()},
        'triple_plus_count': triple_plus,
        'all_posts': len(rows),
    }

    # 4. Temporal: per-year theme totals + per-year post volume
    yearly = conn.execute(
        f"""SELECT strftime('%Y', p.created_utc, 'unixepoch') as year,
                  t.category, COUNT(DISTINCT t.post_id) as n
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.source='post' AND p.subreddit IN ({sub_ph})
             AND year IS NOT NULL
           GROUP BY year, t.category
           ORDER BY year""",
        T1_T3
    ).fetchall()
    yearly_posts = conn.execute(
        f"""SELECT strftime('%Y', created_utc, 'unixepoch') as year, COUNT(*) as n
           FROM posts
           WHERE subreddit IN ({sub_ph}) AND created_utc IS NOT NULL
           GROUP BY year
           ORDER BY year""",
        T1_T3
    ).fetchall()
    yr_theme = defaultdict(lambda: defaultdict(int))
    for y, c, n in yearly:
        yr_theme[y][c] = n
    yr_vol = {y: n for y, n in yearly_posts}
    stats['yearly_theme_rates'] = {
        y: {
            'total_posts': yr_vol.get(y, 0),
            'theme_counts': dict(yr_theme[y]),
            'theme_pct': {c: 100*n/yr_vol.get(y, 1) for c, n in yr_theme[y].items()},
        }
        for y in sorted(yr_theme.keys()) if y
    }

    # 5. Calendar concentration: top 5 dates per theme (volume-spike check)
    cal_conc = {}
    for theme in THEMES:
        rows = conn.execute(
            f"""SELECT date(p.created_utc,'unixepoch') as post_date,
                      COUNT(DISTINCT t.post_id) as n
               FROM post_keyword_tags t
               JOIN posts p ON p.id = t.post_id
               WHERE t.category = ? AND t.source='post' AND p.subreddit IN ({sub_ph})
               GROUP BY post_date
               ORDER BY n DESC
               LIMIT 5""",
            (theme, *T1_T3)
        ).fetchall()
        cal_conc[theme] = [(r['post_date'], r['n']) for r in rows]
    stats['top_calendar_days'] = cal_conc

    # 6. Specifically: 2023 Replika ERP era as fraction of sex/ERP totals
    feb_2023_erp_pct = conn.execute(
        f"""SELECT COUNT(DISTINCT t.post_id) as n
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.category = 'sexual_erp' AND t.source='post' AND p.subreddit IN ({sub_ph})
             AND strftime('%Y-%m', p.created_utc, 'unixepoch') BETWEEN '2023-02' AND '2023-04'""",
        T1_T3
    ).fetchone()[0]
    sex_erp_total = conn.execute(
        f"""SELECT COUNT(DISTINCT t.post_id) as n
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.category = 'sexual_erp' AND t.source='post' AND p.subreddit IN ({sub_ph})""",
        T1_T3
    ).fetchone()[0]
    stats['feb_2023_share_of_sex_erp'] = {
        'feb_mar_apr_2023_count': feb_2023_erp_pct,
        'total': sex_erp_total,
        'pct': 100 * feb_2023_erp_pct / sex_erp_total if sex_erp_total else 0,
    }

    out = RESULTS / "adv_stats_2026-05-13.json"
    with open(out, "w") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"  wrote {out.name}")
    return stats


def main():
    random.seed(SEED)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    build_tagged_comment_samples(conn, T1_T3)
    build_untagged_comment_recall(conn, T1_T3)
    stats = compute_stats(conn, T1_T3)
    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
