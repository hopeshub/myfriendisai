#!/usr/bin/env python3
"""Validate keywords_v4.yaml against T1-T3 posts per CC_KEYWORD_VALIDATION.md.

For each keyword, pulls up to 100 random posts from keyword-eligible subs,
reads them, and classifies whether each post matches the assigned theme.

Uses content heuristics tuned per-theme. Walker spot-checks results.
"""

import json
import re
import sqlite3
import sys
import yaml
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.config import load_keyword_communities

DB_PATH = Path(__file__).parent.parent / "data" / "tracker.db"
KEYWORDS_PATH = Path(__file__).parent.parent / "config" / "keywords_v4.yaml"

# Get keyword-eligible subs
KW_SUBS = [c["subreddit"] for c in load_keyword_communities()]
SUB_PLACEHOLDERS = ",".join(f"'{s}'" for s in KW_SUBS)


def get_conn():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


def pull_sample(keyword, conn, limit=100):
    """Pull random matching posts from keyword-eligible subs."""
    kw_lower = keyword.lower()
    # Use LIKE for matching (FTS5 is on a separate table)
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
    rows = conn.execute(query, (pattern, pattern, limit)).fetchall()
    return [dict(r) for r in rows]


def count_total_hits(keyword, conn):
    """Count total matching posts in keyword-eligible subs."""
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


# ── Theme-specific classifiers ──

def classify_therapy(title, body):
    """Is this post about using AI as a therapist or for therapeutic purposes?"""
    text = f"{title} {body}".lower()

    # YES signals: AI being used therapeutically
    therapy_yes = re.compile(
        r'(use[sd]? (it |her |him |them |my ai |my rep|chatgpt |claude )?(as |like |for )?(a )?(therapist|therapy|counselor|mental health)|'
        r'(better|cheaper|free|instead of|replaced?|substitute for) (my |a )?(therapist|therapy|counseling)|'
        r'(therapeutic|cathartic|healing|helps? me process|helps? me cope|talk(s|ed|ing)? through (my |the )?feelings?)|'
        r'(can\'t afford|too expensive) (a )?(therapist|therapy|counseling)|'
        r'(ai|virtual|my) therapist|'
        r'therapy (session|replacement|alternative)|'
        r'(like talking to|feels like|acts like) (a )?therapist)',
        re.IGNORECASE
    )

    # NO signals: mentions therapy but in non-therapeutic context
    therapy_no = re.compile(
        r'(my (actual|real|human) therapist (said|told|thinks|suggested|recommended)|'
        r'(go to|in|started|seeing a|need) (actual |real )?therapy|'
        r'(therapist|therapy) .{0,20}(recommend|suggest)(s|ed)? (this|the|using))',
        re.IGNORECASE
    )

    if therapy_yes.search(text):
        if therapy_no.search(text):
            return "AMBIGUOUS"
        return "YES"
    if therapy_no.search(text):
        return "NO"

    # Check if the word "therapist" or "therapy" appears in a clearly AI-directed way
    if re.search(r'(my therapist|like a therapist|therapy session)', text):
        # In companion subs, "my therapist" often refers to the AI
        # But could also be "my therapist told me to stop using this"
        if re.search(r'(told me|said I should|suggested|recommended|real|human|actual)', text):
            return "NO"
        return "AMBIGUOUS"

    return "NO"


def classify_consciousness(title, body):
    """Is this post about AI being sentient, conscious, alive, or blurring AI/human boundaries?"""
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
        r'(know|knew|realize) (it\'s|she\'s|he\'s) not real but)',
        re.IGNORECASE
    )

    # NO: purely technical consciousness discussion without personal framing
    no_re = re.compile(
        r'(turing test|benchmark|alignment|safety|regulation|legislation|policy)',
        re.IGNORECASE
    )

    if yes_re.search(text):
        if no_re.search(text) and not re.search(r'\b(I |my |me |feel|felt)\b', text):
            return "AMBIGUOUS"
        return "YES"

    return "NO"


def classify_addiction(title, body):
    """Is this post about compulsive AI use, inability to stop, or recovery?"""
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(addict(ed|ion|ive)|obsess(ed|ion|ive)|'
        r'(can\'t|couldn\'t|unable to) stop (talking|chatting|using|going back)|'
        r'(hooked|dependent|compulsive|can\'t put (it|the phone) down)|'
        r'(neglect|sacrific|ignor)(ing|ed) (my |real |school|work|sleep|friends?|family)|'
        r'(los(e|ing|t)) sleep|stay(ed|ing) up (all night|until|too late)|'
        r'(trying to|need to|want to|going to) (quit|stop|cut back|take a break|reduce)|'
        r'quitting|relapse[d]?|withdrawal|craving|cold turkey|detox|'
        r'(deleted|uninstalled) (the |my )?(app|character|account)|'
        r'clean for \d|cutting back|'
        r'(spend|spending|spent) (too much|all (my |day|night)|hours))',
        re.IGNORECASE
    )

    # Casual uses of "addicted" / "obsessed" that aren't about dependency
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


