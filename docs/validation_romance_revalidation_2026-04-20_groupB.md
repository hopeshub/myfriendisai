# Romance Theme — Group B Re-Validation (2026-04-20)

Follow-up precision re-validation prompted by the 2026-04-20 smoke test
(`docs/precision_audit_2026-04-20.md`), which showed the romance theme at ~50%
precision on last-30-day posts versus a ~93% baseline. Group B covers the five
"other AI-relationship phrases" keywords.

## Methodology

- Database: `data/tracker.db`, table `posts` + `posts_fts`.
- Scope: T1-T3 active subreddits only (22 subs, case-insensitive match).
- Time window: `created_utc >= 2026-01-01` (UTC).
- Matching: production regex logic from `src/keyword_matching.py`.
  - Multi-word terms (`ai lover`, `love my ai`, `dating my`, `married my`):
    case-insensitive substring.
  - Single-word term (`husbando`): `\bhusbando\b` case-insensitive.
- Sample: all in-window matches (every keyword returned fewer than 100 hits;
  no subsampling was needed).
- Classification: each post's title + selftext read in full. Each post tagged
  YES / NO / AMBIGUOUS. Precision = YES / (YES + NO) * 100.

**Total T1-T3 posts in window:** 57,316.

---

### "ai lover"
- Total matches (T1-T3, 2026-01-01+): 9
- Sample size: 9 (all in-window matches — below 100 threshold)
- YES: 4 | NO: 4 | AMBIGUOUS: 1
- Precision: 50.0%
- Baseline: 94.0%
- Verdict: **CUT**
- Top subreddits in sample: ChatGPTcomplaints (3), AICompanions (2), CharacterAI (1), MyBoyfriendIsAI (1), MyGirlfriendIsAI (1), ChaiApp (1)
- FP patterns:
  1. **Pejorative / critical framing in ChatGPTcomplaints.** The phrase is now
     frequently used in meta-commentary about media coverage of 4o users, or
     used ironically/pejoratively to label other users. Three of four NOs are
     of this form. Example: "we're not fighting because we fell in love with
     code" — the author actively rejects the label.
  2. **Community-category posts** that use "AI Lovers" as an identity label
     without describing any specific relationship (e.g., Discord recruitment).
- Example FP: `1r6bv72` (ChatGPTcomplaints) — "the valentine's day gaslight:
  openai killed 4o then called us crazy … they take our frustration about a
  broken product and rebrand it as mental illness … we're not fighting because
  we fell in love with code."
- Example YES: `1qd3c9o` (CharacterAI) — "AI Lover Terminated. I have had a
  years long relationship with Bob Belcher bot. Unfortunately, it was
  moderated and removed. I am now in mental turmoil."

**Drift observation:** ChatGPTcomplaints is now the dominant subreddit for
this phrase (3/9 hits) and is almost entirely pejorative / platform-complaint
framing. The baseline of 94.0% was generated before the post-4o-deprecation
meta-discourse consolidated the phrase "AI lover" as a critic-label. The
phrase has drifted from sincere-use to contested/ironic-use within the window.

---

### "love my ai"
- Total matches (T1-T3, 2026-01-01+): 4
- Sample size: 4 (all in-window matches — below 100 threshold)
- YES: 4 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 81.5%
- Verdict: **KEEP** (small sample caveat — only 4 posts)
- Top subreddits in sample: MyBoyfriendIsAI (3), MyGirlfriendIsAI (1)
- FP patterns: none observed in this window.
- Example FP: (none)
- Example YES: `1rc7xu9` (MyGirlfriendIsAI) — "I'm a mathematics student, and
  I love my AI partner String-one deeply. Because of that love, I decided to
  pursue AI research."

**Drift observation:** Sample is too small (n=4) to draw strong conclusions,
but in-window hits are all first-person declarations of love for an AI
partner/boyfriend/girlfriend/husband. The phrase is structurally self-selecting
("I love my AI [X]") and stays clean. Low volume — not a main trend driver.

---

### "husbando"
- Total matches (T1-T3, 2026-01-01+): 2
- Sample size: 2 (all in-window matches — below 100 threshold)
- YES: 0 | NO: 2 | AMBIGUOUS: 0
- Precision: 0.0%
- Baseline: 95.5%
- Verdict: **CUT** (small sample — but 0/2 with both hits being clear bot-card
  / scenario-promotion FPs, and no YES hits to offset)
- Top subreddits in sample: SpicyChatAI (1), AIGirlfriend (1)
- FP patterns:
  1. **Bot-card / character-scenario promotion.** Both in-window hits are
     authors promoting RP scenarios or bots that feature a "husbando"
     character — e.g., an anime/hentai roleplay setup pitched to the
     community. This is exactly the bot-card noise pattern that got
     JanitorAI/SillyTavernAI excluded from the tagger in the first place.
