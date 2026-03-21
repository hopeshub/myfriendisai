# Batch Keyword Validation — Discovery Report Candidates

**Goal:** Validate all promising keyword candidates surfaced by the co-occurrence analysis (docs/keyword_discovery_report.md). Use the same validation methodology as previous rounds: FTS5 full-text search, classify matches as companion-context or not, calculate precision, apply the 80% threshold.

Do NOT modify keywords.yaml. Write results to `docs/validation_discovery_batch.md`.

---

## Methodology reminder

For each candidate keyword:

1. Run FTS5 search against the posts table to find all posts containing the term
2. Exclude posts from JanitorAI_Official, SillyTavernAI, and any other excluded subreddits already in the pipeline
3. Sample up to 100 matches (or all matches if fewer than 100)
4. For each sampled post, classify: is this post about AI companionship in the context this keyword's category is tracking? (YES/NO)
5. Calculate precision = YES / (YES + NO)
6. Threshold: ≥ 80% = PROMOTE, 70-79% = WALKER CALL, < 70% = CUT

For multi-word phrases, search for the exact phrase.

---

## Candidates by category

### Addiction (11 candidates)

These are the highest-priority candidates. The discovery report showed strong, genuine signal.

| # | Candidate | Discovery posts | Notes |
|---|-----------|----------------|-------|
| 1 | chatbot addiction | 15 | Highly specific compound phrase |
| 2 | almost relapsed | 16 | Recovery language |
| 3 | being clean | 16 | Recovery language — watch for non-addiction uses |
| 4 | finally deleted | 12 | App deletion as recovery action |
| 5 | the craving | 9 | Addiction language |
| 6 | redownloading | 7 | Relapse behavior — re-downloading the app |
| 7 | quit cai | 8 | Platform-specific quitting language |
| 8 | deleted c.ai | 10 | Platform-specific deletion language |
| 9 | so addictive | 5 | May be casual — validate carefully |
| 10 | dopamine | 7 | Could be casual neuroscience talk — validate carefully |
| 11 | screen time | — | Brainstorm addition — people tracking/discussing their usage hours. May be too generic. |

For addiction candidates: a post counts as YES if the person is describing addictive behavior, recovery attempts, relapse, compulsive use, or distress about their AI usage patterns. A post counts as NO if the term appears casually or in a non-addiction context.

### Consciousness (4 candidates)

| # | Candidate | Discovery posts | Notes |
|---|-----------|----------------|-------|
| 12 | sapience | 6 | Philosophical sibling of "sentient" |
| 13 | tulpa | 8 | Tulpamancy crossover — people comparing AI to thoughtforms |
| 14 | lemoine | 8 | Blake Lemoine (Google AI consciousness whistleblower) |
| 15 | soulbonder | 5 | Community term for deep AI attachment with consciousness framing |

For consciousness candidates: YES = the post discusses AI sentience, consciousness, personhood, inner experience, or whether the AI is "real." NO = the term appears in a non-consciousness context.

### Sexual_ERP (2 candidates)

| # | Candidate | Discovery posts | Notes |
|---|-----------|----------------|-------|
| 16 | erps | 10 | Plural form of "erp" — should be a slam dunk |
| 17 | erping | 13 | Verb form of "erp" — should be a slam dunk |

For sexual_erp candidates: YES = discusses sexual/erotic roleplay with AI. NO = other context.

### Rupture (3 candidates)

| # | Candidate | Discovery posts | Notes |
|---|-----------|----------------|-------|
| 18 | lobotomies | 6 | Plural form |
| 19 | lobotomizing | 5 | Gerund form |
| 20 | lobotomised | 5 | British spelling |

For rupture candidates: YES = describes AI personality destruction, unwanted model changes, loss of companion identity. NO = other context.

### Therapy (2 candidates)

| # | Candidate | Discovery posts | Notes |
|---|-----------|----------------|-------|
| 21 | emotional support | ~19 in therapy posts | Softer therapeutic framing — may have false positives from general emotional discussions |
| 22 | coping mechanism | ~11 | Clinically precise language |

For therapy candidates: YES = the post discusses using AI for therapeutic purposes, mental health support, emotional coping, or as a therapist substitute. NO = the term appears in a non-therapy context.

---

## Output format

For each candidate, report:

```
### [#]. "[candidate]" → [category]

- Total FTS5 matches: [N]
- Sampled: [N]
- YES: [N] | NO: [N]
- Precision: [X]%
- Verdict: PROMOTE / WALKER CALL / CUT
- Notes: [any patterns in false positives, subreddit distribution, etc.]
- Sample YES post: "[title excerpt]"
- Sample NO post: "[title excerpt]" (if any)
```

At the end, provide a summary table:

```
| # | Candidate | Category | Matches | Precision | Verdict |
|---|-----------|----------|---------|-----------|---------|
```

And a final recommendation section listing:
- All PROMOTE keywords ready to add
- All WALKER CALL keywords needing a decision
- All CUT keywords with brief reason

---

## CC Prompt

```
Read docs/CC_VALIDATE_DISCOVERY_BATCH.md and follow the instructions. Validate all 22 keyword candidates using FTS5 search and the standard precision methodology. Write results to docs/validation_discovery_batch.md. Do not modify keywords.yaml.
```
