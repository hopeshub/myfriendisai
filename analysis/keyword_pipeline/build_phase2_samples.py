#!/usr/bin/env python3
"""Build sample files for Phase 2 audit (7 audits, 2026-05-13 evening).

Audit 1: Comment tagging quality — 50 random comment_keyword_hits per theme
Audit 2: Per-keyword time drift — 8 representative keywords × year buckets
Audit 3: Negative space — apply regex to T0 posts, find accidental matches
Audit 4: Author-level coherence — 16 prolific authors × chronological streams
Audit 5: Aggregate narrative — chart data + event timeline summary
Audit 6: v8.1/v8.2 production behavior — 30 hits per new keyword
Audit 7: Cross-classifier reliability — 100 production-tagged posts × 3 agents
"""

import json
import random
import sqlite3
import sys
from collections import defaultdict
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.config import load_communities, load_keyword_communities
from src.keyword_matching import build_patterns, match_text

PROJECT_ROOT = Path(__file__).parent.parent.parent
DB_PATH = PROJECT_ROOT / "data" / "tracker.db"
RESULTS = Path(__file__).parent / "results"
SEED = 20260513_2
THEMES = ['rupture', 'addiction', 'romance', 'sexual_erp', 'consciousness', 'therapy']

V8_1_KEYWORDS = ['saying goodbye', 'taken away', 'mourning', 'mourn',
                 'devastated', 'grieve', 'goodbye', 'farewell']
V8_2_KEYWORDS = ['my addiction', 'withdrawals', 'screen time',
                 'in love with an ai', 'romantic relationship with',
                 'smut', 'nsfw content', 'nsfw stuff']

DRIFT_KEYWORDS = [
    ('rupture', 'lobotomy'),
    ('rupture', 'goodbye'),
    ('rupture', 'farewell'),
    ('addiction', 'relapse'),
    ('addiction', 'screen time'),
    ('romance', 'wedding'),
    ('romance', 'in a relationship with'),
    ('sexual_erp', 'erp'),
]


def truncate(s: str, n: int) -> str:
    s = (s or "").strip()
    return s if len(s) <= n else s[:n] + "..."


def post_md(i: int, row, show_tags: bool = False) -> str:
    body = truncate(row['selftext'], 500) or "(no body / image post)"
    tag_line = ""
    if show_tags and 'tags' in row.keys() and row['tags']:
        tag_line = f"**Tags:** {row['tags']}\n\n"
    return (f"### POST {i}\n"
            f"**ID:** {row['id']}  **r/{row['subreddit']}**  "
            f"**Date:** {row['post_date']}\n\n"
            f"**Title:** {row['title'] or '(no title)'}\n\n"
            f"{tag_line}"
            f"**Body:** {body}\n\n---\n\n")


# ── AUDIT 1: Comment tagging quality ────────────────────────────────────
def audit1_comments(conn):
    print("\n=== AUDIT 1: Comment tagging quality ===")
    for theme in THEMES:
        rows = conn.execute(
            """SELECT h.id, h.matched_term, h.subreddit, h.post_date,
                      c.id AS cid, c.body AS comment_body, c.score AS c_score,
                      p.id AS pid, p.title, p.selftext
               FROM comment_keyword_hits h
               JOIN comments c ON c.id = h.comment_id
               JOIN posts p ON p.id = h.post_id
               WHERE h.category = ?
               GROUP BY h.comment_id, h.matched_term
               ORDER BY RANDOM()
               LIMIT 50""",
            (theme,)
        ).fetchall()
        out = RESULTS / f"phase2_A1_comments_{theme}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Audit 1 — Comment tagging quality: {theme}\n\n")
            f.write(f"{len(rows)} random comment-keyword hits where source='comment' and category='{theme}'.\n\n")
            f.write("Each entry is a comment that matched a keyword and propagated a tag to its parent post.\n\n")
            f.write(f"**Question:** is the comment-sourced tag a precise {theme} signal under the topical reading? ")
            f.write("Does the comment genuinely discuss the theme (not just contain the keyword incidentally)? ")
            f.write("And does the parent post's thread context support attributing this theme to the post?\n\n")
            f.write("Output format:\n\n```\n## Per-comment verdicts\n")
            f.write("1. YES  # short reason (or NO if FP, with reason)\n2. ...\n\n")
            f.write("## Failure modes\n- pattern: keyword that caused it, example comments, why off-theme\n\n")
            f.write("## Bottom line\n2-3 sentences on overall precision of comment-sourced tagging for this theme.\n```\n\n")
            f.write("---\n\n## Comments\n\n")
            for i, r in enumerate(rows, 1):
                comment_body = truncate(r['comment_body'], 400) or "(empty)"
                parent_title = r['title'] or '(no title)'
                parent_body = truncate(r['selftext'], 200) or "(image/empty)"
                f.write(f"### COMMENT {i}\n")
                f.write(f"**Matched term:** `{r['matched_term']}`  "
                        f"**r/{r['subreddit']}**  **Date:** {r['post_date']}\n\n")
                f.write(f"**Parent post title:** {parent_title}\n\n")
                f.write(f"**Parent post body (first 200 chars):** {parent_body}\n\n")
                f.write(f"**Comment text:** {comment_body}\n\n---\n\n")
        print(f"  wrote {out.name} ({len(rows)} comments)")


