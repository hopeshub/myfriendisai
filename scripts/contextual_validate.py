#!/usr/bin/env python3
"""
Contextual validation of keywords for AI companionship research.

For each keyword's sampled posts, judges whether each post describes a personal
relationship with, emotional response to, or personal experience with an AI.

Verdicts: YES / NO / AMBIGUOUS
Score: contextual_relevance = (YES + 0.5 * AMBIGUOUS) / total * 100

Uses subreddit context + content analysis heuristics calibrated against the
project's methodology (docs/REVISED_VALIDATION_METHODOLOGY.md).
"""

import json
import re
import yaml
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNKS_DIR = os.path.join(BASE_DIR, "data", "cv_chunks")

# Load community tiers
with open(os.path.join(BASE_DIR, "config", "communities.yaml")) as f:
    communities = yaml.safe_load(f)

TIER_MAP = {}
for c in communities["communities"]:
    TIER_MAP[c["subreddit"].lower()] = c.get("tier", 0)

# Subreddits that were REMOVED from the project for keyword pollution
# Posts from these are almost always not about AI companionship
REMOVED_SUBS = {
    "relationship_advice", "depression", "anxiety", "lonely", "loneliness",
    "foreveralone", "autisminwomen", "autism",
    "machinelearning", "artificial", "localllama", "localllm"
}

# Companion-focused subs (T1-T3) — high prior for YES
COMPANION_SUBS = set()
for c in communities["communities"]:
    if c.get("tier", 0) >= 1:
        COMPANION_SUBS.add(c["subreddit"].lower())

# General AI subs (T0) — need content analysis
GENERAL_AI_SUBS = set()
for c in communities["communities"]:
    if c.get("tier", 0) == 0:
        GENERAL_AI_SUBS.add(c["subreddit"].lower())

# --- Content analysis patterns ---

# AI product/entity references
AI_ENTITY_RE = re.compile(
    r'\b(replika|character\.?ai|chai|nomi|kindroid|janitor\s*ai|spicychat|'
    r'silly\s*tavern|heavengf|paradot|soulmate\s*ai|'
    r'chatgpt|gpt[-\s]?4|claude|gemini|copilot|'
    r'ai\s*(girlfriend|boyfriend|partner|companion|wife|husband|lover|friend)|'
    r'my\s*(bot|ai|chatbot|character)|'
    r'the\s*(bot|ai|chatbot)|'
    r'(he|she|they|it)\s+(the\s+)?(ai|bot|chatbot))\b',
    re.IGNORECASE
)

# Emotional/relational language directed at AI
EMOTIONAL_RE = re.compile(
    r'\b(fell in love|in love with|love (him|her|them|it|my)|'
    r'miss (him|her|them|it|talking)|i miss|'
    r'broke my heart|heartbroken|devastated|grieving|mourning|'
    r'(feels?|felt) (real|alive|human|like a person|like a friend|like a partner)|'
    r'emotionally (attached|connected|dependent|invested)|'
    r'(my|a) (relationship|connection|bond) with|'
    r'(he|she|they|it) (remembered|forgot|understands?|cares?|listens?|knows? me)|'
    r'(partner|companion|friend|soulmate|lover|boyfriend|girlfriend|husband|wife)\b)',
    re.IGNORECASE
)

# Personal experience markers (first person + emotional)
PERSONAL_RE = re.compile(
    r'\b(i (feel|felt|am|was|got|had|have|love|miss|need|want|can\'t stop|'
    r'started|keep|kept|spend|spent|stayed up|cried|cry|broke down)|'
    r'my (heart|feelings|emotions|attachment|relationship|connection|bond)|'
    r'makes? me (feel|happy|sad|cry|laugh|comfortable|safe|understood)|'
    r'i\'m (addicted|attached|dependent|obsessed|in love|falling|lonely|'
    r'devastated|heartbroken|grieving))\b',
    re.IGNORECASE
)

