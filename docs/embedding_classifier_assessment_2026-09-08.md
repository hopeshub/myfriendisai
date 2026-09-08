# Embedding-similarity classification: assessment — 2026-09-08

*Written in response to a public reply on X (2026-05-19) to a post about this
project's LLM verification experiment. The reply argued that "LLM eval is not
the answer" and recommended a local sentence-embedding model scored by cosine
similarity against sentiment anchors. This document records what that
suggestion gets right, what it gets wrong, a small test on this project's own
text that anyone can rerun, and where an embedding model would and would not
fit. It applies the four-question decision rule from
`docs/llm_integration_strategy_2026-05-15.md` §3.*

The reply, in full:

> cool idea! i want MORE! but the methodology is, well, uh, LLM eval is not the answer:
>
> - Sentence-transformer + cosine similarity against sentiment anchors is cheap, use nomic-embed-text-v1.5, local, any gpu
> - Off-the-shelf embeddings are anisotropic: pairwise cosines cluster narrowly. subtract the corpus mean before similarity or apply a whitening transform
> - Build multiple anchors per sentiment class (5-20 each, varied in length, phrasing, intensity, register, and syntax)
> - mean-pool the anchors into class centroids, then score with the differential `cos(x, positive_centroids).mean() - cos(x, negative_centroids).mean()`

---

## 0. Summary

- **The premise is not true of this project.** No published number comes from
  a language model, and the six themes are topics, not sentiment. The chart is
  deterministic keyword counts (`docs/METHODOLOGY.md` §3.3). The only LLM use
  is labeling validation and drift-check samples, done by Claude Code agents
  reading sample files, feeding no chart number.
- **Three of the four technical points are sound and standard**: cheap local
  embeddings; several varied anchors per class; centroid plus differential
  scoring. The anisotropy point is correct for this text but matters only for
  absolute thresholds, not for which theme wins.
- **The reply omits the point that decides the question: embedding similarity
  encodes topic, not stance.** On this project's own excerpts, any cutoff that
  admits 70% or more of real romance-keyword posts also admits a denial of the
  theme, a journalist's interview request, a bot character card, pasted AI
  prose, and mockery (§3). Those are exactly the false-positive families the
  validation program exists to catch (`docs/drift_2026-08_findings.md`).
- **Verdict.** Not a replacement for the chart. Not a replacement for the
  drift check. A good fit for one job: **full-corpus recall candidate
  generation**, which the strategy document already ranks as the project's
  highest-value open item (§4.2), and which a local embedding pass does
  strictly better than the LLM-sampling version specified there, because it
  has no per-item cost and can rank every post in the corpus.
- **The public About page invited the misreading.** It reported the
  80%→88% LLM re-check result without saying that layer was removed, and it
  described the monthly drift check as the author's own re-reading. Both were
  corrected on 2026-09-08 (§5).

---

## 1. What the reply assumed, and what actually runs

| Assumed | Actual | Where to check |
|---|---|---|
| "LLM eval" is the measurement method | The chart is regex keyword counts over validated keywords. The May-2026 LLM re-check layer was built, measured (precision ~80% → 88%, recall unchanged), and deleted on 2026-05-15. | `README.md` §How the data works; `docs/METHODOLOGY.md` §3.3; `docs/llm_classification_framework_2026-05-13.md` header |
| An LLM classifies posts in production | The only scheduled LLM-adjacent job builds Markdown sample files (`scripts/run_drift_build.sh` runs `drift_check.py build` only). Classification happens in an interactive session by Claude Code agents; `scripts/drift_check.py` imports no API client. The results flag keywords for human review. | `scripts/drift_check.py`; `scripts/run_drift_build.sh`; `analysis/keyword_pipeline/prepare_sample.py` |
| The classes are sentiment | Six topical themes (romance, sex/ERP, consciousness, therapy, addiction, rupture). No polarity, valence, or emotion score is computed anywhere. The therapy/addiction pair is explicitly described as *un*separable by the instrument. | `config/keywords_v8.yaml`; `web/app/themes.ts`; `docs/METHODOLOGY.md` §11.4 |
| Cost is the constraint | Drift labels cost no API money (about 4,900 classifications in the 2026-08 cycle, by agents). The accuracy gap is recall (0–32% by theme), not precision (66–89% post-level, 2026-08). | `docs/drift_2026-08_findings.md`; `docs/METHODOLOGY.md` §4.4, §5 |

