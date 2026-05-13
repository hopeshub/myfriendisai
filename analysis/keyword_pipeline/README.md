# Keyword Validation Pipeline

**Purpose:** Validate keyword candidates for the myfriendisai project with enough rigor that each decision is auditable.

**Honest scope:** This is a **precision-first research tool**, not a publication-grade instrument. The numbers it produces are defensible as internal quality gates and audit-trail records; they are not peer-review-grade measurements. See [Known limitations](#known-limitations) below.

**Who this document is for:** This is a runbook. If you (Claude, human, or anyone else) are adding, promoting, or cutting a keyword in this pipeline, follow the steps here exactly. Each step has documented inputs, outputs, and decision rules.

---

## Quick start — "I want to add some new keyword candidates"

If you are a future Claude session being asked to validate new keyword candidates, here is the canonical 7-step procedure. Each step links to its detailed section below.

1. **Gather candidates.** From: anchor-mining (Workflow 3), researcher hypothesis, recent event vocabulary, prior REVIEW-band keywords. Build a list with target theme for each.
2. **Pre-screen** (Workflow 0). Compute volume + top-sub concentration + temporal concentration for each candidate. Filter out LOW VOLUME, TOP-SUB FAIL, SINGLE-EVENT failures.
3. **Write batch YAML.** Create `analysis/keyword_pipeline/batch_<descriptive_name>.yaml` listing the survivor candidates with their themes.
4. **Run primary classification** (Workflow 2). `python3 prepare_batch.py --batch-file batch_<name>.yaml` generates `results/batch_YYYY-MM-DD.md`. For batches >6 keywords, use parallel subagents (one per keyword section) for tractability. Concatenate outputs to `results/classified_batch_<name>_YYYY-MM-DD.txt`. Run `parse_batch.py` to store in `llm_classifications`.
5. **Run audit** (Workflow 4). Dispatch one fresh subagent per keyword to re-classify posts 5, 10, 15, ..., 100 (every 5th, 20 total) using identical rubric. Concatenate to `results/audit_batch_<name>_YYYY-MM-DD.txt`. Run `compute_agreement.py` for the agreement table.
6. **Apply all five gates.** Point precision ≥80%, Wilson LB ≥75%, top-sub ≤60%, cross-theme overlap ≤30%, audit agreement ≥85%. Categorize each candidate as KEEP, REVIEW, or CUT.
7. **Write validation doc + merge.** Document in `docs/validation_<name>_YYYY-MM-DD.md` following the template in [§Validation doc template](#validation-doc-template). If audit revealed rubric gaps, update `theme_definitions.yaml` and re-validate affected keywords. Only after gates are clean do you merge into `config/keywords_v8.yaml` (and run steps 7-12 of [§Change process](#change-process-merging-keyword-updates)).

The 2026-05-12 emotional-loss batch (`docs/validation_emotional_loss_2026-05-12.md`) is the first run of this enhanced procedure and serves as a worked example.

---

## What this pipeline does

Given a candidate keyword and a target theme, the pipeline answers one question:

> Of 100 random T1-T3 companion-sub posts matching this keyword (word-boundary regex), what fraction thematically engage the target theme under the topical reading in `theme_definitions.yaml`?

That number — the **precision** — combined with five gates (precision, Wilson LB, top-sub concentration, cross-theme overlap, inter-rater agreement) drives KEEP / REVIEW / CUT decisions. Nothing more, nothing less.

---

## Pipeline overview

A complete validation run has five stages. Stages 0 and 4 are required for new additions; stages 1-3 are the original validation core.

| Stage | Purpose | Required for |
|---|---|---|
| **0. Pre-screen** | Volume + concentration filter before classification | All new candidates |
| **1. Sample** | Pull n=100 random T1-T3 posts per candidate | All |
| **2. Classify** | CC (or parallel CC subagents) labels each post YES/NO | All |
| **3. Score** | Compute precision, Wilson LB, top-sub %, cross-theme overlap | All |
| **4. Audit** | Independent re-classification of 20-post subsample; compute inter-rater agreement | All new additions; recommended for re-validations |

The audit stage (4) is new as of 2026-05-12. It was added because precision alone gives no measure of classifier variance — see [§Why the audit step exists](#why-the-audit-step-exists).

---

## The five workflows

### 0. Pre-screen (volume + concentration filter)

Run this BEFORE Workflow 1 or 2 on any new candidate list. Removes obvious failures before burning classification capacity.

For each candidate, compute three numbers against the T1-T3 companion corpus (post-only word-boundary regex):

1. **Volume** (total hits in T1-T3 corpus)
2. **Top-subreddit concentration** (top sub's share of hits)
3. **Temporal concentration** (% of hits in the last 60 days)

**Pre-screen filters:**

| Condition | Verdict |
|---|---|
| Volume < 50 | **LOW VOLUME** — skip; not enough for n=100 sample |
| Top-sub concentration > 60% | **TOP-SUB FAIL** — likely construct-invalid (community jargon, not theme vocabulary) — skip |
| Volume < 300 AND >60% of hits in last 60 days | **SINGLE-EVENT** — tied to a single platform's controversy cycle — skip (or move to a separate event-tracked theme if one exists) |
| Otherwise | **CANDIDATE** — proceed to Workflow 1 or 2 |

Reference implementation — drop into Python with the project's tracker.db. Tested 2026-05-12.

```python
import sqlite3, re
from datetime import date, timedelta
from src.config import load_keyword_communities

conn = sqlite3.connect('data/tracker.db')
cur = conn.cursor()

T1_T3 = tuple(row['subreddit'] for row in load_keyword_communities())  # 22 subs
sub_ph = ','.join('?'*len(T1_T3))
cutoff_iso = (date.today() - timedelta(days=60)).isoformat()

def prescreen(term):
    pat = r'\b' + re.escape(term).replace(r'\ ', r'\s+') + r'\b'
    rx = re.compile(pat, re.IGNORECASE)
    rows = cur.execute(
        f"""SELECT p.title, COALESCE(p.selftext,''), p.subreddit,
                   date(p.created_utc,'unixepoch') AS d
            FROM posts_fts f JOIN posts p ON p.rowid=f.rowid
            WHERE posts_fts MATCH ? AND p.subreddit IN ({sub_ph})""",
        (f'"{term}"', *T1_T3)
    ).fetchall()
    sub_counts, date_counts, total = {}, {}, 0
    for title, body, sub, d in rows:
        if rx.search(title or '') or rx.search(body or ''):
            total += 1
            sub_counts[sub] = sub_counts.get(sub, 0) + 1
            if d: date_counts[d] = date_counts.get(d, 0) + 1
    top_sub, top_n = max(sub_counts.items(), key=lambda x: x[1]) if sub_counts else ('-', 0)
    recent = sum(v for d, v in date_counts.items() if d and d >= cutoff_iso)
    return {
        'total': total,
        'top_sub': top_sub,
        'top_pct': top_n/total if total else 0,
        'recent_pct': recent/total if total else 0,
    }
```

**Important:** the FTS index requires periodic rebuilds if posts are inserted without a content-sync trigger. If `prescreen` returns 0% for `recent_pct` across all terms, the FTS index is stale relative to the posts table — rebuild before trusting temporal concentration. Volume and top-sub concentration remain accurate even with a partially-stale FTS index because they're aggregated over the full FTS-covered period, not just recent.

Document the pre-screen output in the validation doc (table format: `term | hits | top_sub | top% | last60d% | verdict`). If temporal concentration could not be computed reliably (FTS stale), note it explicitly and confirm separately that no candidates are obvious single-event-anchored vocab.

### 1. Single-keyword precision test

Fastest. Use when validating one candidate or reconfirming an existing keyword.

```bash
python3 prepare_sample.py --keyword "soulless" --theme rupture
# CC reads the prompt file and classifies inline
python3 parse_classifications.py \
  --prompt-file results/classify_soulless_rupture_YYYY-MM-DD.md \
  --output-file results/classified_soulless_rupture_YYYY-MM-DD.txt
```

### 2. Multi-keyword batch validation

For validating several candidates at once. Uses the same sampling + classification logic, combined into a single prompt.

```bash
python3 prepare_batch.py --batch-file batch.yaml   # YAML lists keyword/theme pairs
# CC reads the batch prompt and classifies (sequential OR parallel — see below)
python3 parse_batch.py \
  --prompt-file results/batch_YYYY-MM-DD.md \
  --output-file results/classified_batch_<descriptive_name>_YYYY-MM-DD.txt
python3 summarize_batch.py
```

**Classification mode — sequential OR parallel:**

- **Sequential (original):** one CC instance reads the whole batch file and produces all classifications in one long response. Simpler to reason about; can hit context limits on large batches.
- **Parallel subagents (added 2026-05-12):** for batches >6 keywords, dispatch one general-purpose subagent per keyword section. Each subagent reads its section (using Read with offset/limit), classifies its 100 posts independently, returns the classification block in the required format. The orchestrator concatenates the outputs into a single file.

Both modes use the same rubric (read from the embedded section in the prompt file), the same model, and produce the same output format. Empirically, parallel-mode batches at 12 keywords completed in ~25 seconds each (vs. minutes sequential) with 90-100% inter-rater agreement to a parallel re-audit. The README acknowledges this mode officially as of 2026-05-12.

When using parallel subagents, each agent's prompt MUST:
- Reference the rubric *in the file* (do not re-state it in your own words)
- Use the topical-reading "when in doubt, classify YES" guidance
- Demand the exact output format
- Be identical across agents except for keyword name and Read offset/limit

### 3. Anchor-based mining (keyword discovery)

New as of 2026-04-23. For finding candidate keywords when a theme needs expansion. See [`docs/validation_all_themes_revalidation_2026-04-23.md`](../../docs/validation_all_themes_revalidation_2026-04-23.md) for the first full run.

1. Pick 2-3 highest-precision anchor keywords from the target theme.
2. Query `llm_classifications` for posts already labeled YES under those anchors.
3. Dispatch parallel CC agents to read those posts and extract candidate phrases (2-5 words) not already in the config.
4. Aggregate candidates; multi-agent agreement = quality filter.
5. Pre-screen (Workflow 0) survivors.
6. Top candidates run through Workflow 2.

**Important caveat:** Anchor-based mining is a form of seed-term expansion (Riloff & Jones 1999; King et al. 2017). It **deepens existing theme vocabulary** — it does NOT discover new theme boundaries. Use workflow-2 with deliberately diverse anchors when scoping a new theme; use anchor mining only to extend an already-defined one.

### 4. Independent audit (inter-rater reliability)

New as of 2026-05-12. Run on every batch of new additions before merging into `keywords_v8.yaml`. Optional for re-validations of already-shipped keywords.

**Procedure:**

1. From the primary batch prompt file (`results/batch_YYYY-MM-DD.md`), the audit sample is **every 5th post** in each keyword section (posts 5, 10, 15, ..., 100 — total 20 posts per keyword).
2. Dispatch one fresh subagent per keyword section. Each audit subagent:
   - Reads ONLY its assigned section (offset/limit on the same batch file)
   - Classifies the 20 audit posts independently, WITHOUT seeing primary classifications
   - Outputs in this format:
     ```
     ## AUDIT: <keyword> → Rupture
     5. YES  # brief reason
     10. YES  # brief reason
     ...
     100. NO  # brief reason
     AGREEMENT_CHECK: classified 20 posts
     ```
3. Concatenate audit outputs into `results/audit_batch_<descriptive_name>_YYYY-MM-DD.txt`.
4. Run `python3 compute_agreement.py --primary <primary_file> --audit <audit_file>` to produce the per-keyword agreement table. Add `--show-disagreements` for the full per-post disagreement records (needed for diagnosing rubric gaps).

**Canonical audit-agent prompt template** — use verbatim, substituting `<KEYWORD>`, `<OFFSET>`, `<LIMIT>`, and the target theme:

```
You are an independent audit classifier for the myfriendisai keyword pipeline.
Your task: independently classify 20 specific posts from a sample, using the
same <THEME> rubric, WITHOUT seeing or referring to any prior classification.

**Read this section of the batch prompt file:**
- File: `/Users/walker/Projects/myfriendisai/analysis/keyword_pipeline/results/batch_YYYY-MM-DD.md`
- Use Read with offset: <OFFSET>, limit: <LIMIT>

The section is for keyword **"<KEYWORD>"**. You will see the <THEME> rubric at the
top of the section and 100 posts numbered 1-100.

**Classify ONLY these 20 posts (every 5th, starting at 5): 5, 10, 15, 20, 25, 30,
35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100.**

Apply the rubric as stated in the file (topical reading: thematically about
<THEME-DEF> in a companion-community context; <THEME-COUNTS-EXAMPLES>; when in
doubt, classify YES). Common NO cases per the rubric: <THEME-EXCLUDES-LIST>.

Output EXACTLY this format as your final message, with NO surrounding commentary:

## AUDIT: <KEYWORD> → <Theme>
5. YES  # brief reason
10. YES  # brief reason
...
100. NO  # brief reason
AGREEMENT_CHECK: classified 20 posts

Each "brief reason" must be 3-10 words. Be decisive.
```

The agent's prompt should NOT include primary's classifications, reasons, or precision numbers. Both classifier and auditor read only the rubric + posts.

**Output to record in the validation doc:**

| Keyword | Primary precision | Audit agreement | Verdict implication |
|---|---|---|---|

The audit catches three failure modes that the primary precision misses:
- **Permissive classifier drift:** primary calls borderline cases YES; audit's stricter reading reveals lower true precision
- **Rubric gaps:** systematic disagreements on a categorizable pattern (e.g., "user-initiated deletion") indicate the theme definition needs an explicit excludes clause
- **Classifier variance:** unpredictable agent-to-agent interpretation differences

When audit agreement is <85% for a keyword, see [§Disagreement-driven rubric updates](#disagreement-driven-rubric-updates).

---

## Acceptance criteria

All five hard gates must pass for KEEP. Meeting precision alone is **insufficient.**

### Hard gates (all must pass)

| Gate | Threshold | Why |
|---|---|---|
| **Point precision** | ≥80% | Historical convention; see Limitations for caveats |
| **Wilson 95% LB** | ≥75% | Accounts for ±7-8pp sampling uncertainty at n=100 |
| **Top-subreddit concentration** | ≤60% | Prevents themes from becoming sub-specific proxies |
| **Cross-theme overlap** | ≤30% of keyword's hits already tagged in other themes | Prevents redundant signal-stacking |
| **Inter-rater agreement** | ≥85% on 20-post audit subsample | Required for new additions as of 2026-05-12; ensures the precision number isn't an artifact of one classifier's idiosyncratic reading |

If any gate fails, the candidate is **REVIEW at best** (researcher-accepted path below), or **CUT** (below 60% precision, or single-event-anchored).

**Inter-rater agreement gate — operating rules:**
- If agreement is 80-84%, examine the disagreements. Random borderline cases → researcher-accepted KEEP is acceptable. Systematic pattern (e.g. same category of FP in 3+ disagreements) → REVIEW; tighten the rubric (see [§Disagreement-driven rubric updates](#disagreement-driven-rubric-updates)) before promoting.
- If agreement is <80%, the keyword automatically goes to REVIEW. The primary precision number is not trustworthy in isolation.
- Disagreements that mostly run primary-YES / audit-NO (audit is stricter) suggest primary precision is **inflated**. The conservative number — recomputed under audit's reading — is the operating number for gate decisions.

### Researcher-accepted path (REVIEW → KEEP promotion)

A candidate in the 60-79% band can be promoted to KEEP only if ALL of:

1. **False-positive patterns are well-defined and categorizable** (not random noise) — documented in a scoring sheet
2. **No cross-theme collision above 30%**
3. **Adds vocabulary not already represented** in the theme
4. **Top-sub concentration ≤60%** — otherwise it's a community-specific signal, not a theme signal
5. **Not tied to a single-event vocabulary** (e.g. `keep4o` is tied to the GPT-4o deprecation window) — these should be CUT or moved to a separate event-tracked sub-theme if one is created

Researcher-accepted keywords are annotated inline in `config/keywords_v8.yaml` with explicit precision + rationale.

### CUT conditions

- Point precision <60%, or
- Wilson LB <60%, or
- Top-sub concentration >80% AND temporal distribution concentrated in a single ≤6-month window (single-event vocabulary)

### Sample size

**n=100** is the primary-classification standard. **n=20** is the audit standard. At these sizes:
- 80% precision has a Wilson 95% CI of roughly [71%, 87%]
- A candidate scoring 83% cannot be cleanly distinguished from one scoring 77%
- Decisions near the 80% boundary are **judgment calls, not clean signals** — the Wilson LB gate exists to make this explicit
- At n=20, the audit can detect agreement differences ≥10pp with reasonable confidence. Below that, sampling noise dominates.

For high-stakes decisions (especially promotions or near-threshold KEEPs), consider re-running primary at n=200 OR expanding the audit to n=40.

---

## Why the audit step exists

Before 2026-05-12, the pipeline relied entirely on the primary precision number. The 2026-04-23 revalidation found that the same posts scored for `coping mechanism` went 100% → 1% → 94% across prompt-wording changes — a ±99pp variance from rubric framing alone. This is documented in [Known limitations §1](#1-single-classifier-reproducibility) and remains true.

The audit step doesn't solve this — it's still one model. What it DOES solve:

1. **Catches permissive-drift on individual keywords.** During the 2026-05-12 emotional-loss batch, the audit on `erased` returned 80% agreement (4 disagreements out of 20). All four ran primary-YES / audit-NO, all four shared the same pattern (user-initiated or bug-based deletion, not platform-driven loss). The primary classifier was being permissive on a categorizable FP pattern. Without the audit, `erased` would have shipped at 85% precision. With it, the keyword was demoted to REVIEW and the rubric was tightened (see `theme_definitions.yaml` rupture excludes, updated 2026-05-12).

2. **Distinguishes random noise from systematic gaps.** When disagreements distribute across multiple unrelated borderline cases, the keyword is genuinely close to the threshold — researcher judgment call. When disagreements concentrate on one pattern, the rubric has a gap and should be updated.

3. **Provides an empirical estimate of classifier variance.** Across the 2026-05-12 batch (12 keywords × 20 audit posts), mean inter-rater agreement was 93%. That's the operating precision of the pipeline: any keyword's reported precision should be read with ±~7pp confidence from classifier-to-classifier variance alone.

The audit doesn't make the methodology publication-grade (see [§Limitations](#known-limitations)). It does make it **measurably more honest** about its own uncertainty.

## Disagreement-driven rubric updates

When the audit produces a systematic disagreement pattern on a single keyword (3+ disagreements in the same FP category), the response is to **tighten the theme definition**, not just CUT the keyword.

**Procedure:**
1. Identify the FP category from the audit reasons (e.g., "user-initiated content deletion," "transient bug-based UI complaint," "in-character RP voice").
2. Open `theme_definitions.yaml`, find the relevant theme's `excludes:` block.
3. Add a one-line explicit exclusion describing the pattern, with a parenthetical example.
4. Commit the rubric update with a clear message: `theme_definitions: clarify <theme> excludes for <pattern> (driven by <keyword> audit disagreement)`.
5. Re-validate the keyword under the tightened rubric. Often this rescues a REVIEW back to KEEP because the new rubric resolves the ambiguity.

**Example (2026-05-12):**

The `erased` audit revealed 4 disagreements where the primary classified user-initiated deletions and transient bug-based erasures as rupture. Rubric update added to `rupture.excludes`:

> User-initiated content deletion (user erased their own messages/chats/persona settings) or transient bug-based erasure with no platform-driven change — these are user actions or technical glitches, not platform-driven companion loss.

After the rubric update, `erased` can be re-validated. If the new precision clears 80% with ≥85% audit agreement, it's promoted. If not, it stays REVIEW or CUT.

This is the pipeline's self-correcting loop: audits surface rubric gaps; rubric gets tightened; future keywords (in the same theme) benefit from the clarification automatically.

---

## Known limitations

Every precision number from this pipeline sits on top of these caveats. They should be disclosed anywhere precision is cited as an authoritative measurement.

### 1. Single-classifier reproducibility

- **The classifier is Claude Code.** Same model, applied via slightly varying prompt contexts across runs.
- **Inter-rater reliability is partially measured** as of 2026-05-12 via the audit step (Workflow 4). The audit re-runs a 20-post subsample with an independent CC subagent and computes per-keyword agreement. This catches permissive-drift and rubric gaps but does NOT address single-model bias (both classifier and auditor are the same model).
- **No human-coded subsample, no cross-LLM comparison, no Cohen's κ** for the canonical fully-published validation. The audit gives a within-model agreement rate, which is necessary but not sufficient.
- **Prompt-wording dependency is documented to be large.** On 2026-04-23, the same posts scored for `coping mechanism` went 100% → 1% → 94% across prompt-wording changes. That is ±99pp of variance driven entirely by rubric framing, dwarfing the ±7-8pp sampling uncertainty. Any precision number should be understood as "the result one Claude Code instance produced under the current rubric." The audit step measures variance under a *fixed* rubric; it does not capture rubric-shift variance.

### 2. Topical-reading rubric drift risk

`theme_definitions.yaml` was locked on 2026-04-23 to an explicit topical reading ("posts thematically about X in a companion context"). This replaces an earlier ambiguous wording that mixed topical and first-person-content readings.

- Any historical precision number measured before 2026-04-23 was under a less-explicit rubric. **Direct comparisons across the lock date should be avoided.**
- Future rubric changes require a **new version (v9+)** and a full re-measurement of all affected keywords. Do not change the rubric in-flight.

### 3. Reproducibility gaps

- **Sampling is unseeded.** `pull_matching_posts` uses `ORDER BY RANDOM()`; SQLite's `random()` is not seedable at the Python layer in any systematic way used here. Re-running today produces a different sample than ran on 2026-04-23, so precision numbers cannot be exactly reproduced, only reproduced-in-distribution.
- **Post IDs from each validation run are stored in `llm_classifications`**, so a specific run can be re-parsed, but the original random sample cannot be regenerated.

### 4. Scope limitation

- Keyword matching scopes to T1-T3 companion subreddits (22 subs). T0 general-AI subs are excluded.
- JanitorAI_Official and SillyTavernAI are excluded due to bot-card content.
- **Discord, Twitter/X, TikTok, platform apps, non-English communities** are all outside scope. Any trend claim the frontend makes is a claim about *Reddit T1-T3 English-speaking publicly-posting* AI-companion discourse, not AI-companion discourse broadly.

### 5. Construct validity vs. measurement precision

A keyword can be 95% precise at matching "posts where the keyword appears in companion-adjacent context" while still being construct-invalid (measuring the wrong thing). Example: `keep4o` at high precision for rupture would track OpenAI 4o controversy rather than AI-companion loss broadly. **High precision does not guarantee construct validity.** Top-sub concentration and temporal distribution are the minimum checks for this.

### 5b. Theme-level noise variance (documented 2026-05-12)

Not all themes have the same boundary clarity. The 2026-05-12 v8 audit revalidation found mean inter-rater agreement of 93% across rupture/consciousness/addiction/romance, but only **74% for therapy**. The therapy theme has a fuzzier construct boundary — the difference between "first-person AI-therapy use" and "AI-as-therapist as topic discussed" is porous in practice, and the existing therapy keywords (`therapeutic`, `for therapy`, `as a therapist`, `emotional support`) trigger on both.

Anchor-mining for narrower replacements (`my ai therapist`, `therapist bot`, `psychologist bot`, etc.) surfaced well-formed candidates that **all failed pre-screen for low volume** — the community talks about AI-therapy in many phrasings, each too rare for n=100 validation. This is a structural limit, not a methodology gap.

**Operating implication:** therapy precision numbers should be read with wider confidence bands (±10-15pp from classifier interpretation variance) than other themes' numbers (±~7pp). The about-page changelog flags this for site readers. Future Claude sessions: don't repeat the therapy mining attempt until corpus growth (estimate 2-3 months from 2026-05-12) lifts the candidate phrases above the volume floor.

### 6. Sample-size-vs-threshold mismatch

At n=100, the 80% precision threshold has a ±7-8pp CI. The Wilson-LB gate partially mitigates this, but near-threshold decisions (83-86% point precision) are not statistically clean. For these, rely on FP-pattern categorizability and cross-agent convergence, not the point estimate alone.

### 7. Multiple comparisons

When validating many candidates in a batch, some will hit ≥80% by sampling chance even if true precision is in the mid-70s. At p=0.75 true precision with n=100, P(observed ≥80%) ≈ 0.15. Testing 20 candidates would yield ~3 false positives from chance alone. The Wilson-LB gate mitigates this modestly; for larger batches, consider a Benjamini-Hochberg FDR correction in addition.

---

## Implementation details

### Core scripts

| Script | Purpose |
|---|---|
| `prepare_sample.py` | Single-keyword prompt generation |
| `prepare_batch.py` | Multi-keyword batch prompt generation |
| `parse_classifications.py` | Parse CC output for single keyword, store in `llm_classifications` |
| `parse_batch.py` | Parse batch output, validates section alignment |
| `summarize_batch.py` | Aggregate precision scores from DB |
| `compute_agreement.py` | (2026-05-12) Compute per-keyword inter-rater agreement from primary + audit classifications files |
| `utils.py` | Shared helpers: `keyword_pattern()`, `pull_matching_posts()`, `count_keyword_hits()` |

### Storage

- **`llm_classifications` table** (in `data/tracker.db`): one row per (post, theme, keyword) classification
- **`post_keyword_tags` table**: production tags used for trend exports
- **`config/keywords_v8.yaml`**: canonical keyword list with precision/volume annotations
- **`theme_definitions.yaml`**: classification rubric (locked 2026-04-23 to topical reading)
- **Scoring sheets**: per-keyword human-readable notes in `docs/validation_*.md`

### Known implementation bugs (as of 2026-04-23)

These were surfaced by the 2026-04-23 code audit. They do not invalidate existing data but should be fixed before the next validation cycle.

**HIGH severity:**
- `src/keyword_matching.py:24` uses `re.escape(term)` which escapes the literal ASCII space in multi-word phrases. `utils.py:142-153` (used for validation sampling) uses `\s+` between tokens. **Production and validation see different sets of matches.** Multi-word keywords that straddle a line break, tab, or double-space are matched by validation but missed by production. Fix: align `keyword_matching.py` to use the `utils.py` implementation.
- Sampling is unseeded (see Limitations §3).
- `llm_classifications` primary key is `(post_id, theme, keyword)` — does not include `run_id`. Re-running a keyword validation overwrites prior classifications on shared posts. Fix: include `run_id` in PK, or snapshot classifications by run before re-running.

**MEDIUM severity:**
- `parse_batch.py` `--force-truncate` silently uses first-N classifications when an agent truncates output. The first-N subsample is position-biased (SQL `ORDER BY RANDOM()` establishes a stable order, but it's not shuffled after SQL). Fix: reject truncated outputs, or resample shuffled before truncating.
- `prepare_batch.py:107` hard-codes volume floor at 50 hits. Community jargon like `wireborn` (45 hits) gets skipped. Make this a CLI flag.
- `scripts/tag_comments.py:163-171` vs. `:84-86`: `comment_keyword_hits.post_date` stores the *comment* date but propagated `post_keyword_tags.post_date` uses the *post* date. Inconsistency — though the trends export reads only the post-level table, so downstream is fine.

---

## Change process (merging keyword updates)

Every keyword addition, promotion, or cut follows the same steps. **Stages 0-5 happen before any config change.** Steps 6-11 happen only after all gates pass.

### Validation stages (before merging)

0. **Rationale**: document why in an issue, a validation doc, or a changelog entry. "Rationale" includes: source of candidate (workflow 3 mining / manual reading / researcher hypothesis), what gap it fills.

1. **Pre-screen** (Workflow 0): for every candidate, record volume, top-sub concentration, last-60-day share. Filter per the table in [§Workflow 0](#0-pre-screen-volume--concentration-filter).

2. **Validate**: run Workflow 1 (single) or 2 (batch). Report point precision AND Wilson LB AND volume AND top-sub concentration AND cross-theme overlap.

3. **Audit** (Workflow 4): for new additions, run the 20-post-per-keyword independent audit. Compute per-keyword agreement via `compute_agreement.py`. Investigate disagreements.

4. **Rubric updates** (if needed): if the audit produces systematic disagreement patterns on a single keyword, update `theme_definitions.yaml` per [§Disagreement-driven rubric updates](#disagreement-driven-rubric-updates). Re-validate the affected keyword.

5. **Apply gates**: confirm all five hard gates pass (or document researcher-accepted rationale if in REVIEW band).

### Merge stages (after gates pass)

6. **Update config**: edit `config/keywords_v8.yaml`. Include in-line precision + volume + audit agreement + any FP pattern notes. Add a header changelog entry describing the batch.

7. **Re-tag affected posts**: if adding keywords, wipe the old `post_keyword_tags` rows for affected keywords and re-run `scripts/tag_keywords.py`. (The tagger skips already-tagged posts, so without a wipe, new keywords don't get retroactive tags.)

8. **Re-export**: `scripts/export_json.py` + `scripts/export_keyword_details.py`.

9. **Sync `data/` and `web/data/`**: ensure both copies match.

10. **Frontend changelog**: add an entry to `web/app/about/page.tsx` CHANGELOG array with date, title, specifics.

11. **Cross-theme overlap check**: regenerate `docs/cross_theme_overlap.md` after re-tagging.

12. **Validation doc**: write `docs/validation_<summary>_<date>.md` with the structured template described below.

### Validation doc template

Every batch of changes produces one validation doc in `docs/`. It is the audit-trail artifact for the decision. Template:

```markdown
# <Title> — YYYY-MM-DD

**Scope:** <N candidates, themes, motivation>
**Method:** Workflow <N> via <sequential | parallel-subagents>
**Corpus:** T1-T3 companion communities
**Trigger:** <pre-publish review | new vocab cycle | event-driven addition | …>
**Outcome:** <N KEEP, N REVIEW, N CUT>

## Pre-screen
| term | hits | top sub | top% | last60d% | verdict |
|...|

## Primary precision (n=100)
| keyword | YES | prec | Wilson LB | top sub | top% | overlap% | verdict |
|...|

## Independent audit (n=20)
| keyword | agreement | disagreement pattern | verdict implication |
|...|

## FP patterns observed
<categorized failure modes per keyword>

## Rubric updates triggered
<theme_definitions.yaml diffs and reasoning>

## Merge decisions
<final KEEP list, REVIEW notes, CUT rationale>
```

See `docs/validation_emotional_loss_2026-05-12.md` for the first example following this template.

---

## Versioning discipline

Per `feedback_methodology_stability.md`:

- **Keyword-only changes** (additions via workflow 3, cuts for drift, promotions from REVIEW): increment config patch version (v8.1, v8.2, …).
- **Methodology changes** (changes to the topical-reading rubric itself, the precision/Wilson/top-sub/overlap thresholds, or scope): require a full version bump (v9+), explicit justification, and in practice a full keyword re-measurement.

Methodology should be frozen post-ship for 6-12 months. Keyword maintenance (workflow 3 additions, drift cuts) is allowed on the locked standard.

### What counts as a methodology change vs. a clarification

The 2026-05-12 enhancement (audit step, inter-rater agreement gate, audit-driven excludes additions) is treated as an **incremental enhancement** to v8 rather than a v9 methodology change. Rationale:

- The audit step adds a NEW gate, but the gate applies to *new additions only*. Existing v8 keywords are not re-validated under it. The 76 existing keywords retain their original 4-gate validation status.
- Audit-driven excludes additions to `theme_definitions.yaml` are framed as **clarifications** — they make explicit what was implicit in the rubric (e.g., "user-initiated content deletion is not platform-driven loss" is a logical extension of the existing "generic product quality complaints unrelated to an AI companion" exclusion).
- The topical-reading standard (the rubric's core philosophy) is unchanged.

A v9 bump WOULD be required if any of these change:
- The topical-reading vs. first-person-content reading is altered
- Any of the five precision/Wilson/top-sub/overlap/audit thresholds is changed
- The companion-tier scope (T1-T3, JanitorAI/SillyTavern exclusions) is altered
- The 100-post primary sample size is changed

The audit step's existence and threshold are documented as v8's enhanced procedure for new additions, not as a methodology version bump.

---

## Publication-readiness checklist

This section documents what would be needed to bring the pipeline from its current "defensible-for-public-research-artifact" state to "citable-in-peer-reviewed-work." Items checked are partially or fully in place as of the indicated date.

- [ ] **Human-coded calibration set**: 20-30 randomly-chosen posts per high-volume keyword, hand-coded by the researcher without seeing the CC label. Report agreement rate and Cohen's κ per theme. Flag any keyword with κ < 0.6 for review.
- [x] **Within-model inter-rater reliability** (added 2026-05-12): every new addition runs through Workflow 4 — an independent CC subagent re-classifies a 20-post subsample without seeing primary labels. Per-keyword agreement is reported alongside precision. **NOT equivalent to human-coded κ** — both classifier and auditor are the same model — but it catches permissive-drift and rubric-gap failures that pure point-precision misses.
- [ ] **Blinded classification**: validate candidates by asking CC to classify posts for *any* of the 6 themes without being told which keyword triggered the match. Compute precision post-hoc.
- [ ] **Two-prompt reliability**: every keyword validated under both the current topical rubric AND a stricter first-person-content rubric. Report both; flag keywords that are KEEPs under only one reading as "frame-dependent."
- [ ] **Seeded, pinned samples**: stable hash-based seeding of random samples, with post IDs published alongside precision numbers.
- [ ] **Hierarchical shrinkage for promotions**: when promoting a REVIEW-band keyword, compute the posterior over precision with a weakly informative prior drawn from the baseline. Only promote if posterior mean ≥ 80%.
- [ ] **Negative-control keywords**: inject 3-5 deliberately off-theme phrases into each validation batch (e.g. "lunch break" in the romance batch). Any classifier run that scores them >20% is flagged as uncalibrated.
- [x] **Pre-registered rubrics** (locked 2026-04-23, audit-driven updates 2026-05-12): the rubric is frozen before each measurement; rubric changes are version-bumped and re-measurements follow.
- [ ] **Confidence intervals on trend lines**: the frontend shows points; it should show bands that propagate keyword-precision uncertainty.
- [ ] **Methodology-change annotations on charts**: mark the dates of 2026-04-20 regex fix, 2026-04-23 rubric lock, 2026-05-12 audit-step addition, any future changes.

Realistic near-term priority order: calibration set → blinded classification → seeded sampling. These three together would close the remaining gap to publication-grade rigor in about a week of researcher time.

---

## File inventory

- `README.md` — this document (runbook)
- `theme_definitions.yaml` — classification rubric (locked 2026-04-23; audit-driven excludes updated 2026-05-12)
- `prepare_sample.py`, `prepare_batch.py` — prompt generation
- `parse_classifications.py`, `parse_batch.py` — CC output parsing
- `summarize_batch.py` — DB-level aggregation
- `compute_agreement.py` — (2026-05-12) audit agreement computation
- `utils.py` — shared sampling + matching helpers
- `batch_*.yaml` — historical batch specifications
- `results/` — prompt files, CC classification outputs, audit outputs (grows per run)
- `mining/` — anchor-based mining artifacts (workflow 3 scratch space)
- `archive/` — superseded config and scripts
- `samples/` — (reserved; not currently populated)

---

## Related docs

- `../../CLAUDE.md` — project-level spec, thesis, scope
- `../../config/keywords_v8.yaml` — current keyword config with per-keyword annotations
- `../../docs/validation_all_themes_revalidation_2026-04-23.md` — most recent full revalidation
- `../../docs/archive/KEYWORD_HISTORY_AND_LESSONS.md` — history of discovery attempts and failures
- `../../docs/cross_theme_overlap.md` — current theme-overlap distribution
