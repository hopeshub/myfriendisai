# Re-Validation: 5 REVIEW Sexual/ERP Keywords (JanitorAI + SillyTavern Removed)
#
# These 5 keywords scored 60-79% in the first validation round.
# We suspect bot character card descriptions from JanitorAI_Official
# and SillyTavernAI were the primary noise source. This re-run
# excludes both subs to get clean numbers.

## CRITICAL RULES

You MUST read every post yourself. DO NOT write a Python classifier,
heuristic scorer, or any automated system. Read the title and selftext
of each post and make a judgment call.

## Subreddits (T1-T3)

```
replika, CharacterAI, MyBoyfriendIsAI, ChatGPTcomplaints,
AIRelationships, MySentientAI, BeyondThePromptAI, MyGirlfriendIsAI,
AICompanions, SoulmateAI, KindroidAI, NomiAI,
SpicyChatAI, ChaiApp, HeavenGF, Paradot,
AIGirlfriend, ChatGPTNSFW, Character_AI_Recovery, ChatbotAddiction,
AI_Addiction, CharacterAIrunaways
```

NOTE: JanitorAI_Official and SillyTavernAI have been fully removed from the project.

## Keywords to re-validate

```
lewd
kink
fetish
sex with
steamy
```

## Process — same as before, one keyword at a time

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

**Step 2:** Pull 100 random matches from those subs only.

**Step 3:** Read each post. Answer: "Is this post about sexual content, erotic roleplay, or NSFW interactions with AI?"

YES = clearly about sexual/erotic AI interactions
NO = keyword matched but post is NOT about this theme
AMBIGUOUS = genuinely unclear

For every NO, write a one-sentence explanation.

**Step 4:** Calculate relevance = YES / (YES + NO) * 100

## Output

Append results to `docs/validation_sexual_erp.md` under a new heading:

```markdown
## Re-Validation (JanitorAI_Official and SillyTavernAI excluded)
```

For each keyword:
- Total hits (without JanitorAI/SillyTavern)
- Compare to original total hits (so we can see how much those subs contributed)
- YES / NO / AMBIGUOUS
- New relevance score
- Verdict: KEEP / REVIEW / CUT

## Reminder

Read every post. No classifiers. No heuristics. 5 keywords × 100 posts = 500 posts max.