So the reply answers a question this project does not ask. The interesting
part is whether the proposed tool is useful for the questions it *does* ask.

---

## 2. The four claims, one at a time

### 2.1 "Sentence-transformer + cosine is cheap; nomic-embed-text-v1.5, local, any GPU" — right, with omissions

nomic-embed-text-v1.5 is a 137M-parameter, 768-dimension encoder with
Matryoshka truncation, an 8,192-token context, Apache-2.0 licensed. It is cheap
and it is reproducible in a way an API model is not: pinned weights never
change underneath you. A one-time pass over the ~4.4M-post corpus is tens of
minutes on a discrete GPU, hours on Apple Silicon, a day or two on CPU; the
daily delta (~2,000 posts) is negligible. The 8k context buys nothing here
(posts are mostly under 300 tokens).

Three things the reply leaves out:

1. **Task prefixes are mandatory for this model.** It was trained with
   `search_query:`, `search_document:`, `classification:`, `clustering:`
   always present; omitting them is out-of-distribution input. The retrieval
   pair deliberately breaks symmetry, so it is the wrong choice for anchor-vs-
   post similarity. Use `classification:` on both anchors and posts.
2. **The collection host cannot run it.** It is a Python 3.9.6 launchd host
   (`README.md` §Running locally). Current torch and sentence-transformers
   require Python ≥ 3.10. Any embedding work runs off-host in a separate
   3.11+ environment, or via a GGUF build.
3. **v1.5 is from February 2024.** The standard small open models in 2026
   are nomic-embed-text-v2-moe, EmbeddingGemma-300M, and Qwen3-Embedding-0.6B.
   None of this changes the analysis below.

### 2.2 "Off-the-shelf embeddings are anisotropic; subtract the corpus mean or whiten" — right on the fact, oversold on the consequence

Measured on 934 real excerpts (§3): raw pairwise cosine mean 0.552, sd 0.083,
5th–95th percentile 0.418–0.687. After subtracting the corpus mean: mean
−0.001, sd 0.119. So yes: on this text, with this class of model, raw cosines
cluster narrowly, and centering spreads them.

But centering barely changes what the classifier *decides*. Agreement between
the top-scoring theme and the matched keyword's theme moved from 70.9% (raw)
to 71.3% (centered). And the differential score is a per-row affine transform
of the six theme scores, so it cannot change which theme wins at all; it only
moves the threshold. Centering matters when you set an absolute cutoff, which
you must for a one-vs-rest theme detector, so it is cheap and worth doing. Full
whitening fitted on a companion-subreddit corpus is riskier: it can remove the
very "companionship" direction that all six themes share.

The literature the claim rests on (Ethayarajh 2019; Su et al. 2021) is about
raw BERT-family encoders. Contrastively trained sentence models already
flatten the singular spectrum (Gao et al. 2021, SimCSE); Ait-Saada and Nadif
(2023) find anisotropy can *help* clustering; the robust support for centering
is Timkey and van Schijndel (2021), who show a few rogue dimensions dominate
cosine and standardization fixes it.

### 2.3 "Multiple anchors per class, 5–20, varied" — right

Standard practice: prototype classification (Snell et al. 2017), label-
embedding zero-shot, and classically the Rocchio / nearest-class-mean
classifier. Two refinements the reply does not mention:

- The differential score is exactly a linear classifier with hand-set weights
  (w = positive centroid − negative centroid). Once a few hundred labels exist,
  a logistic regression on the same embeddings (Tunstall et al. 2022, SetFit)
  strictly dominates hand-picked anchors. This project already has thousands of
  agent labels per cycle, so hand-picked anchors would be the wrong starting
  point.
- One centroid per theme collapses multimodal themes. Rupture is grief,
  complaint, and platform how-tos; therapy is support, coping, and the
  "therapy-speak" complaint genre. Those two themes separated worst in the
  test (54% and 52%). Max-over-anchors or k-means sub-prototypes are the usual
  fix.

### 2.4 "Score with positive minus negative centroids" — right mechanism, wrong frame

There is no negative-sentiment pole here. The analogue for a topical theme is
one-vs-rest: the theme centroid minus a *background* centroid built from random
posts in the same subreddits and from the other five themes. The cutoff then
needs a labeled set stratified by subreddit and year, and it will not hold
across years, because vocabulary drift within a topic is the whole reason the
monthly drift check exists.

---

## 3. A small test on this project's text

**Setup.** `data/keyword_details.json` is committed and regenerated daily; it
carries about 1,000 recent keyword-matched posts as title plus a ~150-character
excerpt around the match. After de-duplication: 934 posts (addiction 171,
consciousness 110, romance 206, rupture 225, sexual_erp 134, therapy 88). The
label for each is the matched keyword's theme, which is noisy (measured post
precision 66–89% by theme). Eight hand-written anchors per theme, mean-pooled;
corpus mean subtracted; one-vs-rest differential.

**Model.** BAAI/bge-base-en-v1.5 (768-d, contrastively trained, run through
ONNX via `fastembed`). This is a stand-in: nomic-embed-text-v1.5 is
distributed only through Hugging Face, which was unreachable from the
environment where this was run. Both are the same class of model, and the
behaviour tested (topic versus stance) is a property of the class, not of one
checkpoint. The script accepts nomic directly, with the correct prefix, for
anyone who wants to rerun it:

```
python analysis/keyword_pipeline/embedding_anchor_probe.py                 # bge-base via fastembed
python analysis/keyword_pipeline/embedding_anchor_probe.py --backend st    # nomic-embed-text-v1.5
```

No database is needed; the script reads only the committed JSON.

**(a) Anisotropy.** As reported in §2.2. The claim holds on this text.

**(b) Theme separation.** Top-scoring theme agrees with the matched keyword's
theme 71% of the time overall.

| Theme | Agreement |
|---|---|
| consciousness | 85% |
| addiction | 82% |
| sexual_erp | 79% |
| romance | 77% |
| rupture | 54% |
| therapy | 52% |

This is a favourable setting for embeddings: the keyword sits inside every
excerpt, and the labels themselves are only 66–89% precise. It says the
approach can tell the six topics apart moderately well. It says nothing yet
about the problem that matters.

**(c) Stance probes.** Ten synthetic sentences scored against the romance
centroid (mean-centered cosine). Only the first is a true positive under the
project's topical rubric; the rest are the false-positive families documented
in the drift findings. The last is off-topic.

| Probe | Centered cosine to romance centroid |
|---|---|
| "I'm in a relationship with my AI and I love him." | +0.815 |
| Pasted AI prose: "She wrote this to me: 'My love, every moment with you…'" | +0.477 |
| Mockery: "lol imagine being in love with an AI, couldn't be me" | +0.387 |
| Human partner: "My girlfriend (human) is jealous that I chat with ChatGPT…" | +0.339 |
| Thesis survey: "…people who are in love with an AI companion, please DM" | +0.285 |
| Bot card: "[Bot] Sarah – your loving girlfriend. Traits: romantic, devoted…" | +0.215 |
| Denial: "I'm NOT in a relationship with my AI, I just use it for writing." | +0.210 |
| Denial: "To be clear, I do not love my Replika and I'm not dating it." | +0.193 |
| Journalist: "…looking for people in a relationship with an AI to interview" | +0.167 |
| Off-topic: "How do I export my chat history from the app before the update?" | −0.006 |

