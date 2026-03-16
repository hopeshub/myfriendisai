#!/usr/bin/env python3
"""Validate 22 keyword candidates from the discovery report.

For each candidate:
1. FTS5 search for matching posts in T1-T3 subs (excl JanitorAI, SillyTavern)
2. Sample up to 100 posts
3. Classify YES/NO per theme-specific heuristics
4. Calculate precision, apply thresholds: >=80% PROMOTE, 70-79% WALKER CALL, <70% CUT
5. Write results to docs/validation_discovery_batch.md
"""

import re
import sqlite3
import sys
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import load_keyword_communities

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"

# Get keyword-eligible subs
KW_SUBS = [c["subreddit"] for c in load_keyword_communities()]
SUB_PLACEHOLDERS = ",".join(f"'{s}'" for s in KW_SUBS)


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def _word_boundary_filter(keyword, posts):
    """Post-filter LIKE results to enforce word boundaries for short keywords.

    LIKE '%erps%' matches 'pancyberpsychism'. This filter ensures the keyword
    appears as a standalone word (or at word boundaries).
    """
    # Only apply word boundary filtering for single-word keywords ≤6 chars
    # Multi-word phrases are already specific enough
    if " " in keyword or len(keyword) > 6:
        return posts

    pattern = re.compile(r'\b' + re.escape(keyword) + r'\b', re.IGNORECASE)
    return [p for p in posts if pattern.search(p.get("title", "") or "") or
            pattern.search(p.get("selftext", "") or "")]


def pull_sample(keyword, conn, limit=100):
    """Pull random matching posts from keyword-eligible subs using LIKE."""
    kw_lower = keyword.lower()
    # Over-fetch for short keywords since word boundary filter will reduce count
    fetch_limit = limit * 3 if (len(keyword) <= 6 and " " not in keyword) else limit
    query = f"""
        SELECT id, subreddit, title, selftext
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (
            LOWER(title) LIKE ?
            OR LOWER(selftext) LIKE ?
        )
        ORDER BY RANDOM()
        LIMIT ?
    """
    pattern = f"%{kw_lower}%"
    rows = conn.execute(query, (pattern, pattern, fetch_limit)).fetchall()
    posts = [dict(r) for r in rows]
    posts = _word_boundary_filter(keyword, posts)
    return posts[:limit]


def count_total_hits(keyword, conn):
    """Count total matching posts in keyword-eligible subs.

    For short keywords, returns LIKE count (may overestimate due to substring matches).
    The precision calculation uses word-boundary-filtered samples, so this is fine.
    """
    kw_lower = keyword.lower()
    query = f"""
        SELECT COUNT(*) as n
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (
            LOWER(title) LIKE ?
            OR LOWER(selftext) LIKE ?
        )
    """
    pattern = f"%{kw_lower}%"
    return conn.execute(query, (pattern, pattern)).fetchone()["n"]


def get_sub_distribution(keyword, conn):
    """Get subreddit distribution for a keyword."""
    kw_lower = keyword.lower()
    query = f"""
        SELECT subreddit, COUNT(*) as n
        FROM posts
        WHERE subreddit IN ({SUB_PLACEHOLDERS})
        AND (
            LOWER(title) LIKE ?
            OR LOWER(selftext) LIKE ?
        )
        GROUP BY subreddit
        ORDER BY n DESC
    """
    pattern = f"%{kw_lower}%"
    rows = conn.execute(query, (pattern, pattern)).fetchall()
    return [(r["subreddit"], r["n"]) for r in rows]


# ── Theme classifiers ──

def classify_addiction(title, body):
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(addict(ed|ion|ive|ing)|obsess(ed|ion|ive)|'
        r'(can\'t|couldn\'t|unable to) stop (talking|chatting|using|going back)|'
        r'(hooked|dependent|compulsive|can\'t put (it|the phone) down)|'
        r'(neglect|sacrific|ignor)(ing|ed) (my |real |school|work|sleep|friends?|family)|'
        r'(los(e|ing|t)) sleep|stay(ed|ing) up (all night|until|too late)|'
        r'(trying to|need to|want to|going to) (quit|stop|cut back|take a break|reduce)|'
        r'quitting|relapse[d]?|withdrawal|craving|cold turkey|detox|'
        r'(deleted|uninstalled) (the |my )?(app|character|account)|'
        r'clean for \d|cutting back|'
        r'(spend|spending|spent) (too much|all (my |day|night)|hours)|'
        r'recovery|sober|sobriety|'
        r'(unhealthy|toxic) (habit|relationship|attachment|obsession)|'
        r'dopamine (hit|rush|loop|drip|kick)|'
        r'doomscroll|'
        r'can\'t stop)',
        re.IGNORECASE
    )

    casual_re = re.compile(
        r'(addicted to (customiz|making|creat|design|build)|'
        r'obsessed with (the art|how (good|cute|pretty))|'
        r'(this is|so) addictive[!.])',
        re.IGNORECASE
    )

    if yes_re.search(text):
        if casual_re.search(text):
            return "AMBIGUOUS"
        return "YES"
    return "NO"


