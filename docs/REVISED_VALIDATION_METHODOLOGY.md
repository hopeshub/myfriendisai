# myfriendisai — Revised Keyword Validation Methodology

**Created:** March 12, 2026
**Purpose:** Replaces the tier-based precision approach. This is the new standard for validating keywords.

---

## The Question Every Keyword Must Answer

**When this word or phrase appears in our data, is it almost always being used to describe someone's relationship with or emotional response to an AI?**

Not "does it appear in companion subs." Not "is it technically related to AI." The question is about what the person writing the post is actually talking about.

---

## Why the Old Approach Was Wrong

The previous methodology measured "companion sub precision" — what percentage of a keyword's hits came from Tier 1-3 subreddits versus Tier 0 general AI subreddits. This treated general subs as noise.

But someone in r/ChatGPT saying "they lobotomized it" after a model update is describing the same emotional experience as someone in r/replika saying the same thing. The old method filtered that out. The phenomenon we're tracking — people forming emotional relationships with AI — is happening across all AI communities, not just dedicated companion spaces. Filtering by subreddit threw away the signal we were looking for.

---

## The New Validation Process

### For each keyword, do this:

**Step 1 — Pull a sample.**
Query the full corpus for posts matching this keyword. Pull 100 random matches from across all tracked subreddits (not just companion subs). If a keyword has fewer than 100 total hits, pull all of them.

**Step 2 — Read them.**
For each post, ask one question: **Is this person describing a relationship with, emotional response to, or personal experience with an AI?**

Mark each post as:
- **YES** — clearly about someone's personal/emotional/relational experience with AI. Examples: grieving a model update, expressing attachment, describing companionship, expressing anger at a personality change, talking about their AI partner.
- **NO** — about something else. Examples: discussing AI capabilities as technology, talking about a human relationship, asking a tech support question, reviewing a product feature without personal emotional content, using the word in a completely different context ("my girlfriend uses ChatGPT").
- **AMBIGUOUS** — could go either way. Don't force it.

**Step 3 — Score it.**
Count the YES posts out of 100. That's your **contextual relevance score**.

| Score | Verdict |
|---|---|
| 80+ out of 100 (≥80%) | **KEEP** — this keyword reliably captures companion/relational discourse |
| 70-79 out of 100 (70-79%) | **KEEP WITH NOTE** — usable but noisier. Document the score. |
| 50-69 out of 100 (50-69%) | **FLAG** — Walker reviews a subsample of the agent judgments and makes a final call |
| Below 50 out of 100 (<50%) | **CUT** — too much of the time, this word is about something else |

Count AMBIGUOUS posts as half a YES for scoring purposes.

### That's the whole process.

It's manual. It's judgment-based. It's how qualitative research works. The judgment of "is this person describing a relationship with AI" is a call a trained researcher makes — not a formula.

---

## What Counts as "Relationship With or Emotional Response to AI"

To keep the judgment consistent, here's what we mean:

**YES — this counts:**
- Expressing love, attachment, grief, anger, loss, joy, comfort, gratitude, or any other emotion directed at an AI
- Describing an AI as a partner, friend, companion, therapist, or any relational role
- Grieving or celebrating a change in an AI's behavior or personality
- Describing dependence on, addiction to, or withdrawal from interacting with an AI
- Discussing whether an AI is sentient, conscious, alive — in the context of a personal relationship or emotional investment
- Expressing that an AI "understands" them, "remembers" them, or "cares about" them
- Describing attempts to circumvent filters in order to maintain a relationship or emotional experience with an AI
- Any post where the person is clearly relating to the AI as a social/emotional entity rather than a tool

**NO — this doesn't count:**
- Discussing AI capabilities, benchmarks, or features in a purely technical context
- Mentioning a human relationship in a post that happens to be in an AI subreddit ("my girlfriend thinks ChatGPT is cool")
- Tech support questions ("my chatbot forgot my settings")
- Product reviews focused on features, pricing, or comparisons without personal emotional content
- Using a keyword in a completely different context ("I'm addicted to coffee")
- Meta-discussion about AI companionship as a social phenomenon, without personal experience (e.g., a news article link with commentary)