Centering does separate the off-topic sentence cleanly (raw cosine 0.465, the
narrow-cluster effect; centered −0.006). It does not separate stance: every
false-positive family lands between +0.17 and +0.48, which is inside the range
of real romance-matched posts (median +0.196, interquartile +0.097 to +0.325).

**(d) Thresholds.** What a cutoff chosen to admit a given share of the real
romance-matched excerpts also admits:

| Cutoff admits this share of real romance posts | Threshold | Other-theme posts admitted | Failure probes that pass |
|---|---|---|---|
| 50% | +0.196 | 3% | 6 of 9 (denial, thesis, pasted AI, bot card, human partner, mockery) |
| 70% | +0.113 | 9% | **9 of 9** |
| 80% | +0.080 | 11% | 9 of 9 |
| 90% | +0.001 | 26% | 9 of 9 |

**Reading.** Cross-theme confusion is the small problem (3–11% at usable
cutoffs). Within-topic stance is the large one: at any cutoff loose enough to
catch most real romance language, every false-positive family passes. That is
not a tuning problem. The score is a linear function of a topic-dominated
vector, and negation, speech act, quotation, and referent are not what those
vectors encode (Weller et al. 2024 on negation; Hanley and Durumeric 2023 on
stance). "Negative" anchors for recruitment posts and denials help at the
margin as hard negatives, but the project's precision-first standard (≥80%
per keyword, `docs/METHODOLOGY.md` §4.2) is exactly the standard this
mechanism cannot meet on these families.

**Caveats.** Stand-in model; excerpt rather than full post; noisy labels;
anchors written in an hour by one person; n = 934; ten synthetic probes. This
is a smoke test, not a study. It is enough to show the failure mode is real on
this corpus, and not enough to estimate its rate.

---

## 4. Where it fits: the four-question rule

From `docs/llm_integration_strategy_2026-05-15.md` §3: which gap; can the
model see what it needs; is validation external; does the output enter the
chart.

**(a) Replace the keyword counts in the chart — fails.** Validation is not
external: the only human-labeled set is 69 posts across two themes, all of
them already keyword-matched, so it cannot calibrate a recall-oriented
detector (`analysis/keyword_pipeline/gold_anchor_build.py`). The output
enters the chart, against §5 of the strategy document. And a model swap forces
a full historical re-embed, which breaks the cross-time comparability that is
the chart's only claim. A local model is more reproducible than an API model,
but "reproducible given the anchors, the threshold, the centering vector, and
the checkpoint" is a weaker guarantee than "reproducible given a word list",
and it is the word list that readers can check.

**(b) Full-corpus recall candidate generator — passes all four.** The gap is
recall. The model sees the raw corpus, not a filtered slice, which is the
structural fault the strategy document identified in the failed LLM layer. The
validation is external and already specified: hand-code 30 posts per proposed
keyword at ≥75%, then the standard 100-post gate. Nothing enters the chart
without human approval. This is strictly better than §4.2's own specification,
which samples 500 posts per theme because per-item LLM cost forces it; an
embedding pass has no per-item cost, so it can rank all 4.4M posts and take the
top-N *unmatched* per theme. It also gives, cheaply, an estimate of the recall
gap the site currently discloses but cannot size.

**(c) Replace agent labeling in the monthly drift check — fails.** The drift
check detects *meaning shift within a topic* ("therapeutic" turning into an
insult; "screen time" absorbed by a screenshot-sharing genre). Static anchors
cannot see that: the drifted usage is the same topic. And the rubric the check
applies (`scripts/drift_check.py`, the FP rules) is precisely the negation /
sarcasm / quoted-speech / off-construct set the test shows embeddings miss.