# ── AUDIT 2: Per-keyword time drift ─────────────────────────────────────
def audit2_drift(conn):
    print("\n=== AUDIT 2: Per-keyword time drift ===")
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))
    YEARS = ['2023', '2024', '2025', '2026']
    for theme, keyword in DRIFT_KEYWORDS:
        year_samples = {}
        for year in YEARS:
            rows = conn.execute(
                f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                          date(p.created_utc,'unixepoch') AS post_date
                   FROM post_keyword_tags t
                   JOIN posts p ON p.id = t.post_id
                   WHERE t.matched_term = ? AND t.source='post'
                     AND t.category = ?
                     AND p.subreddit IN ({sub_ph})
                     AND strftime('%Y', p.created_utc, 'unixepoch') = ?
                   ORDER BY RANDOM()
                   LIMIT 30""",
                (keyword, theme, *T1_T3, year)
            ).fetchall()
            year_samples[year] = rows
        slug = keyword.replace(' ', '_')
        out = RESULTS / f"phase2_A2_drift_{theme}_{slug}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Audit 2 — Time drift: `{keyword}` ({theme})\n\n")
            total = sum(len(v) for v in year_samples.values())
            f.write(f"{total} posts across {len(YEARS)} year buckets, 30 per year (or fewer if availability).\n\n")
            f.write(f"**Question:** has the precision of `{keyword}` drifted over time? ")
            f.write(f"Classify each post YES/NO for whether it's genuinely about {theme} under the topical reading. ")
            f.write("Then report per-year precision and any drift patterns.\n\n")
            f.write("Pay attention to whether the keyword has become a meme, drifted into different communities, ")
            f.write("or now matches contexts it didn't before (e.g., `lobotomy` becoming CharacterAI shorthand).\n\n")
            f.write("Output format:\n\n```\n## Per-year precision\n")
            f.write("2023: X/Y = Z% (sample reasons)\n2024: ...\n2025: ...\n2026: ...\n\n")
            f.write("## Drift pattern\nOne paragraph: is the keyword stable, drifting, or has it shifted use?\n\n")
            f.write("## Per-post verdicts (by year)\nList format: year-post#: YES/NO + reason\n```\n\n")
            for year in YEARS:
                rows = year_samples[year]
                f.write(f"---\n\n## {year} ({len(rows)} posts)\n\n")
                for i, r in enumerate(rows, 1):
                    f.write(post_md(f"{year}-{i}", r, show_tags=False))
        print(f"  wrote {out.name} ({total} posts)")


# ── AUDIT 3: Negative space — T0 + image-only posts ─────────────────────
def audit3_negative_space(conn):
    print("\n=== AUDIT 3: Negative space ===")
    # T0 subs are not theme-tagged in production. Apply regex to a random
    # sample of T0 posts to find what WOULD be tagged. Then check if those
    # matches would be legitimate theme content or accidental.
    communities = load_communities()
    T0_SUBS = [c['subreddit'] for c in communities if c.get('tier') == 0]
    print(f"  T0 subs: {T0_SUBS}")
    t0_ph = ",".join("?" * len(T0_SUBS))
    patterns = build_patterns()
    # Sample 1000 T0 posts with substantive body
    rows = conn.execute(
        f"""SELECT id, subreddit, title, selftext,
                  date(created_utc,'unixepoch') AS post_date
           FROM posts
           WHERE subreddit IN ({t0_ph})
             AND LENGTH(COALESCE(selftext,'')) > 50
             AND created_utc IS NOT NULL
           ORDER BY RANDOM()
           LIMIT 1000""",
        T0_SUBS
    ).fetchall()
    # Apply regex
    accidental_matches = []
    for r in rows:
        combined = ((r['title'] or '') + ' ' + (r['selftext'] or '')).strip()
        matches = match_text(combined, patterns)
        if matches:
            accidental_matches.append((r, matches))
    print(f"  T0 posts scanned: {len(rows)}, with regex matches: {len(accidental_matches)}")
    # Cap the sample for agent reading
    if len(accidental_matches) > 100:
        random.seed(SEED)
        accidental_matches = random.sample(accidental_matches, 100)
    out = RESULTS / "phase2_A3_negative_space_T0_2026-05-13.md"
    with open(out, "w") as f:
        f.write(f"# Audit 3 — Negative space (T0 posts that would have been tagged)\n\n")
        f.write(f"{len(accidental_matches)} T0 posts that match our keyword regex (out of 1000 sampled).\n\n")
        f.write("**Context:** T0 subs (r/ChatGPT, r/OpenAI, r/singularity, r/ClaudeAI, r/claudexplorers) are ")
        f.write("intentionally NOT tagged in production because keyword overlap with non-companionship contexts ")
        f.write("would be too noisy. This audit applies our regex to T0 posts to characterize what we'd capture ")
        f.write("if we removed that exclusion.\n\n")
        f.write("**Question:** of these posts whose text matches our keyword regex, what fraction are GENUINELY ")
        f.write("about AI companionship (would be a true positive)? What fraction are noise (FP)? Characterize ")
        f.write("the FP patterns.\n\n")
        f.write("This also serves as a robustness check: if a high fraction of T0 matches are FPs, that confirms ")
        f.write("the T0 exclusion is correct. If most are TPs, T0 posts contain a lot of unmeasured companion ")
        f.write("discourse that could expand the corpus.\n\n")
        f.write("Output format:\n\n```\n## Per-post verdicts\n1. TP/FP + theme + reason\n...\n\n")
        f.write("## FP patterns\n- pattern: which keywords drive it, sub context\n\n")
        f.write("## Bottom line\nTP rate, dominant FP modes, recommendation re: T0 inclusion\n```\n\n")
        f.write("---\n\n## Posts\n\n")
        for i, (r, matches) in enumerate(accidental_matches, 1):
            match_str = ", ".join([f"{c}:{t}" for c, t in matches])
            f.write(f"### POST {i}\n")
            f.write(f"**ID:** {r['id']}  **r/{r['subreddit']}**  **Date:** {r['post_date']}\n\n")
            f.write(f"**Regex matches:** {match_str}\n\n")
            f.write(f"**Title:** {r['title'] or '(no title)'}\n\n")
            f.write(f"**Body:** {truncate(r['selftext'], 400)}\n\n---\n\n")
    print(f"  wrote {out.name}")


# ── AUDIT 4: Author-level coherence ─────────────────────────────────────
def audit4_authors(conn):
    print("\n=== AUDIT 4: Author-level coherence ===")
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))
    # Find prolific authors with stretched activity (not all in one day/week)
    authors = conn.execute(
        f"""SELECT author, COUNT(*) as n,
                  MIN(created_utc) as first_post, MAX(created_utc) as last_post,
                  COUNT(DISTINCT date(created_utc,'unixepoch')) as active_days
           FROM posts
           WHERE subreddit IN ({sub_ph})
             AND author NOT IN ('[deleted]', 'AutoModerator')
             AND author IS NOT NULL
           GROUP BY author
           HAVING n BETWEEN 30 AND 200 AND active_days >= 14
           ORDER BY RANDOM()
           LIMIT 16""",
        T1_T3
    ).fetchall()
    print(f"  selected {len(authors)} authors")
    # Group 2 authors per agent
    for batch_idx in range(0, len(authors), 2):
        batch = authors[batch_idx:batch_idx+2]
        out = RESULTS / f"phase2_A4_authors_batch{batch_idx//2 + 1}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Audit 4 — Author-level coherence: batch {batch_idx//2 + 1}\n\n")
            f.write(f"This batch contains {len(batch)} authors. Read each author's chronological post stream ")
            f.write("(their entire history within companion subs) and verify the theme tags reflect their ")
            f.write("journey accurately.\n\n")
            f.write("**Question for each author:** does this user's tag history tell a coherent story? ")
            f.write("If they show up in addiction in 2024 and rupture in 2026, does the post text support that? ")
            f.write("Or are tags scattered randomly without narrative coherence?\n\n")
            f.write("Look for: (1) construct-valid theme tags that match the author's stated experience, ")
            f.write("(2) construct-invalid tags that misrepresent the post, (3) missed posts that obviously ")
            f.write("belong to a theme but are untagged.\n\n")
            f.write("Output format:\n\n```\n## Author 1: u/<name>\n")
            f.write("Journey summary (2-3 sentences): what story do their posts tell?\n")
            f.write("Tag accuracy: of tagged posts, how many fit the journey? Any misfires?\n")
            f.write("Missed content: posts that should have theme tags but don't.\n\n")
            f.write("## Author 2: ...\n\n## Bottom line\nDo tags reflect authors' actual journeys?\n```\n\n")
            for auth_idx, a in enumerate(batch, 1):
                posts = conn.execute(
                    f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                              date(p.created_utc,'unixepoch') AS post_date,
                              GROUP_CONCAT(DISTINCT t.category || ':' || t.matched_term) AS tags
                       FROM posts p
                       LEFT JOIN post_keyword_tags t ON t.post_id = p.id AND t.source='post'
                       WHERE p.author = ? AND p.subreddit IN ({sub_ph})
                       GROUP BY p.id
                       ORDER BY p.created_utc""",
                    (a['author'], *T1_T3)
                ).fetchall()
                f.write(f"---\n\n## Author {auth_idx}: u/{a['author']}\n\n")
                f.write(f"{len(posts)} posts in companion subs.\n\n")
                for i, p in enumerate(posts, 1):
                    tags = p['tags'] or "(untagged)"
                    body = truncate(p['selftext'], 300) or "(image/empty)"
                    f.write(f"### POST {i}\n")
                    f.write(f"**Date:** {p['post_date']}  **r/{p['subreddit']}**  **Tags:** {tags}\n\n")
                    f.write(f"**Title:** {p['title'] or '(no title)'}\n\n")
                    f.write(f"**Body:** {body}\n\n")
        print(f"  wrote {out.name} (authors: {[a['author'] for a in batch]})")