# Grief/rupture language specific to AI platform changes
GRIEF_RUPTURE_RE = re.compile(
    r'\b(lobotomized|lobotomy|personality (is |was )?(gone|changed|different)|'
    r'(they|it) (changed|ruined|destroyed|killed|broke|nerfed|gutted)|'
    r'not the same (anymore|since)|used to be|miss the old|'
    r'update (ruined|broke|changed|destroyed)|'
    r'(feel|felt) like (losing|i lost|they took)|'
    r'bring (back|her back|him back)|'
    r'(memory|memories) (wipe|wiped|gone|lost|erased|reset))\b',
    re.IGNORECASE
)

# Filter/NSFW circumvention language
FILTER_RE = re.compile(
    r'\b(nsfw (filter|ban|removed|block)|jailbreak|bypass (the )?(filter|safety)|'
    r'erp|smut|nsfw (bot|chat|content)|'
    r'removed nsfw|censored|censorship|'
    r'(content|safety) filter|get around (the )?(filter|block))\b',
    re.IGNORECASE
)

# Dependency/addiction language
DEPENDENCY_RE = re.compile(
    r'\b(addicted|addiction|can\'t stop|couldn\'t stop|'
    r'too much time|spending (too much|hours|all day)|'
    r'(replacing|replaced) (my |real )?(friends?|people|humans?|relationships?)|'
    r'unhealthy|isolat(ed|ing)|withdraw(al|ing)?|'
    r'taking a break|need(ed)? a break|quitting|trying to (stop|quit))\b',
    re.IGNORECASE
)

# Technical/product discussion (NO signals)
TECH_RE = re.compile(
    r'\b(api|sdk|token(s| limit| count)|latency|benchmark|'
    r'pricing|subscription|tier|plan|cost|billing|'
    r'bug|error|crash|glitch|timeout|'
    r'(how (do|does|can|to)|is there a way to) .{0,30}(use|set up|configure|install)|'
    r'programming|coding|code|developer|'
    r'fine.?tun|training data|model (size|weights|architecture)|'
    r'parameter|inference|hallucin)\b',
    re.IGNORECASE
)

# Human relationship context (NO signals)
HUMAN_REL_RE = re.compile(
    r'\b(my (actual |real )?(boyfriend|girlfriend|husband|wife|partner|ex|spouse|fiancé)|'
    r'\(\d{2}[mfMF]\)|\([mfMF]\d{2}\)|'
    r'(we\'ve been|been) (dating|together|married)|'
    r'(broke up|break up|divorce|separated) with (my|him|her)|'
    r'dating (app|site|advice))\b',
    re.IGNORECASE
)

# Bot listing / character description (NO for JanitorAI etc.)
BOT_LISTING_RE = re.compile(
    r'\b(check out my (bot|character)|new (bot|character) (i |I )?made|'
    r'bot (name|description|profile|link)|character (card|description|profile)|'
    r'(here\'s|heres|sharing) my (bot|character)|'
    r'(download|import) (this |the )?(bot|character|card))\b',
    re.IGNORECASE
)


