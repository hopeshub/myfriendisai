> **Filed 2026-05-15** by Claude Code, as provided by the project owner, during the
> LLM-verification post-mortem. Stored verbatim below as a strategy / decision document —
> it is not an implementation plan (see its own §1).
>
> **One factual correction from the session that filed this**, relevant to §4.1's
> implementation spec: the monthly drift watchdog is `scripts/drift_check.py`, and it is
> *agent-based* — it writes sample files that Claude Code subagents classify — and it
> *already* uses a neutral/strict rubric ("FP rules (strict): …"). The "generous /
> default-TP" prompt that §4.1 says to retune lives only in `src/llm_classifier.py`
> (`SYSTEM_TEMPLATE`) and `scripts/llm_verify_tags.py` — the *abandoned* API-verification
> path, not the watchdog. So §4.1's retune is effectively already true for the watchdog as
> it actually runs; confirm the current `drift_check.py` rubric before acting. Everything
> else in the document stands.
>
> ---

# Where LLM Classification Could Be Additive to MyFriendIsAI

**Status:** Strategy document, not an implementation plan. Written 2026-05-15 after the post-mortem on the failed LLM verification layer. Intended as a handoff to Claude Code for selective implementation.

**Read this first:** Most of this document is about what NOT to build. The successful uses are narrow. Resist the urge to build more than what's specified here. The failure we just recovered from was caused by treating "add an LLM somewhere" as obviously good. It isn't. It's only good in specific places.

---

## 1. The lesson from the failed integration

The previous attempt used LLMs as a filter *behind* the keyword matcher. The LLM read keyword-flagged posts and judged whether each tag was correct. Three things made this structurally wrong:

- **It addressed precision, not recall.** The bigger gap in this project is recall (3–32% per theme), not precision (~80%). The LLM filter could only see posts the keywords already caught, so it could never recover the posts keywords missed. It worked on the smaller problem.
- **The validation was circular.** Claude wrote the keywords. Claude classified posts. Claude audited the classifications. Agreement between Claude-graded and Claude-classified is consistency, not correctness.
- **The scale forced the architecture.** At 3.84M posts, LLM-on-everything wasn't affordable, so the LLM ended up downstream of a filter. Anything downstream of a filter inherits the filter's blind spots.

**The principle that comes out of this:** LLM classification is additive to this project only when (a) the LLM gets to see the raw corpus rather than a filtered slice, OR (b) the LLM produces a different *kind* of output than the keywords do — qualitative, exploratory, or proposing inputs to the keyword system rather than competing with it.

Any proposed LLM use that fails both tests should be rejected. The four-question decision rule in §3 makes this concrete.

---

## 2. What "additive" actually means here

There are four error modes / gaps in the current system. Naming them lets us match each to the right tool:

| Gap | Description | Current tool | Can LLM help? |
|---|---|---|---|
| **Precision** | Some keyword-flagged posts aren't really about the theme | Hand-coding + adversarial audit | Marginally; not worth the architecture |
| **Recall** | Most theme-relevant posts aren't caught by keywords | Acknowledged limitation | **Yes, but only via candidate generation** — see Tier 1 |
| **Depth** | Counts say nothing about *what* people are actually saying | Nothing | **Yes** — see Tier 2 |
| **Novelty** | New themes outside the 6-theme schema are invisible | Nothing | **Yes, in bounded form** — see Tier 2 |

The previous integration attacked the precision row only — and it was already the smallest gap. The interesting uses below all target the other three rows, which the keyword system literally cannot address.

---

## 3. The decision rule (use before adding any LLM step)

Before any new LLM integration, answer these four questions explicitly. Any unclear answer is a stop.

1. **Which gap does this address?** (precision / recall / depth / novelty) Be specific. "Improves the project" is not an answer.
2. **Can the LLM see what it needs to see?** If the input is a pre-filtered slice, the LLM inherits the filter's blind spots. If the input is too large for full-corpus LLM-classification within budget, this is probably the wrong intervention.
3. **What does validation look like, and is it external?** "We checked the LLM with another LLM" is circular. Real validation needs human ground truth or behavioral signal.
4. **Does this output enter the live chart, or live alongside it?** Anything entering the chart changes the methodology and triggers reproducibility concerns. Anything alongside it can be looser and more exploratory.

---

## 4. Candidate uses, ranked by value-to-risk

### Tier 1 — Low risk, clear value

#### 4.1 Monthly drift watchdog (already planned; retune)

**Gap addressed:** Precision maintenance over time.
**What it does:** Once a month, an LLM reads a small sample of keyword-flagged posts and flags keywords that appear to be drifting (e.g., `therapeutic` shifting from supportive use to insult).
**Why it's safe:** Doesn't enter the chart. Doesn't change methodology. Catches problems that hand-coding can't catch at this frequency.
**Required change from current state:** Prompt is currently "generous" (defaults to TP). For a watchdog this is exactly wrong — a watchdog should be *sensitive*, not flattering. Retune to neutral/skeptical.
**Cost:** ~$30/year on Haiku-class model.
**Validation:** Quarterly, hand-code a sample of what the watchdog flagged and didn't flag. Track agreement.

