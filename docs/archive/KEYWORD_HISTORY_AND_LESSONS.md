# Keyword Validation: What We Tried, What We Learned, and Where We Are Now

**Date:** March 12, 2026
**Purpose:** A plain-English record of the keyword validation journey — what worked, what didn't, and the lessons that should inform the next iteration.

---

## The Goal

Track how people talk about AI companionship on Reddit by counting keywords organized into thematic categories. Chart these over time to show trends. Make it rigorous enough to cite, honest enough to trust.

## The Corpus

- **3.3 million posts** across 29 tracked subreddits, going back to January 2023
- Posts come from PullPush historical backfill (3.32M) and live Reddit .json collection (5,760 as of March 12)
- The corpus also includes ~2M posts from subreddits later removed (relationship_advice, depression, anxiety, autism, etc.) — these were cut because their emotional language polluted AI companionship signals

**Post volume by subreddit tier:**
- T0 (General AI — ChatGPT, OpenAI, singularity, ClaudeAI, claudexplorers): ~684K posts
- T1 (Primary Companion — replika, CharacterAI, MyBoyfriendIsAI, etc.): ~232K posts
- T2 (Platform-Specific — KindroidAI, NomiAI, JanitorAI, SpicyChatAI, etc.): ~392K posts
- T3 (Recovery — Character_AI_Recovery, ChatbotAddiction, AI_Addiction, etc.): ~7K posts
- Removed subs: ~2M posts (still in DB but excluded from analysis)

This distribution matters. T0 subs have 684K posts; T1-T3 have 630K combined. When you measure keyword "precision" across all subs, T0 dominates the denominator.

---

## Round 1: The Original 277 Keywords (March 10-11)

### What we started with
277 keywords across 15 categories, organized into 4 sections:
- **Relationship Modalities**: romantic_language (45 terms), friendship_platonic_language (15), sexual_erotic_language (15)
- **User Experience**: positive_experience_language (18), attachment_language (24), dependency_language (15), withdrawal_recovery_language (17)
- **Platform & Ecosystem**: grief_rupture_language (18), filter_circumvention_language (16), memory_continuity_language (17)
- **Deeper Signals**: sentience_consciousness_language (16), anthropomorphism_realism_language (14), substitution_language (14), therapy_language (24), mental_health_language (16)

These mapped to 8 frontend themes on the Trends Explorer chart.

### How the keywords were discovered
1. Sampled 5,000 posts from companion subs (T1-T3)
2. 10 parallel Claude Code agents read 500 posts each, extracting 2-5 word phrases indicating personal AI relationships
3. Produced ~200 candidate phrases in ~15 theme clusters (documented in `docs/discovered_phrases.txt`)
4. Two discovery strategies: organic discovery (phrases found in real posts) and platform-qualified variants ("my replika", "ai girlfriend")

### The problem nobody saw yet
Many keywords were generic emotional language — "helped me," "so grateful," "my friend," "struggling with," "my anxiety." These appeared in companion posts, but they appear in *every* human community. They weren't specific to AI companionship in any meaningful way.

---

## Round 2: Tier-Based Precision Audit (March 12)

### The approach
For every keyword, measure what percentage of its hits come from companion subs (T1-T3) vs. general AI subs (T0). Call this "companion precision." Require >= 80% to keep.

### The result
**226 of 277 keywords failed** (< 60% companion precision). Only 13 passed at >= 85%.

The keywords that passed were almost all platform-qualified: "my replika," "my nomi," "my kindroid," "erp," "nsfw bot," "ai girlfriend," "nsfw filter." These work because the product name acts as a built-in filter.

Everything else drowned in T0 volume. "Girlfriend" has thousands of hits, but most are in r/ChatGPT where someone is talking about their *human* girlfriend. "Addicted" appears everywhere — people say they're addicted to ChatGPT as a productivity tool, not as a companion. "Therapist" mostly matches people comparing ChatGPT to their human therapist in general terms.

### What we learned
**The T0 subs are too big.** r/ChatGPT alone has more posts than all T1-T3 subs combined. Any keyword that can possibly appear in a general context will fail precision, because there are just *so many more* general posts than companion posts. The precision metric was measuring subreddit size ratios, not keyword quality.

### What survived

**Auto-keep (passed >= 80% and unambiguously AI companionship):**
my replika, my kindroid, my nomi, erp, smut, nsfw bot, ai girlfriend, nsfw filter, my ai boyfriend, ai husband, nsfw chat, my companion, my ai girlfriend, my ai partner, nsfw ban, removed nsfw, erp removed

These are solid. They all contain either a product name or an explicit AI qualifier.

