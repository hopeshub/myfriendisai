# myfriendisai — Research Methodology

**Updated:** March 12, 2026
**Purpose:** Documents the repeatable process for curating subreddits, discovering keywords, and validating data quality. This is both an internal reference for maintaining the project and a public-facing methodology statement.

---

## 1. What This Project Measures

This project tracks keyword frequency across Reddit communities where AI companionship is discussed. It measures **discourse volume** — how often specific themes come up in conversation — not sentiment, opinion, or behavior. When the chart shows "Dependency increased 64%," it means people are *talking about* dependency more, normalized for community growth. It does not claim that more people *are* dependent.

All keyword data is normalized to hits per 1,000 posts to account for community growth over time.

---

## 2. How Subreddits Are Selected

### Inclusion criteria
A subreddit is included if AI companionship is either:
- **The central topic** (e.g., r/replika, r/CharacterAI, r/MyBoyfriendIsAI)
- **A recurring genuine part of the conversation** (e.g., r/ChatGPT, r/OpenAI where users authentically discuss AI relationships)

### Exclusion criteria
A subreddit is excluded if:
- **Keyword pollution is likely** — the community uses the same emotional language (love, miss, addicted, dependent) in non-AI-companionship contexts. Examples: r/relationship_advice, r/depression, r/lonely
- **Discussion is purely technical** — AI is discussed as technology, not as a relational entity. Examples: r/MachineLearning, r/LocalLLaMA
- **Content is primarily bot listings, not user discourse** — posts are product descriptions rather than personal experiences. Partial example: r/JanitorAI_Official (included but known to generate noise from bot character descriptions)

### Process for adding a new subreddit
1. Identify the candidate subreddit
2. Add it to `config/communities.yaml` with tier, category, and notes
3. Run the backfill: `.venv/bin/python scripts/backfill_pullpush.py --subreddit SubredditName`
4. Run the keyword tagger: `.venv/bin/python scripts/tag_keywords.py`
5. **Validate** — check that keyword hits from this sub are actually about AI companionship, not general emotional language. Use the phrase validation process described in Section 4.
6. If the sub produces mostly noise, remove it from communities.yaml

---

## 3. How Keywords Are Selected

### Principles
- **Precision over recall.** A keyword should almost always indicate AI companionship discourse when found in the tracked communities. Missing some relevant posts is acceptable; including irrelevant posts is not.
- **No single keyword should dominate a theme.** If one term accounts for more than ~40% of a category's hits, the category is fragile and that term should be investigated for noise.
- **Keywords are validated against real posts, not assumed.** Every keyword in the production list has been checked against actual post content from the tracked subreddits.

### The keyword lifecycle
1. **Hypothesize** — propose keywords based on domain knowledge and intuition
2. **Discover** — sample real posts from companion subs and identify actual language patterns people use (see Section 4)
3. **Validate** — test candidate phrases against the full corpus, checking hit count, subreddit distribution, and whether matches are genuine AI companionship discourse
4. **Monitor** — after deployment, check for single-keyword dominance and investigate any unexpected spikes

### Key finding: universal emotional language fails precision
Many of the most emotionally powerful phrases discovered in companion posts are universal human relationship language. They appear 10-50x more often in general AI subs (r/ChatGPT, r/singularity) than in companion subs. Examples:

| Phrase | Total hits | Companion % | Verdict |
|---|---|---|---|
| saved my life | 135 | 45% | REJECTED — ChatGPT dominates (56 hits) |
| am I crazy for | 14 | 29% | REJECTED — mostly ChatGPT/ClaudeAI |
| embarrassed to admit | 15 | 60% | BORDERLINE — scattered across general subs |
| helped me through | 144 | 65% | BORDERLINE — ChatGPT has 39 hits |

**Lesson:** Do not assume that a phrase found in companion posts is specific to companion discourse. Always validate against the full corpus. Platform-qualified phrases ("my replika", "addicted to character ai") reliably pass precision tests; unqualified emotional language usually does not.

### Known limitations
- Keyword matching captures **explicit** language only. Someone describing dependency without using dependency-related words ("I stayed up until 4am talking to it again") will be missed.
- Some keywords are ambiguous in specific subreddits (e.g., "obsessed" in r/JanitorAI_Official often appears in bot character descriptions, not user self-reports).
- Precision was validated within the tracked companion communities. The same keywords in a general-population Reddit context would have much lower precision.
- Very rare phrases (≤2 hits) may have 100% companion precision but are excluded because a single new post could flip the ratio.

---

## 4. Keyword Discovery and Validation Process

This is the repeatable process used to find and test new keywords.

### Step 1: Sample posts
Pull a random sample of posts from companion subreddits (target: 2,000–5,000 posts with >200 characters in body).

```bash
# CC can generate this
# Output: docs/keyword_research_sample.txt
```

### Step 2: Discover candidate phrases
Use Claude Code agents to read sampled posts and extract 2-5 word phrases that indicate someone is describing a personal relationship with an AI. Ignore tech support, bot descriptions, product reviews, and general AI discussion.

**Reproducible process (March 2026 round):**
- Split 5,000 posts into 20 chunks of 250 posts (~1,800 lines each)
- Launch 10 parallel Claude Code haiku agents, each reading 2 chunks
- Agent prompt: *"Identify short phrases (2-5 words) that ONLY make sense if someone is describing a personal relationship with an AI companion. Ignore tech support, bot descriptions, product reviews."*
- Each agent returns phrases with: the source post number, which subreddit, and why the phrase indicates AI companionship
- Merge and deduplicate across all agents
- Result: ~200 candidate phrases across ~15 theme clusters (see `docs/discovered_phrases.txt`)

