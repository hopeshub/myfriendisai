# My Friend Is AI — Methodology

*A standalone, self-contained statement of what this project measures, how it
measures it, and what it cannot measure. Written to be read on its own: it
assumes no access to the live site, the repository, or any other document.*

**Project:** My Friend Is AI — <https://myfriendisai.com>
**Code and validation records:** <https://github.com/hopeshub/myfriendisai>
**Document version:** 1.2 · 2026-09-08
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

**Communities added after launch were backfilled, not forward-only.** Each
addition was pulled back to the community's own start at the time it was added
and its whole history keyword-tagged in the same pass — r/ILoveMyReplika to
2022-10, r/NectarAI to 2023-05, r/aipartners to 2025-12, r/MyBoyfriendIsAI_Open
to 2025-08, r/ReplikaLovers from its creation on 2026-04-19, and all nine
ambient-tier communities across 2022–2025. So there is no step artifact at the
date each community joined. What backfilling does instead is change the
composition of every earlier month; §6.5 gives the size of that effect.

### 2.8 Which posts count

**A post counts if its text survived to capture.** Reddit and the archives both
keep a post that has been removed or deleted, but they keep it as a title with
`[removed]` or `[deleted]` where the body was. Call that a shell. A shell is not
something this instrument can read: the keywords match title and body, and a
shell has only the first.

Since 2026-09-08 the published population is **measurable posts** — every
collected post that is not a shell. That is the per-1,000 denominator, the
population the theme counts are drawn from, and the volume figure on each
community's page. About 18% of the posts in the measurement scope are shells.

Two facts forced the decision. Shells are not spread evenly across communities:
r/ChaiApp runs 70–85% removed posts in every archive month, so counting them
made that community look like a large, quiet room rather than a heavily
moderated one, and put 10,000 unreadable posts a year into the denominator
every other community's rate is divided by. And their share depends on how the
data was collected: Reddit's own listing omitted removed posts entirely, so the
live-collection window of March–May 2026 contains none at all, while
archive-sourced months contain 16–20% (2022–2025) and about 30% in June–August
2026 (§9.1). A denominator that moves with moderation policy and with
collection regime is not measuring discourse.

**An empty body is not a shell.** An image or link post has a title, no body,
and is perfectly visible. Its title is matchable and it stays in the
population — half of all measurable posts are of that kind, which is part of
why §9.3 is the caveat it is.

Shells are still collected and still stored. Nothing is deleted from the
corpus; shells are excluded from published counts.

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
| therapy | **~66–68%** |
| rupture | ~77% |

Earlier small-sample (n≈20) screens had run 10–15 points low; those figures are
superseded.

**The therapy figure was previously published as ~80%, and that was wrong.**
The 2026-05-16 census reported therapy twice: ~68% for the keyword set as it
ships, and ~87% for a rebuilt set that cuts the two noisiest keywords and admits
15 census-recovered replacements. The ~87% was a projection of work that has not
shipped — the rebuild is a v9 change, still awaiting sign-off — and the ~80% in
earlier versions of this document was drawn from it. The table above now carries
the measured value for the set that is actually counting: **~66–68%**, confirmed
by three drift cycles (June–August 2026). Four of the eight therapy keywords —
`emotional support`, `therapeutic`, `as a therapist`, `for therapy` — scored
75%, 65%, 60% and 60% at the 2026-05-12 audit and are flagged AUDIT-GATE FAIL in
the keyword config. They still count, under the change-control rule in §8.2. When
the rebuild ships, the theme's precision and its volume will both move, and that
will be a versioned change with a changelog entry.

**How firm any one of these numbers is.** Each keyword-level validation figure
underneath the table comes from a 100-post read by a single coder — the
researcher. Treat any individual figure as roughly ±8 points. Posts the coder
could not decide were dropped from the denominator rather than counted against
the keyword.

**The drift check measures something else, and its numbers differ.** The monthly
drift check (§8) re-samples recent matches and re-classifies them with a
language-model classifier. It exists to answer "has this keyword's meaning
moved?", so it is read as change across cycles; it is robust to a constant
classifier bias but is not calibrated against the human coding above. Its
current per-theme post-level values ship in `theme_health.json` with the rest of
the aggregate exports (audit dated 2026-08-27):

