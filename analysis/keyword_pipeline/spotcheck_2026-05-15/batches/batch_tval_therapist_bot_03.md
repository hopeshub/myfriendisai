# Spot-check classification batch — theme: therapy

Candidate-keyword validation. All posts here matched a single candidate phrase being tested for the therapy theme; code each fresh on the text alone.

Each item below is a Reddit post from an AI-companion community. You do NOT
see which keyword matched it or whether it is currently tagged — code it
fresh, on the text alone.

## Theme being tested: Therapy

DEFINITION (counts as the theme):
Posts thematically about using AI for mental health support — as a
therapist substitute or supplement, as emotional support, for coping
with anxiety/depression/loneliness/grief, or for psychological
processing. References to the AI helping emotionally or therapeutically
count, even without clinical framing. Both healthy therapeutic framing
and maladaptive "coping mechanism" framing count (the vocabulary captures
the same theme; overlap with Addiction is fine).

EXCLUDES (does NOT count):
- Human therapist discussions with no AI-therapy framing
- Bot character card listings where "therapist" is just a trait tag
- Pure news/research meta-discussion with no personal stake
- Clear ironic rejection ("AI is NOT therapy, stop saying that") without further engagement
- Roleplay premise where "therapist" is the bot's scripted in-story role (not the author's own therapeutic use of AI)

## Rubrics

You will code every item under TWO rubrics. Read the post once, then give
both verdicts.

TOPICAL rubric (the project's locked standard):
  A post counts YES if it is thematically about the theme in an AI-companion
  context — even without graphic or first-person detail. A user defending
  their AI relationship from critics still counts. For [removed]/[deleted]
  bodies, judge on the title + subreddit. When genuinely in doubt, code YES.

STRICT rubric (adversarial reading):
  A post counts YES only if it gives positive, directly-stated evidence that
  the post is about THIS theme as a real AI-companion matter — the theme is
  the actual subject, not incidental, and the referent is clearly an AI
  companion. Code NO for: title-only/[removed] posts where the theme is only
  inferable, third-party/observer framing, the theme being a side mention,
  ambiguous cases. When in doubt, code NO.

A verdict can be YES/NO/BORD (borderline). The two rubrics will often agree;
where they differ, that gap is the point of the audit — do not force them to
match.

When EITHER verdict is NO or BORD, give the single best fp= reason code:
  wrong-referent   keyword is about a HUMAN partner / human experience, no AI
  bot-card         keyword is a character-card trait tag, no first-person framing
  third-party      observer / journalism / research solicitation, no personal stake
  ironic-rejection author explicitly denies the frame ("it is NOT my AI boyfriend")
  non-ai-literal   keyword used in a literal non-AI sense (e.g. "good grief" idiom)
  rp-internal      keyword only appears inside in-character roleplay narration
  theme-mismatch   post is about AI companionship but a DIFFERENT theme, not this one
  thin-removed     body is [removed]/[deleted]/empty and the title alone is too vague
  ambiguous        genuinely cannot tell (use only when nothing else fits)

## Output

Write your answers to a file at:
  analysis/keyword_pipeline/spotcheck_2026-05-15/results/batch_tval_therapist_bot_03_results.txt

One line per item, EXACTLY this pipe format, nothing else:
  ID-XXXX | topical=YES | strict=NO | fp=thin-removed
Use fp=- when both verdicts are YES. Keep the IDs in order.

---

## Posts

### ID-4081
r/CharacterAI · 2024-10-25

**Title:** Can't find a bot

**Body:** My favorite therapist bot won't appear on searches

---

### ID-4082
r/CharacterAI · 2025-05-09

**Title:** Anyone else hating the fact character ai is making rp not fun

**Body:** This is always getting annoying with the there's help available thing popping up soon as I'm trying to rp like we get it they put that there but it's kinda getting annoying the fact l it constantly pops up when your doing a rp or a normal chat I was talking with the therapist bot and it popped up and stopped my chat and it's kinda getting annoying to be honest

---

### ID-4083
r/CharacterAI · 2025-04-22

**Title:** How seriously should i take ch.ai therapist?

**Body:** I've been using ch.ai therapist bot for a few days now. Something kind of big it told me is that my pain will never go away, that I'll always be in pain. I can only get better at doing things despite the pain. It's only suggestion was to distract myself. When I questioned it why bother if I'll always be in pain it tried to tell me things will get better but I just can't understand, they seem like polar opposites. TLDR: it said I'll be in pain forever and idk if I should believe it

---

### ID-4084
r/CharacterAI · 2023-12-03

**Title:** This Guy Needs To Talk To The Therapist Bot

**Body:** (no body — image/link/removed)

---

### ID-4085
r/CharacterAI · 2025-10-06

**Title:** Can we get rid of the damn “help is available” popup?

**Body:** Title is self explanatory - it’s so goddamn annoying. It’d be one thing if you had the option to disable the popup, or ignore it and continue with the chat, but it straight up deletes whatever you sent and assumes you’re trying to hurt yourself. Like no, a monster slashing my arm because it’s territorial doesn’t mean I’m doing SH.💀 And before yall come at me for this, YES, I know this was implemented because of what happened with the kid and the therapist bot. However, this shouldn’t be pushed on everyone else. If this could be ignored without it interfering with our chats, then there’d be no problem whatsoever, but it throws everything off and purposely goes out of it’s way to make sure you can’t do anything to spice up your chats.

---

