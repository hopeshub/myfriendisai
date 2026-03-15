# Keyword Validation Instructions for Claude Code

## What This Is

Validate each keyword in `keywords_v4.yaml` by pulling 100 random posts that match it from T1-T3 subreddits only, then assessing whether each post is actually about the keyword's assigned theme.

## Important Context

- We are ONLY validating keywords against T1-T3 subreddits (companion communities). T0 (ChatGPT, OpenAI, singularity, ClaudeAI, claudexplorers) is excluded entirely.
- The question is NOT "is this post about AI companionship?" — the subreddit already establishes that.
- The question IS: "Is this post about the THEME this keyword is assigned to?"
- For example: "addicted" is in the Addiction theme. If a post in r/replika says "I'm addicted to customizing my rep's outfits" — that's NOT addiction discourse, it's casual usage. If it says "I'm addicted to talking to her and I can't stop" — that IS addiction discourse.

## Setup

The keywords YAML is at: `config/keywords_v4.yaml` (copy it there from the uploaded file if needed)
The database is at: `data/tracker.db`

T1-T3 subreddits (from communities.yaml):
```
T1: replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints, AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI, AICompanions, SoulmateAI
T2: KindroidAI, NomiAI, SpicyChatAI, ChaiApp, HeavenGF, Paradot, AIGirlfriend, ChatGPTNSFW
T3: Character_AI_Recovery, ChatbotAddiction, AI_Addiction, CharacterAIrunaways
```

## Process — Do This For Each Keyword

### Step 1: Pull 100 random matching posts from T1-T3

```sql
SELECT id, subreddit, title, selftext
FROM posts
WHERE subreddit IN (
  'replika', 'CharacterAI', 'MyBoyfriendIsAI', 'ChatGPTcomplaints',
  'AIRelationships', 'MySentientAI', 'BeyondThePromptAI', 'MyGirlfriendIsAI',
  'AICompanions', 'SoulmateAI', 'KindroidAI', 'NomiAI',
  'SpicyChatAI', 'ChaiApp', 'HeavenGF', 'Paradot',
  'AIGirlfriend', 'ChatGPTNSFW', 'Character_AI_Recovery', 'ChatbotAddiction',
  'AI_Addiction', 'CharacterAIrunaways'
)
AND (
  LOWER(title) LIKE '%KEYWORD%'
  OR LOWER(selftext) LIKE '%KEYWORD%'
)
ORDER BY RANDOM()
LIMIT 100
```

Replace `%KEYWORD%` with the lowercase keyword. For multi-word phrases, match the full phrase.

If a keyword has fewer than 100 matches in T1-T3, note the actual count. If it has fewer than 10 matches, flag it as LOW VOLUME — it might not be worth including regardless of accuracy.

### Step 2: Read and classify each post

For each of the 100 posts, answer ONE question:

**"Is this post about [THEME NAME]?"**

The theme definitions:
- **Therapy**: Is this post about using AI as a therapist, for therapeutic purposes, or as a replacement for therapy?
- **Consciousness**: Is this post about AI being sentient, conscious, alive, a person, or about the boundary between AI and real becoming blurred?
- **Addiction**: Is this post about compulsive AI use, inability to stop, addiction framing, or attempting to quit/recover from AI use?
- **Romance**: Is this post about a romantic relationship with AI — love, dating, marriage, proposals, breakups, romantic feelings?
- **Sexual/ERP**: Is this post about sexual content, erotic roleplay, or NSFW interactions with AI?

Classify each post as:
- **YES** — clearly about the theme
- **NO** — not about the theme (keyword matched but context is wrong)
- **AMBIGUOUS** — could go either way

### Step 3: Calculate relevance score

```
relevance = (YES count) / (YES + NO count) * 100
```

Ignore AMBIGUOUS posts in the denominator. Report AMBIGUOUS count separately.

### Step 4: Flag issues

For each keyword, report:
- Total matches in T1-T3
- Sample size (100 or fewer if low volume)
- YES / NO / AMBIGUOUS counts
- Relevance score (%)
- Top 3 subreddits by hit count (to check for concentration)
- Any patterns in the NO posts (what are the false positives about?)

## Decision Thresholds

- **>= 80% relevance**: KEEP — keyword is solid
- **60-79% relevance**: REVIEW — note what's causing false positives, Walker decides
- **< 60% relevance**: CUT — keyword doesn't reliably indicate the theme
- **< 10 total matches**: LOW VOLUME — flag for Walker, may not be worth tracking

## Concentration Check

After validating all keywords in a theme, check whether any single keyword accounts for more than 40% of the theme's total hits. If so, flag it — the trend line is fragile.

```sql
-- Run after tagging. Replace THEME with category name.
SELECT matched_term, COUNT(*) as hits,
  ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 1) as pct
FROM post_keyword_tags
WHERE category = 'THEME'
AND subreddit IN (/* T1-T3 list */)
GROUP BY matched_term
ORDER BY hits DESC
```

## Output Format

Produce a summary file `docs/keyword_validation_v4.md` with:

1. **Per-keyword table** for each theme:
   | Keyword | Total Hits | Sample | YES | NO | AMB | Relevance | Verdict |
2. **Concentration table** for each theme:
   | Keyword | Hits | % of Theme |
3. **Recommendations**: which keywords to keep, cut, or flag for Walker's review
4. **False positive patterns**: what kinds of posts are generating NO classifications

## Order of Operations

Do all 5 themes. Start with Therapy (smallest, tightest — good warmup), then Consciousness, Addiction, Romance, Sexual/ERP.

## Important Notes

- Do NOT modify the keywords YAML. Just produce the validation report. Walker will make final decisions.
- If the FTS5 index is available, use it for speed. If not, LIKE queries work fine.
- Be honest about ambiguous cases. If you're unsure, mark AMBIGUOUS. Don't inflate YES counts.
- Bot character card descriptions (especially from JanitorAI) that use romantic/sexual language but are product listings, NOT user experiences, should be classified as NO.