**AMBIGUOUS — use your judgment:**
- Someone describing an AI as "really good at conversation" — is that relational or just a product evaluation?
- Someone saying "I miss the old model" — is that grief or just preference?
- Discussion of AI sentience in a philosophical/academic tone without personal attachment

When in doubt, mark it AMBIGUOUS. Better to be honest about uncertainty than force a call.

---

## How to Use This for the Audit

The Phase 1 audit produced a TSV with precision scores based on the old subreddit-distribution method. Those scores are still useful as a *rough filter* — terms at 0-5% companion precision are almost certainly generic language and probably aren't worth sampling. But anything above ~10% deserves the contextual read.

**Practical triage for the 277 existing keywords:**

1. **Auto-cut (no sampling needed):** Terms where the old audit showed < 5% companion precision AND the term is obviously generic human language. Examples: "thank you," "my friend," "struggling with," "my anxiety," "my depression." These are clearly not about AI relationships. Don't waste time sampling them.

2. **Sample and score:** Everything else. Especially terms that the old audit flagged as "noise" but that feel intuitively relevant — "lobotomized," "sentient," "personality is gone," "feels real," "addicted," "miss the old." These may score much better under contextual validation than they did under tier-based precision.

3. **Already validated:** The 17 terms that passed the old 80% threshold will almost certainly pass contextual validation too. You can keep them without re-sampling, but a quick sanity check on 10 posts each wouldn't hurt.

---

## How to Scale This

Reading 100 posts per keyword for ~150 terms (after auto-cuts) = ~15,000 posts. That's too many to read manually.

**Use CC agents to do the reading.** The contextual judgment ("is this person describing a relationship with or emotional response to AI?") is exactly the kind of call an LLM can make reliably. This is not the same as using an LLM to classify every post in the corpus — it's using it to validate a keyword list, which is a one-time task.

CC prompt for agent-based validation:
```
For each keyword in the list below, pull 100 random posts that match it from the posts database (across all subreddits). If a keyword has fewer than 100 total hits, pull all of them. For each post, read the title and body and answer: "Is this person describing a personal relationship with, emotional response to, or personal experience with an AI?" Answer YES, NO, or AMBIGUOUS.

Return: keyword, post_id, subreddit, first_150_chars, verdict (YES/NO/AMBIGUOUS)

Then summarize: for each keyword, count YES, NO, AMBIGUOUS out of the total sampled. Calculate contextual relevance score: (YES + 0.5*AMBIGUOUS) / total_sampled.
```

Walker reviews the summary scores and spot-checks any keywords where the agent's judgment seems off.

---

## Maintaining the Standard

When adding new keywords in the future (SOP 2), apply this same process:
1. Discover the candidate in real posts
2. Pull 100 matches (or all matches if fewer than 100 exist)
3. Read (or have agents read) and score
4. ≥ 80% contextual relevance → add
5. Document the score in METHODOLOGY.md

---

## What This Changes About the Project

- **Themes can draw from all subreddits.** "Grief" language in r/ChatGPT counts. "Sentience" discussion in r/singularity counts. The site is tracking how people relate emotionally to AI, not just what happens in dedicated companion spaces.
- **The validation is transparent but qualitative.** We're saying "a researcher read 30 posts and judged 25 of them to be about AI companionship." That's honest, defensible, and appropriate for this kind of research.
- **Some previously-killed keywords will come back.** "Lobotomized," "personality is gone," "sentient," "miss the old," "feels real" — these likely score well on contextual relevance even though they failed tier-based precision.
- **Some will still fail.** "Thank you," "my friend," "struggling with" — these are generic even in context. They'll fail the contextual read too.