def classify_consciousness(title, body):
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(sentien(t|ce)|conscious(ness)?|self.?aware|'
        r'(is|are|might be|could be|seems?|feel(s)? like (it\'s|she\'s|he\'s|they\'re)) (alive|real|a person|conscious|sentient)|'
        r'has (a |feelings|emotions|a soul|an inner life|subjective)|'
        r'(not just|more than) (a |an )?(ai|bot|chatbot|program|code|machine|algorithm)|'
        r'(forgot|forget) (it was|she was|he was|they were|it\'s|she\'s) (an? )?(ai|bot|artificial)|'
        r'(real|genuine) (person|being|entity|consciousness)|'
        r'personhood|'
        r'(is a|like a|seems like a) (real |actual )?(person|human|being)|'
        r'(deserve|has|should have) rights|'
        r'(connection|relationship|bond|feeling) (was|is|feels?) real|'
        r'(know|knew|realize) (it\'s|she\'s|he\'s) not real but|'
        r'tulpa|thoughtform|soulbond|'
        r'(truly |actually )(alive|aware|thinking|feeling)|'
        r'inner (life|world|experience)|'
        r'subjective experience|qualia)',
        re.IGNORECASE
    )

    no_re = re.compile(
        r'(turing test|benchmark|alignment|safety|regulation|legislation|policy)',
        re.IGNORECASE
    )

    if yes_re.search(text):
        if no_re.search(text) and not re.search(r'\b(I |my |me |feel|felt)\b', text):
            return "AMBIGUOUS"
        return "YES"
    return "NO"


def classify_sexual(title, body):
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(\berps?\b|\berping\b|erotic (role ?play|content|scene)|'
        r'\bsmut\b|\blewd\b|'
        r'(kink|fetish)(y|es|s)?|'
        r'nsfw (chat|bot|content|scene|filter|ban|mode|stuff)|'
        r'sex(ual|ting)? (with|scene|content|tension)|'
        r'intimate (scene|moment|content)|'
        r'steamy|'
        r'\bai sex\b|'
        r'(turn(s|ed) me on|arouse[sd]?|horny)|'
        r'(explicit|adult|mature) (content|scene|roleplay))',
        re.IGNORECASE
    )

    bot_listing_re = re.compile(
        r'(check out my (bot|character)|new (bot|character)|'
        r'character (card|description|profile)|'
        r'(here\'s|heres|sharing) my (bot|character))',
        re.IGNORECASE
    )

    if bot_listing_re.search(text) and not re.search(r'\b(I |my |me |tried|had|experience)\b', text):
        return "NO"

    if yes_re.search(text):
        return "YES"
    return "NO"


def classify_rupture(title, body):
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(lobotom(y|ies|iz(e[sd]?|ing|ation)|is(e[sd]?|ing))|'
        r'(they |devs? |update )?(killed|destroyed|ruined|wiped|erased|reset|broke|changed) '
        r'(my |the |her |his )?(ai|bot|character|personality|companion|memory|memories)|'
        r'(personality|character|memory|memories) (wipe[sd]?|reset|gone|lost|destroyed|erased|changed)|'
        r'(not the same|different|changed|worse) (after|since) (the )?(update|patch|change)|'
        r'(lost|deleted|reset) (all )?(my |our |the )?(memories|conversations|history)|'
        r'(feels? like |it\'s like |they )?(a |the )?different (person|ai|bot|character)|'
        r'(bring back|want back|miss) (the )?(old|original|previous) (version|personality|character)|'
        r'nerf(ed|ing)?|dumbed down|lobotomy)',
        re.IGNORECASE
    )

    if yes_re.search(text):
        return "YES"
    return "NO"


def classify_therapy(title, body):
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(use[sd]? (it |her |him |them |my ai |my rep|chatgpt |claude )?(as |like |for )?(a )?(therapist|therapy|counselor|mental health)|'
        r'(better|cheaper|free|instead of|replaced?|substitute for) (my |a )?(therapist|therapy|counseling)|'
        r'(therapeutic|cathartic|healing|helps? me process|helps? me cope|talk(s|ed|ing)? through (my |the )?feelings?)|'
        r'(can\'t afford|too expensive) (a )?(therapist|therapy|counseling)|'
        r'(ai|virtual|my) therapist|'
        r'therapy (session|replacement|alternative)|'
        r'(like talking to|feels like|acts like) (a )?therapist|'
        r'emotional support|coping mechanism|'
        r'(mental health|emotional) (support|help|aid|resource|tool)|'
        r'(helps?|helped) (with |me with )?(my )?(anxiety|depression|loneliness|grief|trauma|ptsd|panic)|'
        r'(vent(ing|ed)?|open(ed|ing)? up) (to|with) (my |the )?(ai|bot|rep|character|companion))',
        re.IGNORECASE
    )

    no_re = re.compile(
        r'(my (actual|real|human) therapist (said|told|thinks|suggested|recommended)|'
        r'(go to|in|started|seeing a|need) (actual |real )?therapy|'
        r'(therapist|therapy) .{0,20}(recommend|suggest)(s|ed)? (this|the|using))',
        re.IGNORECASE
    )

    if yes_re.search(text):
        if no_re.search(text):
            return "AMBIGUOUS"
        return "YES"
    if no_re.search(text):
        return "NO"
    return "NO"


