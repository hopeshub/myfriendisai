# Keyword Validation: SEXUAL / ERP Theme
#
# Run this file ALONE. Do not combine with other themes.
# When this is complete, all 5 themes are validated.

## YOUR TASK

For each keyword in the Sexual/ERP theme, pull 100 random matching posts
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

### The Sexual/ERP keywords to validate

```
erp
erotic roleplay
smut
lewd
kink
fetish
sex with
intimate scene
steamy
sexual tension
ai sex
nsfw chat
nsfw bot
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

**"Is this post about sexual content, erotic roleplay, or NSFW interactions with AI?"**

This includes:
- Describing erotic roleplay with AI
- Discussing sexual features or NSFW capabilities of AI platforms
- Sharing experiences of sexual interactions with AI
- Asking about or recommending NSFW AI chatbots
- Discussing the removal or restriction of sexual/ERP features

This does NOT include:
- Bot character card descriptions that use sexual language as marketing
  ("sexy vampire will seduce you") — these are product listings, not user experiences
- Meta-discussion about content policy that doesn't involve personal sexual AI use
- Posts where the keyword appears in a flair, tag, or subreddit rule quote
- Using "lewd" or "steamy" casually to describe non-sexual content

Mark each post as:
- **YES** — the post is clearly about sexual/erotic AI interactions
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

Write results to `docs/validation_sexual_erp.md`

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

After validating all 13 keywords, check whether any single keyword
accounts for more than 40% of total Sexual/ERP hits across T1-T3.

## IMPORTANT NOTE ON BOT LISTINGS

This theme is the most vulnerable to bot character card noise from
bot-listing communities (JanitorAI and SillyTavernAI have been removed from tracking;
SpicyChatAI and AIGirlfriend remain). Character
cards often contain terms like "erp," "nsfw," "kink," "fetish,"
"lewd," and "smut" as feature tags — not as user discourse.

For every keyword, note what percentage of NO posts are bot listings
versus other types of false positives. If bot listings dominate the
false positives for a keyword, flag it — we may need to exclude
specific subs from this theme's trendline.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 13 keywords × 100 posts = up to 1,300 posts.
Take your time. Get it right.
