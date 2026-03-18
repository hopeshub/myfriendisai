# Keyword Validation Pipeline Review

**Date:** March 16, 2026
**Scope:** Review of the pipeline in `analysis/keyword_validation/`
**Purpose:** Capture the main criticisms, risks, and recommended improvements for the current keyword discovery and validation workflow.

## Overall Assessment

The current pipeline is a strong step forward. It has the right overall shape:

**Discovery -> Validation -> Integration -> Monitoring**

That is the correct design for this problem. It treats keyword work as an ongoing system rather than a one-time brainstorm, and it separates candidate generation from acceptance into production. That is a major improvement over earlier, more ad hoc validation approaches.

The pipeline is also grounded in the right sampling frame. It assumes that subreddit selection establishes the AI companionship context, and that keywords should be evaluated for **theme fit within that context**, rather than being forced to prove AI-relatedness across the whole corpus. That design is much more defensible for this project.

That said, the current pipeline still has a few methodological weak points. None of them invalidate the approach, but they do matter if the methodology is going to be presented as rigorous and stable.

## What Looks Strong

### 1. The workflow is conceptually sound

The system has distinct phases for:

- discovering candidate terms
- validating whether those terms actually fit a target theme
- integrating only approved terms into production
- periodically checking whether active terms degrade over time

This is the right architecture for a keyword system that is meant to evolve with the discourse it tracks.

### 2. Manual precision review is the right anchor

The precision sampler is the strongest part of the pipeline. For this kind of task, human judgment is more trustworthy than a purely formulaic score. The key question is inherently interpretive:

> Does this keyword match the theme it is supposed to represent in real posts?

That question should be answered by reading examples, not by relying only on distributional statistics.

### 3. Monitoring is a major strength

Most keyword systems validate once and then silently decay. The existence of a health-check stage is one of the best aspects of this design. Language shifts, product changes, and community drift can all change keyword quality over time, so monitoring should be part of the methodology.

### 4. Volume and collision checks are useful supporting gates

The volume check and cross-theme check are good secondary tests. They help catch two real risks:

- keywords that are too rare to matter
- keywords that belong partly or mostly to a different theme

These checks should remain part of the pipeline.

## Main Criticisms

### 1. Discovery is partly circular

The biggest methodological weakness is in discovery.

The corpus-comparison script defines the positive corpus using posts already tagged by the current theme keyword set. That means the system is discovering new candidate language from posts identified by old keywords. In practice, this makes discovery path-dependent.

This is not fatal, but it does create a bias:

- the pipeline will be good at finding variations of what the current theme already captures
- the pipeline will be worse at finding language the current theme completely misses

In other words, the system is better at local expansion than true discovery.

### 2. The current sample size is too small for hard thresholds

The current validation rule uses a sample of 20 posts, with a 70% precision threshold. That is workable as a fast screen, but it is not very stable. On a sample this small, one or two borderline judgments can change the verdict.

This matters especially for:

- mid-precision terms
- terms with multiple senses
- terms concentrated in one subreddit
- terms where the theme boundary is inherently fuzzy

If the methodology is going to describe these thresholds as meaningful gates, the sample size should be a bit more robust for any keyword close to the decision boundary.

### 3. Ambiguity is currently under-modeled

The precision sampler uses `yes`, `no`, and `skip`. In practice, `skip` is acting as an ambiguity bucket, but those posts are excluded from the denominator.

That creates a risk: a keyword with many unclear cases can appear cleaner than it really is.

Ambiguous or hard-to-code examples are not noise in the evaluation process. They are a sign that the keyword may be semantically fuzzy, and the pipeline should preserve that information.

### 4. Cross-theme checking is useful but not yet strong enough to be definitive

The cross-theme check is a good idea, but it is still based on a small manual sample and a single best-fit theme label per post. That means it can flag obvious collisions, but it may miss more subtle overlap.

Some keywords really do sit between themes, especially in areas like:

- romance vs sexual ERP
- therapy vs dependence
- rupture vs consciousness

The current check is best treated as a warning layer, not a strong guarantee that a keyword is truly theme-specific.

### 5. Subreddit concentration is visible but not yet formalized as a decision rule

The pipeline includes per-subreddit breakdowns, which is good, but subreddit concentration is not yet elevated into a formal gate.

This matters because a keyword can look precise overall while still being fragile if:

- most of its hits come from one subreddit
- that subreddit has unusual posting norms
- that subreddit contains recurring structured content, bot listings, or template-style language

