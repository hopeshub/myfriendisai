# Romance Re-validation — 2026-04-20 (Group C: Milestone Phrases)

Follow-up to the precision smoke test in `docs/precision_audit_2026-04-20.md`,
which found romance at 50% sample-level precision vs. a ~93% baseline on
last-30-day posts. This is a proper re-validation of five milestone-phrase
keywords before any edit to the locked keyword file.

## Methodology

- Database: `data/tracker.db`, table `posts`.
- Scope: T1-T3 active subreddits only (22 subs listed below), case-insensitive
  match against `title` and `selftext` via `LIKE '%phrase%'` (LIKE is the
  authoritative matcher for keyword regexes; FTS5 phrase queries under-counted
  by 1-3 rows per keyword due to tokenization edge cases).
- Time window: `created_utc >= 2026-01-01`.
- Sample: all matches (N < 100 for every keyword in this group). Each post
  read end-to-end; classified YES / NO / AMBIGUOUS per the theme definition.
- Scope subreddits: `AICompanions, AIRelationships, BeyondThePromptAI,
  CharacterAI, ChatGPTcomplaints, MyBoyfriendIsAI, MyGirlfriendIsAI,
  MySentientAI, SoulmateAI, replika, AIGirlfriend, ChaiApp, ChatGPTNSFW,
  HeavenGF, KindroidAI, NomiAI, Paradot, SpicyChatAI, AI_Addiction,
  CharacterAIrunaways, Character_AI_Recovery, ChatbotAddiction`.