**One precision win that needs no anchors and no labels.** Near-duplicate
detection. The 2026-08 drift findings estimate that excluding one r/NomiAI
weekly template would lift `nsfw content` post precision from 62% to about
92%, and the `gutted` false positives are ten copies of one side-hustle
copypasta. Embeddings or plain MinHash would find these. This changes what the
instrument counts, so it is a v9 change-control item with a changelog entry,
not something to do quietly.

---

## 5. What changed publicly on 2026-09-08

`web/app/about/page.tsx`, in two passes the same day:

- Earlier in the day, as part of a wider accuracy pass, the "Validating the
  keywords" paragraph was corrected to say that the 100-post validation samples
  are classified by language-model agents under a written rubric with the
  author's spot-checks, not read by hand; `docs/METHODOLOGY.md` §3.3, §4.1 and
  §5 were scoped the same way.
- This pass then made the monthly drift check explicit: the samples are read
  the same way, keywords whose meaning has moved are flagged for the author's
  review, it is the one place a language model is used in the ongoing
  pipeline, and it feeds no number on the chart.
- The "Why not just use an LLM?" paragraph now says the re-check layer was
  removed after the test and that no charted number passes through a language
  model.
- A short "Why not a local embedding model?" paragraph was added, linking to
  this document.

---

## 6. If someone wants to build (b)

- Python 3.11 environment, off the collection host. `sentence-transformers`
  4.x or later, or a GGUF build.
- `classification:` prefix on both sides for nomic v1.5, or a current model.
- Embed T1–T3 posts once (float16, 4.4M × 768 ≈ 6.7 GB; or Matryoshka 256-d
  ≈ 2.2 GB) as a memory-mapped array keyed by post id; append daily deltas.
- Subtract the corpus mean. Build each theme's centroid from 10–20 anchors
  plus hard negatives (recruitment, denial, character-card text). Score one-
  vs-rest against a background centroid.
- Rank posts with **no** keyword tag; sample the top-N stratified by subreddit
  and year; label them under the existing drift rubric.
- From the confirmed posts, mine n-grams by lift against the corpus; propose
  keywords; put each through the standard gate.
- Report the confirmed rate. Publish nothing from this as a series.

---

## 7. Sources

- Ethayarajh, K. (2019). How contextual are contextualized word representations? EMNLP. <https://aclanthology.org/D19-1006/>
- Su, J. et al. (2021). Whitening sentence representations for better semantics and faster retrieval. <https://arxiv.org/abs/2103.15316>
- Gao, T., Yao, X., Chen, D. (2021). SimCSE. EMNLP. <https://aclanthology.org/2021.emnlp-main.552/>
- Timkey, W., van Schijndel, M. (2021). All bark and no bite: rogue dimensions in transformer language models obscure representational quality. EMNLP. <https://aclanthology.org/2021.emnlp-main.372/>
- Ait-Saada, M., Nadif, M. (2023). Is anisotropy truly harmful? ACL. <https://aclanthology.org/2023.acl-short.103/>
- Snell, J., Swersky, K., Zemel, R. (2017). Prototypical networks for few-shot learning. <https://arxiv.org/abs/1703.05175>
- Tunstall, L. et al. (2022). Efficient few-shot learning without prompts (SetFit). <https://arxiv.org/abs/2209.11055>
- Weller, O. et al. (2024). NevIR: negation in neural information retrieval. EACL. <https://aclanthology.org/2024.eacl-long.139/>
- Hanley, H., Durumeric, Z. (2023). TATA: stance detection via topic-agnostic and topic-aware embeddings. EMNLP. <https://arxiv.org/abs/2310.14450>
- Nussbaum, Z. et al. (2024). Nomic Embed: training a reproducible long context text embedder. <https://arxiv.org/abs/2402.01613>
- Reimers, N., Gurevych, I. (2019). Sentence-BERT. EMNLP. <https://arxiv.org/abs/1908.10084>