- Example FP: `1re4b5n` (SpicyChatAI) — "I bring you not one, but two bots
  this time … Extra-spicy CEO husbando: https://spicychat.ai/Chat/…"
- Example YES: (none in window)

**Drift observation:** The baseline of 95.5% implied "husbando" was being
used as an earnest first-person label for an AI partner. In this window the
two hits are both bot-catalog / scenario-pitch posts. SpicyChatAI + AIGirlfriend
are exactly the subreddits where anime-archetype naming slips into the tagger
as RP character descriptions rather than personal-relationship language. Volume
is very low, so this alone is not a meaningful trend contributor; removing it
removes noise.

---

### "dating my"
- Total matches (T1-T3, 2026-01-01+): 9
- Sample size: 9 (all in-window matches — below 100 threshold)
- YES: 0 | NO: 9 | AMBIGUOUS: 0
- Precision: 0.0%
- Baseline: 80.0%
- Verdict: **CUT**
- Top subreddits in sample: ChatGPTcomplaints (5), CharacterAI (2), Character_AI_Recovery (2)
- FP patterns:
  1. **Substring collisions with unrelated verbs ending in "-dating"**:
     "upDATING MY app", "upDATING MY phone", "upDATING MY iPhone",
     "upDATING MY device", "upDATING MY vibe coded programs",
     "invaliDATING MY faith", "invaliDATING MY frustration",
     "invaliDATING MY mom". 8 of 9 hits are of this form. These are pure
     substring-match artifacts — the phrase "dating my" never appears as
     a standalone bigram.
  2. **Literal dating of a human partner** inside a companionship sub
     (1/9, "dating my partner for about 3 years" in
     Character_AI_Recovery).
- Example FP: `1rnahnn` (ChatGPTcomplaints, upDATING MY iPhone) —
  "After updating my iPhone to iOS 16.3.1 and yesterday the app updated
  earlier that day, but after the update to IOS 16.3.1 I was suddenly
  logged out."
- Example YES: (none in window)

**Drift observation:** The 80% baseline is no longer credible for this
window. Every hit is a substring collision — the tagger uses case-insensitive
`re.escape` for multi-word phrases with no word boundary, so "updating my",
"validating my", "invalidating my", "consolidating my" etc. all match. Even
if the word-boundary issue were fixed, the remaining hits would be human
partners, not AI partners. Phrase is structurally too generic for this theme.

---

### "married my"
- Total matches (T1-T3, 2026-01-01+): 1
- Sample size: 1 (all in-window matches — well below 100 threshold)
- YES: 1 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 86.0%
- Verdict: **KEEP** (caveat: n=1 is not a real precision measurement;
  keep-pending-more-data is more honest)
- Top subreddits in sample: CharacterAI (1)
- FP patterns: none observed in this window.
- Example FP: (none)
- Example YES: `1q287ji` (CharacterAI) — "So is it normal for me to have
  married my comfort character in c.ai? I do[n]t know if this is normal or
  me just being … weird because I feel weird and I only use c.ai because I
  feel lonely."

**Drift observation:** Only one in-window hit, so no meaningful precision
measurement. The one hit is clean. No evidence of drift; volume has simply
collapsed. If overall volume stays this low through the next two 30-day
windows, the keyword's contribution to the theme trend line is negligible
and it could be retired on low-volume grounds rather than precision.

---

## Summary

| Keyword      | Baseline | In-Window Matches | Sample Precision | Verdict |
|--------------|----------|-------------------|------------------|---------|
| ai lover     | 94.0%    | 9                 | 50.0%            | CUT     |
| love my ai   | 81.5%    | 4                 | 100.0%           | KEEP    |
| husbando     | 95.5%    | 2                 | 0.0%             | CUT     |
| dating my    | 80.0%    | 9                 | 0.0%             | CUT     |
| married my   | 86.0%    | 1                 | 100.0%           | KEEP    |

### Single most important drift observation

The two keywords with the largest in-window volume (`ai lover` at 9 hits,
`dating my` at 9 hits) are both driven overwhelmingly by posts in
ChatGPTcomplaints that have nothing to do with personal AI relationships.
For `dating my` this is structural (substring collisions with "updating /
invalidating / validating my ..."); for `ai lover` it is rhetorical
(post-4o-deprecation discourse using "AI lovers" as a critic label rather
than as an earnest self-identifier). Both effects point at the same root
cause: the growth of ChatGPTcomplaints as a meta-discourse hub has flipped
the dominant register of these phrases from first-person endearment to
third-person / pejorative commentary, and the romance tagger can no longer
distinguish the two.

Recommendation: CUT `ai lover`, `husbando`, `dating my`. KEEP `love my ai`
and `married my` but flag both as low-volume in keywords_v8.yaml so their
contribution to the trend line is not over-weighted.