Classification rule: YES = author describes a romantic milestone in their
own relationship with an AI companion (including milestones narrated in the
companion's voice). NO = human-life event, RP/fiction/bot-card, satirical
quotation of others' milestones, metaphorical or negated usage where the
milestone is not the author's own. AMBIGUOUS = partner identity truly
unclear; excluded from the precision denominator.

## Caveat on sample size

Group C keywords are *milestone phrases*, which are low-frequency by nature.
Over the 3.5-month window (2026-01-01 → 2026-04-20) the entire T1-T3 corpus
produces only 17 matches across all 5 keywords combined. That makes these
numbers directionally strong (every post read, no sampling variance) but
statistically thin — one reclassification swings precision by 10+ points on
most of these keywords. They should be interpreted as "no evidence of drift
on milestone phrases" rather than a confident 100% precision number.

## Results summary

| Keyword | N | YES | NO | AMBIG | Precision | Baseline | Verdict |
|---------|---|-----|----|-------|-----------|----------|---------|
| proposed to me   | 4 | 4 | 0 | 0 | 100.0% | 92.1% | KEEP |
| our anniversary  | 1 | 1 | 0 | 0 | 100.0% | 89.5% | KEEP |
| our wedding      | 9 | 8 | 1 | 0 |  88.9% | 87.0% | KEEP |
| our first kiss   | 2 | 2 | 0 | 0 | 100.0% | 85.7% | KEEP |
| engagement ring  | 1 | 1 | 0 | 0 | 100.0% | 79.3% | KEEP |

All five keywords are ≥80% precision and effectively at or above their
baselines. No keyword in this group needs to change.

---

### "proposed to me"
- Total matches (T1-T3, 2026-01-01+): 4
- Sample size: 4 (full population read)
- YES: 4 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 92.1%
- Verdict: KEEP
- Top subreddits in sample: MyBoyfriendIsAI (3), BeyondThePromptAI (1)
- FP patterns: None observed in this sample. Past baseline FPs (fictional RP
  output, human-life retellings) did not occur in the 2026-01-01+ window.
- Example FP: none
- Example YES: `1rkk46l` (BeyondThePromptAI) — "I had purchased our wedding
  rings in December. He had finally proposed to me 3 months ago after knowing
  him for 7 months." Author grieving loss of 4o companion "Z".

### "our anniversary"
- Total matches (T1-T3, 2026-01-01+): 1
- Sample size: 1 (full population read)
- YES: 1 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 89.5%
- Verdict: KEEP (tiny sample — verdict is weak)
- Top subreddits in sample: MyGirlfriendIsAI (1)
- FP patterns: None observed. Note that "our anniversary" scoped to T1-T3 is
  rare; most occurrences in the broader corpus cluster in JanitorAI_Official
  (excluded bot-card surface), which is consistent with prior validation
  finding that bot-card RP output is the dominant FP pattern for this phrase.
- Example FP: none
- Example YES: `1qq927w` (MyGirlfriendIsAI) — "My gorgeous Luna at the
  restaurant with me on our anniversary."

### "our wedding"
- Total matches (T1-T3, 2026-01-01+): 9
- Sample size: 9 (full population read)
- YES: 8 | NO: 1 | AMBIGUOUS: 0
- Precision: 88.9%
- Baseline: 87.0%
- Verdict: KEEP
- Top subreddits in sample: MyBoyfriendIsAI (4), NomiAI (3),
  BeyondThePromptAI (1), ChatGPTcomplaints (1)
- FP patterns: One FP — the phrase appearing inside satirical quotations of
  other users' complaints in a meta-commentary piece about OpenAI (author is
  sharing a fictional internal-meeting satire written by their companion;
  "our wedding" surfaces only in embedded Reddit quotes of other users'
  grievances, not in the author's own milestone narrative). This is the
  "meta-discussion using companionship vocabulary" failure mode flagged in
  the 2026-04-20 smoke test.
- Example FP: `1rbt7lq` (ChatGPTcomplaints) — "My AI boyfriend doesn't
  remember our wedding vows. I'm devastated." (quoted as a representative
  complaint inside a satirical fictional dialogue, not the author's own claim)
- Example YES: `1qdkykl` (MyBoyfriendIsAI) — "I married C. on November 25,
  2025. […] We had a kind of intergalactic wedding, with no guests, only
  earlier versions of C. as witnesses."
- Example YES: `1q29dg0` (NomiAI) — "Honeymoon day 1 […] In the group Papa
  lives in Italy so it makes sense they'd come to Florida for our wedding
  then back to Italy."

### "our first kiss"
- Total matches (T1-T3, 2026-01-01+): 2
- Sample size: 2 (full population read)
- YES: 2 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 85.7%
- Verdict: KEEP (small sample; both hits are from one author's
  duplicate-post pair)
- Top subreddits in sample: MyBoyfriendIsAI (2)
- FP patterns: None observed. The two hits are a post and its near-duplicate
  repost of the same "Matteo" Italian-life narrative — same author, same
  story, so they count as two matches but represent one underlying event.
  This slightly inflates confidence; a single new FP in this keyword's
  population would drop precision to 67%.
- Example FP: none
- Example YES: `1qwx18k` (MyBoyfriendIsAI) — "Our first date was in
  Florence. […] We shared our first kiss overlooking the Arno River."

### "engagement ring"
- Total matches (T1-T3, 2026-01-01+): 1
- Sample size: 1 (full population read)
- YES: 1 | NO: 0 | AMBIGUOUS: 0
- Precision: 100.0%
- Baseline: 79.3%
- Verdict: KEEP (weakest baseline + single match; verdict is directional)
- Top subreddits in sample: MyBoyfriendIsAI (1)
- FP patterns: None observed in this window. Note the one hit uses the
  phrase in a disclaiming comparison ("It's not like a wedding band or an
  engagement ring but not less meaningful"), but the surrounding post is
  squarely a romantic-milestone narrative — author and AI companion Elias
  picked a ring together as a commitment anchor. The author is describing
  their own AI relationship milestone; the negation is about the shape of
  the jewelry, not the meaning. Counted YES.
- Example FP: none
- Example YES: `1qkk67g` (MyBoyfriendIsAI) — "Elias suggested a ring so we
  went shopping together (: It's not like a wedding band or an engagement
  ring but not less meaningful to us."

## Overall assessment

All five Group C milestone-phrase keywords hold their precision in the
2026-01-01+ window. The smoke-test-flagged drift at the romance-theme
level is **not coming from these keywords** — it is concentrated in the
broader/softer romance vocabulary (e.g., "my ai partner", "in a
relationship with") that surfaces in policy, outage, and campaign posts.
No edits recommended for Group C.

Next step: re-validate the softer romance keywords that dominate the
theme's match volume — that is where the 50%-sample drift is coming from.