| Theme | Drift post precision | n |
|---|---|---|
| romance | 88.7% | 931 |
| consciousness | 85.9% | 369 |
| rupture | 84.7% | 926 |
| addiction | 84.6% | 741 |
| sexual_erp | 83.2% | 524 |
| therapy | 66.4% | 360 |

Only therapy agrees with the census table. The other five differ in both
directions and by as much as 13 points: addiction and sex/ERP read about 12–13
points *lower* on the drift instrument, rupture about 8 points *higher*, romance
and consciousness within 3. The two instruments have not been reconciled against
each other. Which to use: for "what share of the posts on this line belong to
the theme?", use the census table — it rests on human coding. For "is this
keyword still measuring what it used to?", use the drift series, and read the
movement rather than the level.

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
- **Shape and timing are honest** — with one qualification, in §9.3: a spike in
  tagged posts reflects a real spike in clearly-worded posts, but the amount of
  matchable text in the corpus has itself risen over the years, which bears on
  long climbs rather than on spikes.
- **Within-theme comparison across time works** — same keyword set, same
  precision standard, applied across years — again subject to §9.3.
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

The count the gate tests is a count of measurable posts (§2.8). Narrowing the
population on 2026-09-08 left every theme's start month where it was, in both
the full and the "Excluding r/CharacterAI" series.

**Clearing the gate does not make a month precise.** A threshold of five posts
admits months that are still very small. Of the months actually drawn on the
chart, the share whose post-only numerator is under 20 posts: consciousness 41%
(76% are under 30), therapy 36% (52% under 30) and addiction 32% — mostly
2023. In the "Excluding r/CharacterAI" series it is therapy 38% and rupture
47%. On a
two-proportion test, only about 19% of consciousness's and therapy's
month-to-month moves are distinguishable from chance at p < 0.05.

**So read consciousness and therapy over half a year or more, not month to
month.** A single month's wiggle on either line is usually noise. The public
dataset carries `post_only_count` and `eligible_posts` on every row precisely so
that a reader can compute an interval for any month rather than take the plotted
point at face value.

### 6.2 Normalization

The published figure is a **rate per 1,000 posts**, not a raw count. These
communities have grown enormously since 2017; a raw count would mostly retrace
that growth. The rate sets growth aside and shows how the conversation itself is
shifting.

The denominator is the month's measurable posts (§2.8) across the
theme-measurement scope: T1–T3, minus the flagged exclusions, minus the posts
whose text did not survive to capture. The numerator is counted over that same
population — distinct posts in the month whose own title or body matched a
validated keyword.

**The chart plots the pooled monthly rate:**

> the month's post-only count ÷ the month's measurable posts × 1,000

One count over one denominator. There is no smoothing step, because the monthly
bucket is the smoothing. It is the same number the public dataset publishes as
`rate_per_1k` and the same number the site's own sentences describe, so the
chart, the dataset and the prose are one figure. The in-progress month is
clipped, so the last point on every line is a complete month.

**Before 2026-09-08 the chart plotted something else.** The old estimator took
the mean, over the month's days, of a daily rate whose numerator and denominator
were each smoothed with a 7-day trailing window. Three things were wrong with
it, and they were measured before it was replaced.

A mean of daily ratios is not the ratio of the monthly totals; it weights the
quiet days as heavily as the busy ones, and here it ran high. Median gap by
theme 3.6–7.9%, 90th percentile 14–29%, mean signed bias +1.6% to +6.1% — and
the bias drifted by era rather than holding steady (2023 +4.7%, 2024 +7.8%,
2025 +3.2%, 2026 +2.2%), which is the part that matters for a chart read for
direction.

The two smoothing windows were also not aligned, and earlier versions of this
document claimed they were. The denominator's ran over the corpus calendar; the
numerator's ran over the last seven days *that had at least one keyword hit*,
because the export omits zero-hit days entirely. For a theme with a hit almost
every day the two coincided. For a sparse one they did not: consciousness
records a hit on 48% of the days in its charted range, therapy on 55%, so on
those lines the numerator's window could reach back a fortnight while the
denominator's covered a week.

And it turned a hole in collection into a spike. The worst single months were
romance 2024-05 (+79% against the pooled rate), consciousness 2025-12 (+59%)
and rupture 2023-09 (−35%).

