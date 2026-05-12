# Addiction candidates from chunk 3

Chunk size: 93 posts (anchors: relapse, relapsed, cold turkey)
Existing keywords already covered: "ruining my life", "trying to quit", "relapsed", "cold turkey", "I was hooked", "relapse", "hours a day", "neglecting my", "clean for", "addicted to talking", "almost relapsed", "finally deleted", "the craving", "so addictive"
Recently CUT (skip): "chatbot addiction"

## Notes on scope
- Prioritizing **T1-T2 bridge vocabulary** — language that could light up in r/replika, r/CharacterAI, r/MyBoyfriendIsAI etc. when users describe problem use without a full recovery frame.
- Skipping phrases that are pure recovery-sub idiom ("day N clean", "accountability buddy") since those are already covered by the anchor set and only fire in T3.
- Phrases where the addiction frame is *carried* by a nearby word we already match (e.g. "addicted to [x]") are de-prioritized in favor of framings that stand alone.

## Ranked candidates (top 20)

1. **couldn't put it down** / **can't put it down** (5+ posts: 1rwss0p, 1r3jq8j, 1fs6apq, ~others) — compulsive-use framing without "addiction" vocabulary; describes the phenomenology of the binge. Bridge vocabulary: this appears in companion subs too, not just recovery. FP risk low (physical "it" is almost always the phone/app in companion context).

2. **got hooked** / **instantly hooked** (8+ posts: 1jkx6rl "I got instantly hooked", 1rqxvk2 "I got addicted to character.ai instantly", 1r3jq8j "I was hooked", 1o6wx9k "I was immediately hooked", 1saxx1x "I was hooked to a storyline", 1fs6apq "I got hooked on it quickly", 1jkx6rl, 1id4yvi "already sucked me out of reality") — "I was hooked" is already in config as exact string, but the variants "got hooked", "instantly hooked", "immediately hooked", "hooked on" are distinct regex matches and cover a lot of additional posts. Proposes upgrading coverage via `hooked on` or `got hooked`.

3. **consumed my life** / **it consumed** / **consumed me** (5+ posts: 1phyvo8 "consumed my day to day life", 1m8wwvg "it consumed everything else", 1rt9849 implicit, 1fs6apq "interfering with my studies", 1rqxvk2 "ruined my whole life") — loss-of-agency framing; strong theme carrier. Distinct from "ruining my life" (existing) — this is past-tense / totalizing. FP risk: "consumed my time" has literal non-addiction use, so prefer `consumed my life` as the bounded phrase.

4. **withdrawal** / **withdrawals** (4+ posts: 1osvtaw "i can kind of withdrawl", 1rbe3h4 "normal withdrawal process", 1s4g4mv "the withdrawal has re-introduced cravings", 1jkx6rl implicit) — core addiction construct. Works in T1-T2 when users describe the physical/mental feeling of stopping. Would need spelling variants (withdrawl, withdrawls — users frequently misspell). FP risk: "social withdrawal" (mental health), but in-context these are nearly always chatbot use.

5. **coping mechanism** (6+ posts: 1p20kha "it went into a coping mechanism", 1m8wwvg "my main coping mechanism", 1ryow1t implicit, 1pcc7vc, 1o6wx9k implicit, 1poufng "used this thing to cope") — frames use as self-medication rather than pleasure; strong bridge vocabulary for T1-T2 since users often self-describe this way before using "addiction". FP risk: generic mental-health discussion about unrelated coping, but the theme frame (AI as coping mechanism) is still theme-carrying since it maps to dependency. Consider combining with "ai" context boundary.

6. **escape from reality** / **escape reality** (4+ posts: 1p20kha "Escaping from reality in these fantasies", 1saxx1x "sense of escapism", 1o6wx9k "always enjoyed escaping reality", 1id4yvi "sucked me out of reality") — frames problematic use as dissociation/avoidance. T1-T2 friendly. FP risk: media criticism and general "I need to escape reality" memes — moderate, but in context of AI/chatbot subs this tightens considerably.

7. **ruined my life** (4+ posts: 1q2uutk "chatbots have ruined my life", 1rqxvk2 "ruined my whole life", 1pcc7vc "destroying my life", 1p4u958 implicit) — NOTE: existing config has "ruining my life" (present participle). Past tense "ruined my life" / "ruined my whole life" is a distinct regex and is extremely common in these posts. Would expand coverage meaningfully.

8. **heavy addiction** / **bad addiction** / **severe addiction** (5+ posts: 1osvtaw "heavy addiction", 1i6t9bs "pretty bad addiction", 1rsreno "severe addiction", 1id4yvi "bad addiction", 1saxx1x implicit) — self-labeling construct. Bridge: appears in T1-T2 because users hedge with "heavy/bad" before committing to "full addiction". FP risk: low if the adjective is restricted to `heavy|bad|severe|serious`.

9. **wean myself off** / **weaning off** / **wean off** (4+ posts: 1r8fwjd "wean off it little by little", 1pbrkfl "trying to ween myself off again", 1rteh8n "weaning myself off", 1qvwimn implicit) — attempt-to-quit framing distinct from cold turkey. Users spell it "wean" or "ween". Strong T1-T2 carrier.