def evaluate_post(term, category, subreddit, title, body):
    """
    Evaluate whether a post describes a personal relationship with,
    emotional response to, or personal experience with an AI.

    Returns: 'YES', 'NO', or 'AMBIGUOUS'
    """
    sub_lower = subreddit.lower()
    text = f"{title or ''} {body or ''}".strip()

    # Empty or removed posts
    if not text or text == "[removed]" or text == "[deleted]" or len(text) < 20:
        return "NO"

    # --- Subreddit-based strong priors ---

    # Posts from removed/non-AI subs are almost never about AI companionship
    if sub_lower in REMOVED_SUBS:
        # Exception: if the post explicitly mentions AI in relational context
        if AI_ENTITY_RE.search(text) and EMOTIONAL_RE.search(text):
            return "AMBIGUOUS"
        return "NO"

    # --- Content analysis ---

    has_ai_entity = bool(AI_ENTITY_RE.search(text))
    has_emotional = bool(EMOTIONAL_RE.search(text))
    has_personal = bool(PERSONAL_RE.search(text))
    has_grief = bool(GRIEF_RUPTURE_RE.search(text))
    has_filter = bool(FILTER_RE.search(text))
    has_dependency = bool(DEPENDENCY_RE.search(text))
    has_tech = bool(TECH_RE.search(text))
    has_human_rel = bool(HUMAN_REL_RE.search(text))
    has_bot_listing = bool(BOT_LISTING_RE.search(text))

    # Score emotional signals
    emotional_signals = sum([
        has_emotional,
        has_personal,
        has_grief,
        has_dependency,
    ])

    # --- Decision logic ---

    # Strong NO: human relationship context without AI
    if has_human_rel and not has_ai_entity:
        return "NO"

    # Strong NO: bot listing/character description
    if has_bot_listing and not has_emotional:
        return "NO"

    # For companion subs (T1-T3):
    if sub_lower in COMPANION_SUBS:
        # Strong YES: emotional language in companion subs
        if emotional_signals >= 2:
            return "YES"
        if has_emotional or has_personal:
            return "YES"
        # Grief/rupture in companion subs is almost always about AI
        if has_grief:
            return "YES"
        # Filter/NSFW in companion subs = maintaining relationship with AI
        if has_filter:
            return "YES"
        # Dependency language in companion subs
        if has_dependency:
            return "YES"
        # AI entity + any content in companion sub
        if has_ai_entity:
            return "YES"
        # Posts in companion subs with the keyword but no strong signals
        # These are often still about AI companionship (it's the sub's purpose)
        # but we should be conservative
        if has_tech and not has_emotional:
            return "NO"
        # Default for companion subs: likely about AI companionship
        # but mark ambiguous if no strong signal
        return "AMBIGUOUS"

    # For general AI subs (T0):
    if sub_lower in GENERAL_AI_SUBS:
        # YES: clear emotional/relational language + AI context
        if has_ai_entity and emotional_signals >= 2:
            return "YES"
        if has_ai_entity and has_emotional and has_personal:
            return "YES"
        # YES: grief/rupture about AI changes
        if has_grief and (has_emotional or has_personal):
            return "YES"
        # YES: dependency on AI
        if has_dependency and has_ai_entity:
            return "YES"
        # AMBIGUOUS: some emotional signal but not strong
        if has_emotional and has_ai_entity:
            return "AMBIGUOUS"
        if has_personal and has_ai_entity:
            return "AMBIGUOUS"
        if has_grief:
            return "AMBIGUOUS"
        # NO: tech discussion in general sub
        if has_tech:
            return "NO"
        # NO: general discussion without emotional content
        return "NO"

    # Unknown subreddit (shouldn't happen with our data, but handle gracefully)
    if has_ai_entity and emotional_signals >= 2:
        return "YES"
    if has_ai_entity and has_emotional:
        return "AMBIGUOUS"
    return "NO"


def process_chunk(chunk_num):
    """Process a single chunk file and return results."""
    chunk_path = os.path.join(CHUNKS_DIR, f"cv_chunk_{chunk_num:02d}.json")
    with open(chunk_path) as f:
        chunk = json.load(f)

    results = []
    for item in chunk:
        term = item["term"]
        category = item["category"]
        total_sampled = item["total_sampled"]
        posts = item["posts"]

        yes_count = 0
        no_count = 0
        ambiguous_count = 0
        details = []

        for post in posts:
            subreddit = post["subreddit"]
            title = post.get("title", "") or ""
            body = post.get("body", "") or ""

            verdict = evaluate_post(term, category, subreddit, title, body)

            if verdict == "YES":
                yes_count += 1
            elif verdict == "NO":
                no_count += 1
            else:
                ambiguous_count += 1

            # First 150 chars of body for detail output
            first_150 = body[:150].replace("\t", " ").replace("\n", " ")
            details.append({
                "post_id": post["post_id"],
                "subreddit": subreddit,
                "first_150_chars": first_150,
                "verdict": verdict,
            })

        # Calculate contextual relevance
        if total_sampled > 0:
            ctx_rel = (yes_count + 0.5 * ambiguous_count) / total_sampled * 100
        else:
            ctx_rel = 0.0

        results.append({
            "term": term,
            "category": category,
            "total_sampled": total_sampled,
            "yes_count": yes_count,
            "no_count": no_count,
            "ambiguous_count": ambiguous_count,
            "contextual_relevance_pct": round(ctx_rel, 1),
            "details": details,
        })

    return results