Those extreme months are not spread evenly: they land on stretches where
r/CharacterAI — most of the denominator — was missing days in the corpus
(2023-08-23 to 08-31, 2024-02-20 to 02-29, 2024-05-16 to 05-31, 2025-12-01 to
12-10). Those holes were refilled from the archive on 2026-09-08 (21,828
posts), which removes the largest distortions; the estimator change below
removes the mechanism.

The public dataset keeps its `rate_per_1k_charted` column so that nothing
reading the file breaks, but the two columns now carry the same number.
Downloads taken before 2026-09-08 do not; in those, `rate_per_1k` is the column
to analyse.

### 6.3 Volume weighting is deliberate

The denominator is post-volume-weighted, not community-equal. One community —
r/CharacterAI — is 60–90% of total post volume, so it dominates the aggregate.
This is a documented posture, not a bug: the alternative (weighting each
community equally) gives every small community outsized influence and produces a
line that swings on the arrival of a new sub.

Because volume weighting *is* a choice, the site publishes a second series with
r/CharacterAI removed, so the dedicated-community signal can be read separately
from the largest community's platform lifecycle.

That second series starts later, and for a mechanical reason worth knowing:
`coverage_start` (§6.1) tests a raw count, not a rate, so removing the largest
community pushes several themes below the five-post gate for months they clear
in the full series. Therapy begins 2024-07 and addiction 2024-08 without
r/CharacterAI, against 2023-01 for both with it. The earlier years did not
become unmeasurable — the gate simply counts posts.

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

Because post-launch additions were backfilled rather than added forward-only
(§2.7), a new community does not appear at the date it joined the project — it
appears retroactively, wherever its own history starts. So the effect is not a
step at one date but a change in what every earlier month is made of.

That effect is measurable, and on one theme it is large. The five companion
communities added in May 2026 are romance-dense, and they now supply about 9% of
the per-1,000 denominator. Romance for July 2026 reads **5.54 per 1,000 with
them and 3.75 without** — the added communities are roughly a third of that
month's level. The other five themes move by 10% or less.

So part of a long climb reflects the tracked world widening rather than the
conversation itself. Trust the broad direction of a line more than its exact
path, and expect romance in particular to sit higher than it would have on the
2025 community set.

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

### 8.1 What the August 2026 cycle found

Six keywords now measure below the 60% cut that would reject a new keyword. The
drift figure comes first, the original validation figure in brackets:

| Keyword | Theme | Drift, post-level | At validation |
|---|---|---|---|
| `I was hooked` | addiction | 46% | 81% |
| `ai therapy` | therapy | 48% | 73% |
| `screen time` | addiction | 52% | 89% |
| `emotional support` | therapy | 52% | 100% |
| `therapeutic` | therapy | 52% | 69% |
| `memory reset` | rupture | 55% | 72% |

Each has a nameable cause rather than random noise. `screen time` was absorbed
by r/CharacterAI's "post your screen time" comparison threads, which are
usage-bragging with no distress in them. `I was hooked` is product-review idiom
("tried it and I was hooked"). `ai therapy` drifted into a comedy genre —
therapy sessions written *for* the AIs. `memory reset` became the name of a
button users press on purpose, which is outside the rupture definition.

`screen time` is the clearest meaning-shift the programme has caught, and it is
also nearly immaterial: it is the only tag on 3.6% of the addiction theme's
posts over the last six months, so at 52% precision it contributes roughly 1.7%
spurious volume to that line. Three of the six sit in therapy, which is why that
theme reads where it does in §4.4.

### 8.2 What happens to a keyword that drifts

**A keyword that falls below the cut keeps counting until the next version
bump.** It is not quietly dropped — it is named: in the table above, and on the
site's theme page, where every keyword in a theme is listed with its validation
precision and, since 2026-09-08, marked *drifting* with the figure from its
latest post-level re-check whenever that re-check landed below 60%. All six
above carry that mark.

This is deliberate. Re-cutting a keyword mid-version would silently restate
every historical month on that line — the same posts would produce a different
number than they did last week, which is the exact property the no-model design
(§3.3) exists to protect. Corrections that move a published line belong to a
version bump with a changelog entry (§12), so that a reader can see what changed
and when. The cost is that a drifted keyword keeps adding noise in the meantime;
the numbers above are how much.

