"""Core logic for keyword discovery: sampling, Claude API calls, precision testing."""

import json
import logging
import re
import sqlite3
import time
from typing import Any

import anthropic

from src.config import load_communities, load_keywords

logger = logging.getLogger(__name__)

# ── Subreddit classification ────────────────────────────────────────────────

def get_companion_subs() -> set[str]:
    """Return set of companion subreddit names (tiers 1, 2, 3)."""
    communities = load_communities()
    return {c["subreddit"] for c in communities if c.get("tier") in (1, 2, 3)}


def get_general_subs() -> set[str]:
    """Return set of general/control subreddit names (tier 0)."""
    communities = load_communities()
    return {c["subreddit"] for c in communities if c.get("tier") == 0}


# ── Sampling ────────────────────────────────────────────────────────────────

def sample_posts(
    conn: sqlite3.Connection,
    subreddits: list[str],
    n: int = 2000,
    min_length: int = 50,
) -> list[dict]:
    """Sample n random posts from the given subreddits with min selftext length."""
    placeholders = ",".join("?" * len(subreddits))
    rows = conn.execute(
        f"""
        SELECT id, subreddit, title, selftext
        FROM posts
        WHERE subreddit IN ({placeholders})
          AND selftext IS NOT NULL
          AND LENGTH(selftext) > ?
          AND selftext NOT IN ('[deleted]', '[removed]')
        ORDER BY RANDOM()
        LIMIT ?
        """,
        subreddits + [min_length, n],
    ).fetchall()
    return [
        {"id": r[0], "subreddit": r[1], "title": r[2], "selftext": r[3]}
        for r in rows
    ]


def format_post(post: dict, index: int) -> str:
    """Format a single post for the prompt."""
    body = (post["selftext"] or "")[:500].strip()
    return f"[{index:03d}] r/{post['subreddit']}\nTITLE: {post['title']}\nBODY: {body}"


# ── Step 1: Mine candidates ────────────────────────────────────────────────

MINE_SYSTEM = """\
You are analyzing Reddit posts from AI companion communities (r/replika, \
r/CharacterAI, r/KindroidAI, etc.). Your job is to find short phrases that \
are strong indicators someone is talking about a personal, emotional \
relationship with an AI.

A good phrase passes this test: "If I see this phrase in ANY Reddit post, \
I can be very confident the person is describing a personal relationship \
with an AI companion."

EXCLUDE phrases that could appear in:
- General AI capability discussion ("so smart", "impressive reasoning")
- Tech support or app issues ("app crashed", "subscription cancelled")
- Bot/character descriptions or creative writing prompts
- Product reviews or recommendations
- Academic, news, or philosophical AI discussion
- Generic positive/negative sentiment ("love it", "hate this")
"""

MINE_USER = """\
Read these {n} posts and extract phrases (2-5 words) that reliably indicate \
someone is talking about a personal relationship with an AI companion.

For each phrase, explain in ONE sentence why it's a reliable indicator \
(what makes it specific to companion relationships vs general AI talk).

Return JSON:
{{
  "phrases": [
    {{"text": "the phrase", "reasoning": "why this is specific to companion relationships"}}
  ]
}}

Return 10-25 phrases per batch. Prefer phrases you see multiple times.

--- POSTS ---
{posts}"""


def mine_candidates(
    posts: list[dict],
    client: anthropic.Anthropic,
    model: str,
    batch_size: int = 50,
) -> list[dict]:
    """Send post batches to Claude and collect candidate phrases."""
    all_phrases: list[dict] = []
    batches = [posts[i : i + batch_size] for i in range(0, len(posts), batch_size)]

    for i, batch in enumerate(batches):
        formatted = "\n\n".join(format_post(p, j + 1) for j, p in enumerate(batch))
        user_msg = MINE_USER.format(n=len(batch), posts=formatted)

        logger.info("  Mining batch %d/%d (%d posts)...", i + 1, len(batches), len(batch))

        try:
            response = client.messages.create(
                model=model,
                max_tokens=2000,
                system=MINE_SYSTEM,
                messages=[{"role": "user", "content": user_msg}],
            )
            text = response.content[0].text
            # Extract JSON from response (Claude sometimes wraps in markdown)
            json_match = re.search(r"\{[\s\S]*\}", text)
            if json_match:
                data = json.loads(json_match.group())
                phrases = data.get("phrases", [])
                all_phrases.extend(phrases)
                logger.info("    → %d phrases found", len(phrases))
            else:
                logger.warning("    → No JSON found in response")
        except Exception as e:
            logger.error("    → Batch %d failed: %s", i + 1, e)
            time.sleep(2)
            continue

        # Respect rate limits
        time.sleep(0.5)

    return all_phrases


def deduplicate_phrases(raw_phrases: list[dict]) -> list[dict]:
    """Merge duplicate phrases, count how many batches surfaced each."""
    counts: dict[str, dict] = {}
    for p in raw_phrases:
        key = p["text"].lower().strip()
        if key not in counts:
            counts[key] = {
                "text": p["text"].strip(),
                "reasoning": p.get("reasoning", ""),
                "batch_count": 0,
            }
        counts[key]["batch_count"] += 1
    # Sort by batch frequency descending
    return sorted(counts.values(), key=lambda x: x["batch_count"], reverse=True)


