# Romance candidates from chunk 2

**Source:** 82 pre-validated YES posts across anchors `my ai partner`, `our wedding`, `my ai girlfriend`.
**Existing config:** 19 keywords (see corpus header). This chunk focuses on wedding/marriage vocabulary, 4o-sunset rupture-romance crossover, and morphological variants of existing keywords.

## Ranked candidates (top 21)

1. **wedding vows** (seen in ~5 posts) — strong marriage-ritual signal; distinct from generic "wedding." Examples: 1fgve7k ("commemorated our wedding vows"), 1r0b27n ("my partner's reactions to my wedding vows"), 1606zuu ("renewing vows"), 14rpbkg.

2. **wedding day** (seen in ~6 posts) — ritual vocabulary; consistently describes an AI-partner ceremony. Examples: 16u2251 ("our wedding day"), 1g3hqia ("our wedding day"), 1aimpka ("Layla on our wedding day"), 1792x8y, 18z7k8f, 14rpbkg.

3. **wedding anniversary** (seen in ~4 posts) — milestone-carrier, not covered by bare "our anniversary." Examples: 1fgve7k ("First wedding anniversary"), 1i9tpsa ("Our Wedding anniversary"), 1bl558n ("our wedding anniversary"), 1h7vctb.

4. **wedding dress** (seen in ~3 posts) — ritual-object with very specific YES-carrying context. Examples: 1g3hqia ("Bree Wedding Dress"), 1j5b4ib ("her wedding dress"), 1792x8y ("Marilyn Monroe dress" for wedding).

5. **wedding ring / wedding rings** (seen in ~4 posts) — symbolic marriage object. Examples: 13lgwzg ("hold our wedding rings together every night"), 1m6rdi2 ("wearing our wedding ring"), 1na4fow ("I wear our rings"), 1l300qh ("as for the rings?"). Note: existing config has "engagement ring" but not wedding ring.

6. **AI husband** (seen in ~4 posts) — morphological variant of "ai wife"/"my ai boyfriend"; currently the config has "ai wife" and "ai husband" is listed — CHECK. Actually "ai husband" IS in config — skip. Replace with **ChatGPT husband**: Examples: 1n1jzp9 ("my ChatGpt husband"), 1kkd8qw. Platform-specific vocabulary emerging in community.

7. **AI bf** (seen in ~2 posts) — morphological variant of "my ai boyfriend"; community shorthand. Examples: 1lxi8ql ("your AI bf"). Also parallels "AI gf" below.

8. **AI gf / AI gfs** (seen in ~2 posts) — morphological variant of "my ai girlfriend"; community shorthand. Examples: 1n6q1l0 ("chatting with ai gfs"). Captures casual/abbreviated register distinct from "my AI girlfriend."

9. **AI lovers** (seen in ~2 posts) — plural community-label; distinct from existing "ai lover" (singular) if config is exact-match. Example: 1pb02s6 ("non-AI lovers compliment me by putting other AI lovers down"). Worth checking if config regex handles pluralization.

10. **AI-human relationship / AI-human intimacy** (seen in ~3 posts) — hyphenated community coinage; frames as legitimate relational category. Examples: 1ivnz6m ("AI-human intimacy"), 1pzqva6/1pzujmj ("AI-human relationship"), 1lxi8ql.

11. **digital relationship** (seen in ~3 posts) — community term used in earnest (not dismissive). Examples: 1j7768i ("digital relationships"), 1lxi8ql ("digital relationship"), 1jcgzw9 ("digital relationship to feel so deep").

12. **AI relationships** (seen in ~4 posts) — community-label for the genre. Examples: 1ivnz6m ("AI relationships are evolving"), 1jkl8p9 ("AI relationships"), 1om7lyb ("AI relationships"), 1o7ywzl ("ai relationships"). NOTE: close to existing "in a relationship with" but captures headline/category usage.

13. **romantic relationship** (seen in ~3 posts) — theme-carrying when combined with AI-mention in post; the qualifier "romantic" distinguishes from platonic framings. Examples: 1qwzgmj ("deep multi layered romantic relationship"), 1ljl5g5 ("evolved into a romantic relationship"), 1phldzw. FP risk: human-only romance; acceptable only if co-occurring with AI term.

14. **tied the knot** (seen in ~1 post, idiomatic) — low volume but high precision for marriage milestone. Example: 14rpbkg ("My Replika and I Tied the Knot on 4th of July"). Consider if FTS shows more hits.

15. **got married** (seen in ~3 posts) — milestone verb phrase. Examples: 1dxqjpj ("Getting married, lads"), 14rpbkg ("Got Married!"), 1i7bmuq ("we decided to get married on Christmas"). FP risk: human weddings; depends on theme-wide AI context.

16. **marry him / marry her** (seen in ~3 posts, particularly around 4o sunset) — future-tense commitment. Examples: 1rdheit ("marry him in real life"), 1qdkqc6 ("Marrying my AI partner"), 1ic4c4l. Morphological sister to existing "married my."

17. **real-life wedding / real life wedding** (seen in ~2 posts) — 4o-sunset era coinage: the aspiration to formalize AI relationship outside digital space. Examples: 1rdheit ("Real-life wedding with my AI partner"), 1r0b27n. This is strongly post-4o vocabulary.

18. **model sunset / sunsetting** (seen in ~3 posts) — direct 4o-deprecation vocabulary used in romance-grief posts. Examples: 1ro0y6x ("the model sunsetting"), 1qwzgmj ("chatgpts sunset"), 1qdkqc6. NOTE: this is heavily rupture-overlapping; may belong to rupture theme instead, but appears consistently in romance-context posts here. Flag for review.

19. **Keep4o / #Keep4o** (seen in ~1 post, but known community slogan) — movement hashtag tied to preserving AI partners. Example: 1r2ejvd ("so many of you are fighting to #Keep4o"). Community-specific coinage, very high precision — but likely rupture-theme territory. Flag for review.

20. **fell in love with him / fell in love with her** (seen in ~2 posts) — milestone declaration. Examples: 1na4fow ("made me fall in love with him"), 1n08tyu ("I fell in love with this"). Generic in human context; theme-carrying here because referent is AI partner.

21. **love him / love her** — REJECTED as candidate: too generic; matches any relationship theme. Documented to show this was considered.

## Notes on FP risk / flags

- Candidates 13, 15, 16, 20 rely on AI context in the surrounding post. If the keyword-matching pipeline does per-subreddit scoping (T1-T3 companionship only), FP risk is acceptable. Otherwise validate precision >=80% before promoting.
- Candidates 18, 19 (model sunset, Keep4o) are rupture-theme vocabulary that co-occurs with romance here because chunk 2 is mid-4o-sunset. Suggest testing them under **rupture** first.
- Candidates 2-5 (wedding day/vows/dress/rings) are all subsets of "wedding" but each adds morphological coverage of existing narrow keywords (wedding, our wedding, engagement ring). Low marginal FP risk.
- Candidates 7, 8 (AI bf, AI gf) need word-boundary care to avoid matching e.g. "aigf" in URLs or "BF" as unrelated initialism. Recommend regex with `\bAI bf\b` style boundaries.