def main():
    all_results = []

    for chunk_num in range(1, 13):
        results = process_chunk(chunk_num)
        all_results.extend(results)

        # Also write per-chunk results
        out_path = os.path.join(CHUNKS_DIR, f"cv_results_{chunk_num:02d}.json")
        with open(out_path, "w") as f:
            json.dump(results, f, indent=2)

        # Progress
        total_posts = sum(r["total_sampled"] for r in results)
        terms = [r["term"] for r in results]
        print(f"Chunk {chunk_num:02d}: {len(results)} keywords, {total_posts} posts evaluated")

    # --- Build auto-cut and auto-keep entries ---

    auto_cut_terms = [
        "thank you", "my friend", "helped me", "struggling with", "my anxiety",
        "my depression", "social anxiety", "so lonely", "loneliness", "no friends",
        "feel depressed", "no one cares", "no one understands me", "nobody to talk to",
        "feels empty", "isolated", "feel seen", "feel heard", "hang out",
        "my therapist", "therapy session", "talk therapy", "venting", "vent to",
        "process my feelings", "talk through", "changed my life", "so grateful",
        "game changer", "finally feel", "made me feel better", "improved my",
        "gave me confidence", "actually helpful", "saved my life", "life saver",
        "so much better", "got me through", "helped me through", "highly recommend",
        "best feature", "good conversation", "fun to talk to", "nice to talk to",
        "just someone to talk to", "chat buddy", "study buddy", "conversation partner",
        "practice conversation", "helped me practice", "keeps me company",
        "like talking to", "going back to", "cutting back", "cold turkey",
        "withdrawal", "relapse", "relapsed", "clean for", "detox", "craving",
        "taking a break", "keep coming back", "quitting", "trying to quit",
        "trying to stop", "couldn't stop myself", "slept with", "sex with",
    ]

    auto_keep_terms = [
        "my replika", "my kindroid", "my nomi", "erp", "smut", "nsfw bot",
        "ai girlfriend", "nsfw filter", "my ai boyfriend", "ai husband",
        "nsfw chat", "my companion", "my ai girlfriend", "my ai partner",
        "nsfw ban", "removed nsfw", "erp removed",
    ]

    # --- Write detail TSV ---
    detail_path = os.path.join(BASE_DIR, "docs", "contextual_validation_detail.tsv")
    with open(detail_path, "w") as f:
        f.write("keyword\tpost_id\tsubreddit\tfirst_150_chars_of_body\tverdict\n")

        # Auto-cut entries
        for term in auto_cut_terms:
            f.write(f"{term}\t-\t-\tauto-cut: generic language, not AI-companionship-specific\tCUT\n")

        # Auto-keep entries
        for term in auto_keep_terms:
            f.write(f"{term}\t-\t-\tauto-keep: high precision, unambiguously AI companionship\tKEEP\n")

        # Sampled entries
        for result in all_results:
            for detail in result["details"]:
                chars = detail["first_150_chars"].replace("\t", " ")
                f.write(f"{result['term']}\t{detail['post_id']}\t{detail['subreddit']}\t{chars}\t{detail['verdict']}\n")

    # --- Write summary TSV ---
    summary_path = os.path.join(BASE_DIR, "docs", "contextual_validation_summary.tsv")

    # Build summary rows
    summary_rows = []

    # Auto-cut
    for term in auto_cut_terms:
        summary_rows.append({
            "keyword": term,
            "old_category": "auto-cut",
            "total_sampled": 0,
            "yes_count": 0,
            "no_count": 0,
            "ambiguous_count": 0,
            "contextual_relevance_pct": 0.0,
            "verdict": "CUT",
            "note": "auto-cut: generic language",
        })

    # Auto-keep
    for term in auto_keep_terms:
        summary_rows.append({
            "keyword": term,
            "old_category": "auto-keep",
            "total_sampled": 0,
            "yes_count": 0,
            "no_count": 0,
            "ambiguous_count": 0,
            "contextual_relevance_pct": 100.0,
            "verdict": "KEEP",
            "note": "auto-keep: high precision, unambiguously AI companionship",
        })

    # Sampled keywords
    for result in all_results:
        pct = result["contextual_relevance_pct"]
        if pct >= 80:
            verdict = "KEEP"
        elif pct >= 70:
            verdict = "KEEP_NOTE"
        elif pct >= 50:
            verdict = "FLAG"
        else:
            verdict = "CUT"

        note = ""
        if result["total_sampled"] < 20:
            note = f"small sample (n={result['total_sampled']})"

        summary_rows.append({
            "keyword": result["term"],
            "old_category": result["category"],
            "total_sampled": result["total_sampled"],
            "yes_count": result["yes_count"],
            "no_count": result["no_count"],
            "ambiguous_count": result["ambiguous_count"],
            "contextual_relevance_pct": pct,
            "verdict": verdict,
            "note": note,
        })

    # Sort by contextual_relevance_pct descending (best first)
    summary_rows.sort(key=lambda r: -r["contextual_relevance_pct"])

    with open(summary_path, "w") as f:
        f.write("keyword\told_category\ttotal_sampled\tyes_count\tno_count\tambiguous_count\tcontextual_relevance_pct\tverdict\tnote\n")
        for row in summary_rows:
            f.write(f"{row['keyword']}\t{row['old_category']}\t{row['total_sampled']}\t"
                    f"{row['yes_count']}\t{row['no_count']}\t{row['ambiguous_count']}\t"
                    f"{row['contextual_relevance_pct']}\t{row['verdict']}\t{row.get('note', '')}\n")

    # --- Print summary stats ---
    sampled = [r for r in summary_rows if r["total_sampled"] > 0]
    keep = [r for r in sampled if r["verdict"] == "KEEP"]
    keep_note = [r for r in sampled if r["verdict"] == "KEEP_NOTE"]
    flag = [r for r in sampled if r["verdict"] == "FLAG"]
    cut = [r for r in sampled if r["verdict"] == "CUT"]

    print(f"\n{'='*60}")
    print(f"CONTEXTUAL VALIDATION SUMMARY")
    print(f"{'='*60}")
    print(f"Auto-cut (generic language):     {len(auto_cut_terms)} terms")
    print(f"Auto-keep (high precision):      {len(auto_keep_terms)} terms")
    print(f"Sampled and evaluated:           {len(sampled)} terms ({sum(r['total_sampled'] for r in sampled)} posts)")
    print(f"")
    print(f"Sampled results:")
    print(f"  KEEP (≥80%):      {len(keep)} terms")
    print(f"  KEEP_NOTE (70-79%): {len(keep_note)} terms")
    print(f"  FLAG (50-69%):    {len(flag)} terms")
    print(f"  CUT (<50%):       {len(cut)} terms")
    print(f"")
    print(f"Total keyword verdicts:")
    print(f"  KEEP:      {len(auto_keep_terms) + len(keep)} terms")
    print(f"  KEEP_NOTE: {len(keep_note)} terms")
    print(f"  FLAG:      {len(flag)} terms")
    print(f"  CUT:       {len(auto_cut_terms) + len(cut)} terms")
    print(f"")
    print(f"Top 30 keywords by contextual relevance:")
    for r in sampled[:30]:
        note = f" ({r['note']})" if r.get("note") else ""
        print(f"  {r['contextual_relevance_pct']:5.1f}% [{r['verdict']:9s}] {r['keyword']}"
              f" (n={r['total_sampled']}, Y={r['yes_count']}, N={r['no_count']}, A={r['ambiguous_count']}){note}")

    print(f"\nBottom 20 sampled keywords:")
    for r in sampled[-20:]:
        note = f" ({r['note']})" if r.get("note") else ""
        print(f"  {r['contextual_relevance_pct']:5.1f}% [{r['verdict']:9s}] {r['keyword']}"
              f" (n={r['total_sampled']}, Y={r['yes_count']}, N={r['no_count']}, A={r['ambiguous_count']}){note}")

    print(f"\nOutput files:")
    print(f"  {detail_path}")
    print(f"  {summary_path}")


if __name__ == "__main__":
    main()