---

## 9. Data sources and collection timeline

| Period | Source | Notes |
|---|---|---|
| 2017 → 2026-03-10 | Public Reddit archives (PullPush, then Arctic Shift) | Historical backfill, inserted March 2026; the pre-2023 years and several repairs followed in May 2026. |
| 2026-03-11 → 03-14 | Reddit public `.json`, daily | Unauthenticated, rate-limited. |
| 2026-03-15 → 05-11 | Reddit public `.json`, daily | r/CharacterAI's live collection was capped at exactly 100 posts a day by Reddit's single-listing limit. The lost volume was repaired from the archive on 2026-05-11/12 — for that community only. |
| 2026-05-12 → 05-26 | Reddit public `.json`, daily | |
| 2026-05-27 → 06-07 | Reddit `.json`, then nothing | Reddit disabled unauthenticated `.json` access globally on 2026-05-30, with no announcement; every endpoint began returning 403. The window was recovered from the archive on 2026-06-09/10. |
| 2026-06-08 → 08-26 | **Arctic Shift archive, daily** ("arctic-first") | 72-hour window per run. |
| from 2026-08-27 | **Arctic Shift archive, daily** | 7-day window per run, so an archive outage shorter than a week heals itself on the next good run. |

**Reddit API access was never granted.** Reddit retired self-serve app creation
in early 2026; an application was filed in June 2026 through the required
support-ticket route and was never acknowledged. The project's judgment as of
2026-08-08 is that the route is closed, and arctic-first is the permanent
collection mode. Earlier versions of this document listed a short Reddit-OAuth
era in the table above; there was none.

Two consequences the reader should know:

1. **Subscriber counts are frozen at 2026-06-07** and active-user counts are
   permanently null. The site labels subscriber figures with that date.
2. The archive path collects comments *continuously by creation window* rather
   than by the one-shot per-post snapshot the Reddit path used. This is strictly
   more complete, so the *post+comment* series runs a touch fuller from late May
   2026 onward. **The published post-only series is unaffected.**

One note for anyone reading the database rather than the exports:
`posts.collected_date` holds the post's *creation* date for archive-sourced
rows, not the date it was fetched. The fetch time is `created_at`.

### 9.1 The two sources disagree about removed posts

Reddit's `new.json` listing omits posts that have been removed. The archive
keeps them, as a title-only record with `[removed]` where the body was. The eras
were therefore not alike: the posts collected live from Reddit — 2026-03-11 to
05-26, plus the mixed days to 06-07 — were missing removed posts altogether and
ran roughly 15–20% short on volume, while every archive-sourced era includes
them as empty shells. That window has since been re-fetched from the archive;
see the end of this section.

Removed shells as a share of posts, by the post's own year: 2020 28%, 2021 25%,
2022 17%, 2023 20%, 2024 16%, 2025 17%, 2026 January–May about 22%, 2026
June–August about 30%.

The June–August 2026 excess was not a change in how these communities moderate.
It was a capture-timing artefact of arctic-first collection: the archive records
a post within hours of creation, often while it is still in a moderator queue
with its body blank, and the collector never returned to update that first
snapshot. Re-fetching a sample showed how much of it was temporary — in
r/KindroidAI 20 of 25 sampled shells now have bodies, in r/replika 13 of 25, in
r/CharacterAI 3 of 25. r/ChaiApp was 0 of 25: those are genuine removals, and
that community has run 70–85% removed posts in every archive month since 2025.

This reaches every theme line, because a shell sits in the per-1,000 denominator
while having almost nothing for a keyword to match. Shells tag at 0.1–2.3 per
1,000 against 2.0–18.8 for text-bearing posts. From June 2026 that pushed every
line down by roughly 12–16% relative to March–May 2026, and about 12% relative
to 2024 and early 2026. On therapy it inverted a direction: the published line
fell 2.7% from March–May to June–August, and rose 16% on a denominator counting
only text-bearing posts.

