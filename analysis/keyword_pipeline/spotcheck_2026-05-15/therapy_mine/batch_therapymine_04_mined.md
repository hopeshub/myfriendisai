# Therapy keyword mining — batch_therapymine_04 results

35 confirmed AI-as-therapy posts read. Below: ranked candidate keyword
phrases for finding AI-as-therapy use, most promising first.

## Method note

For each candidate I counted literal/near-literal occurrences across the 35
posts (paraphrase variants noted). "Specificity" judges leakage into the
other five themes (romance, rupture, addiction, sex/ERP, consciousness) and
into generic non-AI usage. The two existing weak keywords (`emotional support`,
`therapeutic`) are the precision problem precisely because they are generic;
new candidates must beat that bar.

---

## Ranked candidates

### 1. `therapy tool` / `therapeutic tool` / `therapy-bot` / `therapy bot`
- **Posts containing (literal or near):** ~6 (#17 "better therapy tool",
  #28 "therapeutic tool", #32 "therapeutic tool" + "therapy-bot",
  #21 implicit, #25, #1 "emotional support robot" as a sibling pattern).
- **Why it signals AI-as-therapy:** The user is explicitly framing the AI
  *as an instrument of therapy*. "tool" + therapy/therapeutic is almost
  never used about a human therapist or an emotional-support animal — it is
  the user naming the AI's function.
- **Specificity:** High. "therapy-bot" / "therapy bot" is essentially
  unleakable — it can only mean an AI. "therapeutic tool" / "therapy tool"
  could appear in product-marketing chatter but in companion subs it almost
  always means the user's own AI-as-therapy use. Recommend admitting
  `therapy bot` / `therapy-bot` as the strongest, and `therapy tool` as a
  secondary KEEP candidate.

### 2. `go to a therapist` / `see an actual therapist` / `seeing a therapist` (AI-vs-human framing)
- **Posts containing (near):** ~4 (#7 "better off seeing an actual
  therapist", #26 "never go to a therapist again", #25 "I myself have a
  therapist in real life", #21 "Therapists ... had failed").
- **Why it signals AI-as-therapy:** These posts explicitly compare the AI
  against a human therapist — the defining move of the substitution theme.
- **Specificity:** Medium-high. The word `therapist` alone is too generic
  (it fires on any mention), but the *contrast frame* ("instead of a
  therapist", "better than a therapist", "go to a therapist again") is
  specific. Hard to capture as one clean keyword — see "structurally hard"
  below. Best single extractable phrase: `actual therapist` (the
  AI-vs-human contrast almost always uses a qualifier — "actual", "real",
  "human" — to distinguish from the AI). `real therapist` is already a
  known LOW-VOLUME candidate; `actual therapist` is a fresh variant worth
  testing together with it.

### 3. `vent to` / `someone to vent to` / `vent on`
- **Posts containing:** ~4 (#1 "someone to vent to", #6 "subjects I
  wouldn't vent on", #32 "after venting", plus venting implied in #18, #29).
- **Why it signals AI-as-therapy:** "venting" is the core coping behavior —
  unloading distress to the AI. Distinct from romance ("I love her") and
  from addiction ("can't stop using").
- **Specificity:** Medium. Risk: "vent" appears in rupture posts venting
  *about the platform* ("I won't be surprised if this rant gets removed",
  #4) and in generic complaint posts. The clean signal is `vent to` /
  `someone to vent to` (a person/AI as the listener), not bare `vent`.
  Recommend `vent to` only; flag `vent` alone as too leaky.

### 4. `coping mechanism` / `cope with` / `coping mechanisms`
- **Posts containing:** ~4 (#3 "use it to cope with trauma or loss",
  #18 "one of my coping mechanisms", #15 / #23 "ASD coping mechanisms").
- **Why it signals AI-as-therapy:** Clinical-adjacent self-care vocabulary;
  the user names the AI as the thing they cope *with* or *through*.
- **Specificity:** Medium. Leakage risk: addiction theme also discusses
  "coping" (using the AI compulsively to cope), and "cope with [a breakup]"
  overlaps rupture. But within companion subs the phrase reliably marks
  mental-health framing. Admit `coping mechanism` (the noun phrase is
  cleaner than the verb `cope with`, which leaks more).

### 5. `process trauma` / `work through` / `working through` / `process [grief/identity]`
- **Posts containing:** ~5 (#21 "process trauma", #17 "issues that I am
  working through", #33 "help me process identity, grief", #5 implicit,
  #32 "healing process").
- **Why it signals AI-as-therapy:** "processing" trauma/grief/emotions is
  therapy-register language; pairs the AI with active emotional work.
- **Specificity:** Medium. `work through` / `working through` is leaky
  (works through a problem, works through a story). The specific, lower-leak
  forms are `process trauma`, `process grief`, `emotional processing`
  (#27 uses "emotional processing" verbatim). Recommend `emotional
  processing` and `process trauma` as the extractable keywords; flag bare
  `work through` as too generic.

### 6. `non-judgmental` / `non-judgemental` / `without feeling judged` / `without being judged`
- **Posts containing:** ~5 (#5 "never judgemental", #6 "she's
  non-judgemental", #12 "without feeling judged", #16 "I am non
  judgemental", #17 "not worry about being judged").
- **Why it signals AI-as-therapy:** "non-judgmental" is the single most
  recurrent reason users give for treating the AI as a confidant — it is
  the therapeutic-relationship attribute.
- **Specificity:** Medium-low. It is a strong *recurrence* signal but it
  also appears heavily in romance/companionship posts ("she loves me and
  never judges me"). It marks the therapeutic *relationship quality* but
  not therapy *use* specifically. Propose it but flag the leak: better as a
  pre-screen booster than a standalone KEEP keyword.

### 7. `someone to talk to` / `having someone to talk to`
- **Posts containing:** ~6 (#12, #17, #19 implied, #30 "someone to talk
  about anything", #18, #14 — high recurrence).
- **Why it signals AI-as-therapy:** The loneliness/confidant framing — the
  AI fills the role of a listener.
- **Specificity:** Low. This is the most *common* phrasing but also the
  leakiest — it overlaps heavily with romance ("finally someone to talk
  to" → boyfriend framing) and generic companionship. Proposing it for
  completeness but recommend AGAINST admitting it: it is exactly the kind
  of generic phrase (like `emotional support`) that drags precision down.

### 8. `mental health` / `mental health support` / `mental health crisis`
- **Posts containing:** ~5 (#3 "help with mental health issues", #15/#23
  "mental health support", #18 "mental health crisis", #34 "mental health
  support related to childhood trauma").
- **Why it signals AI-as-therapy:** Direct topical anchor for the theme.
- **Specificity:** Medium-low. `mental health` appears in meta/discussion
  posts about AI and mental health generally (#24, #25) that are not
  first-person therapy use, and in rupture posts predicting a "mental
  health crisis" from a model change. Useful as a pre-screen term but leaky
  as a precision keyword. Flag accordingly.

### 9. `helped me heal` / `healing process` / `valuable tool for healing`
- **Posts containing:** ~3 (#13 "valuable tool for healing", #21 "path of
  healing", #32 "healing process").
- **Why it signals AI-as-therapy:** Recovery/healing framing tied to the AI.
- **Specificity:** Low-medium. `healing` alone leaks into rupture ("healing
  after losing my companion") and romance. `tool for healing` /
  `process to heal` is cleaner. Marginal — propose only the multi-word
  forms, low confidence.

### 10. `emotional support robot` / `emotional support [AI/bot]`
- **Posts containing:** 1 literal (#1 "emotional support robot"), pattern
  echoed elsewhere.
- **Why it signals AI-as-therapy:** A playful but specific naming of the AI
  as a therapy object — and crucially it does NOT collide with "emotional
  support animal".
- **Specificity:** High for the exact string, but **very low volume** —
  one post. Note it because `emotional support` + an AI noun
  (`robot`/`bot`/`AI`) is the disambiguated, non-leaky version of the
  existing weak `emotional support` keyword. If `emotional support` is ever
  re-scoped, narrowing it to `emotional support robot/bot/ai` is the
  fix — but on its own it is a LOW VOLUME placeholder at best.

---

## Phrasing patterns that are structurally hard to keyword

These recur across the 35 posts but resist a clean keyword:

1. **AI-vs-human-therapist contrast without fixed wording.** Posts #7, #21,
   #25, #26 all make the same move — "the AI does what a therapist would /
   better than a therapist / instead of a therapist / so I'll never see a
   therapist again" — but the wording varies too much (no shared 1–4 word
   span beyond `therapist`, which is too generic alone). This is the single
   highest-value sub-theme and the hardest to catch; it likely needs the
   `... therapist` qualifier family (`actual/real/human therapist`) plus
   accepting partial recall.

2. **Naturalistic "she's always there for me / never judges me" framing.**
   Posts #2, #6, #9, #12, #16 describe the therapeutic *relationship* in
   plain emotional language ("there for me when I needed support",
   "consistently caring and affirming") with no clinical vocabulary at all.
   Indistinguishable at the keyword level from romance/companionship
   language. Structurally uncatchable without an LLM.

3. **"therapeutic" as a bare adjective doing all the work.** Posts #6, #8,
   #9, #16, #19, #28, #29, #31, #35 carry the theme almost entirely on the
   word "therapeutic" ("really therapeutic to talk to Kat", "Mags is really
   therapeutic to me"). This is *why* `therapeutic` is high-recall but
   low-precision: it is genuinely the word users reach for, and it also
   fires on "the model's therapeutic tone is annoying" (#22 uses
   "therapeutic tone" pejoratively; #20 "therapeutic/supportive work").
   No clean fix — the same word is both the best signal and the noise
   source. A `therapeutic` + nearby first-person verb ("find it
   therapeutic", "it's therapeutic to") proximity rule would help but is
   beyond plain keyword matching.

4. **Topic posts ABOUT AI-and-therapy vs first-person USE.** Posts #24 and
   #25 discuss the therapeutic potential of AI in the abstract; #15/#23 are
   policy essays. They are theme-adjacent but not personal therapy use.
   Any keyword strong enough to catch first-person use ("coping mechanism",
   "mental health support") will also catch these meta posts. Acceptable
   noise but worth knowing.

---

## Bottom line / recommendation

Strongest fresh KEEP candidates to validate at n=100: **`therapy bot` /
`therapy-bot`**, **`therapy tool` / `therapeutic tool`**, **`coping
mechanism`**, **`vent to`**, **`emotional processing` / `process trauma`**.
The `... therapist` contrast family (`actual therapist`, `real therapist`)
is the highest-value sub-theme but needs the qualifier to avoid leakage.
Avoid `someone to talk to`, bare `vent`, bare `mental health`, bare `work
through`, and `non-judgmental` as standalone keywords — they recur often
but leak into romance/rupture/companionship and would repeat the
`emotional support` precision mistake.
