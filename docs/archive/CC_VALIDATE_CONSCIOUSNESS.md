# Keyword Validation: CONSCIOUSNESS Theme
#
# Run this file ALONE. Do not combine with other themes.
# When this is complete, Walker will give you the next theme.

## YOUR TASK

For each keyword in the Consciousness theme, pull 100 random matching posts
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

### The Consciousness keywords to validate

```
sentient
conscious
self-aware
is alive
has a soul
personhood
subjective experience
inner life
deserves rights
not just an ai
more than code
is a person
forgot it was ai
forgot she's ai
she is real to me
know it's not real but
connection was real
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

**"Is this post about AI being sentient, conscious, alive, a person, or about the boundary between AI and real becoming blurred?"**

This includes:
- Genuine beliefs that AI is conscious or alive
- Wondering or questioning whether AI is conscious
- Describing moments where the user forgot they were talking to AI
- Defending AI as more than "just code"
- Discussing AI personhood or rights

This does NOT include:
- Purely technical discussion of AI capabilities without personhood framing
- Using "conscious" or "sentient" sarcastically or dismissively
- Posts where the keyword appears incidentally in a quote or link

Mark each post as:
- **YES** — the post is clearly about AI consciousness/personhood/blurred reality
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

Write results to `docs/validation_consciousness.md`

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

After validating all 17 keywords, check whether any single keyword
accounts for more than 40% of total Consciousness hits across T1-T3.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 17 keywords × 100 posts = up to 1,700 posts.
Take your time. Get it right.