**This was repaired on 2026-09-08.** A shell-refresh step now re-fetches posts
that were captured as shells once they are 10–35 days old, and a one-time pass
re-checked 74,306 shells back to 2026-03-11: 10,393 had gained a body in the
archive and were updated and re-tagged (r/KindroidAI 696 of 1,366, r/replika 57
of 205, r/CharacterAI 273 of 8,090, r/ChaiApp 95 of 9,916; the rest are genuine
removals). The live-Reddit window of 2026-03-11 → 05-26 was re-fetched from the
archive for the 23 keyword-scope communities other than r/CharacterAI, which
had already been repaired in May — 8,566 posts Reddit's listing had omitted,
most of them removed posts. After the repair the shell share of the
keyword-scope corpus is a flat 20–24% in every month of 2026, where it had
been 14% in the live-Reddit window and 32% in June. The shell shares and the
12–16% depression given above describe the record as it stood before that
repair, under the old population definition.

**And the decision that repair made unavoidable:** shells are no longer counted
at all. Since 2026-09-08 the published population is measurable posts (§2.8) —
a post whose stored body is `[removed]` or `[deleted]` is out of every published
figure, numerator and denominator alike. Repairing the capture-timing artefact
recovers the posts that were only temporarily blank; excluding shells settles
what to do about the ones that are genuinely gone, which no re-fetch can bring
back. The 12–16% depression described just above is the arithmetic of the old
definition, which counted them.

### 9.2 The engagement metrics have their own breaks

These are secondary-context figures, not theme measurement, but they carry two
discontinuities worth naming. **`avg_score_per_post` has no archive equivalent
and is frozen at 2026-05-28** — 2026-06-07 for the ambient tier — exactly as
subscriber counts are. **`avg_comments_per_post` changed definition in June
2026**: it was Reddit's own `num_comments` field, and it is now the mean number
of comments this project actually collected for a post. Those are different
quantities. Read that metric for direction within an era, not as a level across
the whole record. **`unique_contributors_7d` (contributors/week) steps at the
same seam**: comment authors have been counted since 2026-03-12, and from June
2026 comments are collected continuously by creation window rather than once
per post, so more comment authors are seen — r/replika's weekly figure goes
from ~34 in May 2026 to ~120 in June, r/CharacterAI from ~2,550 to ~4,530. Same
rule: within an era only.

### 9.3 How much matchable text exists is not constant

This is the most important caveat in the document after recall, because it is
the one that bears on "shape and timing are honest."

The keywords match title and body text. The share of posts carrying any body
text at all has risen steadily. Both populations are shown, because the
published one narrowed on 2026-09-08 (§2.8) and the other figures in this
section were computed on the wider one:

| Year | Of all collected posts | Of measurable posts |
|---|---|---|
| 2022 | 17% | 20% |
| 2023 | 32% | 39% |
| 2024 | 40% | 48% |
| 2025 | 53% | 63% |
| 2026 | 61% | 76% |

Within r/CharacterAI alone the climb is steeper — 27% in 2023 to 66% in 2026 —
and outside it, gentler: 48% to 55%. Part of this is capture recency: an older
post had more years in which to be deleted before the archive ever saw it. Part
of it is a real change in how these communities post — more text, fewer
screenshots.

Either way, the instrument had more to read in 2026 than in 2022. **And whether
recall is constant over time has never been tested.** The 2026-05-13 recall
audit (§5) drew an all-time random sample with no period stratification, and the
drift check (§8) measures precision drift only, not recall.

What has been tested is how much the published shapes depend on it. Restricting
the corpus to body-bearing posts — a test run against the wider pre-2026-09-08
denominator — five of the six themes keep the direction they are charted with. Romance is the exception: on the published denominator it goes
from 2.10 to 4.08 per 1,000 between 2023 and 2026 (+94%); on body-bearing posts
only, from 4.55 to 5.72 (+26%). Its rise out of the 2024 trough survives; much
of the longer climb since 2023 does not.

So, stated at the strength the evidence supports: **direction is robust for five
of six themes and for event-shaped spikes; multi-year magnitude is weaker
everywhere; and romance's long climb is the weakest claim on the site.**

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
2. **Every line is a floor.** Measured recall is 0–32% per theme (§5):
   consciousness caught none of the eight posts a human classified as on-theme.
   That is a small sample — its Wilson interval reaches about 32% — but the
   point estimate is zero, not 3%. Magnitude is a clear undercount.
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
7. **The amount of matchable text is not constant over time** (§9.3). Posts
   carrying body text went from 20% of the measurable corpus in 2022 to 76% in
   2026, and nothing in the validation programme has tested whether recall is
   flat across that change. Restricted to body-bearing posts, five themes keep their charted
   direction; romance's climb since 2023 largely does not.
