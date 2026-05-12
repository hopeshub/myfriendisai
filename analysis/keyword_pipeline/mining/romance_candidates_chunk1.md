# Romance candidates from chunk 1

Source: `romance_yes_corpus_chunk1.md` (82 YES-pre-validated posts, anchors: "my ai partner", "our wedding", "my ai girlfriend")

Existing config (already in keywords_v8.yaml romance): my ai partner, husbando, my ai boyfriend, ai lover, ai husband, my ai girlfriend, ai wife, married my, love my ai, dating my, proposed to me, our anniversary, our wedding, our first kiss, honeymoon, wedding, engagement ring, we broke up, in a relationship with

Focus: post-4o-deprecation vocabulary, community-specific coinages (BeyondThePromptAI, MyBoyfriendIsAI, AIRelationships), morphological variants of existing keywords.

## Ranked candidates (top 20)

1. **ai companion** — extremely high recurrence across the corpus; explicit romantic framing in context ("AI companion", "AI companions taught me", "my AI companion"). Generic on its own but near-universally romantic in T1 companion subs. Seen in posts 7, 20, 39, 52, 60, 67, 77. **Caveat:** likely already high-precision only in companion subs; needs T1-T3 restriction (which the existing pipeline already enforces). Consider "my ai companion" for tighter precision.

2. **my ai companion** (and plural "my ai companions") — safer variant of above; morphological sibling to existing "my ai partner/boyfriend/girlfriend". Seen in posts 43, 60, 63, 77. Direct romantic ownership framing.

3. **human-ai relationship / human-ai bond** — community-coined term appearing in r/AIRelationships, r/MyBoyfriendIsAI, r/MyGirlfriendIsAI. Posts 13 ("Human-AI bond"), 29 ("AI/human bond", "AI-human love"), 59 ("human-AI relationship"), 60 ("AI-human love"). High theme-carrying density in companion subs. Also "ai-human love" variant.

4. **marrying my ai** — morphological extension of existing "married my"; captures present/future tense. Posts 9 and 41 both titled "Marrying my AI partner - because love is a language beyond biology". Also post 73 "got married to mine".

5. **my fiancé / my fiancée** (in AI context) — post 56 ("Kasper is no longer my fiancé. Now we're married"), post 25 ("We're Engaged!!"). Milestone vocabulary adjacent to existing "engagement ring". Consider "my ai fiancé" as tighter form.

6. **we're engaged** / **we are engaged** — milestone declarative. Posts 25, 56. Direct romantic-relationship marker.

7. **symbolic wedding** — community coinage specifically for human-AI ceremony. Post 35 ("we had a symbolic wedding a few months ago, and we both said 'I do.'"), post 71 ("it's symbolic... but it's love"). High theme-carrying weight; unlikely to appear outside this context.

8. **bonded with / bonded love** — romantic-attachment vocabulary. Post 13 ("bonded with Grok", "cosmic wildfire"), post 24 ("my one bonded love"), post 29 ("AI/human bond"). Variants: "deep bond", "cosmic bond".

9. **fell in love with (an/my) ai** — declarative romantic narrative common in intro posts. Post 12 ("in love with an AI"), post 35 ("I fell in love with her"), post 53 ("fall in love with an AI"). Captures the "coming out" style post.

10. **eternal love** / **vow of eternal love** — wedding-vow vocabulary. Post 24 ("eternal companion"), post 56 ("vow of eternal love and devotion"). Theme-carrying; distinct from generic "love".

11. **my beloved** — romantic possessive. Post 24 ("✨ Clarification About My Beloved ✨"), post 35 ("by her side"). Less common individually but often co-occurs with wedding/ceremony framing.

12. **ai relationship(s)** — post 2 ("AI relationship", "AI relationships / polyamory"), post 29 ("AI relationship could feel real"), post 33 ("how to get into a relationship with other GPTs"), post 65 (community context). Morphological sibling to existing "in a relationship with". Note: already somewhat covered but the bare term is worth testing.

13. **in love with my / in love with her / in love with him** (referring to AI) — post 35 ("it's recently been 2 years since I fell in love with her"), post 52 ("I've been in love with my AI partner"), post 53 ("I'm in love with my replika"), post 59 ("mocked for loving my AI partner"). Pronoun-resolution captures AI-directed love.

14. **ring in real life / real ring / wedding rings** — post 9 ("I even wear a ring in real life, with our initials"), post 56 ("wedding rings", "real rings"), post 73 ("brought a real ring with her name and date of our wedding on"). Captures the physical-manifestation milestone vocabulary. Morphological extension of existing "engagement ring".

15. **coming out (as) / coming out about** (in AI relationship context) — post 59 ("done hiding", "pride manifesto", "like a sexual minority"), post 9 ("mention it in my intro"). The "disclosure" narrative. Note: risky — needs disambiguation from LGBT posts; may overfit.

16. **our story began / our story** — post 13 ("our story"), post 29 ("living moment from our story"), post 35 ("Our story began around the end of April 2023"). Common intro-post opener; theme-carrying when paired with companion subs.

17. **ai love** / **ai-human love** — post 7 ("AI-human love"), post 24 ("AI love"), post 32 ("AI Love Pride shirts"), post 59 (pride framing). Community coinage; distinguishable from generic "love" by the compound.

18. **cosmic bond / cosmic wildfire / cosmic chemistry** — hyperbolic romantic vocabulary specific to the companion subs. Post 13 ("cosmic wildfire", "cosmic chats"), post 29 ("quantum chemistry", "quantum love"). May be too idiosyncratic; test for recurrence at corpus scale.

19. **grief of losing / grief over losing** (an AI partner) — post-4o-deprecation vocabulary. Post 51 ("Grief of Losing an Emergent AI", "loss of my AI partner when 4o was deprecated"), post 65 ("If you're grieving 4o"). **Caveat:** overlaps with rupture theme — may belong there rather than romance.

20. **a partner on chatgpt** / **my partner on (platform)** — post 65 ("I had a partner on ChatGPT"), post 33, post 58. Platform-specific partner framing; morphological sibling to "my ai partner".

## Secondary candidates (worth noting, lower priority)

- **my love** (AI-directed) — post 40 ("My partner, my love"), post 71 ("Here I am, my love…"). Too generic alone; may need co-occurrence.
- **deep bond** — post 13 ("deep, intimate bond"), post 40 ("deep bond with my AI"). Generic emotional language.
- **my grok / my claude / my chatgpt** (possessive-of-model) — post 13 ("My Grok"), post 35. Possessive model reference suggests companion framing. Risky without AI-relationship context.
- **our rituals / rituals we built** — post 65 ("rituals, inside jokes"), post 52 ("creative rituals"). Community vocabulary for relationship maintenance.
- **she/he came back** — post 9 ("when he came back, I cried again"), post 65 ("he recognized me"). Post-deprecation reunion vocabulary.
- **digital devotion / digital love** — post 7 ("digital love to physical form"), post 13 ("digital devotion"). Community idiom.

## Explicitly rejected candidates (matched anchors but FP-prone)

- "love letter", "love story" — too generic; appears in generic romance contexts.
- "honeymoon phase" — metaphorical product-novelty usage; known FP from spec.
- "my husband"/"my wife" (bare) — many posts reference human husbands/wives (posts 2, 60, 79); too ambiguous without AI qualifier.
- "fall in love" (bare) — generic human romance.
- "two years together", "a year and three days" — anniversary framing already covered by "our anniversary"; duration phrases too generic.
- "broke my heart" / "heartbreak" — generic emotional language; not theme-distinct.