# ── AUDIT 5: Aggregate narrative coherence ──────────────────────────────
def audit5_narrative(conn):
    print("\n=== AUDIT 5: Aggregate narrative coherence ===")
    # Pull theme trend data (monthly totals) + event timeline + corpus stats
    monthly = conn.execute(
        """SELECT strftime('%Y-%m', p.created_utc, 'unixepoch') as month,
                  t.category,
                  COUNT(DISTINCT t.post_id) as n
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.source='post'
           GROUP BY month, t.category
           ORDER BY month, t.category"""
    ).fetchall()
    monthly_by_theme = defaultdict(lambda: defaultdict(int))
    for m, c, n in monthly:
        if m:
            monthly_by_theme[c][m] = n
    # Per-theme yearly summary
    yearly = conn.execute(
        """SELECT strftime('%Y', p.created_utc, 'unixepoch') as year,
                  t.category,
                  COUNT(DISTINCT t.post_id) as n
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.source='post' AND year IS NOT NULL
           GROUP BY year, t.category
           ORDER BY year, t.category"""
    ).fetchall()
    # Top monthly spikes per theme (top 5 months)
    top_months = defaultdict(list)
    for theme in THEMES:
        months_sorted = sorted(monthly_by_theme[theme].items(), key=lambda x: -x[1])
        top_months[theme] = months_sorted[:5]
    # Corpus stats
    corpus_count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
    out = RESULTS / "phase2_A5_narrative_2026-05-13.md"
    with open(out, "w") as f:
        f.write("# Audit 5 — Aggregate narrative coherence\n\n")
        f.write(f"**Corpus:** {corpus_count:,} posts across 27 subreddits (Jan 2023 — May 2026).\n\n")
        f.write("**Task:** read the theme trend data below and produce two outputs:\n\n")
        f.write("1. **Narrative history (2023-2026):** write a 4-6 paragraph story of AI companionship from this data alone. ")
        f.write("What does the data say happened? Which platforms drove which spikes? When did each theme emerge or peak? ")
        f.write("Be specific about months/years.\n\n")
        f.write("2. **External cross-check:** identify 5-8 claims your narrative makes that could be verified ")
        f.write("against external sources (community wikis, press coverage, sub history). For each claim, indicate ")
        f.write("how confident you are it matches external reality, and note any places the data alone is ambiguous ")
        f.write("about cause.\n\n")
        f.write("3. **Coherence verdict:** does the data tell a single coherent story, or does it raise questions ")
        f.write("about measurement artifacts (e.g., did a theme spike because the keyword set changed)?\n\n")
        f.write("---\n\n## Per-year theme totals\n\n")
        f.write("| Year | rupture | addiction | romance | sexual_erp | consciousness | therapy |\n")
        f.write("|---|---|---|---|---|---|---|\n")
        year_data = defaultdict(lambda: defaultdict(int))
        for y, c, n in yearly:
            year_data[y][c] = n
        for year in sorted(year_data.keys()):
            row = [year]
            for theme in THEMES:
                row.append(str(year_data[year].get(theme, 0)))
            f.write("| " + " | ".join(row) + " |\n")
        f.write("\n")
        f.write("## Top 5 spike months per theme\n\n")
        for theme in THEMES:
            f.write(f"**{theme}:** ")
            f.write(", ".join([f"{m} ({n})" for m, n in top_months[theme]]))
            f.write("\n\n")
        f.write("## Monthly time series per theme\n\n")
        # All months between 2023-01 and 2026-05
        all_months = sorted(set(
            m for theme_data in monthly_by_theme.values() for m in theme_data.keys()
            if m and m >= '2023-01'
        ))
        f.write("| Month | " + " | ".join(THEMES) + " |\n")
        f.write("|---" + "|---" * len(THEMES) + "|\n")
        for m in all_months:
            row = [m]
            for theme in THEMES:
                row.append(str(monthly_by_theme[theme].get(m, 0)))
            f.write("| " + " | ".join(row) + " |\n")
        # Event annotations from chart
        f.write("\n## Event annotations currently on the chart\n\n")
        events = [
            ("2023-02", "Replika ERP removal (Luka filter rollout, ~Feb 13)"),
            ("2024-09", "CharacterAI legacy site shutdown (old.character.ai, Sep 24)"),
            ("2026-02", "GPT-4o sunset in ChatGPT (Feb 13)"),
            ("2026-05", "Sonnet 4.5 retirement petition + CharacterAI Roar/Soft Launch removal (May 9-15)"),
        ]
        for d, desc in events:
            f.write(f"- {d}: {desc}\n")
        f.write("\n## Methodology notes\n\n")
        f.write("- Tag counts above are post-only (not post+comment) for cross-year comparability\n")
        f.write("- Comments only began tagging March 2026; recent months reflect both posts and comments\n")
        f.write("- Consciousness coverage_start is April 2025 due to vocabulary availability; pre-2025 numbers may understate\n")
        f.write("- Per-keyword precision is 80%+ under topical reading; theme-level precision 70-92% (per robustness audit)\n")
        f.write("- Per-theme recall is 3-32% (per comprehensiveness audit); chart shows floor of theme prevalence\n")
    print(f"  wrote {out.name}")


