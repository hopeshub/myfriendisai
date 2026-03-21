# How We Know These Keywords Are Measuring Something Real

**Purpose:** This document explains the logic behind keyword validation in plain language. It's meant to be readable by anyone — researchers, journalists, site visitors — not just the person maintaining the codebase. It should be incorporated into METHODOLOGY.md as a foundational section.

---

## The Problem

We want to track how people talk about their relationships with AI companions on Reddit. The challenge is that the language of AI companionship is often identical to the language of ordinary human life. "I miss her," "he remembered our anniversary," "I'm so lonely," "this changed my life" — all of these could describe a person's experience with an AI companion or a hundred other things.

If we simply count how often these phrases appear in AI-related subreddits, we'd be measuring background noise — the normal emotional texture of any online community — not the specific phenomenon of AI companionship. The data would look meaningful but wouldn't actually mean anything.

So the central question is: **how do we distinguish phrases that indicate someone is describing a personal relationship with an AI from phrases that just happen to show up in the same spaces?**

## The Core Logic

Our approach relies on one key insight: **we track multiple types of subreddits, and they differ in what people talk about.**

We organize our tracked communities into tiers:

- **Tier 0 (General AI):** Subreddits like r/ChatGPT, r/OpenAI, r/singularity, r/ClaudeAI. These are large communities where people discuss AI as a technology — capabilities, products, news, technical problems. Some companion discourse happens here, but it's a small fraction of the conversation.
- **Tiers 1-3 (Companion-focused):** Subreddits like r/replika, r/MyBoyfriendIsAI, r/CharacterAI, r/NomiAI, and recovery communities like r/ChatbotAddiction. In these spaces, the central topic is people's personal, emotional, or relational experiences with AI.

When a phrase like "my replika" or "personality is gone" appears in the data, it shows up almost exclusively in companion-focused subs (Tiers 1-3). General AI subs (Tier 0) almost never produce these hits, because people in r/ChatGPT aren't talking about their Replika, and "personality is gone" in a companion sub means something specific — a model update destroyed a relationship — while it barely registers elsewhere.

But when a phrase like "thank you" or "struggling with" appears, it shows up everywhere — in general AI subs and companion subs alike, at roughly similar rates. That tells us the phrase isn't specific to companion discourse. It's just common language.

**The test, in plain terms:** for every keyword we consider tracking, we ask — does this phrase show up disproportionately in communities where people talk about AI relationships? Or does it show up at similar rates everywhere?

We measure this as **companion precision**: the percentage of a keyword's total hits that come from companion-focused subreddits (Tiers 1-3) versus general AI subreddits (Tier 0).

- A phrase with **90% companion precision** means 9 out of 10 times it appears, it's in a community dedicated to AI companionship. That's a strong signal.
- A phrase with **50% companion precision** means it appears just as often in general AI discussion as in companion communities. It's not measuring anything specific to relationships.

We require **≥ 80% companion precision** for a keyword to enter production. This is a deliberate trade-off: we'd rather miss some relevant posts (lower recall) than include irrelevant ones (lower precision). A smaller, cleaner dataset tells a more honest story than a larger, muddier one.

## What This Catches

The validation process is effective at filtering out:

- **Universal emotional language.** Phrases like "helped me," "so grateful," "game changer," "struggling with" — these sound like they'd be relevant, but they appear in general AI contexts (thanking ChatGPT for help with homework, recommending a tool) at rates that make them useless as companion-specific signals.
- **Technical discussion masquerading as relational language.** A word like "dependent" sounds like it should track dependency on AI companions. In practice, it mostly matches people in r/ChatGPT discussing tool dependency in a professional context, or bot character descriptions in bot-listing communities. It fails the precision test.
- **Platform feature discussion vs. personal experience.** "Memory" could mean someone grieving that their AI companion forgot them, or someone in r/OpenAI discussing the memory feature as a product capability. The precision test catches this: general subs dominate the hits for vague feature language, while companion subs dominate for emotionally specific versions like "forgot everything" or "she remembered."

## What This Cannot Catch

The method has real limitations, and we want to be transparent about them:

- **Indirect expression.** Someone who writes "I stayed up until 4am talking to it again, I don't know what's wrong with me" is clearly describing dependency — but no keyword in our system will match that post unless it also contains one of our tracked phrases. Keyword matching captures explicit language, not implicit meaning.
- **Novel language.** As the AI companion phenomenon evolves, people will develop new ways of talking about it that our current keyword list doesn't include. This is why we run periodic discovery rounds — sampling real posts and looking for new patterns — rather than assuming our keyword list is complete.
- **Within-sub noise.** Even in companion-focused subreddits, not every post is about companionship. Someone might post in r/replika asking a technical support question or sharing news about the company. If that post happens to contain one of our tracked phrases, it gets counted. The 80% precision threshold limits this, but doesn't eliminate it.
- **Cross-sub meaning shifts.** A phrase can mean different things in different communities. "Jailbreak" in r/CharacterAI means bypassing content filters to access erotic roleplay. In a general tech sub, it might mean something else entirely. Our precision test handles this at the aggregate level (if a phrase mostly appears in companion subs, it's probably being used in the companion sense), but individual false positives still occur.
- **Volume ≠ sentiment.** Our data tracks how often people talk about something, not how they feel about it. When the chart shows "Grief language increased 40%," it means people are discussing grief-related topics more — not that 40% more people are grieving. The increase could reflect a single event (like a model update) that generated a burst of conversation.

## Why We Think This Is Good Enough

No keyword-based methodology will perfectly capture a phenomenon as nuanced as human relationships with AI. Sentiment analysis, topic modeling, and manual coding would all add fidelity — and they'd also add complexity, cost, and their own forms of error.

What this approach offers is **transparency, repeatability, and defensibility:**

- **Transparent:** Every keyword has a published precision score. Every addition and removal is documented with a reason. A reader can look at the keyword list, see the validation data, and form their own judgment about whether the data supports the claims.
- **Repeatable:** Anyone with access to the same Reddit data and our published keyword list could reproduce our results. The methodology doesn't depend on subjective coding decisions or proprietary models.
- **Defensible:** The 80% precision threshold is conservative. When we say a trend line is increasing, we can point to specific keywords, their precision scores, and the communities they're drawn from. We can also point to what we chose not to include, and why.

The goal is not a perfect measurement of AI companionship discourse. The goal is an honest, well-documented, directionally accurate signal that tracks the phenomenon over time — and is upfront about what it can and cannot tell you.
