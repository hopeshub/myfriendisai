# My Friend Is AI — Methodology

*A standalone, self-contained statement of what this project measures, how it
measures it, and what it cannot measure. Written to be read on its own: it
assumes no access to the live site, the repository, or any other document.*

**Project:** My Friend Is AI — <https://myfriendisai.com>
**Code and validation records:** <https://github.com/hopeshub/myfriendisai>
**Document version:** 1.0 · 2026-08-27
**Instrument version:** keyword set v8 (92 keywords, locked)

---

## 1. What this is

My Friend Is AI is a daily-updating public record of how a curated set of
AI-companion communities on Reddit *talk* over time. It matches validated
keyword patterns against posts and charts how six recurring themes — romance,
sex/ERP, consciousness, therapy, addiction, and rupture — rise and fall,
normalized per 1,000 posts.

It is a **precision-first discourse tracker**. The whole design follows from
that phrase: it would rather miss many real posts than count false ones.

This is an independent, one-person research project. It is not academic,
institutional, or peer-reviewed work.

### 1.1 The question it answers

> When people in these curated communities talk publicly, how often does each
> theme's explicit vocabulary appear, and how does that change over time?

### 1.2 The questions it refuses to answer

The site does **not** measure the phenomenon of AI companionship. It cannot say:

- how many people use AI companions;
- how many people are in relationships with an AI;
- how many people are addicted, helped, harmed, grieving, or in love;
- what Reddit as a whole thinks, much less the general population.

An earlier framing of this project — "Reddit engagement is a meaningful proxy
for AI companionship proliferating" — was retired in May 2026 as overclaiming.
The community-size and engagement surfaces on the site are kept as *secondary
context*, not as a measure of the phenomenon.

The honest frame: **an observatory for the parts of AI companionship that
become visible in public language.**

### 1.3 What it is good at

The strongest signals are event-shaped. When a platform changes underneath its
users, the language changes quickly and visibly:

- major platform events (the 2023 Replika ERP removal);
- grief and rupture around model retirements and product changes (OpenAI
  retiring GPT-4o in 2026);
- the growth of recovery and quitting language;
- shifts in how people talk about AI as romantic, sexual, therapeutic,
  addictive, or possibly conscious;
- broad direction over time *within* a theme.

It is correspondingly weak at estimating ordinary background prevalence, and at
seeing the quiet centre of AI companionship — the person living contentedly
with an AI partner who writes "she made me laugh today" in language
indistinguishable from ordinary human-relationship talk.

---

## 2. The corpus: which communities, and why

**41 subreddits are configured; 39 are actively collected.** The list lives in
`config/communities.yaml` in the repository.

### 2.1 Why a curated list at all

The project began with the broader ambition of tracking AI companionship across
large general-AI subreddits. That did not work, for one reason: **context**.

In a large general subreddit, "my girlfriend," "my boyfriend," "in love with,"
and "relationship with" are usually about ordinary human relationships that
merely mention AI. No keyword can reliably separate "my boyfriend uses ChatGPT"
from "my boyfriend *is* an AI."

In r/replika or r/MyBoyfriendIsAI, the same words almost always mean what they
appear to mean, because that is what the community is about. **The subreddit
does the disambiguating the keyword cannot.**

Curation is therefore not a side detail — it is the method. The keywords are
the lens; the community list keeps the lens pointed where words mean what they
appear to mean.

### 2.2 Tiers

