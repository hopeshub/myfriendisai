# Guide: Request Reddit API access and finish OAuth setup (full hand-off)

**Status:** ticket FILED 2026-06-11 (via Claude + Chrome). Ticket number pending —
watch walkerbockley@gmail.com (and spam) for the Zendesk confirmation email and
record the number here. Part 1 is DONE; we are now in Part 2 (waiting).
Filing details: form submitted signed-out of the help center under account
u/GuardEither6527, email walkerbockley@gmail.com. The live form turned out to be
the structured Devvit-era "Data Access Request" form (role: "I'm a developer";
inquiry: "build a Reddit App that does not work in the Devvit ecosystem"), so the
ticket text below was adapted across its fields: benefit/purpose, detailed
description (read-only scope, ~360-470 req/day, policy-compliance affirmations,
.json-endpoint history), what's-missing-from-Devvit (external read-only pipeline,
no on-Reddit surface), source link (github.com/hopeshub/myfriendisai +
myfriendisai.com), all 40 subreddits, operating username u/GuardEither6527.
No-reply nudge date (4 weeks): 2026-07-09.
**Who can do this:** anyone with (a) access to Walker's Reddit account in a browser
and (b) access to this Mac. No coding required; every command is copy-paste.
**Goal:** get Reddit's explicit approval to create an API app, then create the app,
install the credentials, and verify — so daily collection runs on Reddit's API
again instead of the Arctic Shift fallback.

**Why this exists.** Reddit retired self-serve API app creation (~March 2026).
`reddit.com/prefs/apps` now redirects everyone to the
[Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy),
whose first rule is *"Approval is required: You must request access and get explicit
approval before accessing any Reddit data through our API."* So the old quick path
in `docs/oauth_setup_guide.md` Step 2 is dead until Reddit approves a request.

**There is no urgency.** The site is healthy on the Arctic Shift fallback — theme
trends stay current; only subscriber snapshots and comment collection are paused.
Never use workarounds (no extra accounts, no borrowed API keys, no third-party
keys). If anything below fails repeatedly, stop and tell Walker.

---

## Part 1 — File the access request ticket (~10 minutes)

1. In a browser, sign in to **Walker's Reddit account** at https://www.reddit.com
   (his main/durable account — ask him which if unsure; note the username, you
   need it in step 4).
2. Open the developer request form:
   **https://support.reddithelp.com/hc/en-us/requests/new?ticket_form_id=14868593862164&tf_42139884615700=api_request_type_developer_clone**
   (This is the official "file a ticket" link from the Responsible Builder Policy
   for non-commercial developers. If the link 404s, go to
   https://support.reddithelp.com → submit a request → choose the **Developer /
   API** form and the **developer** request type in the role dropdown.)
3. Fill the form's standard fields:
   - **Email:** `walkerbockley@gmail.com`
   - **Role / request type** (if shown): **developer** (NOT "researcher" — that
     dropdown routes to the academic Reddit-for-Researchers program, which
     requires university affiliation we don't have; this is a non-commercial
     public website, which is their developer track)
   - **Subject:** copy from the ticket text below
   - **Description:** copy the ticket body below, **replacing
     `<REDDIT_USERNAME>`** with the account you signed in as
4. Submit, and note the ticket number Reddit emails back.

### Ticket text (copy-paste)

**Subject:**

```
API access request — non-commercial public-interest tracker (read-only, ~400 requests/day)
```

**Body:**