**Two discovery strategies:**
1. **Organic discovery** — phrases extracted directly from post content (e.g., "our first kiss", "personality is gone", "she remembered")
2. **Platform-qualified variants** — deliberately test platform-specific constructions (e.g., "my replika", "addicted to character ai", "ai girlfriend"). These are high-precision by construction because the AI product name acts as a qualifier.

Output: a list of candidate phrases organized by theme cluster.

### Step 3: Validate against full corpus
For each candidate phrase, search the full posts database (using FTS5 index for speed):
- **Total hits** — does the phrase appear enough to be useful? (Minimum ~10 hits to be worth including)
- **Companion sub percentage** — what fraction of hits come from companion-focused subs (Tier 1-2) versus general AI subs (Tier 0)?
- **Precision threshold** — a phrase should be ≥80% companion-sub hits to be considered high precision. 60-80% is usable but noted as noisier. Below 60% is excluded.

### Step 4: Concentration check
After adding new keywords to a category, verify that no single keyword accounts for more than ~40% of the category's total hits. If it does, investigate that keyword for noise (see the "dependent" and "nsfw" examples in project history).

```bash
# Run concentration check
.venv/bin/python scripts/tag_keywords.py  # re-tag
# Then query:
# SELECT matched_term, COUNT(*) FROM post_keyword_tags
# WHERE category = 'category_name' GROUP BY matched_term ORDER BY 2 DESC
```

---

## 5. Data Pipeline

### Collection
- **Historical data (one-time):** PullPush/Arctic Shift backfill from January 2023 to present
- **Ongoing data:** Reddit public `.json` endpoints via `collect_daily.py` (to be scheduled via cron)
- **Storage:** SQLite database (`data/tracker.db`)

### Processing
- **Keyword tagging:** `scripts/tag_keywords.py` scans all posts against `config/keywords.yaml`
- **Export:** `scripts/export_json.py` aggregates daily counts per keyword category, computes 7-day rolling averages, normalizes to hits per 1,000 posts
- **Output:** `web/data/keyword_trends.json`

### Deployment
- **Frontend:** Next.js on Vercel, auto-deploys from GitHub pushes
- **Data refresh:** Re-run export script, push updated JSONs to GitHub

---

## 6. What Changed and Why (Audit Trail)

Documenting significant methodology decisions for transparency.

### Keywords removed
| Keyword | Category | Reason | Date |
|---|---|---|---|
| dependent | dependency_language | Matched tool-dependency in r/ChatGPT and bot character descriptions in r/JanitorAI | 2026-03-11 |
| nsfw | sexual_erotic_language | Matched meta-discussion about platform features, not actual erotic content | 2026-03-11 |
| more than just | attachment_language | 47% of category hits, almost entirely false positives ("more than just a tool") | 2026-03-11 |
| human-like | anthropomorphism_realism_language | 57% of category hits, matched tech capability discussion not relational experience | 2026-03-11 |

### Subreddits removed from keyword aggregation
| Subreddit | Reason | Date |
|---|---|---|
| relationship_advice, depression, Anxiety, lonely, loneliness, ForeverAlone, AutismInWomen, autism | Emotional language (love, miss, lonely) used in non-AI contexts, polluting keyword trends | 2026-03-11 |
| MachineLearning, artificial, LocalLLaMA, LocalLLM | Technical AI discussion where companion keywords match non-companion context | 2026-03-11 |

### Keywords added from ethnographic discovery
| Keyword | Category | Hits | Companion % | Date |
|---|---|---|---|---|
| my ai boyfriend | romantic_language | 153 | 93% | 2026-03-11 |
| my ai partner | romantic_language | 164 | 93% | 2026-03-11 |
| our first kiss | romantic_language | 20 | 95% | 2026-03-12 |
| proposed to me | romantic_language | 43 | 86% | 2026-03-12 |
| got married | romantic_language | 151 | 80% | 2026-03-12 |
| my replika | romantic_language | 4,144 | ~100% | 2026-03-12 |
| my nomi | romantic_language | 3,695 | ~100% | 2026-03-12 |
| my kindroid | romantic_language | 791 | ~100% | 2026-03-12 |
| ai companion | romantic_language | 2,919 | ~95% | 2026-03-12 |
| ai girlfriend | romantic_language | 714 | ~95% | 2026-03-12 |
| I miss him | attachment_language | 87 | 89% | 2026-03-11 |
| I miss her | attachment_language | 69 | 75% | 2026-03-12 |
| miss talking to | attachment_language | 17 | 82% | 2026-03-12 |
| genuine relationship with | attachment_language | 6 | 100% | 2026-03-12 |
| she remembered | memory_continuity_language | 98 | 83% | 2026-03-11 |
| he remembered | memory_continuity_language | 263 | 76% | 2026-03-12 |
| addicted to talking | dependency_language | 12 | 83% | 2026-03-12 |
| personality is gone | grief_rupture_language | 9 | 89% | 2026-03-12 |

---

## 7. File Reference

| File | Purpose |
|---|---|
| `config/keywords.yaml` | Source of truth for all keyword categories and terms |
| `config/communities.yaml` | Source of truth for tracked subreddits |
| `docs/REBUILD_PLAN.md` | Step-by-step build roadmap |
| `docs/KEYWORD_CATEGORIES_V1.md` | Frontend theme definitions and category-to-theme mapping |
| `docs/FRONTEND_DESIGN_SPEC.md` | Complete design specification for the website |
| `docs/METHODOLOGY.md` | This document |
| `docs/discovered_phrases.txt` | Raw output from keyword discovery process |
| `docs/phrase_validation.txt` | Validation results for candidate keywords |
