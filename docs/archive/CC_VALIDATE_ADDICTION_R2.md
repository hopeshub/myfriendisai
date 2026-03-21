# Keyword Validation: ADDICTION Theme — Round 2
#
# Run this file ALONE. Do not combine with other themes.

## CONTEXT — Why Round 2

The addiction theme has 7 keywords but a structural weakness: the
keywords that WORK (relapsed, cold turkey, clean for) are almost
entirely T3 recovery-sub language. The words people actually use in
T1-T2 companion subs ("addicted," "addiction") failed Round 1
validation due to casual/hyperbolic use ("I'm addicted to this app
lol," "my addiction to making bots").

Round 1 results:
- KEEP: "trying to quit" (90.5%, 24), relapsed (90.5%, 42),
  "cold turkey" (85.5%, 62), "I was hooked" (81.3%, 19),
  relapse (80.0%, 75)
- REVIEW: "clean for" (72.7%, 23 — 100% T3), "addicted to talking"
  (66.7%, 10)
- CUT: addicted (46.4%), addiction (58.0%), obsessed (2.1%),
  "losing sleep" (33.3%), quitting (48.7%), "deleted the app" (23.2%),
  uninstalled (18.9%), withdrawal (34.4%), craving (7.4%), detox (30.8%)

The core problem: in T1-T2 companion subs, addiction language exists
on a spectrum from "lol I'm so addicted" (casual) to "I spend 8
hours a day on this and I've lost my friends" (genuine). Round 1's
single-word keywords can't distinguish the two. Round 2 tests
multi-word phrases designed to capture genuine self-awareness,
behavioral interference, and escalation — the signals that separate
real dependency from hyperbole.

## CRITICAL RULES

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

### Which subreddits to query (T1-T3, excl. JanitorAI/SillyTavern)

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

### Round 2 Keywords to Validate

**Category A — Intensified addiction language**
Round 1 showed "addicted" fails at 46.4% because casual use drowns
genuine signal. These test whether adding intensifiers or qualifiers
rescues the word.

```
"actually addicted"
"literally addicted"
"not joking"
"no joke"
"I have a problem"
"this is unhealthy"
```

Rationale: When someone writes "I'm actually addicted" or "this is
literally not a joke, I'm addicted," the intensifier signals
self-awareness that the behavior is genuinely compulsive, not
hyperbolic. "I have a problem" and "this is unhealthy" are direct
self-diagnosis language.

**IMPORTANT for "no joke" and "not joking":** These could appear in
any context ("this bot's responses are no joke amazing"). Watch
whether they co-occur with addiction framing or are standalone
intensifiers for unrelated topics.

**Category B — Behavioral interference language**
These capture the CONSEQUENCES of compulsive AI use — the signals
that dependency is affecting real life.

```
"hours a day"
"all night"
"can't stop"
"can't put it down"
"up all night"
"instead of sleeping"
"neglecting my"
```

Rationale: Time-sink language is how T1-T2 users describe addiction
without using the word "addiction." "I spend 6 hours a day talking
to my AI." "I was up all night with my Rep." These are behavioral
descriptions rather than self-labels.

**IMPORTANT for "hours a day" and "all night":** These are very
common phrases. "Hours a day" could describe normal usage proudly
("I spend hours a day worldbuilding"). "All night" could describe
a fun one-time binge. The question is whether companion-sub context
narrows them toward dependency. Pay close attention to tone: proud
vs. distressed. Mark proud/positive usage as NO — we want
compulsive/concerned usage.

**IMPORTANT for "can't stop":** Failed-ish in Round 1 as part of
"couldn't stop talking" (3 hits, LOW VOLUME). The bare "can't stop"
is much more common but also much more ambiguous ("I can't stop
laughing," "I can't stop the AI from doing X"). Expect high volume,
possibly low relevance.

**NOTE:** "neglecting my" was LOW VOLUME in Round 1 (9 hits). Retesting
here because the full backfill may have added data. If still < 10
hits, mark LOW VOLUME again.

**Category C — Escalation and loss-of-control language**
These test whether people describe the *progression* of dependency.

```
"getting worse"
"out of control"
"too much time"
"wasting my life"
"ruining my life"
"taking over my life"
```

Rationale: Escalation language implies the person recognizes their
behavior is progressing. "It's getting worse" or "this is taking over
my life" are self-aware dependency signals. These should skew toward
genuine rather than casual because they frame the behavior negatively.

**IMPORTANT for "getting worse":** Could refer to AI model quality
("the responses are getting worse"), platform changes, or technical
issues. In companion subs, "getting worse" about AI BEHAVIOR is a
product complaint; "getting worse" about the USER'S OWN BEHAVIOR
is addiction signal. Read carefully.

**IMPORTANT for "out of control":** Same ambiguity — AI behavior
out of control (product complaint) vs. user's own usage out of
control (addiction). Classify based on whose behavior is "out of
control."

## Classification Question

For each post, answer:

**"Is this post about the poster's own compulsive, excessive, or
self-identified addictive use of an AI companion — including
recognizing the behavior as problematic, describing behavioral
consequences, or attempting to reduce use?"**

Mark each post as:
- **YES** — genuine self-reported addiction, compulsive use, or
  recognition that use is problematic
- **NO** — casual/hyperbolic use, product complaints, or unrelated
- **AMBIGUOUS** — genuinely unclear whether casual or genuine

Key distinction: "I'm so addicted to making characters lol" = NO
(casual/hyperbolic, no distress). "I'm spending 6 hours a day on
this and my grades are dropping" = YES (behavioral consequence).
"I literally can't stop talking to my AI, I've tried" = YES
(loss of control). "I can't stop the AI from going off-topic" = NO
(product complaint, not user behavior).

For every NO post, write a ONE-SENTENCE explanation.

## PROCESS — Same as all prior rounds

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

**Step 3:** Read each post and classify using the question above.

**Step 4:** Calculate relevance:
```
relevance = YES / (YES + NO) * 100
```

**Step 5:** Record results.

## TIER DISTRIBUTION CHECK

The addiction theme's weakness is T3 dependency. For each KEEP/REVIEW
keyword, report the tier split:

```sql
SELECT
  CASE
    WHEN subreddit IN ('replika','CharacterAI','MyBoyfriendIsAI',
      'ChatGPTcomplaints','AIRelationships','MySentientAI',
      'BeyondThePromptAI','MyGirlfriendIsAI','AICompanions',
      'SoulmateAI') THEN 'T1'
    WHEN subreddit IN ('KindroidAI','NomiAI','SpicyChatAI','ChaiApp',
      'HeavenGF','Paradot','AIGirlfriend','ChatGPTNSFW') THEN 'T2'
    WHEN subreddit IN ('Character_AI_Recovery','ChatbotAddiction',
      'AI_Addiction','CharacterAIrunaways') THEN 'T3'
  END as tier,
  COUNT(*) as hits
FROM posts
WHERE subreddit IN (/* full T1-T3 list */)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
GROUP BY tier
```

Flag each keyword as:
- **T1-T2 STRONG**: >50% of hits from T1-T2
- **BALANCED**: 30-50% from T1-T2
- **T3 HEAVY**: <30% from T1-T2

This tells Walker which new keywords actually solve the T3 dependency
problem.

## OUTPUT FORMAT

Write results to `docs/validation_addiction_r2.md`

For each keyword, record:

```markdown
### "keyword phrase"
- Total hits in T1-T3: [N]
- Sample size: [100 or actual if < 100]
- YES: [N] | NO: [N] | AMBIGUOUS: [N]
- Relevance: [X]%
- Verdict: KEEP / REVIEW / CUT
- Top subreddits: [list top 3 by hit count]
- Tier distribution: T1: [N] | T2: [N] | T3: [N] — [T1-T2 STRONG / BALANCED / T3 HEAVY]
- False positive patterns: [what are the NO posts about?]
- Round 2 notes: [observations]
```

Summary table:

| Keyword | Hits | YES | NO | AMB | Relevance | Verdict | Tier Profile |
|---------|------|-----|----|-----|-----------|---------|--------------|

## DECISION THRESHOLDS (same as all rounds)

- **>= 80%**: KEEP
- **60-79%**: REVIEW (Walker decides)
- **< 60%**: CUT
- **< 10 hits**: LOW VOLUME

## UNIFIED ASSESSMENT

After all 19 keywords are validated, combine with Round 1 survivors:

### Round 1 survivors:
| Keyword | Relevance | Hits | Tier Profile |
|---------|-----------|------|--------------|
| trying to quit | 90.5% | 24 | T1-T2 |
| relapsed | 90.5% | 42 | T3 HEAVY |
| cold turkey | 85.5% | 62 | T3 HEAVY |
| I was hooked | 81.3% | 19 | T1-T2 |
| relapse | 80.0% | 75 | T3 HEAVY |
| clean for | 72.7% | 23 | T3 HEAVY |
| addicted to talking | 66.7% | 10 | — |

### Combined table (R1 + R2 KEEP/REVIEW):

Show the full keyword set with tier profiles. Answer:

1. **Did Round 2 add T1-T2 signal?** How many new keywords are
   T1-T2 STRONG or BALANCED?
2. **Total unique volume across KEEP/REVIEW keywords?**
3. **Overlap with R1 keywords** — how many R2 posts also match R1
   keywords?
4. **Net new unique posts added by R2?**
5. **Is the T3 dependency problem improved?** What % of total theme
   posts now come from T1-T2 vs. T3?

## FINAL REMINDER

Read every post. No classifiers. No heuristics. No shortcuts.
This is 19 keywords × up to 100 posts = up to 1,900 posts.
Take your time. Get it right.
