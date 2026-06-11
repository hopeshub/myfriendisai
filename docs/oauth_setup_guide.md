# Guide: Register the Reddit OAuth app and activate authenticated collection

> **⚠️ BLOCKED as of 2026-06-11 — approval required first.** Reddit retired
> self-serve app creation (~March 2026): `prefs/apps` now redirects everyone to the
> [Responsible Builder Policy](https://support.reddithelp.com/hc/en-us/articles/42728983564564-Responsible-Builder-Policy),
> which requires requesting access and getting explicit approval before any API use.
> **Start with `docs/reddit_api_access_request_guide.md`** (it contains the
> ready-to-paste ticket text and the full hand-off procedure); come back to Step 2
> of this guide only once Reddit approves. The Step 3 table below predates this
> discovery — the policy redirect is the gate itself, not a flaky form.

**Goal:** restore full daily collection for the myfriendisai tracker. Reddit killed
unauthenticated `.json` access on 2026-05-30; the collector already has OAuth
support built in and auto-activates the moment a credentials file is filled in.
This task is: register a Reddit "script" app (~2 min in a browser), put the two
resulting values into one local file, and verify.

**Machine:** Walker's collection Mac, project at `/Users/walker/Projects/myfriendisai`.
**Time:** ~5 minutes if Reddit's form behaves, up to ~15 if it's flaky (see Step 3).

---

## Step 1 — Sign in to Reddit

Open a browser and sign in to Walker's Reddit account at https://www.reddit.com.
Any normal account works (app-only auth; the account is just the app's owner).
If Walker has multiple accounts, use the one he considers his main/durable one —
the app dies if the account does.

## Step 2 — Create the app

1. Go to **https://www.reddit.com/prefs/apps**
   (if that page misbehaves, try **https://old.reddit.com/prefs/apps** — the old
   interface often works when the new one doesn't).
2. Scroll to the bottom → click **"create app"** or **"create another app"**.
3. Fill the form EXACTLY like this:
   - **name:** `ai-companion-tracker`
   - **type:** select **`script`** ← this radio button matters; "script" apps
     are the personal-use type that allows the client_credentials grant
   - **description:** `Daily data collection for myfriendisai.com, a public
     research tracker of AI-companion community discourse` (optional but fill it)
   - **about url:** `https://myfriendisai.com/about` (optional)
   - **redirect uri:** `http://localhost:8080` ← REQUIRED even though we never
     use it; the form silently fails without it
4. Complete any CAPTCHA → click **"create app"**.

## Step 3 — If the form is broken (known issue since the May 2026 API change)

Reported failure modes and workarounds, in order of what to try:

| Symptom | Workaround |
|---|---|
| Page redirects to a policy/announcement page | Use https://old.reddit.com/prefs/apps instead |
| CAPTCHA loops forever | Different browser (Safari if Chrome, vice versa); disable extensions; try a private window (but sign in first) |
| "create app" silently does nothing | Make sure **redirect uri** is filled (`http://localhost:8080`) — it's the hidden required field; also make sure a type radio button is actually selected |
| Form says developer account / verification required | Follow the verification flow (email confirm); retry after |
| Everything fails repeatedly | STOP and report back — don't create accounts or use third-party workarounds. The fallback collection keeps the site alive meanwhile |

## Step 4 — Copy the two credentials

After creation the app appears as a box on the same page:

- **Client ID** = the short string of characters directly **under the app name**,
  next to the icon (labeled "personal use script"). ~14-22 characters.
- **Client secret** = the field explicitly labeled **"secret"**. Click "edit" on
  the app if the secret isn't visible.

Keep this tab open for Step 5. Do NOT paste these values into any chat, commit,
email, or cloud note. They go into exactly one local file.

## Step 5 — Fill in the credentials file

The template already exists at `~/.config/myfriendisai-reddit.env` (chmod 600).
Edit it so the last two lines read (no quotes needed, no spaces around `=`):

```
REDDIT_CLIENT_ID=<paste client id here>
REDDIT_CLIENT_SECRET=<paste secret here>
```

Leave the comment lines alone or delete them — both fine. Then confirm
permissions are still owner-only:

```bash
chmod 600 ~/.config/myfriendisai-reddit.env
ls -l ~/.config/myfriendisai-reddit.env   # should show -rw-------
```

This file is outside the git repo; nothing here can be committed.

## Step 6 — Verify (three checks, ~1 minute)

Run from `/Users/walker/Projects/myfriendisai`:

**6a. The collector sees the creds and switches modes:**
```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from src.reddit_client import RedditClient
c = RedditClient()
print('authenticated:', c.is_authenticated)   # expect: True
print('base_url:', c.base_url)                # expect: https://oauth.reddit.com
"
```

**6b. The token grant actually works (reads creds from the file, never types the secret):**
```bash
set -a; source ~/.config/myfriendisai-reddit.env; set +a
curl -sS -u "$REDDIT_CLIENT_ID:$REDDIT_CLIENT_SECRET" \
  -d grant_type=client_credentials \
  -A 'ai-companion-tracker/1.0 (research project)' \
  https://www.reddit.com/api/v1/access_token
```
Expect JSON containing `"access_token": "..."` and `"expires_in"`. If you get
`{"error": 401}` the ID or secret was mis-pasted (most common: copying the app
NAME instead of the string under it, or trailing whitespace).

**6c. An authenticated end-to-end fetch through the project's own client:**
```bash
.venv/bin/python -c "
import sys; sys.path.insert(0, '.')
from src.reddit_client import RedditClient
c = RedditClient()
about = c.get_about('CharacterAI')
print('subscribers:', about.get('subscribers'))   # expect a number in the millions
"
```

If all three pass, the job is done. **Do not run the full daily collection
manually** — the 6am launchd job picks the credentials up automatically with
zero further changes, and its log will open with
`Reddit client: OAuth mode (creds from ...)`.

## Step 7 — Report back

Tell Walker (or note in the session):
1. Which checks passed (6a/6b/6c)
2. Any form weirdness hit in Step 3 (useful if this ever needs doing again)
3. Reminder for the day after: confirm the 6am run logged OAuth mode and that
   subreddit snapshots resumed — quick check:
   `grep "Reddit client:" /Users/walker/Projects/myfriendisai/logs/collect_daily.log`

## Context if something unexpected comes up

- Full incident background: `docs/reddit_json_shutdown_2026-06-09.md`
- The OAuth implementation: `src/reddit_client.py` (reads the env file at
  client construction; app-only client_credentials grant; auto-refreshes tokens)
- If OAuth can't be made to work at all, nothing breaks: the daily pipeline
  falls back to Arctic Shift automatically (theme trends stay current; only
  subscriber snapshots + comments stay paused). There is no urgency that
  justifies risky workarounds.