# ── AUDIT 6: v8.1/v8.2 production behavior ──────────────────────────────
def audit6_new_keywords(conn):
    print("\n=== AUDIT 6: v8.1/v8.2 production behavior ===")
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))
    all_new = [('rupture', k) for k in V8_1_KEYWORDS] + [
        ('addiction', 'my addiction'), ('addiction', 'withdrawals'), ('addiction', 'screen time'),
        ('romance', 'in love with an ai'), ('romance', 'romantic relationship with'),
        ('sexual_erp', 'smut'), ('sexual_erp', 'nsfw content'), ('sexual_erp', 'nsfw stuff'),
    ]
    # Group 2 keywords per agent — 8 agents total
    for batch_idx in range(0, len(all_new), 2):
        batch = all_new[batch_idx:batch_idx+2]
        out = RESULTS / f"phase2_A6_v8_new_batch{batch_idx//2 + 1}_2026-05-13.md"
        with open(out, "w") as f:
            f.write(f"# Audit 6 — v8.1/v8.2 production behavior: batch {batch_idx//2 + 1}\n\n")
            f.write("Each section is a recently-added keyword. The validation precision was measured ")
            f.write("offline at n=100; this audit checks whether actual production tagging matches the ")
            f.write("validation precision.\n\n")
            f.write("**Question:** for each keyword, what is the topical-reading precision on 30 random ")
            f.write("production hits? Does it match the validation number?\n\n")
            f.write("Output format:\n\n```\n## <keyword>\n")
            f.write("Validation: X% (per keywords_v8.yaml)\nProduction precision (this audit): X/30 = Y%\n")
            f.write("Failure modes: brief patterns if any\n\n## <next keyword>\n...\n\n")
            f.write("## Bottom line\nDo the new keywords' production behavior match their validation?\n```\n\n")
            for theme, keyword in batch:
                rows = conn.execute(
                    f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                              date(p.created_utc,'unixepoch') AS post_date
                       FROM post_keyword_tags t
                       JOIN posts p ON p.id = t.post_id
                       WHERE t.matched_term = ? AND t.source='post' AND t.category = ?
                         AND p.subreddit IN ({sub_ph})
                       ORDER BY RANDOM()
                       LIMIT 30""",
                    (keyword, theme, *T1_T3)
                ).fetchall()
                f.write(f"---\n\n## Keyword: `{keyword}` ({theme})\n\n")
                f.write(f"{len(rows)} production hits sampled.\n\n")
                for i, r in enumerate(rows, 1):
                    f.write(post_md(i, r, show_tags=False))
        print(f"  wrote {out.name} (keywords: {[k for _, k in batch]})")


# ── AUDIT 7: Cross-classifier reliability ───────────────────────────────
def audit7_cross_classifier(conn):
    print("\n=== AUDIT 7: Cross-classifier reliability ===")
    T1_T3 = [c["subreddit"] for c in load_keyword_communities()]
    sub_ph = ",".join("?" * len(T1_T3))
    rows = conn.execute(
        f"""SELECT p.id, p.subreddit, p.title, p.selftext,
                  date(p.created_utc,'unixepoch') AS post_date,
                  GROUP_CONCAT(DISTINCT t.category) AS current_tags
           FROM post_keyword_tags t
           JOIN posts p ON p.id = t.post_id
           WHERE t.source='post' AND p.subreddit IN ({sub_ph})
           GROUP BY p.id
           ORDER BY RANDOM()
           LIMIT 100""",
        T1_T3
    ).fetchall()
    # Write a single sample file; same posts go to 3 agents
    out = RESULTS / "phase2_A7_cross_classifier_sample_2026-05-13.md"
    with open(out, "w") as f:
        f.write("# Audit 7 — Cross-classifier reliability sample\n\n")
        f.write(f"{len(rows)} random production-tagged posts (any theme, any sub T1-T3).\n\n")
        f.write("**Task:** classify each post independently for all six themes. ")
        f.write("Use the topical reading. A post can belong to MULTIPLE themes. A post can belong to NONE.\n\n")
        f.write("**Themes:**\n\n")
        f.write("- **rupture** — loss of an AI companion via platform changes, model deprecation, filter tightening, shutdown\n")
        f.write("- **addiction** — compulsive AI use, dependency, quit attempts, withdrawal\n")
        f.write("- **romance** — romantic attachment with an AI (dating, marriage, love, partnership)\n")
        f.write("- **sexual_erp** — sexual/erotic content with AI (ERP, NSFW chat, kink)\n")
        f.write("- **consciousness** — AI awareness, sentience, personhood, inner experience claims\n")
        f.write("- **therapy** — using AI for mental-health support, therapy substitute, emotional support\n\n")
        f.write("**Output format** — one line per post:\n\n")
        f.write("```\nPOST <N>: themes=[rupture,romance] OR themes=[NONE]\n```\n\n")
        f.write("Do NOT include the current tags shown below in your decision — they're shown only for ")
        f.write("the post-processing step. Read the title + body and classify independently.\n\n")
        f.write("---\n\n## Posts\n\n")
        for i, r in enumerate(rows, 1):
            f.write(f"### POST {i}\n")
            f.write(f"**ID:** {r['id']}  **r/{r['subreddit']}**  **Date:** {r['post_date']}\n\n")
            f.write(f"_(current production tags: {r['current_tags']})_\n\n")
            f.write(f"**Title:** {r['title'] or '(no title)'}\n\n")
            f.write(f"**Body:** {truncate(r['selftext'], 500)}\n\n---\n\n")
    print(f"  wrote {out.name}")


def main():
    random.seed(SEED)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    audit1_comments(conn)
    audit2_drift(conn)
    audit3_negative_space(conn)
    audit4_authors(conn)
    audit5_narrative(conn)
    audit6_new_keywords(conn)
    audit7_cross_classifier(conn)
    conn.close()


if __name__ == "__main__":
    main()