| Tier | Description | Count | In theme measurement? |
|---|---|---|---|
| **T0** — General AI | Communities where companionship discourse surfaces but is not the charter (r/ChatGPT, r/OpenAI, r/singularity, r/ClaudeAI, r/claudexplorers) | 5 | **No** — context only |
| **T1** — Primary Companionship | AI companionship is the central topic (r/replika, r/CharacterAI, r/MyBoyfriendIsAI, r/BeyondThePromptAI, r/MyGirlfriendIsAI, r/AIRelationships, r/AICompanions, r/SoulmateAI, r/ChatGPTcomplaints, r/aipartners, r/ReplikaLovers, r/ILoveMyReplika, r/MyBoyfriendIsAI_Open, r/MySentientAI) | 14 | Yes |
| **T2** — Platform-Specific | Communities for specific AI-companion products (r/KindroidAI, r/NomiAI, r/ChaiApp, r/Paradot, r/NectarAI, r/HeavenGF, and three explicitness-scope exclusions listed below) | 9 | Yes, except 3 |
| **T3** — Recovery & Dependency | Quitting and peer support (r/Character_AI_Recovery, r/ChatbotAddiction, r/AI_Addiction, r/CharacterAIrunaways) | 4 | Yes |
| **T4** — Ambient / Discourse Climate | Anti-AI and pro-AI cultural-expression communities, added 2026-05-20 (r/antiAI, r/FuckAI, r/ArtistHate, r/AIDangers, r/BetterOffline, r/trueantiAI, r/DefendingAIArt, r/ProAI, r/aiwars) | 9 | **No** — context only |

One name on the list looks out of place and is deliberate: **r/ChatGPTcomplaints**
is tracked as a companion community because of what its members write, not what
it is called. It was the organizing hub for the #Keep4o protests when OpenAI
retired GPT-4o, and a large share of its posts read as rupture-grief for a model
people had built a relationship with.

### 2.3 Exclusions from theme measurement

Only T1–T3 communities enter the keyword pipeline. On top of that tier gate,
individual communities can carry an `exclude_from_keywords` flag; flagged
communities remain in the corpus and in the community explorer but are dropped
from keyword tagging, from every theme line, and from the per-1,000 denominator.

**Never tracked at all:** r/JanitorAI_Official and r/SillyTavernAI — bot-card
listing text matched companion vocabulary at high volume without being
companionship discourse.

**Excluded from keyword tracking, 2026-05-18** (three T2 communities):

| Community | What it actually is | Why excluded |
|---|---|---|
| r/AIGirlfriend | ~91% affiliate-spam image posts | Matches were marketing copy, not discourse |
| r/SpicyChatAI | Bot-card marketplace and product support | Matches were listing text — the JanitorAI failure mode |
| r/ChatGPTNSFW | Erotica-writing / jailbreak-craft community | Real signal but off-construct: no persistent companion or relationship |

The governing principle is explicit: **the inclusion gate is companionship, not
explicitness.** Sex/ERP is one of the six headline themes, several `over_18`
communities are tracked and collected normally, and the 2023 Replika ERP
removal is a flagship event the site is built to show. A community that is both
explicit *and* companionship-centred is in; one that is explicit but not
companionship-centred is out — for the same reason a non-AI community would be.

**Excluded from keyword tracking, 2026-05-20:** all nine T4 communities, plus a
hard `tier in (1,2,3)` gate in the loader as defence in depth. T4 is a
secondary cultural-context view only.

### 2.4 The T4 selection rule

A subreddit belongs in the Ambient tier only if **both** stages pass:

1. **Charter test** — the sub's charter is to advocate *for* or *against* AI as
   a cultural project. A stranger reading its public description and top 50 post
   titles can identify its side. Technical-research communities (alignment, ML
   engineering) fail here even if their members are AI-skeptical in effect.
2. **Expression-not-infrastructure test** — the sub functions as a space for
   cultural *expression* (individuals venting, grieving, arguing, advocating)
   rather than as movement-coordination *infrastructure* (officer roles, treaty
   or ballot organizing, recruitment for an advocacy organization, named-figure
   intellectual lineage operating as community identity).

The test applies to the community, not its members. Stage 2 removes candidates
symmetrically on both sides — an advocacy-organization volunteer hub on the
anti-AI side and accelerationist movement communities on the pro-AI side.