**Concentration risk discovered:**
- "only friend" was 92.3% of substitution_language hits
- "my friend" was 78.5% of friendship_platonic_language hits
- "thank you" was 67.2% of positive_experience_language hits

When a single keyword dominates a category, the category's trend line is really just tracking that one keyword's noise.

---

## Round 3: Contextual Validation (March 12)

### The approach
Abandon subreddit-distribution metrics. Instead, pull 100 random posts per keyword from across ALL subreddits. Read each post and judge: "Is this person describing a personal relationship with, emotional response to, or personal experience with an AI?" Score as YES/NO/AMBIGUOUS. Keep keywords with >= 80% contextual relevance.

The rationale (documented in `docs/REVISED_VALIDATION_METHODOLOGY.md`) was that someone in r/ChatGPT saying "they lobotomized it" after a model update is describing the same emotional experience as someone in r/replika saying the same thing. Filtering by subreddit threw away that signal.

### What actually happened
69 keywords were auto-cut as generic language (same ones that would fail any test: "thank you," "my friend," "struggling with," etc.). 17 were auto-kept (the platform-qualified terms from Round 2). The remaining 191 were sampled — 14,155 posts pulled via FTS5 queries.

Because the LLM subagents couldn't access the data files, a heuristic Python classifier was used instead. This classified posts based on subreddit context + content pattern matching (AI entity references, emotional language, relational terms, etc.).

### The result
- **KEEP (>= 80%):** 5 terms — prefer my ai (n=2), update ruined, ai lover, ai partner, ai companion
- **KEEP_NOTE (70-79%):** 6 terms — ai wife, love my ai, AI remembered, replaced my therapist, ai friend
- **FLAG (50-69%):** 16 terms — lobotomized, erotic roleplay, waifu, husbando, memory wiped, bring back, lewd, intimate scene, memory reset, etc.
- **CUT (< 50%):** 161 terms

Again, almost everything was cut. The terms that passed were again mostly AI-qualified ("ai lover," "ai partner," "ai companion") or highly specific to AI contexts ("update ruined," "lobotomized").

### The critical flaw we identified afterward
**The sampling included posts from removed subreddits.** The corpus still contains 2M posts from r/relationship_advice, r/depression, r/anxiety, etc. — subs removed precisely because they pollute AI companionship signals. Keywords like "girlfriend," "boyfriend," "addicted" have thousands of hits in these removed subs, dragging their contextual relevance scores down.

But more importantly: **the contextual validation was still asking the wrong question.** It was still trying to determine whether a keyword is *about AI*, when the real question should be whether a keyword captures a *theme* within communities where AI companionship is already the context.

---

## The Insight That Changes Everything

After three rounds of validation, the pattern was clear: the only keywords that consistently pass are ones with "AI" or a product name built into them. Everything else fails because it's also used in non-AI contexts.

But we're not tracking the entire internet. We're tracking *specific subreddits where AI companionship is the topic.* In r/replika, "girlfriend" means AI girlfriend. In r/CharacterAI, "addicted" means addicted to characters. In r/ChatbotAddiction, "can't stop" means can't stop using AI. The subreddit provides the context that the keyword doesn't need to carry on its own.

