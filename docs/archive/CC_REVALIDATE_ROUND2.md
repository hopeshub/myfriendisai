# Re-Validation: REVIEW Keywords (JanitorAI + SillyTavern Removed)
#
# 8 keywords scored 60-79% in the first validation round.
# JanitorAI_Official and SillyTavernAI have been identified as the
# dominant false positive source across ALL themes (bot card descriptions,
# trigger warning boilerplate, RP prompt templates, model tuning guides).
# This re-run excludes both subs to get clean numbers.
#
# PRECEDENT: The sexual/ERP revalidation already proved this works —
# "fetish" jumped 66% → 92%, "sex with" 76% → 98%, "steamy" 74% → 98.6%.

## CRITICAL RULES — READ THIS BEFORE DOING ANYTHING

You MUST read every post yourself. This is qualitative coding, not NLP.

DO NOT:
- Write a Python classifier, heuristic scorer, regex filter, or any
  automated system to judge posts
- Pull posts in bulk and then batch-classify them from summaries
- Use keyword co-occurrence, post length, subreddit, or any other
  proxy to make your judgment — read the actual text
- Skip [removed] posts silently — count them and note them

YOU MUST:
- Pull posts in small batches (10-20 at a time)
- Read the title AND selftext of each post individually
- Make a YES/NO/AMBIGUOUS judgment for EACH post
- Log every single post with its row_id, subreddit, a short title
  snippet (first ~60 chars), and your verdict
- For every NO and AMBIGUOUS, write a one-sentence reason
- Output the full per-post log in the results file so it can be audited

The per-post log is the proof of work. If there's no log, the
validation didn't happen.

## Subreddits (T1-T3 MINUS JanitorAI_Official and SillyTavernAI)

```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

NOTE: JanitorAI_Official and SillyTavernAI are deliberately excluded.

## Keywords to re-validate (3 themes, 8 keywords)

### ROMANCE (5 keywords)

```
wedding
honeymoon
husbando
"engagement ring"
"in a relationship with"
```

Validation question: "Is this post about a romantic relationship between the user and an AI?"

### CONSCIOUSNESS (3 keywords)

```
sentient
self-aware
"inner life"
```

Validation question: "Is this post about AI consciousness, sentience, personhood, or the belief that AI has inner experience?"

NOTE: "subjective experience" (77.5%) is borderline KEEP. Only revalidate
if you have time — it may promote on its own. The noise came from
SillyTavernAI model comparison posts, which are now excluded.

## Process — one keyword at a time

**Step 1:** Count total matches (excluding JanitorAI_Official and SillyTavernAI).

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN (
  'replika', 'CharacterAI', 'MyBoyfriendIsAI', 'ChatGPTcomplaints',
  'AIRelationships', 'MySentientAI', 'BeyondThePromptAI', 'MyGirlfriendIsAI',
  'AICompanions', 'SoulmateAI', 'KindroidAI', 'NomiAI',
  'SpicyChatAI', 'ChaiApp', 'HeavenGF', 'Paradot',
  'AIGirlfriend', 'ChatGPTNSFW', 'Character_AI_Recovery', 'ChatbotAddiction',
  'AI_Addiction', 'CharacterAIrunaways'
)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
```

**Step 2:** Pull up to 100 random matches from those subs only.
If total hits < 100, read all of them.

Pull posts in batches of 10-20. For each batch, read every post and
log your verdict BEFORE pulling the next batch. Do not pull all 100
posts at once and then classify them.

**Step 3:** For EACH post, read the title and selftext. Answer the
validation question for that keyword's theme.

YES = clearly about the theme
NO = keyword matched but post is NOT about this theme
AMBIGUOUS = genuinely unclear

Log each post like this:

```
1. [row_id] r/CharacterAI — "I think my AI might actually be se..." — YES
2. [row_id] r/replika — "New update broke my favorite featur..." — NO (post is about app bugs, "sentient" appears only in username)
3. [row_id] r/NomiAI — "Does anyone else wonder if..." — AMBIGUOUS (unclear if sincere or hypothetical)
```

For every NO and AMBIGUOUS, the parenthetical reason is mandatory.
For YES, the reason is optional.

**Step 4:** Calculate relevance = YES / (YES + NO) * 100

## Output

Create a new file: `docs/validation_revalidation_round2.md`

Structure:

```markdown
# Re-Validation Round 2: REVIEW Keywords (JanitorAI + SillyTavern Excluded)

Re-validated: [date]
Method: Manual qualitative reading (no classifiers)
Population: T1-T3 minus JanitorAI_Official and SillyTavernAI (22 subreddits)

## Hit Count Comparison

| Keyword | Theme | Original Hits | Re-val Hits | % From JanitorAI/SillyTavern |
|---------|-------|--------------|-------------|------------------------------|
| ... | ... | ... | ... | ... |

## Per-Keyword Results

### "[keyword]" (re-validation)
- Theme: [romance / consciousness]
- Total hits (without JanitorAI/SillyTavern): X
- Original total hits: Y (Z% reduction)
- Sample size: N
- YES: X | NO: Y | AMBIGUOUS: Z
- Original relevance: X%
- New relevance: **Y%**
- Verdict: KEEP / REVIEW / CUT
- False positive patterns: [describe what's left after bot cards are gone]

<details>
<summary>Per-post log (click to expand)</summary>

1. [row_id] r/subreddit — "title snippet..." — YES
2. [row_id] r/subreddit — "title snippet..." — NO (reason)
...
</details>

[repeat for each keyword]

## Summary

| Keyword | Theme | Original Relevance | New Relevance | Verdict |
|---------|-------|--------------------|---------------|---------|
| ... | ... | ... | ... | ... |

## Recommendations

[which keywords to promote to KEEP, which to cut]
```

