# What My Friend Is AI Is

*Canonical statement of project scope and purpose. Written 2026-05-16, when the
project's framing was deliberately narrowed from "a proxy for AI-companionship
proliferation" to "a precision-first discourse tracker." The public About page
(`web/app/about/page.tsx`) and `CLAUDE.md` §1 are reconciled against this
document; where they disagree, this document is the source of truth.*

---

**My Friend Is AI is a daily-updating public record of how AI-companion communities on Reddit talk over time.**

It tracks six recurring themes — romance, sex/ERP, consciousness, therapy, addiction, and rupture — across a curated set of AI-companion subreddits. The post corpus reaches back to 2017, though the theme lines themselves begin in 2022–2023, where monthly volume becomes reliable enough to chart. The method is intentionally simple and transparent: validated keyword patterns are matched against posts, counted over time, and normalized per 1,000 posts.

This project does not measure the whole phenomenon of AI companionship. It measures the parts of the conversation that become explicit enough to track in language.

## The Honest Scope

The site is best understood as a **precision-first discourse tracker**.

It does not ask, “How many people are in relationships with AI?” or “How common is AI addiction?” Those are much larger questions, and this instrument cannot answer them.

Instead, it asks:

> When people in AI-companion communities talk publicly, how often do certain recurring forms of language appear, and how does that change over time?

That narrower question is the one the site can answer honestly.

## Why These Communities

The project began with a broader ambition: tracking AI companionship across large general AI subreddits like r/ChatGPT, r/OpenAI, r/ClaudeAI, and others.

That did not work well.

The problem was context. In a large general subreddit, phrases like “my girlfriend,” “my boyfriend,” “in love with,” or “relationship with” are often about ordinary human relationships that merely mention AI. A keyword cannot reliably tell the difference between “my boyfriend uses ChatGPT” and “my boyfriend is an AI.”

So the project moved toward communities where the room itself supplies the context. In r/replika, r/MyBoyfriendIsAI, r/CharacterAI, r/AIRelationships, or recovery communities for chatbot dependency, the same words are much more likely to mean what they appear to mean.

That curation is not a side detail. It is the method. The site tracks communities where AI companionship is central enough that language can be interpreted with some stability.

## What The Site Can Show

The site can show how explicit language around AI companionship has moved over time inside these communities.

It is especially good at showing:

- major platform events, like the 2023 Replika ERP removal;
- grief and rupture around model retirements or product changes;
- the growth of recovery and quitting language;
- changes in how people talk about AI as romantic, sexual, therapeutic, addictive, or possibly conscious;
- broad direction over time within a theme;
- moments when private attachment becomes public, measurable language.

The strongest signals are event-shaped. When a platform changes underneath users, the language changes quickly and visibly. That is where this kind of tracker is most useful.

## What The Site Cannot Show

The site cannot show how many people use AI companions.

It cannot show how many people are in AI relationships.

It cannot show how many people are addicted, helped, harmed, grieving, or in love.

It cannot represent Reddit as a whole, much less the general population.

It cannot compare theme heights directly. A higher addiction line does not mean addiction is more common than romance. It may simply mean addiction has more distinctive vocabulary. Recovery language like “relapse,” “withdrawal,” or “cold turkey” is easier to detect than ordinary romantic language like “I love him” or “she said something sweet today.”

Each line should be read mostly against itself: its direction, timing, spikes, and broad movement over time.

## The Main Tradeoff

The project chooses precision over coverage.

That means it would rather miss many real posts than count too many false ones. This makes the lines incomplete by design. They are floors, not ceilings.

The ordinary core of AI companionship is often the hardest part to measure. Someone simply living with an AI partner may write in everyday language: “she made me laugh,” “we talked all night,” “I miss him,” “our anniversary.” Those phrases may be real AI-companion language, but they are too close to ordinary human relationship language to use safely as keywords.

So the site sees the edges more clearly than the center. It sees crisis, loss, dependency, erotic-policy conflict, personhood claims, and explicit relationship declarations better than it sees quiet daily companionship.

That is a limitation, but it is also a finding.

## Why Keyword Counting

The site uses keywords because keywords are checkable.

A language model could classify posts more flexibly, but it would also introduce model drift, hidden judgment calls, version changes, and reproducibility problems. A keyword count is plain: the same posts and the same patterns produce the same number.

The careful work happens before the chart: candidate keywords are tested against real posts, false positive patterns are checked, and weak terms are rejected or documented.

The chart is not “AI reading Reddit.” It is a transparent measurement instrument built from validated language signals.

## How To Read The Lines

Read a line as:

> “How often did this theme’s explicit vocabulary appear in these communities at this time?”

Do not read it as:

> “How common was this experience among people?”

Therapy and addiction are the one intentional exception to reading each line on its own. The two themes track the same behavior — emotional reliance on an AI — separated only by the writer's framing. Neutral or positive language (“it's my coping mechanism,” “it helps”) reads as therapy; negative language (“I'm addicted,” “I can't stop”) reads as addiction. The two lines share posts by design and are best read as a linked pair — watch which way the balance tips.

Broad movement matters more than individual wiggles. A sustained rise, a clear spike, or a long decline is meaningful. A single noisy month may not be.

The lines are strongest when they line up with known events: platform shutdowns, model retirements, policy changes, or community migrations. They are weaker as estimates of ordinary background prevalence.

## What Makes The Project Useful

This is not definitive academic research, and it should not pretend to be. Comparable academic work exists, often with stronger methods for frozen snapshots.

The distinctive value here is different:

- it is live;
- it is public;
- it is browsable;
- it is transparent;
- it keeps updating;
- it documents its limits instead of hiding them.

Academic studies often capture a period after the fact. This site watches the conversation as it keeps moving.

## The Best One-Sentence Description

**My Friend Is AI is a live, transparent tracker of explicit AI-companion language in curated Reddit communities — a way to see how themes like romance, dependency, personhood, sexual roleplay, therapeutic use, and loss rise and fall over time.**

## The Frame To Hold

This is not a complete map of AI companionship.

It is an observatory for the parts of AI companionship that become visible in public language.

That is a smaller claim than “tracking the phenomenon.” But it is a claim the project can stand behind.