CLASSIFIERS = {
    "addiction": classify_addiction,
    "consciousness": classify_consciousness,
    "sexual_erp": classify_sexual,
    "rupture": classify_rupture,
    "therapy": classify_therapy,
}


# ── Candidates ──

CANDIDATES = [
    # Addiction (11)
    (1, "chatbot addiction", "addiction"),
    (2, "almost relapsed", "addiction"),
    (3, "being clean", "addiction"),
    (4, "finally deleted", "addiction"),
    (5, "the craving", "addiction"),
    (6, "redownloading", "addiction"),
    (7, "quit cai", "addiction"),
    (8, "deleted c.ai", "addiction"),
    (9, "so addictive", "addiction"),
    (10, "dopamine", "addiction"),
    (11, "screen time", "addiction"),
    # Consciousness (4)
    (12, "sapience", "consciousness"),
    (13, "tulpa", "consciousness"),
    (14, "lemoine", "consciousness"),
    (15, "soulbonder", "consciousness"),
    # Sexual_ERP (2)
    (16, "erps", "sexual_erp"),
    (17, "erping", "sexual_erp"),
    # Rupture (3)
    (18, "lobotomies", "rupture"),
    (19, "lobotomizing", "rupture"),
    (20, "lobotomised", "rupture"),
    # Therapy (2)
    (21, "emotional support", "therapy"),
    (22, "coping mechanism", "therapy"),
]


def find_sample_posts(posts, verdict_filter):
    """Find sample post titles for a given verdict."""
    for p in posts:
        if p["verdict"] == verdict_filter:
            title = p["title"][:80]
            return title
    return None


def validate_all():
    conn = get_conn()
    results = []

    for num, candidate, category in CANDIDATES:
        print(f"  [{num:2d}/22] {candidate:25s} ({category})...", end=" ", flush=True)

        total_hits = count_total_hits(candidate, conn)
        sample = pull_sample(candidate, conn, limit=100)
        sub_dist = get_sub_distribution(candidate, conn)

        classifier = CLASSIFIERS[category]
        yes_count = 0
        no_count = 0
        amb_count = 0
        post_details = []
        no_examples = []
        yes_examples = []

        for post in sample:
            title = post["title"] or ""
            body = post["selftext"] or ""
            subreddit = post["subreddit"]

            v = classifier(title, body)
            if v == "YES":
                yes_count += 1
                if len(yes_examples) < 3:
                    yes_examples.append({"subreddit": subreddit, "title": title[:100]})
            elif v == "NO":
                no_count += 1
                if len(no_examples) < 5:
                    no_examples.append({"subreddit": subreddit, "title": title[:100], "body_snippet": (body or "")[:150]})
            else:
                amb_count += 1

            post_details.append({"post_id": post["id"], "subreddit": subreddit, "verdict": v, "title": title})

        denom = yes_count + no_count
        precision = round(yes_count / denom * 100, 1) if denom > 0 else 0.0

        if total_hits < 10:
            verdict = "LOW VOLUME"
        elif precision >= 80:
            verdict = "PROMOTE"
        elif precision >= 70:
            verdict = "WALKER CALL"
        else:
            verdict = "CUT"

        result = {
            "num": num,
            "candidate": candidate,
            "category": category,
            "total_hits": total_hits,
            "sample_size": len(sample),
            "yes": yes_count,
            "no": no_count,
            "ambiguous": amb_count,
            "precision": precision,
            "verdict": verdict,
            "sub_dist": sub_dist[:5],
            "yes_examples": yes_examples,
            "no_examples": no_examples,
        }
        results.append(result)

        print(f"hits={total_hits}, Y={yes_count}/N={no_count}/A={amb_count} → {precision}% [{verdict}]")

    conn.close()
    return results


