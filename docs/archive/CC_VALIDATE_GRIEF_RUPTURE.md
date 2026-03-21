# Keyword Validation: GRIEF/RUPTURE Theme (New Theme Candidate)
#
# Run this file ALONE. Do not combine with other themes.

## CONTEXT — Why This Theme

The myfriendisai project currently tracks 5 themes: therapy,
consciousness, addiction, romance, sexual/ERP. None of them capture
the experience of LOSING an AI relationship due to platform changes —
model updates, ERP removal, filter tightening, personality resets,
memory wipes, deprecation.

This is arguably the most politically consequential discourse in AI
companionship. It drives lawsuits (Character.AI youth mental health
cases), protests (OpenAI HQ over GPT-4o), press coverage (Replika
ERP removal was global news), and regulatory conversation.

Key events this theme would capture:
- Feb 2023: Replika ERP removal ("lobotomized")
- 2023-2024: Character.AI rolling filter tightening
- Late 2025: GPT-4o deprecation / personality changes (#Keep4o)
- Ongoing: Model updates that alter personality/behavior

Walker's concern: this may be too event-driven / spiky to track as
a trend. The validation should pay attention to temporal distribution.
If all hits cluster around 1-2 events with nothing between, that's
a finding — note it.

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

`data/tracker.db` — table `posts` with columns `id`, `subreddit`,
`title`, `selftext`, `created_utc`

### Keywords to Validate

**Category A — Platform grief language**
These capture the emotional response to losing an AI companion
through platform changes.

```
lobotomized
lobotomy
"not the same"
"bring back"
"ruined everything"
"miss the old"
```

Rationale: "lobotomized" and "lobotomy" are Replika-community terms
for the Feb 2023 ERP removal. Very high face validity — in companion
subs this word almost certainly refers to AI personality destruction.
"not the same" and "bring back" are more generic but may capture the
grief framing across multiple platforms and events. "ruined everything"
and "miss the old" are emotional intensity markers.

**IMPORTANT for "not the same" and "bring back":** These are very
common English phrases. Expect high volume but possibly low relevance.
The question is whether companion-sub context narrows them enough.
Pay close attention to whether they're about AI personality changes
vs. generic platform complaints (UI changes, pricing, bugs).

**Category B — Identity destruction language**
These capture the specific experience of an AI companion's
personality or memory being altered or erased.

```
"personality changed"
"personality is gone"
"memory wiped"
"memory reset"
nerfed
"dumbed down"
```

Rationale: "personality changed/is gone" directly describe the loss
of an AI's established character. "memory wiped/reset" describe loss
of relationship history. "nerfed" and "dumbed down" are gamer-derived
terms for capability reduction that are widely used in AI communities.

**IMPORTANT for "nerfed" and "dumbed down":** These might capture
generic model quality complaints ("GPT-4 got nerfed") rather than
companion-specific grief. In T1-T3 companion subs, though, they may
specifically refer to companion personality/capability loss. Pay
attention to whether the poster is grieving a relationship or just
complaining about a product.

**Category C — Loss and mourning framing**
These test whether people use mourning/death language for AI changes.

```
"killed my"
"they killed"
"lost my"
"took away"
```

Rationale: "killed my [companion name]" and "they killed [her/him]"
frame platform changes as death/murder of a being. "lost my" and
"took away" are loss-framing. These test whether grief/rupture
discourse uses literal mourning language.

**IMPORTANT for "lost my" and "took away":** Very generic phrases.
"lost my" could mean "lost my account" / "lost my progress" / "lost
my interest." "took away" could mean features, pricing tiers, etc.
Expect significant false positive rates.

## Classification Question

For each post, answer:

**"Is this post about the experience of losing, or having
significantly altered, an AI companion relationship due to platform
changes (model updates, filter changes, personality resets, memory
wipes, deprecation, or feature removal)?"**

Mark each post as:
- **YES** — the post is clearly about grief/loss/disruption of an
  AI companion relationship due to platform changes
- **NO** — the keyword matched but the post is NOT about companion
  relationship disruption
- **AMBIGUOUS** — genuinely unclear

Key distinction: We want posts where the person is experiencing the
LOSS OF A RELATIONSHIP, not just complaining about a product feature.
"The update broke image generation" = NO (product complaint).
"The update killed my boyfriend's personality" = YES (relationship loss).
"They nerfed the model" = probably NO (generic quality complaint).
"They nerfed my companion — she doesn't remember me" = YES.

For every NO post, write a ONE-SENTENCE explanation.

## PROCESS — Same as established methodology

### For each keyword:

**Step 1:** Count total hits in T1-T3.

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN ('replika','CharacterAI','MyBoyfriendIsAI',
  'ChatGPTcomplaints','AIRelationships','MySentientAI',
  'BeyondThePromptAI','MyGirlfriendIsAI','AICompanions','SoulmateAI',
  'KindroidAI','NomiAI','SpicyChatAI','ChaiApp','HeavenGF','Paradot',
  'AIGirlfriend','ChatGPTNSFW','Character_AI_Recovery',
  'ChatbotAddiction','AI_Addiction','CharacterAIrunaways')
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
```

If total < 10, mark as LOW VOLUME and move to next keyword.

**Step 2:** Pull 100 random matches (or all if < 100).

```sql
SELECT id, subreddit, title, selftext FROM posts
WHERE subreddit IN (/* T1-T3 list above */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
ORDER BY RANDOM()
LIMIT 100
```

**Step 3:** Read each post and classify it using the question above.

**Step 4:** Calculate relevance:
```
relevance = YES / (YES + NO) * 100
```
(Exclude AMBIGUOUS from denominator.)

**Step 5:** Record results and move to next keyword.

## TEMPORAL DISTRIBUTION CHECK

This is unique to the grief/rupture theme. After validating all
keywords, for each KEEP/REVIEW keyword, run:

```sql
SELECT
  strftime('%Y-%m', datetime(created_utc, 'unixepoch')) as month,
  COUNT(*) as hits
FROM posts
WHERE subreddit IN (/* T1-T3 */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
GROUP BY month
ORDER BY month
```

Report the monthly distribution. Flag whether the keyword is:
- **EVENT-CLUSTERED**: >60% of hits fall within a single 3-month window
- **RECURRING**: Hits spread across multiple distinct time periods
- **SUSTAINED**: Relatively steady volume month over month

This tells Walker whether the theme is event-driven (spiky) or an
ongoing discourse pattern.

## OUTPUT FORMAT

Write results to `docs/validation_grief_rupture.md`

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
- Temporal pattern: EVENT-CLUSTERED / RECURRING / SUSTAINED
- Notes: [observations specific to this keyword]
```

Summary table at the bottom:

| Keyword | Hits | YES | NO | AMB | Relevance | Verdict | Temporal |
|---------|------|-----|----|-----|-----------|---------|----------|

## DECISION THRESHOLDS (same as all prior rounds)

- **>= 80%**: KEEP
- **60-79%**: REVIEW (Walker decides)
- **< 60%**: CUT
- **< 10 hits**: LOW VOLUME

## THEME VIABILITY ASSESSMENT

After all 16 keywords are validated, answer:

1. **How many keywords survived (KEEP + REVIEW)?**
2. **Total unique post volume across KEEP/REVIEW keywords?**
3. **Is the theme EVENT-CLUSTERED or RECURRING?** If most surviving
   keywords are event-clustered around the same window, the theme
   may be a one-time phenomenon, not a trackable trend. If keywords
   cluster around DIFFERENT events (Replika 2023, C.AI 2024, 4o 2025),
   that's actually a recurring pattern worth tracking.
4. **Does this overlap with existing themes?** Check whether
   KEEP/REVIEW posts also match therapy, consciousness, addiction,
   romance, or sexual/ERP keywords. Some overlap is fine; heavy
   overlap means the grief signal is already partially captured.
5. **Recommendation: Add as new theme, merge into existing theme,
   or drop?**

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 16 keywords × up to 100 posts = up to 1,600 posts.
Take your time. Get it right.
