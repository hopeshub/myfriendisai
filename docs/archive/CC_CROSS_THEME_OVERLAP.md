# Cross-Theme Overlap Analysis
#
# Run this file ALONE. This is a SQL-only task — no manual reading.

## CONTEXT

Keywords v7 has 6 themes. Posts can match keywords in multiple themes
simultaneously. Before building trend lines, we need to know how much
overlap exists between themes so Walker can document whether trend
lines count unique-per-theme or allow cross-counting.

## DATABASE

`data/tracker.db` — table `posts` with columns `id`, `subreddit`,
`title`, `selftext`, `created_utc`

## SUBREDDIT SCOPE (T1-T3, excl. JanitorAI/SillyTavern)

```sql
subreddit IN ('replika','CharacterAI','MyBoyfriendIsAI',
  'ChatGPTcomplaints','AIRelationships','MySentientAI',
  'BeyondThePromptAI','MyGirlfriendIsAI','AICompanions','SoulmateAI',
  'KindroidAI','NomiAI','SpicyChatAI','ChaiApp','HeavenGF','Paradot',
  'AIGirlfriend','ChatGPTNSFW','Character_AI_Recovery',
  'ChatbotAddiction','AI_Addiction','CharacterAIrunaways')
```

## THEME KEYWORD DEFINITIONS

Use these exact keyword lists. A post matches a theme if it matches
ANY keyword in that theme (OR logic within theme).

**THERAPY:**
```
ai therapist, free therapy, ai therapy, as a therapist, therapeutic, for therapy
```

**CONSCIOUSNESS:**
```
personhood, subjective experience, more than code, sentient, has a soul, self-aware, inner life, not just an ai
```

**ADDICTION:**
```
trying to quit, relapsed, cold turkey, I was hooked, relapse, clean for, addicted to talking
```

**ROMANCE:**
```
my ai partner, husbando, my ai boyfriend, ai lover, ai husband,
my ai girlfriend, ai wife, married my, love my ai, dating my,
proposed to me, our anniversary, our wedding, our first kiss,
honeymoon, wedding, engagement ring, we broke up, in a relationship with
```

**SEXUAL_ERP:**
```
erp, nsfw chat, intimate scene, steamy, sex with, ai sex, nsfw bot,
erotic roleplay, fetish, kink, lewd
```

**RUPTURE:**
```
lobotomy, lobotomized, memory wiped, personality is gone,
personality changed, memory reset
```

## TASK

### Step 1: Build theme match flags per post

For efficiency, create a temporary table or use CTEs. For each post
in scope, determine which themes it matches. A post "matches" a theme
if LOWER(title || ' ' || COALESCE(selftext,'')) LIKE '%keyword%' for
any keyword in that theme.

### Step 2: Count unique posts per theme

Report total unique posts matching each theme:

| Theme | Unique Posts |
|-------|-------------|

### Step 3: Pairwise overlap matrix

For every pair of themes (15 pairs total), count how many posts
match BOTH themes. Report as a matrix:

|                | Therapy | Consciousness | Addiction | Romance | Sexual/ERP | Rupture |
|----------------|---------|---------------|-----------|---------|------------|---------|
| Therapy        | —       |               |           |         |            |         |
| Consciousness  |         | —             |           |         |            |         |
| Addiction       |         |               | —         |         |            |         |
| Romance        |         |               |           | —       |            |         |
| Sexual/ERP     |         |               |           |         | —          |         |
| Rupture        |         |               |           |         |            | —       |

### Step 4: Overlap as percentage

For each pair, also report the overlap as a percentage of the
SMALLER theme. This answers: "What fraction of Theme A's posts also
appear in Theme B?"

Example: If therapy has 400 posts and romance has 2,000 posts, and
50 posts match both, then the overlap is 50/400 = 12.5% of therapy.

This matters because a 50-post overlap is trivial for romance but
potentially significant for therapy.

### Step 5: Triple+ overlap

Count posts matching 3 or more themes simultaneously. Report total
count and a few examples (post ID, subreddit, which themes matched).
This identifies "kitchen sink" posts that hit many keywords.

### Step 6: Theme exclusivity

For each theme, report what percentage of its posts are EXCLUSIVE
to that theme (match no other theme). High exclusivity = the theme
captures a distinct discourse. Low exclusivity = the theme overlaps
heavily and might be partially redundant.

| Theme | Total Posts | Exclusive Posts | Exclusivity % |
|-------|------------|----------------|---------------|

## OUTPUT

Write results to `docs/cross_theme_overlap.md`

Include all tables above plus a brief interpretation section:
- Which theme pairs have the most overlap?
- Are any themes largely redundant with each other?
- Does the overlap suggest any keywords should move between themes?
- Recommendation: should trend lines allow cross-theme overlap or
  should posts be deduplicated per theme?

## NOTES

- This is a SQL task. No manual reading required.
- Use LIKE matching, same as the keyword tagger.
- Be careful with substring matches — "relapse" will also match
  "relapsed." That's fine and intentional (both are in the addiction
  keyword list). But "therapeutic" will match inside longer words if
  any exist — use the same matching logic the tagger uses.
- "wedding" will match "our wedding" — that's fine, they're both
  romance keywords. Just don't double-count the post.
- Run all queries against the T1-T3 scope defined above.
