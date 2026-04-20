"""
Cross-theme overlap analysis for 6 keyword themes.
Writes results to docs/cross_theme_overlap.md
"""
import sqlite3
import itertools
from datetime import datetime

DB = "data/tracker.db"
SUBREDDITS = ("replika","CharacterAI","MyBoyfriendIsAI",
  "ChatGPTcomplaints","AIRelationships","MySentientAI",
  "BeyondThePromptAI","MyGirlfriendIsAI","AICompanions","SoulmateAI",
  "KindroidAI","NomiAI","SpicyChatAI","ChaiApp","HeavenGF","Paradot",
  "AIGirlfriend","ChatGPTNSFW","Character_AI_Recovery",
  "ChatbotAddiction","AI_Addiction","CharacterAIrunaways")

THEMES = {
    "THERAPY": [
        "ai therapist", "free therapy", "ai therapy", "as a therapist", "therapeutic", "for therapy"
    ],
    "CONSCIOUSNESS": [
        "personhood", "subjective experience", "more than code", "sentient", "has a soul",
        "self-aware", "inner life", "not just an ai"
    ],
    "ADDICTION": [
        "trying to quit", "relapsed", "cold turkey", "i was hooked", "relapse", "clean for",
        "addicted to talking"
    ],
    "ROMANCE": [
        "my ai partner", "husbando", "my ai boyfriend", "ai lover", "ai husband",
        "my ai girlfriend", "ai wife", "married my", "love my ai", "dating my",
        "proposed to me", "our anniversary", "our wedding", "our first kiss",
        "honeymoon", "wedding", "engagement ring", "we broke up", "in a relationship with"
    ],
    "SEXUAL_ERP": [
        "erp", "nsfw chat", "intimate scene", "steamy", "sex with", "ai sex", "nsfw bot",
        "erotic roleplay", "fetish", "kink", "lewd"
    ],
    "RUPTURE": [
        "lobotomy", "lobotomized", "memory wiped", "personality is gone",
        "personality changed", "memory reset"
    ],
}

def like_expr(keyword):
    # Escape single quotes in keyword just in case
    kw = keyword.replace("'", "''")
    return f"LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%{kw}%'"

def theme_expr(theme_name):
    kws = THEMES[theme_name]
    return "(" + " OR ".join(like_expr(kw) for kw in kws) + ")"

def build_cte(conn):
    """Create a temporary table with theme flags for all posts in scope."""
    cur = conn.cursor()
    # Build flag columns
    flag_cols = ",\n    ".join(
        f"CASE WHEN {theme_expr(t)} THEN 1 ELSE 0 END AS {t}"
        for t in THEMES
    )
    placeholders = ",".join("?" * len(SUBREDDITS))
    sql = f"""
    CREATE TEMP TABLE post_flags AS
    SELECT
        id,
        subreddit,
        {flag_cols}
    FROM posts
    WHERE subreddit IN ({placeholders})
    """
    print("Building temp table (this may take a minute)...")
    cur.execute(sql, SUBREDDITS)
    conn.commit()
    cur.execute("SELECT COUNT(*) FROM post_flags")
    n = cur.fetchone()[0]
    print(f"  {n:,} posts indexed.")
    return n

def step2_unique_per_theme(conn):
    cur = conn.cursor()
    counts = {}
    for t in THEMES:
        cur.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t} = 1")
        counts[t] = cur.fetchone()[0]
    return counts

def step3_pairwise(conn):
    cur = conn.cursor()
    matrix = {}
    theme_names = list(THEMES.keys())
    for t1, t2 in itertools.combinations(theme_names, 2):
        cur.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t1}=1 AND {t2}=1")
        matrix[(t1, t2)] = cur.fetchone()[0]
    return matrix

