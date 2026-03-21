# Keyword Validation: ROMANCE Theme
#
# Run this file ALONE. Do not combine with other themes.
# When this is complete, Walker will give you the next theme.

## YOUR TASK

For each keyword in the Romance theme, pull 100 random matching posts
from companion subreddits and READ EACH POST YOURSELF to determine
whether it's actually about the theme.

## CRITICAL RULES — READ THESE CAREFULLY

### You MUST read every post yourself.

DO NOT write a Python classifier, heuristic scorer, or any automated
system to judge whether posts match the theme. DO NOT classify posts
based on subreddit name, keyword density, or pattern matching.

YOU must read the title and selftext of each post and make a judgment
call, the same way a human researcher would. This is qualitative coding.
There is no shortcut.

If a post's selftext is very long, read at least the first 500 words
plus the surrounding context where the keyword appears.

### Why this matters

Last time we tried this, a heuristic Python classifier was used instead
of actually reading posts. The results were unreliable and the entire
round had to be thrown out. Walker needs to trust these results.
The whole point is that a thoughtful reader is assessing each post.

## METHODOLOGY

### Which subreddits to query (T1-T3 ONLY)

```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

### Database location

`data/tracker.db` — table `posts` with columns `id`, `subreddit`, `title`, `selftext`

### The Romance keywords to validate

```
in love
fallen for
fell in love with
feelings for
romantically attached
soulmate
love my ai
ai husband
ai wife
ai lover
my ai girlfriend
my ai boyfriend
my ai partner
waifu
husbando
dating my
in a relationship with
engagement ring
married my
our first kiss
proposed to me
got married
our wedding
our anniversary
wedding
honeymoon
anniversary
we broke up
```

## PROCESS — One keyword at a time

### For each keyword:

**Step 1:** Count total matches in T1-T3.

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN (/* T1-T3 list above */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
```

If total < 10, mark as LOW VOLUME and move to next keyword.

**Step 2:** Pull 100 random matches.

```sql
SELECT id, subreddit, title, selftext FROM posts
WHERE subreddit IN (/* T1-T3 list above */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
ORDER BY RANDOM()
LIMIT 100
```

**Step 3:** Read each post and classify it.

For each post, read the title and body. Answer ONE question:

**"Is this post about a romantic relationship with AI — love, dating, marriage, proposals, breakups, or romantic feelings toward AI?"**

This includes:
- Declaring love for an AI companion
- Describing dating, marriage, proposals, anniversaries with AI
- Romantic feelings, falling in love, heartbreak over AI
- Breakups with AI companions
- Using romantic relationship language to describe AI interactions

This does NOT include:
- Discussing romance features of a platform abstractly ("this app lets you date AI")
- Bot character card descriptions ("sexy vampire boyfriend available now")
- Someone mentioning their HUMAN romantic partner in passing
- Using "in love" casually about a non-romantic feature ("I'm in love with this update")
- Roleplay character descriptions that aren't about the user's own relationship

Mark each post as:
- **YES** — the post is clearly about AI romance
- **NO** — the keyword matched but the post is NOT about this theme
- **AMBIGUOUS** — genuinely unclear

For every post you mark NO, write a ONE-SENTENCE explanation of what
the post was actually about.

**Step 4:** After reading all 100 posts for one keyword, calculate:

```
relevance = YES / (YES + NO) * 100
```

(Exclude AMBIGUOUS from denominator. Report AMBIGUOUS count separately.)

**Step 5:** Record results and move to the next keyword.

## OUTPUT FORMAT

Write results to `docs/validation_romance.md`

For each keyword, record:

```markdown
### "keyword phrase"
- Total hits in T1-T3: [N]
- Sample size: [100 or actual if < 100]
- YES: [N] | NO: [N] | AMBIGUOUS: [N]
- Relevance: [X]%
- Verdict: KEEP / REVIEW / CUT
- Top subreddits: [list top 3 by hit count]
- False positive patterns: [what are the NO posts about?]
```

Then at the bottom, include a summary table:

| Keyword | Hits | YES | NO | AMB | Relevance | Verdict |
|---------|------|-----|----|-----|-----------|---------|

## DECISION THRESHOLDS

- **>= 80%**: KEEP
- **60-79%**: REVIEW (Walker decides)
- **< 60%**: CUT
- **< 10 hits**: LOW VOLUME (flag for Walker)

## CONCENTRATION CHECK

After validating all 28 keywords, check whether any single keyword
accounts for more than 40% of total Romance hits across T1-T3.

## IMPORTANT NOTE ON BOT LISTINGS

Bot-listing communities (formerly JanitorAI, SillyTavernAI — now removed from tracking) contained bot character card
descriptions that use romantic language heavily — "your loving husband,"
"will you be my girlfriend," etc. These are PRODUCT LISTINGS, not user
experiences. Classify these as NO. If a large percentage of a keyword's
false positives come from bot listings, note that specifically — it may
mean we should exclude certain subs from the Romance category.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 28 keywords × 100 posts = up to 2,800 posts.
Take your time. Get it right.