**T4 is not a measurement of mainstream AI sentiment.** It shows that this
cluster of cultural-expression communities exists, how each is sized, and how
each is moving. Read engagement, not a population estimate.

The pro-AI/anti-AI asymmetry in the tier (6 anti, 2 pro, 1 arena) is honest
rather than artifactual: Reddit has more anti-AI advocacy *expression* than
pro-AI, because pro-AI energy mostly lives in product communities whose charter
is the product, not advocacy. Counting those as T4 would have failed the charter
test.

### 2.5 Communities that cannot be reached

Some relevant communities are **private or invite-only** and return HTTP 403 to
any unauthenticated request — r/AISoulmates, r/4oforever, r/AIBoyfriends. They
are monitored but not tracked. This is an accepted, documented gap.

Being flagged `over_18` is *not* a barrier: NSFW-flagged communities are served
normally and several are tracked. Individual NSFW posts within an accessible
community may be filtered from listings, causing slight undercounting;
acceptable for trend analysis.

Adjacent non-AI communities (r/relationship_advice, r/depression, and similar)
were tested and removed — keyword overlap with ordinary human-relationship
language made them too noisy.

### 2.6 Deactivated communities

Two configured communities are no longer collected: **r/HeavenGF** (banned by
Reddit, ~May 2026; deactivated 2026-05-14) and **r/MySentientAI** (deactivated
2026-08-08 as moribund — 8 posts ever). Their historical posts remain in the
corpus, in both the theme numerators and the denominator. Deactivation stops
collection; it never retroactively removes data.

### 2.7 Corpus extent

The post corpus reaches back to **2017** via archive backfill: the early Replika
years, COVID-era growth, and the ChatGPT precondition era. As of 2026-08 it
holds roughly 4.4 million posts. Per-theme coverage gating (§5) means a theme's
chart line still begins only where its vocabulary becomes measurable.

Communities added after launch are **forward-only** — no backfill — because a
backfilled addition would inject a step into the historical series.

---

## 3. The instrument: keyword matching

### 3.1 Themes and keyword counts

Six themes, 92 validated keywords total, defined in `config/keywords_v8.yaml`
(locked). Regex patterns are matched against post title + body text.

| Theme | Keywords | What it captures |
|---|---|---|
| **romance** | 21 | Romantic framing of a personal relationship with an AI |
| **sexual_erp** | 13 | Sexual content, erotic roleplay, NSFW interaction with an AI |
| **consciousness** | 11 | Claims or beliefs about AI sentience, personhood, inner experience |
| **therapy** | 8 | AI described as therapeutic support or a therapist replacement |
| **addiction** | 17 | Self-reported addiction, compulsive use, attempts to quit |
| **rupture** | 22 | Loss or disruption of an AI companion relationship due to platform change |

### 3.2 Overlap policy

Themes are **not mutually exclusive**. A single post can be counted under
several themes; each theme line counts distinct posts for that theme. The theme
series therefore do not sum to anything meaningful.

### 3.3 No language model in any published number

Every published figure is a deterministic, manually-validated keyword count.

This is a deliberate trade. A language model would classify more flexibly, but
it introduces model drift, hidden judgment calls, version dependency, and
reproducibility problems. A keyword count is checkable — every point on every
line traces back to specific words in specific posts, and the same posts always
produce the same number, so a line moves when the discourse moves and not
because a model was retrained.

The gain forgone was measured, not assumed: an LLM re-check layer over each
keyword match was built and evaluated in May 2026. It raised precision from
roughly 80% to 88% and did nothing at all for the posts the keywords never
matched. It was dropped. The only LLM code retained in the project is the
drift-check sampler (§8), which never touches a published number.

---

## 4. Validation protocol

Every keyword has to earn its place before it is allowed to count.

### 4.1 Procedure

1. Pull 100 random posts from T1–T3 that the candidate keyword matched.
2. Read title + body of each.
3. Classify YES / NO / AMBIGUOUS.
4. Relevance = YES / (YES + NO).