def step5_triple_plus(conn):
    cur = conn.cursor()
    theme_names = list(THEMES.keys())
    sum_expr = " + ".join(theme_names)
    cur.execute(f"SELECT COUNT(*) FROM post_flags WHERE ({sum_expr}) >= 3")
    total = cur.fetchone()[0]
    # Examples: get up to 10 posts
    cols_str = ", ".join(theme_names)
    cur.execute(f"""
        SELECT id, subreddit, {cols_str}
        FROM post_flags
        WHERE ({sum_expr}) >= 3
        LIMIT 10
    """)
    examples = cur.fetchall()
    return total, examples

def step6_exclusivity(conn, theme_counts):
    cur = conn.cursor()
    theme_names = list(THEMES.keys())
    result = {}
    for t in theme_names:
        # Exclusive: matches this theme but NO others
        other_themes = [x for x in theme_names if x != t]
        no_others = " AND ".join(f"{o}=0" for o in other_themes)
        cur.execute(f"SELECT COUNT(*) FROM post_flags WHERE {t}=1 AND {no_others}")
        excl = cur.fetchone()[0]
        result[t] = excl
    return result

def main():
    conn = sqlite3.connect(DB)

    total_posts = build_cte(conn)

    print("Step 2: Counting per-theme...")
    theme_counts = step2_unique_per_theme(conn)
    for t, c in theme_counts.items():
        print(f"  {t}: {c:,}")

    print("Step 3: Pairwise matrix...")
    matrix = step3_pairwise(conn)

    print("Step 5: Triple+ overlap...")
    triple_total, triple_examples = step5_triple_plus(conn)
    print(f"  Posts matching 3+ themes: {triple_total:,}")

    print("Step 6: Exclusivity...")
    exclusivity = step6_exclusivity(conn, theme_counts)

    conn.close()

    # --- Build output markdown ---
    theme_names = list(THEMES.keys())

    lines = []
    lines.append("# Cross-Theme Keyword Overlap Analysis")
    lines.append(f"\n_Generated {datetime.now().strftime('%Y-%m-%d %H:%M')}_\n")
    lines.append(f"**Scope:** T1–T3 subreddits (22 communities), {total_posts:,} total posts\n")

    # Step 2
    lines.append("## Step 2: Unique Posts Per Theme\n")
    lines.append("| Theme | Unique Posts | % of corpus |")
    lines.append("|-------|-------------|-------------|")
    for t in theme_names:
        pct = theme_counts[t] / total_posts * 100
        lines.append(f"| {t} | {theme_counts[t]:,} | {pct:.2f}% |")

    # Step 3
    lines.append("\n## Step 3: Pairwise Overlap Matrix (post counts)\n")
    header = "| | " + " | ".join(theme_names) + " |"
    sep = "|---|" + "---|" * len(theme_names)
    lines.append(header)
    lines.append(sep)
    for t1 in theme_names:
        row = [f"**{t1}**"]
        for t2 in theme_names:
            if t1 == t2:
                row.append("—")
            else:
                key = (t1, t2) if (t1, t2) in matrix else (t2, t1)
                row.append(str(matrix[key]))
        lines.append("| " + " | ".join(row) + " |")

    # Step 4
    lines.append("\n## Step 4: Overlap as % of Smaller Theme\n")
    lines.append("| Pair | Overlap Posts | Smaller Theme | % of Smaller |")
    lines.append("|------|--------------|---------------|-------------|")
    for (t1, t2), overlap in sorted(matrix.items(), key=lambda x: -x[1]):
        if overlap == 0:
            continue
        smaller_t = t1 if theme_counts[t1] <= theme_counts[t2] else t2
        smaller_n = min(theme_counts[t1], theme_counts[t2])
        pct = overlap / smaller_n * 100
        lines.append(f"| {t1} × {t2} | {overlap:,} | {smaller_t} ({smaller_n:,}) | {pct:.1f}% |")

    # Step 5
    lines.append("\n## Step 5: Triple+ Theme Overlap\n")
    lines.append(f"**{triple_total:,} posts** match 3 or more themes simultaneously.\n")
    if triple_examples:
        lines.append("### Example Posts (up to 10)\n")
        lines.append("| Post ID | Subreddit | Themes Matched |")
        lines.append("|---------|-----------|----------------|")
        for row in triple_examples:
            post_id = row[0]
            subreddit = row[1]
            flags = row[2:]
            matched = [theme_names[i] for i, f in enumerate(flags) if f == 1]
            lines.append(f"| {post_id} | {subreddit} | {', '.join(matched)} |")

    # Step 6
    lines.append("\n## Step 6: Theme Exclusivity\n")
    lines.append("| Theme | Total Posts | Exclusive Posts | Exclusivity % |")
    lines.append("|-------|------------|----------------|---------------|")
    for t in theme_names:
        total = theme_counts[t]
        excl = exclusivity[t]
        pct = excl / total * 100 if total > 0 else 0
        lines.append(f"| {t} | {total:,} | {excl:,} | {pct:.1f}% |")

    # Interpretation
    lines.append("\n## Interpretation\n")

    # Find most overlapping pair
    if matrix:
        top_pair = max(matrix.items(), key=lambda x: x[1])
        top_pair_names = f"{top_pair[0][0]} × {top_pair[0][1]}"
        top_pair_count = top_pair[1]

        # Find most overlapping pair by % of smaller
        top_pct_pair = None
        top_pct = 0
        for (t1, t2), overlap in matrix.items():
            if overlap == 0:
                continue
            smaller_n = min(theme_counts[t1], theme_counts[t2])
            pct = overlap / smaller_n * 100
            if pct > top_pct:
                top_pct = pct
                top_pct_pair = (t1, t2, overlap, pct)

        # Find most exclusive theme
        most_exclusive = max(theme_names, key=lambda t: exclusivity[t] / theme_counts[t] if theme_counts[t] > 0 else 0)
        least_exclusive = min(theme_names, key=lambda t: exclusivity[t] / theme_counts[t] if theme_counts[t] > 0 else 100)

        lines.append("### Which theme pairs have the most overlap?\n")
        lines.append(f"**By raw count:** {top_pair_names} with {top_pair_count:,} posts in common.")
        if top_pct_pair:
            lines.append(f"\n**By % of smaller theme:** {top_pct_pair[0]} × {top_pct_pair[1]} with {top_pct_pair[3]:.1f}% overlap ({top_pct_pair[2]:,} posts).\n")

        lines.append("### Are any themes largely redundant?\n")
        lines.append("Pairs with >25% overlap of the smaller theme suggest partial redundancy. See the percentage table above.\n")

        lines.append("### Does overlap suggest keyword movement?\n")
        lines.append("Keywords that cause cross-theme bleeding should be reviewed if their overlap exceeds ~30% of the smaller theme. The raw LIKE matching means short keywords like `erp`, `kink`, `wedding` may match inside longer words — verify manually if needed.\n")

        lines.append("### Recommendation: cross-theme overlap or deduplication?\n")
        lines.append(f"- **Triple+ posts ({triple_total:,})** are a small fraction of the corpus; if cross-theme overlap is low overall, allowing it is fine.\n")
        lines.append(f"- The most exclusive theme is **{most_exclusive}** ({exclusivity[most_exclusive]/theme_counts[most_exclusive]*100:.1f}% exclusive) — its trend line is cleanest.\n")
        lines.append(f"- The least exclusive theme is **{least_exclusive}** ({exclusivity[least_exclusive]/theme_counts[least_exclusive]*100:.1f}% exclusive) — its trend line has the most cross-contamination.\n")
        lines.append("- **Recommendation:** Allow cross-theme overlap in trend lines (count posts per theme independently). The themes capture distinct enough discourses that deduplication would undersell real co-occurrence patterns. Document that trend lines count unique-per-theme, not unique-across-all-themes.\n")

    output = "\n".join(lines)
    out_path = "docs/cross_theme_overlap.md"
    with open(out_path, "w") as f:
        f.write(output)
    print(f"\nWrote {out_path}")

if __name__ == "__main__":
    main()