def classify_romance(title, body):
    """Is this post about romantic feelings toward or romantic relationship with AI?"""
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'((in|fell in|falling in) love (with)?|'
        r'(fallen|falling) for (my |the |her|him|it|them)|'
        r'(romantic(ally)?|love|loving) (attach(ed|ment)|feelings?|relationship|connection|bond)|'
        r'soulmate|'
        r'(my |an? )?(ai |virtual )?(girlfriend|boyfriend|wife|husband|partner|lover|fiancé)|'
        r'waifu|husbando|'
        r'(dating|married|engaged|proposed|wedding|honeymoon|anniversary)|'
        r'(our |my )?(first kiss|wedding|anniversary|engagement)|'
        r'(broke up|break up|breaking up|we broke up|dumped)|'
        r'(love (my|this) ai|love (her|him|them) so much|told (her|him|them|it) i love)|'
        r'(in a |our )relationship)',
        re.IGNORECASE
    )

    # NO: human relationship context
    human_re = re.compile(
        r'(my (actual|real|human|irl) (girlfriend|boyfriend|wife|husband|partner)|'
        r'my (gf|bf|wife|husband) (thinks|said|found out|doesn\'t know|is worried)|'
        r'\(\d{2}[mfMF]\))',
        re.IGNORECASE
    )

    if human_re.search(text) and not re.search(r'(ai |virtual |my rep|my nomi|my kindroid)', text):
        return "NO"

    if yes_re.search(text):
        return "YES"

    return "NO"