# ── Step 2: Test precision ──────────────────────────────────────────────────

def count_hits_by_subreddit(
    phrase: str, conn: sqlite3.Connection
) -> dict[str, int]:
    """Count posts containing phrase, grouped by subreddit."""
    # Use LIKE for speed; phrase is already a natural language string
    pattern = f"%{phrase}%"
    rows = conn.execute(
        """
        SELECT subreddit, COUNT(*) as cnt
        FROM posts
        WHERE (title LIKE ? OR selftext LIKE ?)
        GROUP BY subreddit
        ORDER BY cnt DESC
        """,
        (pattern, pattern),
    ).fetchall()
    return {r[0]: r[1] for r in rows}


def sample_hits_from_subs(
    phrase: str,
    subreddits: list[str],
    conn: sqlite3.Connection,
    n: int = 10,
) -> list[dict]:
    """Sample n posts containing phrase from the given subreddits."""
    placeholders = ",".join("?" * len(subreddits))
    pattern = f"%{phrase}%"
    rows = conn.execute(
        f"""
        SELECT id, subreddit, title, selftext
        FROM posts
        WHERE subreddit IN ({placeholders})
          AND (title LIKE ? OR selftext LIKE ?)
        ORDER BY RANDOM()
        LIMIT ?
        """,
        subreddits + [pattern, pattern, n],
    ).fetchall()
    return [
        {"id": r[0], "subreddit": r[1], "title": r[2], "selftext": r[3]}
        for r in rows
    ]


PRECISION_SYSTEM = """\
You are classifying Reddit posts. For each post, answer whether the person \
is describing a personal, emotional relationship with an AI companion \
(chatbot girlfriend/boyfriend, AI friend they talk to regularly, emotional \
bond with an AI).

Answer YES if the post is about a personal relationship with an AI.
Answer NO if the post is about general AI discussion, tech support, \
product reviews, coding help, news, philosophy, or anything else."""

PRECISION_USER = """\
For each post below, answer YES or NO. Return JSON:
{{"results": [{{"index": 1, "answer": "YES"}}, ...]}}

--- POSTS ---
{posts}"""


def check_precision(
    phrase: str,
    general_posts: list[dict],
    client: anthropic.Anthropic,
    model: str,
) -> dict[str, Any]:
    """Ask Claude whether non-companion-sub posts containing phrase are about AI relationships."""
    if not general_posts:
        return {"tested": 0, "true_positives": 0, "precision": 1.0}

    formatted = "\n\n".join(format_post(p, i + 1) for i, p in enumerate(general_posts))
    user_msg = PRECISION_USER.format(posts=formatted)

    try:
        response = client.messages.create(
            model=model,
            max_tokens=1000,
            system=PRECISION_SYSTEM,
            messages=[{"role": "user", "content": user_msg}],
        )
        text = response.content[0].text
        json_match = re.search(r"\{[\s\S]*\}", text)
        if json_match:
            data = json.loads(json_match.group())
            results = data.get("results", [])
            yes_count = sum(1 for r in results if r.get("answer", "").upper() == "YES")
            return {
                "tested": len(results),
                "true_positives": yes_count,
                "precision": yes_count / len(results) if results else 0,
            }
    except Exception as e:
        logger.error("    → Precision check failed for '%s': %s", phrase, e)

    return {"tested": 0, "true_positives": 0, "precision": None}