```
Hello,

Per the Responsible Builder Policy, I'm requesting approval to access the
Reddit Data API for a small non-commercial project, and to create a
script-type app for it.

WHAT THE PROJECT IS
myfriendisai.com is a free public website that charts how discussion themes
rise and fall over time across a fixed set of AI-companion communities
(r/replika, r/CharacterAI, r/MyBoyfriendIsAI, and similar). It publishes
only aggregate, community-level statistics: monthly post volumes and how
often validated keyword vocabularies appear, normalized per 1,000 posts.
It is run by one person (me) with no commercial angle of any kind — no ads,
no paywall, no data sales, no resale of API access. Methodology is public
at https://myfriendisai.com/about.

WHAT ACCESS I NEED
- Read-only. The app never posts, comments, votes, or sends messages.
- Public data only: subreddit about pages and /new listings, plus comments
  on a small number of recent posts.
- Fixed scope: the 40 subreddits listed below.
- Volume: one daily collection run, roughly 360-470 requests/day total,
  throttled to ~1 request per 1.5 seconds — far inside free-tier limits.
- App type: a "script" app using the app-only client_credentials grant,
  owned by this account.

POLICY COMPLIANCE, EXPLICITLY
- No AI/ML training on Reddit data, and no selling, licensing, or
  redistribution of data. Only aggregate trend charts are published.
- No user-level analysis of any kind: no profiles, no tracking of
  individual accounts, no inferring characteristics about any user. Every
  published number is a community-level aggregate.
- No deanonymization, re-identification, or matching with off-platform data.
- Descriptive User-Agent on every request (ai-companion-tracker/1.0).
- Rate limits respected, with exponential backoff on 429s.

HISTORY
The tracker collected this same data via the public .json endpoints from
2025 until their retirement on 2026-05-30, always with a descriptive
User-Agent and conservative throttling (1 request per 6 seconds).

Reddit account: u/<REDDIT_USERNAME>
Site: https://myfriendisai.com

Subreddits (40): r/ChatGPT, r/OpenAI, r/singularity, r/ClaudeAI,
r/claudexplorers, r/replika, r/CharacterAI, r/MyBoyfriendIsAI,
r/ChatGPTcomplaints, r/AIRelationships, r/MySentientAI,
r/BeyondThePromptAI, r/MyGirlfriendIsAI, r/AICompanions, r/SoulmateAI,
r/aipartners, r/ReplikaLovers, r/ILoveMyReplika, r/MyBoyfriendIsAI_Open,
r/KindroidAI, r/NomiAI, r/NectarAI, r/SpicyChatAI, r/ChaiApp, r/Paradot,
r/AIGirlfriend, r/ChatGPTNSFW, r/Character_AI_Recovery,
r/ChatbotAddiction, r/AI_Addiction, r/CharacterAIrunaways, r/antiAI,
r/FuckAI, r/ArtistHate, r/AIDangers, r/BetterOffline, r/trueantiAI,
r/aiwars, r/DefendingAIArt, r/ProAI

Happy to answer questions or adjust scope. Thank you for considering.
```

5. After submitting, record the date + ticket number at the top of this file
   (edit the **Status** line).

## Part 2 — While waiting

- **Nothing needs babysitting.** The daily pipeline keeps running on the Arctic
  Shift fallback, and a GitHub Action already emails Walker if the site goes stale.
- **Watch `walkerbockley@gmail.com`** (and Reddit DMs/modmail on the account) for a
  reply. Zendesk replies sometimes land in spam — check there too.
- If Reddit asks follow-up questions, answer honestly from the ticket text above;
  if a question isn't covered there, ask Walker before answering.
- If Reddit asks the app to **register a developer profile / app profile** at
  https://developers.reddit.com/app-registration, do it — same account, same app
  name (`ai-companion-tracker`), same description as the ticket.
- No reply after **4 weeks**: reply once inside the same ticket asking for status.
  Don't file a second ticket (the policy explicitly prohibits duplicate requests).

## Part 3 — If approved

Reddit will either say app creation is unlocked for the account, or provide
specific instructions. Unless their instructions say otherwise:

1. Follow **`docs/oauth_setup_guide.md` from Step 2** (create the script app at
   reddit.com/prefs/apps) **through Step 7** (verify + report back). That guide is
   self-contained and copy-paste: create app → put the two credentials in
   `~/.config/myfriendisai-reddit.env` → run three verification commands.
2. The next 6am collection run picks the credentials up automatically — nothing
   to restart, nothing to deploy.
3. The day after, confirm OAuth mode is live:
   ```bash
   grep "Reddit client:" /Users/walker/Projects/myfriendisai/logs/collect_daily.log
   ```
   Expect a line saying `OAuth mode`. Tell Walker it's done.

## Part 4 — If rejected (or conditions we can't meet)

Do **not** improvise workarounds. The site is fine on the fallback indefinitely.

1. Save Reddit's full reply (forward the email to Walker).
2. Update the **Status** line at the top of this file with the outcome + date.
3. Tell Walker — deciding any next move (appeal, scope change, staying on the
   fallback permanently) is his call.

## Context links

- Incident background: `docs/reddit_json_shutdown_2026-06-09.md`
- The original credential-setup guide (used in Part 3): `docs/oauth_setup_guide.md`
- Responsible Builder Policy: https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy
- Reddit for Researchers (why we DON'T use it — academic-only, incompatible
  data-retention rules): https://support.reddithelp.com/hc/articles/49381918834964-Reddit-for-Researchers-Program
