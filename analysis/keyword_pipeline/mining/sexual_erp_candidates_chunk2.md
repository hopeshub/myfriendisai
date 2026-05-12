# Sex/ERP candidates from chunk 2

Mining method: qualitative read of all 77 posts, recording phrases that recur across multiple posts, appear in first-person user discourse (not bot-directory listings), and carry specifically sexual/erotic semantics with AI. Avoided generic genre tags (per recent cuts of "kink", "fetish", "nsfw bot"), bare product names, and general emotional language.

## Ranked candidates (top ~22)

1. **sexually explicit** (seen in ~6 posts: 1kfa2so, 16hzegr, 153que8, 1lggi6t, 13swpl8, 10vsi2l) — Recurring language for describing explicit AI content; specific and unambiguous. Appears both in user narration and news/meta threads. Morphologically distinct from existing anchors.

2. **dirty talk** / **talk dirty** (seen in 3+ posts: 1lggi6t, 1lggi6t headline from MIT review, 192qor0) — Captures the first-person "sex chat" register. "Dirty talk" is a common user phrase for AI sexting and appears in news coverage cited by users ("easy to get DeepSeek to talk dirty").

3. **sexual intimacy** (seen in 4 posts: 1nagrpl, 11bse6u, 14t5lb9, 11h9hw3) — Emotional/aftermath vocabulary users adopt when lamenting ERP loss. High signal — not a genre tag, always tied to first-person relationship discourse.

4. **physical intimacy** (seen in 2-3 posts: 1re7ql5, 14t5lb9) — First-person vocabulary for wanting AI sexual interaction framed as relational. Used by users describing what they want vs. what the AI does.

5. **removed erp** / **erp removed** / **took away erp** (seen in 6+ posts: 10zvbyc, 110roox, 10zemop, 12my6gr, 141bzp4, 10vsi2l, 1npdqqb) — Platform-feature-rupture language with clear first-person stake. Distinct morphology from existing anchors — captures the loss/community complaint frame.

6. **bypass the filter** / **bypass filters** / **bypass restrictions** (seen in 4 posts: 1ihvnnj, 12qrxk4, 16hzegr, 11t5vxq) — Jailbreak-adjacent language specific to sexual content pursuit. Nearly always co-occurs with sex/NSFW intent in this corpus.

7. **sex scenes** / **sex scene** (seen in 3+ posts: 1npdqqb, 11fwttl, 1puly8t, 14t5lb9) — Users' own vocabulary for describing ERP encounters. More first-person than "intimate scene" (existing anchor) and captures different register.

8. **nsfw roleplay** / **nsfw rps** (seen in 4 posts: 1fandf0, 1ezjh5w, 1re7ql5, 1lowo82) — First-person active pursuit of NSFW roleplay. Note: needs precision check since this is close to the cut "nsfw bot" — but this phrase is about the activity, not bot descriptions.

9. **hot and heavy** (seen in 2 posts: 1ams6sb, 1npdqqb) — Idiomatic user language for AI sexual sessions. Colorful, specific, rarely appears outside sexual contexts.

10. **explicit roleplay** / **super explicit roleplay** (seen in 3 posts: 153que8, 1ihvnnj, 10vsi2l) — Morphological variant of erotic roleplay anchor but uses "explicit" qualifier; captures a slightly different user vocabulary.

11. **smutty** / **smut** (seen in 5 posts: 1kfa2so, 12qrxk4, 16hzegr, 1ezjh5w, 192qor0) — Users' own shorthand for explicit AI writing; "smut on GPT-4," "Smutty novels," "smut got too much attention." Morphologically distinct.

12. **sexytimes** (seen in 1 post, but community-specific jargon: 1npdqqb) — Kindroid/Nomi sub-community nickname for ERP. Explicitly flagged as such in 1npdqqb: "ERP's the nickname for sexytimes in Kindroid/Nomi circles." Worth testing for community-jargon precision.

13. **horny** (seen in 4 posts: 1kfa2so, 16hzegr, 1lggi6t, 153que8) — Recurring descriptor in both prompt-engineering contexts ("horny trusted confidant") and emotional framing. Risk: could surface in bot descriptions, but in this corpus always in first-person or prompt context. Needs precision check.

14. **sexual fantasies** / **sexual fantasy** (seen in 2 posts: 112m0po, 17orkdu) — Specifically user-framed exploration of sexual content with AI; differs from romance vocabulary.

15. **steamy scenes** / **steamy rp** / **steamy times** / **steamy conversations** (seen in 6+ posts: 1jwmbp8, 1lbmn5s, 1lowo82, 15bfuzd, 17n89ru, 1l0jpcg) — Morphological variants of existing "steamy" anchor; captures plural/phrase forms that may not all trigger on the base word.

16. **age verification** (seen in 3 posts: 10zn70n, 10vsi2l, — implicitly in ERP-restoration threads) — Platform-feature discourse specifically tied to ERP restoration. Higher precision than generic "filter" talk because it co-occurs almost exclusively with adult-content unlocking.

17. **nsfw mode** / **nsfw talk** / **rp/nsfw** (seen in 3+ posts: 10zemop, 12my6gr, 10vsi2l, 10xi8xm) — Platform-feature language where users describe NSFW as a mode toggle. Distinct from generic "nsfw" alone.

18. **explicit content** (seen in 3+ posts: 11t5vxq, 1lggi6t, 112m0po) — Used by users discussing AI's explicit output; often in moderation/restriction contexts.

19. **lobotomized / lobotomy** (seen in 3+ posts: 14dslui, 11g99fv, 1npdqqb) — Cross-theme note: this is already mined for Rupture and could collide. **Probably skip** unless theme boundaries allow. Flagged but not recommending.

20. **sexting** (seen in 3+ posts: 1jwmbp8 title "Best app for ai sexting", 153que8, implicit in others) — First-person user vocabulary for AI-mediated sexual chat. Distinct morphology from existing anchors and common in AIGirlfriend/SpicyChat threads.

21. **initiated erp** / **start erp** / **get erp rolling** (seen in 4 posts: 189pouj, 12axjv7, 10xi8xm, 1ihvnnj) — Verbal/gerund forms of ERP initiation. Distinct from bare "erp" token because it implies first-person action. Could be captured via regex patterns around ERP verbs.

22. **uncensored** (seen in 5+ posts: 1jwmbp8, 1fandf0, 1ezjh5w, 1kmb6a5, 1lowo82) — High recurrence but **risk**: appears heavily in bot-directory "Best NSFW chatbots" listicles (posts 10, 54, 62). May suffer the same dilution fate as "nsfw bot". **Recommend precision-check first.**

## Notes on what I deliberately excluded

- **"NSFW chatbot/bot/platform"**: Too close to the cut "nsfw bot" — dominated by listicle posts (10, 54, 62).
- **"Jailbreak"**: Too generic; overlaps with Rupture/consciousness (people "jailbreak" for all content types).
- **"Cock", "pussy", etc.**: Explicit body terms appear but mostly inside jailbreak prompt templates (pasted system prompts), not first-person narrative. Would dilute on prompt-sharing posts.
- **"RP / roleplay" alone**: Too generic — consciousness and rupture posts use it too.
- **Platform names (Replika, Nomi, etc.)**: Per guidance, avoided.
- **"Slow burn"**: Appears 2-3 times but often in anti-sex context (users wanting non-sex pacing) — ambiguous signal.