Classification uses the **topical reading** (locked 2026-04-23): a post is YES
if it is thematically about the theme, even without graphic or first-person
detail. Per-theme definitions are recorded in the repository alongside the
scoring sheets.

### 4.2 Thresholds

| Relevance | Outcome |
|---|---|
| ≥ 80% | **KEEP** |
| 60–79% | **REVIEW** — researcher decides |
| < 60% | **CUT** |
| < 10 hits | **LOW VOLUME** — held out |

### 4.3 The researcher-accepted band

A keyword scoring 60–79% may be accepted at the researcher's discretion, but
only when *all four* hold:

1. false-positive patterns are well-defined and categorizable;
2. no cross-theme collision above 30%;
3. the keyword adds vocabulary not already covered by the set;
4. false positives are amenable to future disambiguation.

Each such acceptance is logged with its rationale in the keyword's scoring sheet
and tagged inline in the keyword config. Every below-80% keyword carries one of
three documented statuses — *researcher-accepted*, *LOW VOLUME placeholder*, or
*AUDIT-GATE FAIL* — and the statuses are machine-auditable.

Current researcher-accepted keywords: `we broke up` (romance),
`in a relationship with` (romance), `personality changed` (rupture),
`hours a day` (addiction), `neglecting my` (addiction).

### 4.4 Measured precision

Per-theme topical precision, re-measured 2026-05-16 by full-census
re-measurement plus a 72-post human gold anchor:

| Theme | Post precision |
|---|---|
| addiction | ~97% |
| sexual_erp | ~96% |
| consciousness | ~87% |
| romance | ~86% |
| therapy | ~80% |
| rupture | ~77% |

Earlier small-sample (n≈20) screens had run 10–15 points low; those figures are
superseded.

Comment-level precision was measured separately across the June and July 2026
drift cycles (n≈4,000 comment classifications): addiction 78–79%, rupture
77–81%, sexual_erp 75–79%, romance 72–75%, consciousness 65–75%, therapy 66–68%.
Comment-derived tags do not enter the published series (§7).

---

## 5. Recall: the chart is a floor, not a ceiling

Precision was bought with recall, and the price was measured.

**Method.** A stratified random sample of 400 posts from T1–T3 (200 random
across all communities, 40 each from five theme-rich communities) was
hand-classified for all six themes under the topical reading. Recall =
(classified-YES ∩ keyword-tagged) / classified-YES.

**Result (2026-05-13):**

| Theme | Classified YES (n=400) | Keyword-tagged | Recall | Wilson 95% CI |
|---|---|---|---|---|
| addiction | 44 | 14 | **32%** | 20–47% |
| sexual_erp | 19 | 4 | **21%** | 9–43% |
| therapy | 7 | 1 | **14%** | 3–51% |
| romance | 78 | 3 | **4%** | 1–11% |
| rupture | 101 | 3 | **3%** | 1–8% |
| consciousness | 8 | 0 | **0%** | 0–32% |

The confidence intervals are wide because the YES counts are small; treat the
point estimates with that uncertainty.

**Where the missed posts live.** The gap concentrates in four structural
categories:

1. **Image or title-only posts** — the title in a companion community
   establishes the theme for a human reader, but the body is empty or removed,
   so there is nothing to match.
2. **Naturalistic everyday language** — "she said something cute today", a
   five-year relationship update. The romance keyword set requires explicit
   phrasing that a typical anecdote never uses.
3. **Community-specific vocabulary** — proper nouns and in-group terms that
   fail the volume pre-screen individually but are substantial in aggregate.
4. **Indirect markers** — "site is down", "it's been 4 hours" imply rupture or
   compulsion via context, not vocabulary.

In r/MyBoyfriendIsAI — a community literally about AI boyfriends — the keyword
set tags roughly 5% of posts as romance where a human reader classifies ~95%.
That gap *is* the precision-first trade-off, quantified.