**Implementation spec for Claude Code:**
```
- Update prompt in scripts/llm_verify_tags.py from default-TP to neutral.
  Specifically: remove language that says "assume the tag is correct unless 
  clearly wrong." Replace with "judge each tag on the post's evidence alone, 
  without bias toward TP or FP."
- Keep model at Haiku.
- Keep cadence at monthly, sample size at current setting.
- Add a quarterly hand-coding check: 50 posts the watchdog passed, 50 it 
  flagged. Track agreement in docs/watchdog_validation.md.
- Output: existing alert format, no chart changes.
```

#### 4.2 Keyword candidate generation for recall

**Gap addressed:** Recall — the project's biggest gap.
**What it does:** Periodically, an LLM reads a random sample of *unfiltered* posts from tracked subreddits, identifies posts that appear theme-relevant but were *not* caught by current keywords, and proposes keywords or phrases that would catch them. A human reviews and decides whether to add to the schema.
**Why it works where the filter didn't:** The LLM sees the raw corpus, not a filtered slice. It can find what the keywords missed because it doesn't depend on the keywords. It addresses recall directly.
**Why it's safe:** The LLM proposes; humans dispose. Nothing the LLM produces enters the keyword schema (or the chart) without explicit human approval. The LLM is a research input, not a measurement instrument.
**Cost:** ~$15–25 per run. Quarterly is plenty. Annual: ~$60–100.
**Validation:** For each proposed keyword, hand-code 30 posts before adding. Add only if precision ≥75%. Track per-keyword from the start.

**Implementation spec for Claude Code:**
```
Pipeline (proposed name: scripts/discover_recall_gaps.py):

1. Sample 500 posts per theme from raw_posts table, weighted toward recent 
   (last 90 days), from subreddits where that theme is plausible.
2. For each post, run an LLM call with the theme definition and ask:
   "Is this post primarily about [theme]? If yes, what words or phrases 
    in the post would be reliable indicators? Return JSON: 
    {relevant: bool, indicators: [strings] or null, reasoning: string}"
3. Filter to posts where relevant=true AND not currently keyword-matched.
4. Aggregate proposed indicators across posts. Rank by frequency.
5. Output: docs/recall_proposals_YYYY-MM-DD.md with top 30 candidates per 
   theme, example posts each, frequency, and a checkbox for human approval.
6. Approved candidates go through the standard keyword validation flow 
   (hand-coding 30 posts, precision check) before entering schema.

Model: GPT-4o-mini or Haiku. Run quarterly.
Stop conditions for /goal: the markdown report exists with proposals for 
all 6 themes, and a precision-check spec for each proposal.
```

This is probably the highest-value option in this whole document. It's the only one that meaningfully attacks recall.

---

### Tier 2 — Moderate complexity, bounded scope

#### 4.3 Bounded one-time snapshot studies (the arxiv pattern)

**Gap addressed:** Depth — the keyword tracker says volume; an LLM snapshot says what's actually happening.
**What it does:** On a small bounded corpus (~1,000–2,000 posts), use an LLM as the *primary* classifier across multiple dimensions that keywords can't access — attachment style, relationship stage, anthropomorphization level, emotional valence, etc. Produces a one-time study, not a tracked time series.
**Why it works:** This is what the *My Boyfriend is AI* paper did. At ~1,500 posts, LLM-on-everything costs ~$10 and the LLM can see the full corpus. The output is a snapshot characterization, not a trend line, so the LLM's wobbliness doesn't compound across dates.
**Why it's safe:** Lives entirely outside the live tracker. Different artifact, different methodology, different validation expectations. Could become a blog post or a short report.
**Cost:** $10–30 per study.
**Validation:** Document inter-rater reliability with a second model and a small hand-coded sample. Be honest about the reliability number (the arxiv paper reported Spearman 0.5 and called the work exploratory; same standard applies).

**When to consider this:** When you want to write something rich and qualitative about *one* subreddit or *one* theme. Not for "how is the discourse changing" — for "what does this community look like."

#### 4.4 Qualitative companion content

**Gap addressed:** Depth, presented alongside the chart.
**What it does:** Quarterly, run an LLM over a small sample (say 100 posts) of each theme's recent matches, generate a short qualitative summary of what the theme actually looks like at the post level. Publish next to the chart.
**Why it works:** Counts say "Romance posts are up 30%." This says "Romance posts in Q2 were heavily about long-term partner integration and AI memory updates after the Replika feature changes." That's the part readers actually need.
**Why it's safe:** Lives alongside the chart, not in it. Reads as journalism, not measurement. Doesn't pretend to be reproducible.
**Cost:** ~$5–10 per quarter.

**Implementation spec for Claude Code:**
```
- Quarterly cron: for each theme, pull 100 random matched posts from the 
  last 90 days.
- LLM call: "Summarize what these posts are about. What's the dominant 
  emotional register? What's the most common situation people are 
  describing? What's surprising or new compared to last quarter's 
  summary (provided)?"
- Output: web/content/quarterly_qualitative_YYYY-Q.md
- Display: as a collapsible section under each theme on the dashboard, 
  clearly labeled "Qualitative snapshot — LLM-summarized, not for 
  citation, regenerated quarterly."
```