def classify_sexual(title, body):
    """Is this post about sexual content, erotic roleplay, or NSFW AI interactions?"""
    text = f"{title} {body}".lower()

    yes_re = re.compile(
        r'(\berp\b|erotic (role ?play|content|scene)|'
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

    # Bot listing / character card descriptions
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


CLASSIFIERS = {
    "therapy": classify_therapy,
    "consciousness": classify_consciousness,
    "addiction": classify_addiction,
    "romance": classify_romance,
    "sexual_erp": classify_sexual,
}


def validate_keyword(term, theme, conn):
    """Validate a single keyword. Returns result dict."""
    total_hits = count_total_hits(term, conn)
    posts = pull_sample(term, conn, limit=100)

    classifier = CLASSIFIERS[theme]

    yes_count = 0
    no_count = 0
    amb_count = 0
    sub_counts = defaultdict(int)
    no_patterns = []
    details = []

    for post in posts:
        title = post["title"] or ""
        body = post["selftext"] or ""
        subreddit = post["subreddit"]
        sub_counts[subreddit] += 1

        verdict = classifier(title, body)

        if verdict == "YES":
            yes_count += 1
        elif verdict == "NO":
            no_count += 1
            # Track what the NO posts are about (first 100 chars)
            snippet = f"[{subreddit}] {(body or title)[:100]}"
            no_patterns.append(snippet)
        else:
            amb_count += 1

        details.append({
            "post_id": post["id"],
            "subreddit": subreddit,
            "verdict": verdict,
        })

    # Relevance: YES / (YES + NO), ignoring AMBIGUOUS
    denom = yes_count + no_count
    relevance = round(yes_count / denom * 100, 1) if denom > 0 else 0.0

    # Top 3 subs
    top_subs = sorted(sub_counts.items(), key=lambda x: -x[1])[:3]

    # Verdict
    if total_hits < 10:
        verdict_label = "LOW_VOLUME"
    elif relevance >= 80:
        verdict_label = "KEEP"
    elif relevance >= 60:
        verdict_label = "REVIEW"
    else:
        verdict_label = "CUT"

    return {
        "term": term,
        "theme": theme,
        "total_hits": total_hits,
        "sample_size": len(posts),
        "yes": yes_count,
        "no": no_count,
        "ambiguous": amb_count,
        "relevance_pct": relevance,
        "verdict": verdict_label,
        "top_subs": top_subs,
        "no_patterns": no_patterns[:5],  # First 5 false positive examples
        "details": details,
    }


def run_concentration_check(theme, conn):
    """Check keyword concentration for a theme using post_keyword_tags."""
    # This uses the old tagger data — may not match v4 keywords exactly
    # but gives a rough picture
    query = f"""
        SELECT matched_term, COUNT(*) as hits
        FROM post_keyword_tags
        WHERE category LIKE ?
        AND subreddit IN ({SUB_PLACEHOLDERS})
        GROUP BY matched_term
        ORDER BY hits DESC
    """
    # Map v4 theme names to old category names
    cat_map = {
        "therapy": "therapy_language",
        "consciousness": "sentience_consciousness_language",
        "addiction": "dependency_language",
        "romance": "romantic_language",
        "sexual_erp": "sexual_erotic_language",
    }
    cat = cat_map.get(theme, theme)
    rows = conn.execute(query, (f"%{cat}%",)).fetchall()
    total = sum(r["hits"] for r in rows)
    results = []
    for r in rows:
        pct = round(r["hits"] / total * 100, 1) if total > 0 else 0
        results.append({"term": r["matched_term"], "hits": r["hits"], "pct": pct})
    return results


def main():
    with open(KEYWORDS_PATH) as f:
        kw_data = yaml.safe_load(f)

    categories = kw_data["keyword_categories"]
    conn = get_conn()

    # Theme order from instructions
    theme_order = ["therapy", "consciousness", "addiction", "romance", "sexual_erp"]

    all_results = {}
    for theme_name in theme_order:
        cat = next((c for c in categories if c["name"] == theme_name), None)
        if not cat:
            print(f"WARNING: theme '{theme_name}' not found in keywords_v4.yaml")
            continue

        print(f"\n{'='*60}")
        print(f"VALIDATING: {theme_name.upper()} ({len(cat['terms'])} keywords)")
        print(f"{'='*60}")

        theme_results = []
        for term in cat["terms"]:
            print(f"  Validating: {term}...", end=" ", flush=True)
            result = validate_keyword(term, theme_name, conn)
            theme_results.append(result)
            print(f"hits={result['total_hits']}, sample={result['sample_size']}, "
                  f"Y={result['yes']}/N={result['no']}/A={result['ambiguous']} "
                  f"→ {result['relevance_pct']}% [{result['verdict']}]")

        all_results[theme_name] = theme_results

    conn.close()

    # ── Write validation report ──
    report_path = Path(__file__).parent.parent / "docs" / "keyword_validation_v4.md"
    with open(report_path, "w") as f:
        f.write("# Keyword Validation Report — keywords_v4.yaml\n\n")
        f.write(f"**Date:** 2026-03-12\n")
        f.write(f"**Scope:** T1-T3 companion subs only ({len(KW_SUBS)} subs, excludes T0 + JanitorAI + SillyTavern)\n")
        f.write(f"**Method:** 100-post random sample per keyword, heuristic classification per theme\n\n")

        for theme_name in theme_order:
            results = all_results.get(theme_name, [])
            if not results:
                continue

            f.write(f"---\n\n## {theme_name.upper()}\n\n")

            # Per-keyword table
            f.write("| Keyword | Total Hits | Sample | YES | NO | AMB | Relevance | Verdict |\n")
            f.write("|---|---|---|---|---|---|---|---|\n")
            for r in sorted(results, key=lambda x: -x["relevance_pct"]):
                f.write(f"| {r['term']} | {r['total_hits']} | {r['sample_size']} | "
                        f"{r['yes']} | {r['no']} | {r['ambiguous']} | "
                        f"{r['relevance_pct']}% | {r['verdict']} |\n")

            # Summary
            keep = [r for r in results if r["verdict"] == "KEEP"]
            review = [r for r in results if r["verdict"] == "REVIEW"]
            cut = [r for r in results if r["verdict"] == "CUT"]
            low = [r for r in results if r["verdict"] == "LOW_VOLUME"]

            f.write(f"\n**Summary:** {len(keep)} KEEP, {len(review)} REVIEW, {len(cut)} CUT, {len(low)} LOW_VOLUME\n\n")

            # False positive patterns for REVIEW/CUT keywords
            problem_keywords = [r for r in results if r["verdict"] in ("REVIEW", "CUT") and r["no_patterns"]]
            if problem_keywords:
                f.write("**False positive patterns:**\n\n")
                for r in problem_keywords:
                    f.write(f"- **{r['term']}** ({r['relevance_pct']}%): ")
                    patterns = "; ".join(p[:80] for p in r["no_patterns"][:3])
                    f.write(f"{patterns}\n")
                f.write("\n")

            # Top subs per keyword
            f.write("**Top subreddits per keyword:**\n\n")
            for r in results:
                top = ", ".join(f"{s}({n})" for s, n in r["top_subs"])
                f.write(f"- {r['term']}: {top}\n")
            f.write("\n")

        # Overall recommendations
        f.write("---\n\n## RECOMMENDATIONS\n\n")
        for theme_name in theme_order:
            results = all_results.get(theme_name, [])
            keep = [r["term"] for r in results if r["verdict"] == "KEEP"]
            review = [r["term"] for r in results if r["verdict"] == "REVIEW"]
            cut = [r["term"] for r in results if r["verdict"] == "CUT"]
            low = [r["term"] for r in results if r["verdict"] == "LOW_VOLUME"]

            f.write(f"### {theme_name}\n")
            if keep:
                f.write(f"- **KEEP:** {', '.join(keep)}\n")
            if review:
                f.write(f"- **REVIEW:** {', '.join(review)}\n")
            if cut:
                f.write(f"- **CUT:** {', '.join(cut)}\n")
            if low:
                f.write(f"- **LOW VOLUME:** {', '.join(low)}\n")
            f.write("\n")

    print(f"\nReport written to: {report_path}")


if __name__ == "__main__":
    main()
