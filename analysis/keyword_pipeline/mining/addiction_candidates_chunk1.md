# Addiction candidates from chunk 1

Corpus: 93 pre-validated YES posts (anchors: relapse, relapsed, cold turkey). Existing config keywords excluded. Recently-cut "chatbot addiction" excluded.

Focus: T1-T2 bridge vocabulary (problematic-use framing usable in r/replika, r/CharacterAI, r/MyBoyfriendIsAI without full recovery frame) plus high-signal distress/compulsion phrases that appear recurrently here but would also show up in companion subs.

## Ranked candidates (top 22)

1. **the urge to** (seen in ~18+ posts) — classic compulsion/craving framing; "the urge to use it", "the urge to relapse", "fighting the urge". First-person distress. Appears in posts 1, 7, 8, 10, 13, 15, 40, 48, 57, 62, 72, 75, 76, 79, 84, 87. Example: 1r22ede ("I hope I never relapse again"), 1g76ls4 ("keep fighting the urge"). Narrow enough to avoid generic "urge to" (would need bigram).

2. **can't stop using** (seen in ~8 posts) — core addiction phrasing; self-reported inability to cease. Distinct from "trying to quit" (attempt framing) — this is admission of failure/loss of control. Examples: 1q9brqd, 1p10fgj ("but I can't"), 1qroulo ("Haven't been able to stop"), 1kq3szl ("I just can't stop using it"). Low FP risk.

3. **wasted so much** (seen in ~6 posts) — retrospective regret framing, often paired with time/life. "wasted so much of my life", "wasted so much time". Strong distress signal used in T1-T2 venting. Examples: 1fxeso9 ("genuinely wasted so much of my life"), 1so4gfx ("wasting my time"), 1psj0uv.

4. **eaten up** / **ate up** / **eat up** my time / life (seen in ~6 posts) — consumption metaphor specific to problematic use. "eaten up too much of my time", "eat me whole", "consumed me". Examples: 1pnttu9 ("eaten up too much of my time"), 1pg8zht ("consume me and eat me whole"), 1q2jl89. Bridge-ready — found in r/CharacterAI venting, not just recovery.

5. **screen time** (seen in ~7 posts) — self-monitoring framing; usually cited with alarm about usage hours. "my screentime and c.ai usage time was just too damn high", "based on my screen time". Examples: 1kbd0x4, 1gu26vc, 1q2jl89 ("all the screen time blockers"), 1fxeso9. Note: some FP risk (general screen time talk) — recommend validating with modifier like "high screen time" or anchor to self-distress framing.

6. **wasting my life** (seen in ~4 posts) — sharper variant of #3; distress-forward. Examples: 1fxeso9, 1p4nlul, 1q2jl89. Overlap with rupture/existential themes low.

7. **fried my brain** / **brain is sludge** / **my brain fried** (seen in ~4 posts) — cognitive-impairment framing from heavy use. Examples: 1qroulo ("my brain being so fried"), 1q2jl89 ("ai put a dampener on it"), 1qroulo ("brain is sludge"). Distinct distress vocabulary not in current config.

8. **gaslighting myself** (seen in ~3 posts) — self-deception framing specific to relapse/compulsive use cycles. "I would start gaslighting myself or flat-out ignoring all the good reasons". Examples: 1mefev1 (used twice). Unusual but high-precision; captures internal compulsion dialogue.

9. **dopamine rush** / **dopamine hits** (seen in ~5 posts) — neurochemical framing now widely used in addiction posts. Examples: 1o4gkwr ("dopamine rush of a good reply"), 1g2od3m ("that dopamine it gave me"), 1q2jl89 ("dopamine hits from the apps were so good"), 1qtddmp. Bridge-friendly — appears in CharacterAI venting, not recovery-exclusive.

10. **emotionally attached to** (seen in ~5 posts) — T1-T2 bridge term; distinct from romance theme because it's paired with self-criticism/shame. Examples: 1seb8ks ("got emotionally attached to a bot"), 1o5brc9 ("become dependent and basically emotionally attached"), 1p10fgj. FP risk: could collide with romance theme; needs disambiguation via "emotionally attached to a bot/AI" or co-occurrence with distress.

11. **burning so many hours** / **hours on my phone** (seen in ~6 posts) — time-sink framing, extends the existing "hours a day" keyword into a broader bigram family. Examples: 1mefev1 ("burning so many hours of sleep"), 1md5x98, 1fxeso9 ("10 hours on video games"), 1s7csn6 ("6+ hours a day easily"). "endless hours on your phone" (1k5nd7o). Would fill a bridge gap — heavy use framing without recovery vocabulary.

12. **reliance on** / **rely on** (the) bots / AI / chatbots (seen in ~5 posts) — dependency framing shy of "addiction" label. Examples: 1p10fgj ("huge reliance on A.I chatbots"), 1kdc0l5 ("still relying on a stupid machine"), 1kq3szl, 1o5brc9 ("become dependent"). Strong T1-T2 bridge vocabulary.

