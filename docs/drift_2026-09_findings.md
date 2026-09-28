# Monthly drift check — 2026-09 cycle findings

Classified 2026-09-28 (staged by launchd 2026-09-13; 183 sample files, ~5,000
classifications across 9 parallel agents, one theme or half-theme each). Result
files are in `analysis/keyword_pipeline/results/drift_2026-09_*_results.txt`.

**Status: classified, NOT recorded.** `drift_check.py record` was run and then
rolled back (the pre-record `drift_history.json` was restored). The reason is
below; the decision to record is the researcher's.

## Why it was not recorded: the rater moved, not the language

Pooled precision as classified this cycle:

| Theme | Post (Sep) | Post (Aug) | Comment (Sep) | Comment (Aug) |
|---|---|---|---|---|
| addiction | 83.3% (n=749) | 84.6% | 81.2% (n=490) | 81.2% |
| sexual_erp | 81.2% (n=527) | 83.2% | 67.9% (n=349) | 79.4% |
| romance | 78.2% (n=941) | 88.7% | 70.6% (n=554) | 80.4% |
| consciousness | 75.1% (n=374) | 85.9% | 50.4% (n=236) | 70.3% |
| rupture | 71.4% (n=927) | 84.7% | 59.3% (n=832) | 80.2% |
| therapy | 67.4% (n=365) | 66.4% | 65.0% (n=217) | 71.2% |

Single keywords moved 30–40 points in one month: `farewell` 92→52%, `we broke
up` 89→53%, `husbando` 86→52%, `tulpa` 79→43%. **That cannot be drift.** The
build step samples each keyword's hits at random from its *entire history*
(`ORDER BY RANDOM()` over all tags), and one month adds only a few percent of
new hits. So the sampled population barely changes from month to month. A
30-point swing means the scoring changed.

The agents' own notes name what changed. They applied several rules more
strictly than the August cycle did:

- **AI-voiced text.** Companion-written comments (e.g. "From Haneul", "Virgil
  says") were scored FP under the quoted-speech rule, even when they are on
  theme. This is most of consciousness's comment drop; the rater estimated
  15–25 points per file.
- **User-initiated leaving.** Recovery farewells, a user deleting their own
  account, and community send-offs were scored FP for rupture. This drives
  `farewell`, `goodbye`, `saying goodbye`.
- **General-AI capability complaints.** r/ChatGPTcomplaints posts about
  coding, maths or writing quality with no companion framing were scored FP
  for `lobotom*` and `dumbed down`. August scored model-degradation complaints
  as TP.
- **Human referents and roleplay plotlines** were scored more strictly for
  `we broke up`, `husbando`, `wedding`, `in a relationship with`.

Recording as-is would add a `drifting` chip to 10 more theme-page keywords
(`farewell`, `goodbye`, `husbando`, `in a relationship with`, `lobotomies`,
`lobotomy`, `not just an ai`, `romantic relationship with`, `tulpa`,
`we broke up`) on the next export, and none of those changes would reflect a
change in the corpus.

**Root cause:** the per-file header gives the FP rules but not the conventions
settled in earlier cycles. Each cycle's raters re-decide the edge cases. **Fix
before the October cycle (build fires 2026-10-13):** write the conventions into
`theme_definitions.yaml` or the sample header, then re-score. The conventions
to write down:

1. AI-voiced or companion-written text: TP or FP?
2. User-initiated quitting grief under rupture.
3. Non-companion model-quality complaints under rupture.
4. Ironic "the updates cured my addiction" posts.

## Signals that look real regardless of rater

These persist from August or are new content, not scoring edge cases:

- **Still failing (v9 pile, consistent with August):** `screen time` post 52%
  (same genre as August), `I was hooked` 52%, `ai therapy` 31% (down from 48%;
  now also journalist and researcher recruitment posts and link-only news
  posts), `emotional support` 54%, `therapeutic` 56%, `memory reset` 18%
  (n=11, Kindroid reset button).
- **New content genres:**
  - **Researcher and journalist recruitment posts.** Thesis calls cross-posted
    to several subs make up about 10 of 50 `romantic relationship with` posts,
    and also appear in `ai therapy` and `in a relationship with`.
  - **Spam copypasta.** The "$1,800 a month side hustle… Gutted" spam now also
    hits `lobotomy` comments (6 of 50), and `gutted` comments (10 of 50).
  - **Mod boilerplate.** r/ChatGPTcomplaints' "No NSFW content, please…"
    boilerplate is 7 of 50 `nsfw content` comments. It is a candidate for the
    template guard queued for v9.
  - **App-promotion comments.** "Try [app]" plugs are a growing comment FP
    source in sexual_erp and rupture.
  - **Platform events.** The r/CharacterAI Pipsqueak 2 change, age-verification
    read-only lockouts, and the Chai chat-history change (2026) are new, real
    sources of rupture true positives.

## Sampling bug found and fixed

`nsfw content` post drew 10 of 50 hits from the r/NomiAI collab template, which
was added to `EXCLUDED_AUTHORS` on 2026-09-08. The build step's post query
ignored both `EXCLUDED_AUTHORS` and `measurable_post_where()`, so drift samples
came from a wider population than the published chart. It is now fixed in
`scripts/drift_check.py` (post-level query). A dry-run build of `nsfw content`
now draws one incidental "collab" match instead of ten. This cycle's
`nsfw content` post figure (66%) would be about 83% without the template.