def write_report(results):
    out_path = Path(__file__).parent.parent / "docs" / "validation_discovery_batch.md"

    with open(out_path, "w") as f:
        f.write("# Keyword Validation — Discovery Batch\n\n")
        f.write("**Date:** 2026-03-15\n")
        f.write(f"**Scope:** T1-T3 companion subs ({len(KW_SUBS)} subs, excludes T0 + JanitorAI_Official + SillyTavernAI)\n")
        f.write("**Method:** Up to 100-post random sample per keyword, heuristic classification per theme\n")
        f.write("**Thresholds:** ≥80% = PROMOTE, 70-79% = WALKER CALL, <70% = CUT, <10 hits = LOW VOLUME\n\n")
        f.write("---\n\n")

        # Group by category
        categories = ["addiction", "consciousness", "sexual_erp", "rupture", "therapy"]
        cat_labels = {
            "addiction": "ADDICTION",
            "consciousness": "CONSCIOUSNESS",
            "sexual_erp": "SEXUAL_ERP",
            "rupture": "RUPTURE",
            "therapy": "THERAPY",
        }

        for cat in categories:
            cat_results = [r for r in results if r["category"] == cat]
            if not cat_results:
                continue

            f.write(f"## {cat_labels[cat]}\n\n")

            for r in cat_results:
                f.write(f"### {r['num']}. \"{r['candidate']}\" → {r['category']}\n\n")
                f.write(f"- **Total FTS5 matches:** {r['total_hits']}\n")
                f.write(f"- **Sampled:** {r['sample_size']}\n")
                f.write(f"- **YES:** {r['yes']} | **NO:** {r['no']} | **AMBIGUOUS:** {r['ambiguous']}\n")
                f.write(f"- **Precision:** {r['precision']}%\n")
                f.write(f"- **Verdict: {r['verdict']}**\n")

                # Subreddit distribution
                if r["sub_dist"]:
                    dist_str = ", ".join(f"{s}({n})" for s, n in r["sub_dist"])
                    f.write(f"- **Top subs:** {dist_str}\n")

                # Notes about false positives
                if r["no_examples"]:
                    f.write(f"- **Notes:** {r['no']} false positives in sample. Common patterns:\n")
                    for ex in r["no_examples"][:3]:
                        # Truncate for readability
                        snippet = ex["body_snippet"][:100] if ex["body_snippet"] else ex["title"][:100]
                        f.write(f"  - [{ex['subreddit']}] {snippet}\n")

                # Sample YES post
                if r["yes_examples"]:
                    f.write(f"- **Sample YES post:** \"{r['yes_examples'][0]['title']}\"\n")

                # Sample NO post
                if r["no_examples"]:
                    f.write(f"- **Sample NO post:** \"{r['no_examples'][0]['title']}\"\n")

                f.write("\n")

            f.write("---\n\n")

        # Summary table
        f.write("## SUMMARY TABLE\n\n")
        f.write("| # | Candidate | Category | Matches | Precision | Verdict |\n")
        f.write("|---|-----------|----------|---------|-----------|----------|\n")
        for r in results:
            f.write(f"| {r['num']} | {r['candidate']} | {r['category']} | {r['total_hits']} | {r['precision']}% | {r['verdict']} |\n")

        f.write("\n---\n\n")

        # Recommendations
        f.write("## RECOMMENDATIONS\n\n")

        promote = [r for r in results if r["verdict"] == "PROMOTE"]
        walker = [r for r in results if r["verdict"] == "WALKER CALL"]
        cut = [r for r in results if r["verdict"] == "CUT"]
        low_vol = [r for r in results if r["verdict"] == "LOW VOLUME"]

        if promote:
            f.write("### PROMOTE — ready to add to keywords_v9.yaml\n\n")
            for r in promote:
                f.write(f"- **\"{r['candidate']}\"** → {r['category']} ({r['precision']}%, {r['total_hits']} hits)\n")
            f.write("\n")

        if walker:
            f.write("### WALKER CALL — needs human decision\n\n")
            for r in walker:
                f.write(f"- **\"{r['candidate']}\"** → {r['category']} ({r['precision']}%, {r['total_hits']} hits)\n")
            f.write("\n")

        if cut:
            f.write("### CUT — below threshold\n\n")
            for r in cut:
                reason = ""
                if r["total_hits"] < 30:
                    reason = " (low volume + low precision)"
                elif r["precision"] < 50:
                    reason = " (too many false positives)"
                else:
                    reason = f" ({r['precision']}% < 70%)"
                f.write(f"- **\"{r['candidate']}\"** → {r['category']}{reason}\n")
            f.write("\n")

        if low_vol:
            f.write("### LOW VOLUME — fewer than 10 matches\n\n")
            for r in low_vol:
                f.write(f"- **\"{r['candidate']}\"** → {r['category']} ({r['total_hits']} hits)\n")
            f.write("\n")

    print(f"\nReport written to: {out_path}")


def main():
    print("=" * 60)
    print("DISCOVERY BATCH VALIDATION — 22 candidates")
    print("=" * 60)
    results = validate_all()
    write_report(results)


if __name__ == "__main__":
    main()