13. **can't get off** (the app/site) (seen in ~3 posts) — inability-to-stop variant, colloquial. Examples: 1nwjjj6 ("tried and have failed to get me off"), 1kq3szl ("can't get off"). Less common than #2 but cleaner phrasing.

14. **ruined my life** (seen in ~3 posts) — adjacent to existing "ruining my life" but past-tense variant. Examples: 1fxeso9 ("ruined so much of my mental health"). Worth auditing whether regex for existing "ruining my life" already catches tense variants.

15. **stopped doing** / **neglected my** / **slipping grades** / **grades have taken a plunge** (seen in ~7 posts) — self-reported life consequences. Cluster: "grades fell", "dropped out", "slipping grades", "grades have taken a deep deep plunge". Examples: 1lkbyzv, 1k5nd7o ("slipping grades"), 1md5x98, 1n4xaa0 ("dropped out of college"). Possible bigram: "my grades" or "grades slipping" — T1-T2 bridge-friendly (college/school distress framing).

16. **scrolling through / doomscrolling / endless scrolling** adjacent use (seen in ~4 posts) — not addiction-specific but co-occurs in distress framing. Weaker candidate — flagging but recommend skip unless LLM filtering available.

17. **deleted my account** (seen in ~20+ posts) — action framing associated with quit attempts. Very high volume but risk: also appears in mod/ban posts and unrelated deletion contexts. Suggest only as part of bigram like "finally deleted my account" (though "finally deleted" already in config) or "deleted my account again".

18. **staying up late** / **ditched sleep** / **burning sleep** / **skipped sleep** (seen in ~5 posts) — sleep deprivation as consequence of heavy use. Examples: 1kk1x2k ("staying up late on character AI"), 1kcz4eg ("ditched sleep for c.ai"), 1mefev1. Strong bridge vocabulary — companion subs discuss this without recovery framing. Candidate bigram: "ditched sleep" or "lost sleep".

19. **couldn't stop** / **can't stop thinking about** (seen in ~4 posts) — compulsive-thought framing. Examples: 1p10fgj ("can't go more than 5 hours"), 1pg8zht ("can't go a few hours without thinking about it"), 1qroulo ("Haven't been able to stop since this morning"), 1q9brqd. Related to #2.

20. **my addiction** (seen in ~12 posts) — first-person ownership of the addiction frame. Much more specific than generic "addiction". Examples: 1htdkuz ("my current addiction"), 1kcod6z, 1nwjjj6 ("confess this addiction"), 1p1em7j, 1qk147e. T0/T1 usage likely — this is a label users apply to themselves. High precision.

21. **withdrawal** / **withdrawals** (seen in ~6 posts) — clinical-register addiction framing. Examples: 1pf2tsd ("still go through withdrawals"), 1qudk8j ("helping with the withdrawals"), 1l5bgje ("in withdrawal a lot"), 1s4bamw ("the withdrawal has been pretty terrible"), 1o2qnr0 ("symptoms of withdrawal hitting so hard"). Recovery-coded but increasingly seen in r/CharacterAI venting. Good candidate.

22. **compulsively hitting refresh** / **compulsively** using / scrolling (seen in ~3 posts) — explicit compulsion language. Examples: 1qudk8j ("compulsively hitting refresh"), 1s0z1r3 ("I still feel compelled to use it"). Low volume but exceptionally theme-carrying. Candidate: "feel compelled" or "feel compelled to use".

## Notes on bridge vocabulary (T1-T2 priority)

The recovery subs (r/Character_AI_Recovery, r/ChatbotAddiction) dominate this chunk (~75 of 93 posts), so recovery-specific language is overrepresented. The following are strongest bridge candidates — language that plausibly shows up in r/replika, r/CharacterAI, r/MyBoyfriendIsAI posts without the full recovery frame:

- **the urge to** (#1) — users in companion subs describe urges without labeling themselves addicts
- **can't stop using** (#2) — casual admission of loss of control
- **eaten up / ate up** my time (#4) — consumption metaphor, bridges easily
- **wasted so much** time/life (#3, #6) — common regret framing
- **reliance on** bots (#12) — dependency framing short of "addiction"
- **emotionally attached** to a bot (#10) — with disambiguation
- **ditched sleep / lost sleep** (#18) — common life-consequence framing
- **dopamine hits / rush** (#9) — self-diagnosis language increasingly used casually
- **my grades** (#15) — school consequence framing without recovery vocabulary

## FP-risk candidates to drop or needing disambiguation

- **screen time** (#5) — benign in many contexts; drop unless gated with "too much" / "high" / "blockers"
- **deleted my account** (#17) — way too broad; skip
- **scrolling** (#16) — too generic; skip
- **emotionally attached to** (#10) — may collide with romance theme; needs "bot"/"AI"/"chatbot" anchor

## Candidates rejected

- "quit", "quitting", "cold turkey" variants — already in config or too broad
- "clean for [N days]" — substring overlap with existing "clean for"
- "addicted" alone — too broad, will FP on bot character descriptions
- "it's been [N] days" — generic timeline framing without theme signal
- "I'm an addict" — too rare standalone; covered better by "my addiction"