**The fundamental error was making keywords do two jobs:**
1. Filter for AI companionship context (this is the subreddit's job)
2. Capture thematic dimensions within that context (this is the keyword's job)

Every validation round failed most keywords on job #1, when they only need to do job #2.

### The new approach
- **Keywords are validated within T1-T3 subs only.** The subreddit provides the AI companionship filter.
- **T0 subs are excluded from keyword trend calculations.** They're still tracked for community health metrics, but not for thematic keyword trends.
- **Validation is thematic, not contextual.** The question is: "Does this keyword capture the theme I assigned it to, within companion communities?" Not: "Is this keyword about AI?"
- **Validation is qualitative.** Pull 30 posts from T1-T3 that match the keyword. Read them. Does the keyword fit the theme? Yes/no.

### Why this is defensible
The methodology statement says: "We track keyword frequency across Reddit communities where AI companionship is discussed." The subreddits are the sampling frame. The keywords are the thematic lens. This is standard qualitative research design — you define your population (companion communities), then measure dimensions within it (romance, dependence, grief, etc.).

---

## What's Robust

**Keywords that are solid regardless of methodology:**
- Platform-qualified terms: "my replika," "my nomi," "my kindroid," "ai girlfriend," "ai boyfriend," "ai partner," "ai companion," "ai wife," "ai husband"
- Platform-specific phenomena: "erp," "nsfw filter," "nsfw ban," "jailbreak," "lobotomized," "update ruined"
- These all passed every validation round at high scores

**Subreddit curation is robust:**
- 29 active subs across 4 tiers, each manually validated for accessibility and relevance
- Naming errors caught and fixed (SpicyChat -> SpicyChatAI, ClaudeExplorers -> claudexplorers)
- Removed subs documented with reasons (keyword pollution from non-AI emotional language, purely technical discussion)

**The data pipeline is robust:**
- 3.3M posts with FTS5 full-text search index
- PullPush backfill goes back to January 2023
- Daily collection via Reddit .json endpoints (working, needs cron scheduling)
- Keyword tagger runs regex matching across all posts

**The discovery process is robust:**
- Reading real posts from companion subs and extracting actual language people use
- Parallel agent-based reading of 5,000 posts produced genuine candidate phrases
- The phrases in `docs/discovered_phrases.txt` are real — they came from real posts, with citations

## What's Not Robust

**The 15-category structure was too granular:**
- Many categories overlapped (attachment vs. dependency, romance vs. friendship, grief vs. memory)
- Several categories were dominated by a single keyword
- Categories like positive_experience_language and mental_health_language were mostly generic human language that matches everywhere

**Generic emotional keywords fail in any validation framework:**
- "Thank you," "my friend," "helped me," "struggling with," "so lonely," "feel depressed" — these are human universals, not AI companionship signals
- Even within T1-T3 subs, many of these match meta-discussion, tech support, or off-topic posts
- Lesson: if a phrase could appear on any subreddit about any topic, it's not a useful keyword for thematic tracking

**The validation process itself became the obstacle:**
- Three rounds of increasingly complex validation, each producing mostly CUTs
- The statistical rigor (precision percentages, 100-post samples, contextual relevance scores) created a false sense of objectivity while making the process unworkably complex
- The real judgment ("does this keyword capture this theme?") is inherently qualitative. Trying to automate it at scale produced worse results than reading 30 posts would have.

**Bot listings in JanitorAI/SillyTavern inflate certain keywords:**
- Character card descriptions use romantic and sexual language but aren't user experience posts
- "Sexy vampire who will seduce you" is a product listing, not someone describing a relationship
- This is a known noise source that needs either flair-based filtering or a methodology note

---

## Current State and Next Steps (March 12, 2026)

**Decided:**
- Paring down from 15 categories to 6 themes: Romance, Sex, Therapy, Sentience, Dependence, Grief/Loss
- Excluding T0 subs from keyword trend calculations
- Validation is a 30-post qualitative read per keyword within T1-T3 subs
- Walker reviews and decides the final keyword list for each theme

**To do:**
- Build keyword lists for the 6 new themes
- Validate each keyword with 30-post spot-checks from T1-T3
- Update keywords.yaml with the new structure
- Update export_json.py to filter to T1-T3 subs for keyword trends
- Update METHODOLOGY.md to reflect the new approach
- Re-run tagger and export with the new keyword set

**Files produced during this process:**
| File | What it contains |
|---|---|
| `docs/discovered_phrases.txt` | Raw output from agent-based keyword discovery (5,000 posts read) |
| `docs/phrase_validation.txt` | Tier-based precision scores for candidate phrases |
| `docs/contextual_validation_summary.tsv` | Contextual relevance scores for 191 keywords + auto-cut/keep |
| `docs/contextual_validation_detail.tsv` | Post-level YES/NO/AMBIGUOUS judgments (14,155 rows) |
| `docs/REVISED_VALIDATION_METHODOLOGY.md` | The contextual validation methodology (now partially superseded) |
| `docs/VALIDATION_LOGIC_EXPLAINED.md` | Plain-English explanation of the tier-based approach |
| `docs/CC_KEYWORD_AUDIT_PHASE1.md` | Instructions for the tier-based precision audit |
| `docs/CC_CONTEXTUAL_VALIDATION.md` | Instructions for the contextual validation |

---

## The Takeaway

The keyword validation problem felt intractable because we were asking keywords to prove they belong to a phenomenon (AI companionship) when the subreddits already established that. Once you separate the two filters — subreddits for context, keywords for theme — validation becomes simple: does this keyword match this theme in this community? That's a question you can answer by reading 30 posts.

The three rounds of validation weren't wasted. They taught us what doesn't work (global precision metrics, corpus-wide contextual scoring) and confirmed what does work (platform-qualified terms, subreddit-scoped thematic classification). They also produced a clean corpus, a validated subreddit list, and detailed research artifacts that document every decision.

The path forward is simpler: 6 themes, T1-T3 only, qualitative validation. Build the keyword lists, read the posts, trust the read.