Without a concentration rule, some accepted keywords may reflect platform-specific artifacts more than general discourse within the theme.

### 6. The process is documented, but the operational record is still thin

The README describes a good system, but the actual candidate ledger is not yet populated. That means the pipeline is promising, but it has not yet demonstrated a full audit trail from:

- discovered candidate
- validation evidence
- decision
- production status
- later degradation or retention

For methodology purposes, the audit trail matters almost as much as the validation logic itself.

## Recommendations

## Priority 1: Reduce circularity in discovery

Do not rely on a single discovery source.

Keep corpus comparison, but add at least one additional discovery stream that is less dependent on the current keyword set. Good options:

- hand-read seed samples from target subreddits
- random samples from relevant subreddits filtered by post type or date, not current tags
- emergence monitoring for recent language shifts

Recommended framing:

- **Corpus comparison** finds terms near the current theme boundary
- **Independent sampling** finds language outside the current boundary

Using both gives the discovery process a much stronger methodological footing.

## Priority 2: Move to a two-stage validation model

Use the current 20-post review as a **screening round**, not the final word.

Recommended structure:

- **Stage 1:** 20-post screen
- **Stage 2:** 40-50 post review for any keyword that is promising, borderline, or likely to be important

Suggested policy:

- `>= 80%` on the first pass: likely keep, unless concentration/collision issues appear
- `60-79%`: mandatory second-round review
- `< 60%`: usually reject, unless there is a very strong theoretical reason to continue

This keeps the workflow lightweight while making final decisions more stable.

## Priority 3: Replace `skip` with explicit ambiguity

Treat ambiguity as data.

Recommended response options:

- `yes`
- `no`
- `ambiguous`

Then choose one explicit scoring rule and document it:

- count ambiguous as half-credit, or
- report it separately and require low ambiguity for production keywords

Either option is better than letting ambiguity disappear from the precision score.

## Priority 4: Formalize subreddit concentration checks

Add a visible concentration rule to the validation criteria.

Possible forms:

- flag any keyword where one subreddit contributes more than 50% of 1-year hits
- flag any keyword where the top two subreddits contribute more than 75%
- require a written note when a keyword is accepted despite high concentration

This does not mean highly concentrated keywords must be rejected. Some may be legitimate. But concentration should be treated as a methodological property, not just descriptive output.

## Priority 5: Store reasons for acceptance and rejection

Every reviewed keyword should carry one short decision note.

Suggested fields:

- dominant false-positive pattern
- known noisy subreddit, if any
- whether the term is self-qualifying or context-dependent
- whether the term is accepted, borderline, or rejected
- why

This makes the system much easier to defend later. A methodology becomes more credible when it can explain not only what was accepted, but also what was deliberately excluded and why.

## Priority 6: Treat cross-theme collision as a warning tier

Keep the collision check, but frame it correctly.

Recommended interpretation:

- **No collision:** keyword is likely theme-stable
- **Moderate collision:** keyword may still be useful, but should be documented as mixed
- **Strong collision:** reject or place only in the theme where it performs best

This is better than pretending that a small sample can definitively sort every mixed term into a single clean category.

## Priority 7: Build the candidate ledger into the actual workflow

The `candidates.csv` file should become the operational heart of the system.

Each keyword should move through clear states:

- discovered
- screened
- reviewed
- accepted or rejected
- active
- degraded or retired

And each row should preserve:

- source
- date
- validation score
- ambiguity level
- concentration notes
- collision notes
- final decision

That would turn the current pipeline from a good set of scripts into a reproducible research process.

## Suggested Methodology Framing

If this system is described in the public methodology, the strongest honest framing is:

1. The project defines a companion-discourse sampling frame through subreddit selection.
2. Candidate keywords are discovered using a mix of statistical comparison and manual review.
3. Keywords are validated by reading random matched posts and judging whether the match actually represents the intended theme.
4. Keywords are only added if they show adequate precision, sufficient volume, and acceptable thematic specificity.
5. Active keywords are periodically re-checked because discourse changes over time.

That framing is strong, transparent, and appropriate for the actual design.

## Bottom Line

The current pipeline is viable.

Its overall architecture makes sense, and it is much stronger than earlier attempts that tried to validate keywords globally across unrelated contexts. The main things that still need tightening are:

- reducing discovery circularity
- making validation more stable around the decision boundary
- treating ambiguity as data
- formalizing subreddit concentration
- preserving a stronger audit trail

With those improvements, this could become a very defensible methodology for identifying and maintaining theme keywords in this project.
