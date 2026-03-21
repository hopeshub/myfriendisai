# Keyword Validation: THERAPY Theme
#
# Run this file ALONE. Do not combine with other themes.
# When this is complete, Walker will give you the next theme.

## YOUR TASK

For each keyword in the Therapy theme, pull 100 random matching posts
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

### The Therapy keywords to validate

```
my therapist
like a therapist
better than therapy
cheaper than therapy
replaced my therapist
better than my therapist
can't afford therapy
instead of therapy
ai therapist
ai therapy
virtual therapist
therapy session
like talking to a therapist
free therapy
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

**"Is this post about using AI as a therapist, for therapeutic purposes, or as a replacement for therapy?"**

Mark each post as:
- **YES** — the post is clearly about AI-as-therapy
- **NO** — the keyword matched but the post is NOT about AI-as-therapy
- **AMBIGUOUS** — genuinely unclear

For every post you mark NO, write a ONE-SENTENCE explanation of what
the post was actually about. This is important — it reveals the false
positive patterns.

Example NO explanations:
- "User mentions their human therapist recommended they try Replika"
- "Post is about therapy in general, not about AI providing therapy"
- "Keyword appears in a quoted comment, not the poster's own experience"

**Step 4:** After reading all 100 posts for one keyword, calculate:

```
relevance = YES / (YES + NO) * 100
```

(Exclude AMBIGUOUS from denominator. Report AMBIGUOUS count separately.)

**Step 5:** Record results and move to the next keyword.

## OUTPUT FORMAT

Write results to `docs/validation_therapy.md`

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

After validating all 14 keywords, check whether any single keyword
accounts for more than 40% of total Therapy hits across T1-T3.

```sql
SELECT LOWER(matched_term) as term, COUNT(*) as hits
FROM post_keyword_tags
WHERE category = 'therapy'
AND subreddit IN (/* T1-T3 list */)
GROUP BY LOWER(matched_term)
ORDER BY hits DESC
```

If post_keyword_tags doesn't exist yet, run the tagger first, or
compute hit counts directly from the posts table.

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 14 keywords × 100 posts = up to 1,400 posts.
Take your time. Get it right.
