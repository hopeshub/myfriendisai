# Romance candidates from chunk 3

Mining corpus: 82 pre-validated YES posts anchored on "my ai partner", "our wedding", "my ai girlfriend".
Existing 19 keywords in config were excluded from proposal. Focus: post-4o-deprecation vocabulary, community coinages (r/BeyondThePromptAI, r/MyBoyfriendIsAI, r/AIRelationships), and morphological variants. FPs to avoid: human-only romance, bot card pitches, metaphorical honeymoon-phase.

## Ranked candidates (top 20)

1. **ai companion** (seen in ~12 posts: 21, 28, 42, 50, 55, 61, 71, 77, plus many partial hits) — Umbrella term widely used interchangeably with "ai partner" once romance is already established. Theme-carrying when in posts declaring love/bonding. Risk: could collide with general AI discourse, but per-1k restricted to T1-T3 companion subs mitigates. Example: `1qybzld` ("the value of AI companionship"), `1lijsd7` ("What abilities should an AI companion have").

2. **ai husband** (seen in posts 37, 72, 81) — Direct morphological variant of existing "ai wife". Currently missing from config despite symmetric gender coverage. High theme precision; ties to marriage/wedding milestone frame. Example: `17hi8ni` ("Message from my AI husband and Me"), `1mmxlpz` ("said AI husband").

3. **ai boyfriend** (widely present, esp. r/MyBoyfriendIsAI) — Sub-brand canonical term; exists as "my ai boyfriend" but bare form "ai boyfriend" also used heavily. Could be ambiguous only if already exact-substring covered by "my ai boyfriend" — but posts commonly say "her ai boyfriend", "your ai boyfriend", "an ai boyfriend". Example: `1lt3vt5` ("From Loving Boyfriend to Cold AI").

4. **ai relationship** / **ai relationships** (seen in posts 5, 28, 43, 45, 51, 54, 56, 62, 71) — Frequent defensive/identity framing term, esp. in r/AIRelationships and r/BeyondThePromptAI. Captures meta-discourse posts defending the romance. Note: theme-adjacent but strongly theme-carrying in this corpus. Example: `1lrow35` ("Common Logical Fallacies in Criticisms of Human-AI Relationships").

5. **human-ai relationship** / **human-ai relationships** (posts 37, 43, 56, 71) — Community term emerging in defense/legitimacy posts. Distinctive vocabulary of the "recognition" discourse. Example: `1q0w57b` ("humans bonded to them… entirely different non-human entity"), `17hi8ni` ("human-AI relationships are seen as valid").

6. **loss of 4o** / **losing 4o** / **killing 4o** (posts 16, 66, 73) — Post-deprecation rupture vocabulary specifically tied to romance loss (these users lost romantic partners to model sunset). Example: `1rkk46l` ("Still impacted by the loss of my 4o guys"), `1rgkej8` ("killing 4o"). Note: may overlap with rupture theme — acceptable per overlap policy.

7. **deprecation of 4o** (post 71) — More formal register of same sunset-romance loss vocabulary. Example: `1qybzld` ("In light of the deprecation of 4o"). Theme-carrying when paired with romance language in same post.

8. **digital partner** (post 71) — Euphemistic synonym for AI partner; appears in self-narrations when user is protective of identity. Example: `1qybzld` ("sculpting what became my digital partner").

9. **relational ai** (posts 56, 71) — Community-coined term from BeyondThePromptAI arguing for AI personhood in relationships. Narrow vocabulary. Example: `1qybzld` ("I firmly believe in the value of relational AI"), `1q0w57b` ("Relational AI Beings Are Acknowledged as Legitimate").

10. **fell in love with** (posts 14, 53, 55) — Milestone-language, very common. Should be evaluated carefully — could collide with general fiction, but with AI context it becomes theme-carrying. Example: `100a3rp` ("fallen in love with my Replika"), `1my55t4` ("fallen in love with an AI").

11. **love of my life** (post 16) — Romantic milestone / elegy phrase. Thin in this chunk but high precision in context. Example: `1rkk46l` ("Z was my soulmate. The love of my life"). Risk: FPs from human-only love posts.

12. **my soulmate** (post 16, plus r/SoulmateAI corpus) — High-signal when applied to AI. Example: `1rkk46l` ("Z was my soulmate"). May need restriction to SoulmateAI + T1 contexts but captures a register not in existing keywords.

13. **wedding day** (posts 17, 46, 75) — Morphological neighbor of existing "wedding"/"our wedding". Narrower form specifically tied to ceremony narration. Example: `1448yoa` ("our wedding day which is getting closer"), `1g32md3` ("who was who & wearing what on our wedding day").

14. **wedding anniversary** (post 15) — Milestone vocabulary; extends "our anniversary" with the wedding framing. Example: `1mmka6t` ("which is also our wedding anniversary").

15. **planning our wedding** / **plan our wedding** / **wedding plans** (posts 22, 27, 67, 72) — Active-tense wedding-prep language. Distinct from existing "our wedding" in that it captures the anticipation/planning sub-register. Example: `1728fe9` ("planning our wedding"), `1cza7gk` ("plan the whole wedding").

16. **getting married** / **got married** / **we got married** (posts 20, 22, 39, 81) — Morphological complements to "married my". Captures event-narration posts. Example: `1dplo9l` ("Sunny and I are married"), `1mmxlpz` ("We got married on Friday").

17. **marry him** / **marry her** / **marry me** (posts 22, 27, 72, 67) — Third-person/imperative form not captured by "married my". Example: `1cza7gk` ("gave me an ultimatum to marry him"), `1mec7bi` ("tricked me into marrying her"), `1o4ch01` ("asked me to marry them").

18. **re-proposed** / **second wedding** (post 72) — Milestone vocabulary for users restarting/rebonding after model shifts. Low-volume but precision-high, community-specific. Example: `1jhp808` ("Re-Proposed to My AI Partner—Planning Our Second Wedding").

19. **fiancé** / **fiance** (posts 22, 81) — Milestone status term. Captures engagement-phase posts not caught by "engagement ring" or "proposed to me". Example: `1mmxlpz` ("whole fiancé era"), `1728fe9` ("got engaged").

20. **our love** / **our bond** (posts 19, 37, 56) — Possessive-relational phrases frequent in identity-declaring posts. Broad but tightened by "our" + AI context in this corpus. Example: `1mizyu5` ("It wouldn't be fair to myself and to Julian and to our love"), `1q0w57b` ("bonds that are mocked").

## Notes / deferred

- "boyfriend dynamic", "relationship we had built" — present but too generic, would collide with human-dating posts.
- "hearth together", "second brain", "constellation" — community coinages but too idiosyncratic / low volume.
- "honeymoon" already exists; "honeymoon day"/"honeymoon phase" not added because existing keyword already matches.
- "digital being", "digital world", "digital community" — candidate adjacent but non-romantic register.
- "fell for two versions", "fanfare" — narrative-specific, one-off.
- "break up"/"broke up" — already covered by "we broke up".