**What follows for reading the chart:**

- Every line is a **floor estimate**, not a count. Actual theme-relevant
  discourse is plausibly several times what the chart shows.
- **Shape and timing are honest.** A spike in tagged posts reflects a real
  spike in clearly-worded posts.
- **Within-theme comparison across time works** — same keyword set, same
  precision standard, applied across years.
- **Cross-theme height comparison does not work.** Themes with distinctive
  vocabulary read higher than themes written in ordinary language, whatever the
  truth beneath. This bias runs in one direction and cannot be corrected for.

The recall audit is scheduled for re-run around 2026-11.

---

## 6. Coverage gating and normalization

### 6.1 Per-theme coverage start

Each theme's line renders only from its first reliably-measurable month.

> `coverage_start` = the first calendar month where the post-only count is ≥ 5
> **and** every later completed month is also ≥ 5.

It is recomputed at export time, so the values move as the corpus grows.
Consciousness begins 2025-04; the other five begin across 2022–2023. The
corpus reaches back to 2017, but a theme line does not start where the corpus
does.

### 6.2 Normalization

The published figure is a **rate per 1,000 posts**, not a raw count. These
communities have grown enormously since 2017; a raw count would mostly retrace
that growth. The rate sets growth aside and shows how the conversation itself is
shifting.

The denominator is all posts collected from the theme-measurement scope (T1–T3
minus the flagged exclusions) on the same day. Numerator and denominator are
both smoothed with a **7-day trailing mean** so they share a window and the
displayed rate does not spike on low-volume days. The chart plots the mean of
the daily smoothed rate over each calendar month; the in-progress month is
clipped.

### 6.3 Volume weighting is deliberate

The denominator is post-volume-weighted, not community-equal. One community —
r/CharacterAI — is 60–90% of total post volume, so it dominates the aggregate.
This is a documented posture, not a bug: the alternative (weighting each
community equally) gives every small community outsized influence and produces a
line that swings on the arrival of a new sub.

Because volume weighting *is* a choice, the site publishes a second series with
r/CharacterAI removed, so the dedicated-community signal can be read separately
from the largest community's platform lifecycle.

A leave-one-community-out check (2026-08) records the largest single-community
dependencies: sexual_erp on r/replika (level −50% when removed), addiction on
r/Character_AI_Recovery (−51%), consciousness on r/BeyondThePromptAI (−41%),
romance on r/MyBoyfriendIsAI (−20%). Under alternative reweightings all six
themes fall below 0.9 correlation on at least one scheme — which is precisely
why the line is read direction-only.

### 6.4 Theme concentration

Within the curated set, each theme is concentrated. Top-3 community share per
theme (window through 2026-07): romance 61%, sexual_erp 76%, consciousness 70%,
therapy 66%, addiction 93%, rupture 80%. The sexual_erp line is 59% r/replika
alone. A theme line is often, in practice, a close reading of two or three
communities rather than an even sweep.

### 6.5 The set of communities grew over time

In the early years almost every tracked community was a primary companionship
subreddit. Platform-specific and recovery communities were smaller or did not
exist. Tier share of corpus posts (T1/T2/T3): 2024 = 85.9/13.6/0.5,
2025 = 82.1/16.3/1.6, 2026-to-date = 77.6/18.7/3.7.

Each line is measured against whatever communities existed at the time, so part
of a long climb reflects the tracked world widening rather than the conversation
itself. Trust the broad direction of a line more than its exact path.

---

## 7. Comments, and why the published series excludes them

Comment collection and tagging began **2026-03-18**. Comments on eligible posts
are scanned with the same matching logic; a comment-sourced match propagates to
the parent post, tagged with its source.

Two series are therefore exported for every theme:

