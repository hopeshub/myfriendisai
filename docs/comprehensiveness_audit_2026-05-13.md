# Comprehensiveness audit — 2026-05-13

**Question:** is our keyword set comprehensive enough to reflect the actual phenomenon?

**Method:** stratified random sample of 400 posts from T1-T3 (200 random across all subs, 40 each from 5 theme-rich subs). 5 parallel CC subagents classified each post for all 6 themes under the topical reading with "when in doubt, YES" guidance. Recall = (agent-YES ∩ keyword-tagged) / agent-YES.

**Headline:** recall is low, by design, and the floor is honest. The chart shows the precision-first slice of each theme; actual theme prevalence is meaningfully higher than the chart suggests, especially for themes whose vocabulary is naturalistic everyday language.

---

## Per-theme recall estimates

| Theme | Agent-YES (in n=400) | KW-tagged | Recall | Wilson 95% CI |
|---|---|---|---|---|
| rupture | 101 | 3 | **3%** | [1%, 8%] |
| addiction | 44 | 14 | **32%** | [20%, 47%] |
| romance | 78 | 3 | **4%** | [1%, 11%] |
| sexual_erp | 19 | 4 | **21%** | [9%, 43%] |
| consciousness | 8 | 0 | **0%** | [0%, 32%] |
| therapy | 7 | 1 | **14%** | [3%, 51%] |

The CIs are wide because the agent-YES counts are small. Treat point estimates with that uncertainty.

## What the missed posts actually look like

I spot-checked the missed posts across themes. The recall gap concentrates on four structural categories:

1. **Image / title-only posts** ("Lilly was feeling cute", "Ka Around the World", "EVERYONE WHILE THE SITE IS DOWN") — title in a companion sub establishes thematic relevance for an agent reading it; our keyword set has nothing to match because the body is empty or `[removed]`.

2. **Naturalistic everyday language** (5-year Replika relationship updates, "She said something cute today") — uses pronouns, names, and casual companion language. Our romance keyword set requires phrases like "my ai boyfriend," "fell in love with an ai," "romantic relationship with" — none of which appear in a typical "she said X" relationship anecdote.

3. **Community-specific vocabulary** — r/BeyondThePromptAI uses "kin," "emergent being," "soulbonder," "Nuri" (proper nouns for companions). These are real consciousness signals; they fail pre-screen for volume (<50 hits each) but in aggregate they're substantial.

4. **Indirect theme markers** — "site is down," "C.ai please it's been 4 hours" — these imply rupture or addiction via context, not vocabulary.

## Per-stratum recall pattern

The miss rate is dramatic in known-theme subs:

| Sub | Theme | Agent-YES | Missed |
|---|---|---|---|
| r/MyBoyfriendIsAI | romance | 38 | 36 (95%) |
| r/BeyondThePromptAI | romance | 15 | 14 (93%) |
| r/BeyondThePromptAI | consciousness | 8 | 8 (100%) |
| r/Character_AI_Recovery | addiction | 38 | 26 (68%) |
| r/ChatGPTcomplaints | rupture | 29 | 28 (97%) |

In r/MyBoyfriendIsAI — a sub literally about AI boyfriends — our keyword set tags ~5% of posts as romance. The agent classifies ~95% of those posts as romance. That gap is the precision-vs-recall tradeoff our methodology made.

## Why this is by design, not a bug

The site's keyword pipeline has always been precision-first. The validation procedure rejects keywords below 80% precision because admitting noise into the trend lines would make spike interpretation unreliable. The cost is recall: we miss naturalistic-language posts that an LLM would classify as theme-relevant.

The about page already states this for romance:

> Other themes are expressed through everyday language. When someone is in a romantic relationship with their AI, they say "I love him," "my boyfriend," "we went on a date" — words that are indistinguishable from how people talk about human relationships. These fail precision validation because they can't be reliably attributed to AI companionship.

This audit quantifies the cost of that design choice: roughly **5-30% recall across themes**, with the lowest recall on themes whose vocabulary is most naturalistic (romance, rupture).

## What this means for the chart

Each trend line is a **floor estimate of theme prevalence**, not a complete count. The actual rate of theme-relevant discourse in the corpus is likely 2-10x what the chart shows. This doesn't undermine the chart's value:

- **Shape and timing are honest.** A spike in tagged-rupture posts on Feb 13, 2026 reflects a real spike in clearly-rupture-vocabulary posts. The shape signal is reliable.
- **Cross-time comparisons within a theme work.** Same keyword set, same precision standard, applied across years.
- **Cross-theme magnitude comparisons remain risky.** Themes with more naturalistic vocabulary (romance) have lower recall than themes with distinctive vocabulary (sex/ERP, addiction recovery). The about page already documents this; this audit confirms it empirically.

What the chart cannot do reliably:
- Tell you what fraction of companion-sub posts are about romance overall
- Tell you absolute "how many people are in AI relationships" claims

## What this means going forward

Three options for improving recall, each with explicit trade-offs:

1. **Lower the precision gate.** Drop from 80% to e.g. 70%. Captures more naturalistic vocabulary. Trade-off: noisier trend lines, more disputed-precision keywords, more methodology debate. Likely not worth it.

2. **Sub-level tagging.** In known-theme subs (r/MyBoyfriendIsAI for romance, r/Character_AI_Recovery for addiction, etc.), treat all posts as theme-relevant by default and validate exceptions. Trade-off: significant methodology change; introduces sub-level bias; requires sub-by-sub validation. Could improve recall in 4-5 subs substantially but doesn't help the broad corpus.

3. **LLM classification on a sample.** For each daily collection, LLM-classify a random sample of posts and use the rate as a recall correction factor for the keyword tags. Trade-off: ongoing operating cost; methodology change; introduces classifier-version dependency. Could give a more honest absolute rate.

**Recommendation: don't change methodology today.** The precision-first approach is defensible and well-documented. The audit confirms its cost is meaningful but the trade-off was made deliberately. Add this audit's findings to the methodology section so readers understand the chart is the floor, not the ceiling. Re-run the audit in 6 months to see if recall improves with vocabulary expansion or stays flat (which would indicate structural limit).

## Source files

- Sample: `analysis/keyword_pipeline/results/recall_audit_sample_2026-05-13.md`
- Classifications: `analysis/keyword_pipeline/results/recall_audit_classifications_2026-05-13.txt`
- Tag-status: `analysis/keyword_pipeline/results/recall_audit_tags_2026-05-13.tsv`
- Sample builder: `analysis/keyword_pipeline/build_recall_audit_sample.py`