#### 4.5 Emergence detection (themes outside the 6-theme schema)

**Gap addressed:** Novelty.
**What it does:** Quarterly, an LLM reads a random sample of recent posts (not filtered through current keywords) and reports themes that appear *prominent but not well-captured* by the current 6-theme schema. Human decides whether to add a theme, expand an existing one, or ignore.
**Why it works:** Keywords by construction can only find what they're looking for. Emergence — a new vocabulary appearing, a new relationship pattern, a new product moment — is structurally invisible to the keyword system. This is one of the few places where an LLM's open-ended reading is genuinely superior.
**Why it's safe:** Output is a research input, not a measurement. Adding a new theme is a methodology decision that goes through the existing schema-change process.
**Cost:** ~$15 per run. Quarterly.

**Implementation spec for Claude Code:**
```
- Sample 1,000 random recent posts across tracked subreddits.
- LLM call (single batched prompt or per-post): "Read these posts. What 
  themes or patterns appear meaningfully present? For each theme, list: 
  name, 1-sentence description, ~frequency in sample, example post IDs. 
  Then compare to this list of currently-tracked themes [paste the 6]. 
  Which present themes are NOT well-covered by the current list?"
- Output: docs/emergence_YYYY-Q.md
- Human review: triage into add / expand-existing / ignore. Document decision.
```

---

### Tier 3 — Only after Tier 1 has been running for 6+ months

#### 4.6 Hand-coding cross-validation at scale

If the watchdog and candidate-generation pipelines have proven stable and you trust the LLM's behavior in this domain, you can use an LLM to replicate hand-coding decisions on a larger sample — giving a real test of whether hand-coded precision numbers hold up at scale. This is genuinely useful but requires earned trust, which Tier 1 builds.

#### 4.7 Adversarial precision audit

A red-team LLM call specifically prompted to find the *worst* false positives in each keyword — the opposite of the "generous" audit that failed. Cheap and informative *if* you trust the model's judgment, which again Tier 1 establishes.

---

## 5. What NOT to do

Explicit, because the pull back toward these is strong:

- **Do not re-attempt LLM-as-filter on the full corpus.** It's the same architecture that just failed. Scale hasn't changed. Recall problem hasn't changed.
- **Do not put LLM-classified counts into the live chart.** The chart's value is reproducibility over time. LLM classification doesn't give you that.
- **Do not trust LLM-graded-by-LLM as validation.** External ground truth (hand-coding, adversarial check, behavioral signal) is the only valid check.
- **Do not add "Phase 2: AI-classifiable themes" back as a standing pipeline ambition.** A bounded one-off snapshot study (Tier 2, 4.3) is on the table. A standing pipeline is not.
- **Do not let any new LLM use proceed without answering all four questions in §3 explicitly.** Document the answers in the PR.

---

## 6. Suggested rollout sequence

If you decide to act on this:

1. **Now:** Retune the monthly drift watchdog prompt (§4.1). Cheap, fast, fixes a known half-broken thing.
2. **Next month:** Build the recall-gap pipeline (§4.2). This is the highest-value piece in this document. Run it once, hand-validate the proposals, decide whether to add any.
3. **Next quarter:** If §4.2 produced useful proposals, run it again. Consider adding the qualitative companion content (§4.4) as a low-cost depth layer.
4. **Six months out:** Consider emergence detection (§4.5) if the schema feels stale, or a bounded snapshot study (§4.3) if you want to write something deeper about a specific subreddit.
5. **Tier 3 stays closed for now.** Revisit only if Tier 1 has been running cleanly for 6+ months and you have specific reason.

---

## 7. Budget summary

| Use | Cost | Cadence | Annual |
|---|---|---|---|
| Drift watchdog (retuned) | ~$2.50/mo | Monthly | ~$30 |
| Recall candidate generation | ~$20 | Quarterly | ~$80 |
| Qualitative companion | ~$8 | Quarterly | ~$32 |
| Emergence detection | ~$15 | Quarterly | ~$60 |
| **Tier 1 + 2 total** | | | **~$200/year** |

For context, the failed integration cost ~$200 over a few weeks for no usable output. The above buys a year of additive use with structurally sound architecture. Whether all four are worth doing is a separate question; the watchdog alone is clearly worth it, and the recall-gap pipeline (§4.2) is the one I'd most recommend building.

---

## 8. Note on framing in public-facing docs

If any of these get built, the about-page changelog should describe each one accurately, with its specific role and limitations. The pattern that got us into trouble was claiming "LLM verification is rolling out" without specifying what it was verifying or how. Each of the above should be described in plain language: "Once a quarter we use an LLM to suggest keywords we might be missing; a human reviews and decides what to add." Not "LLM-augmented research."

The site's overall claim stays the same: this is a keyword-based tracker with documented limitations. LLM use, where it happens, is in supporting roles around the keyword system, not in the chart itself.