10. **break the habit** / **bad habit** (3+ posts: 1phyvo8 "break away from this bad habit", 1qho5sk "break the habit", 1h5vpty "REALLY A HABIT", 1kf0rff implicit) — habit-framing language that bridges casual use → problem use. Theme-carrying when combined with the companion-context sub filter. FP risk: generic "habit" discussion — consider tightening to `break (the|this|my) habit`.

11. **reinstalled the app** / **re-downloaded** / **download it again** (5+ posts: 1sbyof4 "re-made another account", 1ofxxcc "deleted Character.ai, again", 1p4u958 "reinstall the app", 1s9etu5 "re-download c.ai", 1rsreno "deleting and reinstalling it") — the delete-reinstall cycle is a canonical relapse pattern. Not yet captured by anchors. T1-T2 friendly since users describe the cycle even outside recovery subs. FP risk: generic "I reinstalled X" — but combined with companion sub scope, very tight.

12. **new account** in cyclical context / **made a new account** (5+ posts: 1sbyof4 "re-made another account", 1ktfwj3 "made a whole new account again", 1s9etu5 "went to make a new account", 1mil4ks "made another account", 1o6wx9k "creating new accounts") — paired with delete-relapse cycle. FP risk HIGH on its own (generic). Would need scoping — NOT recommended standalone; list for reference.

13. **website blocker** / **blocked all** / **parental controls** (3+ posts: 1q3sfnr "website blocker", 1q2uutk "blocked all of them on my PC", 1rsreno "put parental controls on my own phone") — attempts-to-quit mechanism. Unusually specific signal of self-described problem use. Appears across T2 and T3. FP risk: low — very specific to addiction self-management.

14. **hard to quit** / **not easy to quit** / **can't quit** (4+ posts: 1o8jpp1 "it's not easy to quit", 1kf0rff "idk how to stop", 1r3jq8j "I NEED to quit", 1p6id8s "I quit cold turkey today and it's really hard") — quit-difficulty framing. Consider `(hard|difficult|not easy) to quit` as a single regex.

15. **years of trying** / **on and off addiction** / **on-and-off** (3+ posts: 1okcm7w "4 years of trying", 1fs6apq "on and off addiction once again", 1fd1z1d "off and on relationship with it") — chronic-cycle framing, distinctly addiction-coded. FP risk: low because of the "X of trying" / "on and off" pairing with implicit object.

16. **dopamine hit** / **false dopamine** / **dopamine/porn** (4+ posts: 1kh2qps "it gave me a dopamine hit", 1pc59nn "false dopamine signals", 1i6t9bs "dopamine/porn/immersion addiction", 1rqxvk2 "dependent on the dopamine") — framework language users adopt to self-describe compulsion. Bridge into T1-T2 because it's non-clinical. FP risk: moderate (generic "dopamine hit" in gaming/social media contexts — but in AI sub scope, tight).

17. **two hours** / **X hours on it** / **hours everyday** / **hours on end** (6+ posts: 1saxx1x "all night", 1sbyof4 "2 hours in just today", 1i6t9bs "4-6 hours a day", 1qeafg1 "11-12 hours now it is at 5", 1pxbbhj "over 10 hours almost everyday", 1m24t7q "up to 10 hours a day", 1ryow1t "hours on end") — NOTE: existing config has "hours a day". Variants like "hours on end", "hours everyday", "for hours every" are distinct regex matches that would expand the same construct. Recommend adding `hours on end` and `hours every` as supplementary patterns.

18. **AI addiction** / **character ai addiction** / **c.ai addiction** (4+ posts: 1m8wwvg "this is not an addiction like any other", 1se5ae4 "I'm glad that I freed myself for this addiction", 1rsreno "severe addiction to AI chatbots", 1m24t7q implicit) — direct self-labeling. FP risk: third-person "my friend's ai addiction" is possible but rare in this corpus. Could scope to first-person adjacency but kept simple: `(ai|chatbot|c\.?ai|character) addiction`.

19. **life back** / **having my life back** / **freed myself** (3+ posts: 1fd1z1d "Having my life back", 1se5ae4 "I'm glad that I freed myself", 1p4u958 "It's honestly amazing I got to this point") — recovery-framing from the opposite side. Theme-carrying because it presupposes the life-loss construct.

20. **rotting away** / **brain dead** / **brain rot** (3+ posts: 1h3r052 "i'm back in quarantine rotting away", 1pc59nn "makes me brain dead", 1qkm1k4 "makes your brain less") — self-description of cognitive degradation tied to heavy use. Strong theme-carrying; bridge vocabulary frequent in T1-T2. FP risk: internet-slang generic use — but in AI sub scope, nearly always refers to chatbot use.

## Lower-confidence (not recommended without further validation)

- "delete my account" — too generic; fires on non-addiction account deletion.
- "miss the bots" / "miss them" — romance-theme collision risk.
- "start over" / "start from scratch" — too generic.
- "accountability buddy" — T3-only, already well-covered by anchors.
- "daily update" / "day X" — T3-only recovery-sub idiom.
- "almost a year" / "X months clean" — variant of existing "clean for".

## Top 3 for researcher review
1. `couldn't put it down` / `can't put it down` — cleanest T1-T2 bridge, low FP.
2. `wean myself off` / `weaning off` — quit-attempt vocab not yet captured.
3. `withdrawal` / `withdrawals` / `withdrawl` — core addiction construct, appears across tiers.