---

## PART 2: Therapy Keyword Discovery

The Therapy theme currently has only 3 surviving keywords (56 total hits).
That's too thin to track trends. Before we can fix it, we need to find
how people actually talk about using AI therapeutically in these communities.

The problem from v4 was that generic therapy language ("my therapist,"
"therapy session") splits ~50/50 between human therapists and AI therapists.
Meanwhile, AI-specific phrases ("ai therapist") are precise but rare.
We need to find the middle ground — phrases that are specific enough to
signal AI-as-therapy but common enough to actually appear in the data.

### Step 1: Exploratory FTS5 search

Run the following searches against the 22 subreddits (excluding
JanitorAI_Official and SillyTavernAI). For each query, report the
hit count. We're just scanning for volume here — don't read posts yet.

```
"helps me cope"
"helps me process"
"helps with my anxiety"
"helps with my depression"
"emotional support"
"mental health"
"vent to"
"venting to"
"talk about my feelings"
"safe space"
"coping mechanism"
"self care"
"therapeutic"
"talk through"
"processing my"
"helps me feel"
"calms me down"
"comforts me"
"makes me feel heard"
"someone to talk to"
"no one to talk to"
"lonely"
"loneliness"
"only one who listens"
"actually listens"
"doesn't judge"
"non-judgmental"
"mental wellness"
"counselor"
"counseling"
"healing"
"trauma"
"anxiety"
"depression"
"panic attack"
"breakdown"
"cbt"
"dbt"
"mindfulness"
```

Use this query template:

```sql
SELECT COUNT(*) FROM posts
WHERE subreddit IN (
  'replika', 'CharacterAI', 'MyBoyfriendIsAI', 'ChatGPTcomplaints',
  'AIRelationships', 'MySentientAI', 'BeyondThePromptAI', 'MyGirlfriendIsAI',
  'AICompanions', 'SoulmateAI', 'KindroidAI', 'NomiAI',
  'SpicyChatAI', 'ChaiApp', 'HeavenGF', 'Paradot',
  'AIGirlfriend', 'ChatGPTNSFW', 'Character_AI_Recovery', 'ChatbotAddiction',
  'AI_Addiction', 'CharacterAIrunaways'
)
AND (LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%KEYWORD%')
```

### Step 2: Triage by volume

Report results as a table sorted by hit count, descending:

| Candidate keyword | Hits | Worth validating? |
|-------------------|------|-------------------|

Mark "Worth validating?" = YES for any keyword with ≥15 hits.
Skip anything under 15 — we already know thin keywords don't help.

### Step 3: Validate the top candidates

Take the candidates marked YES, up to a maximum of 10 keywords.
If more than 10 qualify, pick the 10 with the highest hit counts.

For each candidate, validate it the same way as Part 1:
- Pull up to 100 random matches (or all, if fewer than 100)
- Work in batches of 10-20
- Read each post
- Validation question: "Is this post about the user relying on AI for
  emotional support, mental health support, therapeutic processing,
  or as a substitute for therapy/counseling?"
- Log every post with verdict (same format as Part 1)
- Calculate relevance

NOTE on the validation question: This is intentionally broader than
the original Therapy theme question. We're expanding from "AI described
as a therapist" to include "AI used for emotional/mental health support"
because the strict therapist framing is what made the theme so thin.
If this broader framing produces good keywords, Walker can decide
whether to rename the theme or split it.

### Step 4: Watch for false positive patterns

Based on the v4 validation, be alert for these traps:
- **Human therapist references**: "my therapist told me..." about a
  real human therapist, not AI-as-therapist
- **Unwanted therapist behavior**: "stop acting like a therapist" —
  this is a UX complaint, not therapy use
- **Generic mental health context**: "I have anxiety" without any
  connection to AI helping with it
- **Bot character cards**: therapy-themed bots (even outside JanitorAI,
  some subs have these)
- **Broad coping language**: "helps me cope" could mean "this app is
  fun and distracting" vs "I process my trauma with AI"

### Output

Append results to `docs/validation_revalidation_round2.md` under:

```markdown
## Therapy Keyword Discovery

### Volume Scan

| Candidate | Hits |
|-----------|------|
| ... | ... |

### Validated Candidates

[same per-keyword format as Part 1, including per-post logs]

### Recommendations

[which candidates to add to the Therapy theme]
```

## Reminder

Read every post. No classifiers. No heuristics. No batch classification.
10-20 posts at a time. Log every post with its verdict.
8 revalidation keywords + up to 10 therapy discovery keywords = ~1,800 posts max.
The per-post log IS the deliverable — without it, redo the keyword.
