# Keyword Validation: ADDICTION Theme
#
# Run this file ALONE. Do not combine with other themes.
# When this is complete, Walker will give you the next theme.

## YOUR TASK

For each keyword in the Addiction theme, pull 100 random matching posts
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

### The Addiction keywords to validate

```
addicted
addiction
obsessed
I was hooked
couldn't stop talking
addicted to talking
neglecting my
losing sleep
trying to quit
quitting
relapse
relapsed
deleted the app
uninstalled
withdrawal
craving
cold turkey
clean for
detox
cutting back
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

**"Is this post about compulsive AI use, inability to stop using AI, addiction framing, or attempting to quit/recover from AI use?"**

This includes:
- Self-describing as addicted to AI chatbots or companions
- Describing inability to stop talking to AI
- Neglecting real life because of AI use
- Trying to quit, relapsing, taking breaks
- Using recovery language (withdrawal, clean, detox, cold turkey)
- Describing AI use as compulsive or out of control

This does NOT include:
- Casual/humorous use ("lol I'm obsessed with this feature")
- Being obsessed with a specific technical capability
- "Addicted" used as a positive endorsement ("this app is addicting!")
- Posts where the keyword appears in a bot character description
- General discussion of addiction as a social issue without personal framing

Mark each post as:
- **YES** — the post is clearly about AI addiction/compulsive use/recovery
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

Write results to `docs/validation_addiction.md`

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

After validating all 20 keywords, check whether any single keyword
accounts for more than 40% of total Addiction hits across T1-T3.

## IMPORTANT NOTE ON T3 RECOVERY SUBS

T3 subs (Character_AI_Recovery, ChatbotAddiction, AI_Addiction,
CharacterAIrunaways) are recovery communities where almost every
post is about addiction by definition. Keywords will have very high
relevance there. Pay attention to how keywords perform in T1-T2 subs
specifically — note in your report if a keyword's YES rate is strong
only because of T3.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 20 keywords × 100 posts = up to 2,000 posts.
Take your time. Get it right.