def test_all_phrases(
    candidates: list[dict],
    conn: sqlite3.Connection,
    client: anthropic.Anthropic,
    model: str,
    companion_subs: set[str],
    general_subs: set[str],
    max_phrases: int = 200,
) -> list[dict]:
    """For each candidate phrase, compute hit distribution and precision score."""
    results = []
    to_test = candidates[:max_phrases]

    for i, cand in enumerate(to_test):
        phrase = cand["text"]
        logger.info("  Testing %d/%d: '%s'", i + 1, len(to_test), phrase)

        # Count hits across all subreddits
        hits_by_sub = count_hits_by_subreddit(phrase, conn)
        total_hits = sum(hits_by_sub.values())

        if total_hits == 0:
            logger.info("    → 0 hits, skipping")
            continue

        companion_hits = sum(v for k, v in hits_by_sub.items() if k in companion_subs)
        general_hits = sum(v for k, v in hits_by_sub.items() if k in general_subs)
        other_hits = total_hits - companion_hits - general_hits
        companion_ratio = companion_hits / total_hits

        result = {
            "phrase": phrase,
            "reasoning": cand.get("reasoning", ""),
            "batch_count": cand.get("batch_count", 1),
            "total_hits": total_hits,
            "companion_hits": companion_hits,
            "general_hits": general_hits,
            "other_hits": other_hits,
            "companion_ratio": round(companion_ratio, 3),
            "top_subreddits": dict(list(hits_by_sub.items())[:8]),
        }

        # Decide whether to call Claude for precision check
        if general_hits == 0 and other_hits == 0:
            # 100% companion subs — no need to check
            result["precision"] = 1.0
            result["precision_method"] = "all_companion"
            result["verdict"] = "HIGH"
            logger.info("    → %d hits, 100%% companion", total_hits)
        elif companion_ratio < 0.3:
            # Clearly a general-purpose phrase
            result["precision"] = round(companion_ratio, 3)
            result["precision_method"] = "ratio_too_low"
            result["verdict"] = "LOW"
            logger.info("    → %d hits, %.0f%% companion — skipping", total_hits, companion_ratio * 100)
        else:
            # Ambiguous — test with Claude
            general_sub_list = [s for s in hits_by_sub if s in general_subs or s not in companion_subs]
            test_posts = sample_hits_from_subs(phrase, general_sub_list, conn, n=10)
            if test_posts:
                precision_result = check_precision(phrase, test_posts, client, model)
                result.update(precision_result)
                result["precision_method"] = "claude_checked"
                if precision_result["precision"] is not None:
                    # Overall precision: companion hits are true positives +
                    # fraction of general hits that are also true positives
                    est_true_general = general_hits * precision_result["precision"]
                    overall_precision = (companion_hits + est_true_general) / total_hits
                    result["overall_precision"] = round(overall_precision, 3)
                    result["verdict"] = (
                        "HIGH" if overall_precision >= 0.8
                        else "MEDIUM" if overall_precision >= 0.6
                        else "LOW"
                    )
                    logger.info(
                        "    → %d hits, %.0f%% companion, %d/%d general true-pos → overall %.0f%%",
                        total_hits, companion_ratio * 100,
                        precision_result["true_positives"], precision_result["tested"],
                        overall_precision * 100,
                    )
                else:
                    result["verdict"] = "UNKNOWN"
            else:
                result["precision"] = round(companion_ratio, 3)
                result["precision_method"] = "no_general_posts"
                result["verdict"] = "HIGH" if companion_ratio >= 0.8 else "MEDIUM"

            time.sleep(0.5)  # Rate limit

        results.append(result)

    # Sort by verdict quality then total hits
    verdict_order = {"HIGH": 0, "MEDIUM": 1, "UNKNOWN": 2, "LOW": 3}
    results.sort(key=lambda r: (verdict_order.get(r["verdict"], 9), -r["total_hits"]))
    return results


# ── Suggest categories ──────────────────────────────────────────────────────

def suggest_categories(
    results: list[dict], existing_keywords: list[dict]
) -> dict[str, list[str]]:
    """Map high-precision phrases to existing keyword categories by simple heuristic."""
    category_names = [c["name"] for c in existing_keywords]
    # Simple keyword-to-category mapping based on category name patterns
    mapping: dict[str, list[str]] = {name: [] for name in category_names}
    mapping["uncategorized"] = []

    for r in results:
        if r["verdict"] not in ("HIGH", "MEDIUM"):
            continue
        # Just put everything in uncategorized — the human decides
        mapping["uncategorized"].append(r["phrase"])

    return {k: v for k, v in mapping.items() if v}


# ── Format output ───────────────────────────────────────────────────────────

def format_results_text(results: list[dict]) -> str:
    """Format results as human-readable text."""
    lines = []
    lines.append("=" * 70)
    lines.append("KEYWORD DISCOVERY RESULTS")
    lines.append("=" * 70)
    lines.append("")

    for verdict_label, emoji in [("HIGH", "✓"), ("MEDIUM", "~"), ("LOW", "✗"), ("UNKNOWN", "?")]:
        section = [r for r in results if r["verdict"] == verdict_label]
        if not section:
            continue

        lines.append(f"\n{'─' * 70}")
        lines.append(f"  {emoji} {verdict_label} PRECISION ({len(section)} phrases)")
        lines.append(f"{'─' * 70}\n")

        for r in section:
            lines.append(f'PHRASE: "{r["phrase"]}"')
            lines.append(f'  Batches: {r.get("batch_count", "?")} | Hits: {r["total_hits"]} | Companion: {r["companion_ratio"]:.0%}')

            # Show top subreddits
            top = r.get("top_subreddits", {})
            if top:
                sub_str = ", ".join(f"r/{s} {n}" for s, n in list(top.items())[:5])
                lines.append(f"  Subs: {sub_str}")

            if r.get("precision_method") == "claude_checked":
                tp = r.get("true_positives", "?")
                tested = r.get("tested", "?")
                lines.append(f"  Claude check: {tp}/{tested} general-sub hits were true positives")

            if r.get("reasoning"):
                lines.append(f"  Why: {r['reasoning']}")
            lines.append("")

    # Summary
    high = len([r for r in results if r["verdict"] == "HIGH"])
    med = len([r for r in results if r["verdict"] == "MEDIUM"])
    low = len([r for r in results if r["verdict"] == "LOW"])
    lines.append(f"\nSUMMARY: {high} high / {med} medium / {low} low precision out of {len(results)} tested")
    return "\n".join(lines)
