# NSFW Scope Position

*Canonical statement of the project's goal and its position on NSFW content.
Written 2026-05-18 to ground the r/AIGirlfriend / r/ChatGPTNSFW / r/SpicyChatAI
exclusion decision in a stated principle rather than case-by-case judgment.
Companion to `docs/what_this_is_2026-05-16.md` (the broader scope doc); where
they overlap, `what_this_is` is the source of truth on overall scope and this
doc is the source of truth on NSFW handling.*

---

## 1. What the project is

**My Friend Is AI is a precision-first discourse tracker.** It measures how
explicit AI-companion *language* moves over time inside a curated set of Reddit
communities. It does **not** measure the phenomenon — not how many people use
AI companions, are in AI relationships, or are addicted or helped. It answers a
narrower, honest question: *when people in AI-companion communities talk
publicly, how often does each theme's vocabulary appear, and how does that
change over time?*

The load-bearing principle: **curation is the method, not a side detail.** The
site tracks "communities where AI companionship is central enough that language
can be interpreted with some stability." A keyword like "in love with" only
means what it appears to mean because *the room supplies the context*. This is
why the T0 general subs (r/ChatGPT, r/OpenAI) are excluded from theme lines —
there, "my boyfriend uses ChatGPT" pollutes "my boyfriend is an AI."

**The unit of analysis is the AI-companion community.** Everything follows from
that.

## 2. The project's position on NSFW — two halves, both true

### (a) NSFW is fully in scope. The project does not sanitize.

- sex/ERP is one of the **six headline themes** — not a footnote, not bowdlerized.
- Multiple `over_18` subreddits are tracked and collected normally.
- The 2023 Replika ERP removal is a flagship event the site is *built* to show.
- The project actively *wants* explicit companionship communities (e.g. the
  2026-05 coverage refresh targets r/Replika_uncensored for addition).

→ **Explicitness is never, by itself, a reason to exclude.** The project is
sex-positive about companionship by design.

### (b) But NSFW is tracked as a *facet of companionship* — never as a subject in itself.

- sex/ERP sits beside romance, consciousness, therapy, addiction, rupture —
  five *relational* facets. It is the erotic dimension *of companion
  relationships*, not "erotic AI use" as a free-standing topic.
- The inclusion gate has always been "is this AI-companion discourse?" — never
  "is this NSFW?"
- Precedent: r/JanitorAI_Official and r/SillyTavernAI were never tracked — not
  for being explicit, but for not being companionship discourse (bot-card noise).

## 3. The single principle

> **The inclusion gate is companionship, not NSFW-ness.**

Two NSFW subreddits can land on opposite sides:

- NSFW **and** companionship → **in** (Replika ERP, character-bot ERP,
  AI-girlfriend sexting, r/Replika_uncensored).
- NSFW but **not** companionship → **out** (erotica generation, jailbreak
  craft, AI-porn-image feeds) — excluded for the *same reason a non-AI
  subreddit is*, not for being explicit.

This gives every coverage decision one question — *is this an AI-companion
community?* — and explicitness never enters into it.

## 4. Applied: the 2026-05-18 exclusions

Three previously-tracked T2 subreddits were set `exclude_from_keywords: true`
(removed from the keyword theme lines and the normalization denominator; kept
in the community explorer as engagement context):

| Sub | What it actually is | Why excluded |
|---|---|---|
| r/AIGirlfriend | ~91% affiliate-spam image posts; 1.4% keyword-tag rate | Tags were marketing copy matching romance/sexual vocabulary — false-positive noise, not discourse. |
| r/SpicyChatAI | Bot-card marketplace + product/filter support; 2.4% tag rate | Tags were bot-card listing text — the same failure mode that kept JanitorAI/SillyTavern out. |
| r/ChatGPTNSFW | Erotica-writing / jailbreak-craft community; 10.7% tag rate | **Not noise — real signal, but off-construct.** No persistent companion or relationship; the room's context is "make the model write porn," not "my AI partner." Fails the canonical test of a community where companionship is central. |

r/ChatGPTNSFW is the principled case. It was *not* excluded for being explicit
— in the same coverage refresh the project is **adding** r/Replika_uncensored,
which is more sexually explicit, because it *is* companionship. **Same rule,
opposite outcomes** — which is the test of a real principle.

Effect: r/ChatGPTNSFW had been ~13% of the sex/ERP theme overall and ~36% of it
in 2025, so the sex/ERP line steps down, most visibly across 2024–2025. This is
a correction toward construct validity, disclosed in the public changelog — not
a quiet edit.