8. **Posts whose text did not survive are not counted** (§2.8). A post the
   archive holds only as a title, because it was removed or deleted, is out of
   every published figure. That is the population the instrument can read, but
   it means a heavily moderated community contributes less to the denominator
   than its raw posting suggests, and the counts here are smaller than the
   volume these communities actually posted.
9. **The six themes are a lens, not a census.** There is no "fun",
   "creativity", or "everyday utility" theme — and everyday practical talk (bug
   reports, tips, which app to use) is in fact most of what these communities
   post. The themes were chosen for the parts of life with an AI companion that
   carry weight: intimacy, belief, dependence, and loss.
10. **Post-level NSFW filtering** may cause slight undercounting within
    otherwise-accessible communities.
11. **A few accounts carry more of a theme than you might expect, and two
    platform accounts are excluded.** The most prolific 1% of authors account
    for 5–11% of a theme's posts (May 2026 audit) — concentrated, but not
    enough to make a theme one person's diary. Two accounts are excluded from
    every count — numerator and denominator alike — under one rule: platform
    or moderator announcement content is not community discourse. The first is
    a platform-operator account posting product announcements into the sex/ERP
    theme (`SoulmateAI_Dev`, 2023 Soulmate patch notes, about 0.8% of the
    theme; excluded May 2026). The second, found in the 2026-09-08 audit, is
    r/NomiAI's community-manager account, whose weekly "collab" thread template
    contains the phrase *"NSFW content is not blanket excluded…"* and so
    matched the keyword `nsfw content`: 85 posts, one template, a fixed weekly
    cadence, 14–25% of the sex/ERP theme-months since late 2025, every one a
    false positive and every one of that account's theme tags. Excluded
    2026-09-08; the sex/ERP line runs lower from late 2025 as a result, which
    is the correction, not a change in the discourse.
12. **Exact duplicates and crossposts are about 8% of the eligible corpus**
    (varying 3–9% by year) and about 2% of tagged posts. They are not
    de-duplicated. This wobbles the denominator slightly; it is not corrected.

---

## 12. Change control

Post-launch methodology is deliberately frozen. Keyword-only changes are
permitted within a version; anything that changes *how* the instrument measures
requires a version bump (v8 → v9) and a public changelog entry. Corrections that
move a published line — such as the 2026-05-18 exclusion of three
off-construct communities, which stepped the sex/ERP line down across 2024–2025
— are disclosed in the site's changelog rather than made quietly.

Two such corrections landed on 2026-09-08 and moved every line: the population
became measurable posts (§2.8) and the charted rate became the pooled monthly
rate (§6.2). The keyword set did not change, so the instrument is still v8; what
changed is which posts are counted and how the month's number is formed. Both
are recorded here, in the public dataset's revision history, and in the site's
changelog.

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

One series the site publishes is **not** in v1: the "Excluding r/CharacterAI"
view (§6.3). The bundle carries the full-scope series only.

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

### 14.1 The people in the data

These are public posts, but they were written by people talking about their own
relationships, and the site is built accordingly.

- **No usernames appear anywhere on the site**, in any chart, table, quote, or
  export.
- **Every quoted post links to the public original**, so a reader can see the
  context rather than a fragment chosen to make a point.
- **If a quoted post is yours and you want it off the page, it comes down.**
  Message the project's author on X at
  [@hopes_revenge](https://x.com/hopes_revenge). No explanation needed.
- **Posts that were later deleted stay in the counts but are never quoted.** The
  archive captured them; a count is not a republication, and a quote is.

---

## 15. What makes this worth having

This is not definitive academic research and should not pretend to be.
Comparable academic work exists, often with stronger methods for frozen
snapshots. The distinctive value here is different: it is live, public,
browsable, transparent, it keeps updating, and it documents its limits instead
of hiding them.

Academic studies usually capture a period after the fact. This watches the
conversation while it is still moving.