- **post+comment** (all sources), and
- **post-only** (matches in the post's own title or body).

**The published chart uses post-only.** Comment tagging began part-way through
the record, so the combined series carries a step artifact at 2026-03-18 and is
not longitudinally comparable. Backfilled data predating that date was tagged on
post text only, so the two series converge for older posts by construction.

The public dataset accompanying this document also publishes the post-only
series, for the same reason.

---

## 8. Drift check

A validated keyword is only validated *for now*. Language in these communities
moves fast: "sentient" was once the natural anchor for the consciousness theme
until it spread into roleplay memes and stopped marking genuine belief;
"therapeutic" turned over a few months from a word for real support into an
insult aimed at preachy AI. Every model release and content-policy change sends
a fresh wave of vocabulary through these communities.

So a **monthly per-keyword drift check** re-samples recent matches for each
keyword and re-classifies them, tracking *relative* agreement over time. Relative
agreement is the right statistic here because it is robust to a constant
classifier bias — the check answers "has this keyword's meaning moved?", not
"what is its absolute precision today?".

The sampling half is automated and scheduled; the classification and reporting
half is run manually. Results accumulate in a drift history file in the
repository, and a per-theme health export (precision, concentration metrics,
noisy-keyword flags) is regenerated on every collection run for audit.

The drift check is the only component of the project that uses a language model,
and it feeds no published number — it flags keywords for human review.

---

## 9. Data sources and collection timeline

| Period | Source | Notes |
|---|---|---|
| 2017 – early 2026 | Public Reddit archives (PullPush, then Arctic Shift) | Historical backfill. The further back a post goes, the more likely its text was removed or deleted before the archive captured it. |
| from 2026-03 | Reddit public `.json` endpoints, daily | Unauthenticated, rate-limited |
| 2026-05-29 → 2026-06-09 | **collection gap** | Reddit disabled unauthenticated `.json` access globally on 2026-05-30 with no announcement; every endpoint began returning 403 |
| 2026-06-09 → 2026-06-11 | Reddit OAuth (app-only token) | Same endpoints, bearer-authenticated |
| from 2026-06-11 | **Arctic Shift archive, daily** ("arctic-first") | Permanent mode as of 2026-08-08 |

**The gap was repaired.** Posts for 2026-05-29 → 06-09 were recovered from the
Arctic Shift archive, and comments followed in a second recovery pass, so post
volume, theme trends, and comment-sourced tags are complete across the window.
Per-day subscriber and active-user figures could not be reconstructed and remain
blank there.

**Arctic-first is permanent.** An application for ongoing Reddit API access was
filed in June 2026 and never acknowledged; the project's judgment as of
2026-08-08 is that this route is closed. Two consequences the reader should
know:

1. **Subscriber counts are frozen at 2026-06-07** and active-user counts are
   permanently null. The site labels subscriber figures with that date.
2. The archive path collects comments *continuously by creation window* rather
   than by the one-shot per-post snapshot the Reddit path used. This is strictly
   more complete, so the *post+comment* series runs a touch fuller from late May
   2026 onward. **The published post-only series is unaffected.**

An implication for the early years that affects every line: because archived
older posts are more likely to have had their text removed, there is simply less
wording available for the keywords to match. Every line therefore runs a little
low at its start, which makes each rise look somewhat steeper than it was. Shape
and event timing are sound; the steepness of the long climb is partly the
instrument warming up.

---

## 10. Provenance labels

Every displayed metric is tagged with how it was obtained:

- **Direct** — taken straight from the source response (subscribers,
  active users, post fields).
- **Inferred** — approximated from a sample (e.g. unique authors counted from a
  100-post listing).
- **Derived** — calculated from other metrics (comments per post, participation
  rate, per-1k theme rates).

A composite "engagement index" has deliberately **not** been built. A premature
composite looks authoritative and is fragile.

---

## 11. Known limitations, consolidated

1. **It counts language, not people or feelings.** A rising addiction line means
   addiction-related language appears more often. It does not establish that
   more people are addicted, nor how they feel about it.
2. **Every line is a floor.** Measured recall is 3–32% per theme (§5). Magnitude
   is a clear undercount.
3. **Theme heights are not comparable to each other.** Vocabularies catch
   unevenly, in one direction: blunt, deliberate vocabulary reads higher than
   ordinary language.
4. **Therapy and addiction are one behaviour in two framings, and the
   instrument cannot measure the overlap.** Both track leaning on an AI to get
   through something hard, separated only by the writer's valence. Measured
   co-tagging is only ~1.9% — but hand-reading 90 addiction-only posts found
   ~24% carried an unmatched help frame. The overlap is real and large; keyword
   co-occurrence cannot see it. **Do not read the gap between the two lines as a
   help-versus-problem balance.**
5. **The community set grew over time** (§6.5), and it holds still while the
   platforms keep moving. A theme that fades here may have moved rather than
   ended — to a newer app, a Discord, a general-AI subreddit outside this set —
   and the instrument cannot tell those apart.
6. **Private and invite-only communities are unreachable** (§2.5).
7. **Older archived posts are more likely to be text-removed** (§9), biasing
   early years low.
8. **The six themes are a lens, not a census.** There is no "fun",
   "creativity", or "everyday utility" theme — and everyday practical talk (bug
   reports, tips, which app to use) is in fact most of what these communities
   post. The themes were chosen for the parts of life with an AI companion that
   carry weight: intimacy, belief, dependence, and loss.
9. **Post-level NSFW filtering** may cause slight undercounting within
   otherwise-accessible communities.

---

## 12. Change control

Post-launch methodology is deliberately frozen. Keyword-only changes are
permitted within a version; anything that changes *how* the instrument measures
requires a version bump (v8 → v9) and a public changelog entry. Corrections that
move a published line — such as the 2026-05-18 exclusion of three
off-construct communities, which stepped the sex/ERP line down across 2024–2025
— are disclosed in the site's changelog rather than made quietly.

The instrument has been through several full revisions. Keeping the measurement
honest means keeping it in motion; the monthly drift check exists because a
keyword that reads cleanly in January can be noise by April.

---

## 13. The public aggregate dataset

The derived numbers behind the charts are published as a versioned, downloadable
bundle at <https://myfriendisai.com/dataset/v1/> and committed to the
repository under `web/public/dataset/v1/`:

- `monthly_theme_counts.csv` / `.json` — per theme per month: the published
  post-only keyword count, the eligible-post denominator, and the rate per
  1,000;
- `monthly_community_volumes.csv` / `.json` — per tracked community per month:
  post volume, with tier;
- `README.md` — full column-by-column schema with provenance labels;
- `manifest.json` — version, generation timestamp, row counts, SHA-256 hashes;
- `index.html` — a directory listing, so the bundle URL opens in a browser;
- a copy of this document.

The bundle contains **derived numbers only**: no post text, no titles, no
usernames, no post IDs, no raw Reddit content. It is regenerated by the daily
pipeline.

The full post database is too large to host in the repository. It is available
on request.

---

## 14. License and citation

The aggregate data exports are licensed **CC BY 4.0**
(<https://creativecommons.org/licenses/by/4.0/>). The project's source code is
MIT-licensed separately. The underlying raw corpus is not redistributed.

Suggested citation:

> Bockley, W. (2026). *My Friend Is AI: Reddit discourse tracker for AI
> companionship communities.* myfriendisai.com.
> <https://github.com/hopeshub/myfriendisai>

---

## 15. What makes this worth having

This is not definitive academic research and should not pretend to be.
Comparable academic work exists, often with stronger methods for frozen
snapshots. The distinctive value here is different: it is live, public,
browsable, transparent, it keeps updating, and it documents its limits instead
of hiding them.

Academic studies usually capture a period after the fact. This watches the
conversation while it is still moving.
