// Changelog: a curated list of changes that affect how the chart should be
// read — not the full development history (that's the Git log). Shared by the
// About page (the full list) and the homepage (a most-recent teaser).

export type ChangelogEntry = {
  date: string;
  title: string;
  items: string[];
  recent: boolean;
};

export const CHANGELOG: ChangelogEntry[] = [
  {
    date: "September 2026",
    title: "Collection gaps repaired; copy corrected",
    items: [
      "REPAIR_NOTE_CHANGELOG",
      "A pass over every number in the site's prose against the current data: a few stale figures were corrected (the r/CharacterAI share of the corpus, r/antiAI's rise, the size of the database), the About page now says plainly that the charted lines count post text only, and the methodology document was brought into line with what the pipeline actually does — including that communities added in May 2026 were backfilled, not added forward-only.",
    ],
    recent: true,
  },
  {
    date: "June 2026",
    title: "Collection moved from Reddit to the archive",
    items: [
      "Reddit ended unauthenticated data access without notice on May 30, 2026. Daily collection paused from May 29 to June 9; the missing days were recovered from the Arctic Shift archive, and collection has run from the archive ever since. The charted lines count post text only and are unaffected, but two secondary figures froze: subscriber counts and average post score have no archive equivalent and stay at their late-May values, labeled as such on the community pages.",
    ],
    recent: true,
  },
  {
    date: "August 2026",
    title: "The dataset behind the charts is now downloadable",
    items: [
      "The aggregate numbers behind every chart — monthly counts and rates per theme, and monthly post volume per community — are now published as plain CSV and JSON at /dataset/v1/, alongside a standalone methodology document and a schema. It is derived numbers only: no post text, no usernames. It regenerates with the daily pipeline, and it is built to stay readable on its own even if the site itself ever stops. Licensed CC BY 4.0.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "How to read the therapy and addiction lines",
    items: [
      "A hand-check of 90 posts the keywords had filed as addiction tested how cleanly the two lines separate help from harm. About a quarter of them also carried a help framing the keywords had missed — help language hides in ordinary words (“it got me through”), while problem language announces itself (“relapse,” “days clean”). So the therapy and addiction lines can't be read against each other as a balance: the instrument hears the problem framing far more clearly than the help one. The homepage and About page were corrected to say this plainly.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Five communities added",
    items: [
      "Five more AI-companionship communities joined the tracked set — r/aipartners, r/ReplikaLovers, r/ILoveMyReplika, r/MyBoyfriendIsAI_Open and r/NectarAI. They were picked from a wider candidate list by reading post samples and keeping only those genuinely centered on companionship discourse rather than tech support or platform-migration chatter. Their history was backfilled from the archive and keyword-tagged in the same pass, so no line has a seam at this date. They are romance-heavy and have grown since: by mid-2026 they supply about one post in eleven, and part of the 2026 romance rise is their joining the set.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Three communities removed from the theme charts",
    items: [
      "r/AIGirlfriend, r/ChatGPTNSFW and r/SpicyChatAI were dropped from the keyword theme lines. Two are mostly noise — affiliate-spam image posts (r/AIGirlfriend) and bot-card listings (r/SpicyChatAI). r/ChatGPTNSFW is a real erotica-writing and jailbreak community, but not a companionship one, so it sits outside what the themes measure. All three remain in the community explorer as context. The sex/ERP line steps down from this point — most visibly across 2024–2025 — because r/ChatGPTNSFW had been a large share of it.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Theme accuracy re-checked",
    items: [
      "Re-checked that keywords land on the theme they claim — about 1,800 tagged posts re-read by a separate automated check, then a sample re-coded by hand. Keywords reliably identify AI-companion discourse; sorting it into the right theme is tightest for sex/ERP and addiction, and holds up better for therapy and consciousness than that first automated pass suggested. The re-check also confirmed that therapy and addiction are largely one subject — the same reliance on an AI, framed once as help and once as a problem. No keywords changed: the response to a fast-moving vocabulary is disclosure, not constant edits.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "Post corpus extended back to 2017",
    items: [
      "The post corpus was backfilled from public archives back to 2017. In practice this moved the earliest theme lines from a 2023 start back a few months, into late 2022 — as far back as monthly volume stays reliable enough to chart. The 2017–2021 years exist in the corpus but are too sparse to draw as theme lines, so the early-Replika era is not itself visible on the chart.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Rupture vocabulary expanded",
    items: [
      "Added grief-and-farewell language; the earlier keywords caught only metaphors like “lobotomized.” The whole rupture line was re-counted with the wider net, so it sits higher across its full length — the change is in the instrument, not in the discourse. The hollow marker on the chart dates the change.",
    ],
    recent: false,
  },
  {
    date: "April 2026",
    title: "Keyword set revalidated",
    items: [
      "Every high-volume keyword was re-checked against recent posts. Six were dropped — notably “sentient,” which had drifted into meme and roleplay use. The consciousness line was re-counted without them across its whole length, so it runs thinner throughout, not only after this date.",
    ],
    recent: false,
  },
  {
    date: "April 2026",
    title: "Keyword-matching bug fixed",
    items: [
      "Multi-word keywords had been matching inside unrelated words (“dating my” caught inside “updating my”). Fixing it removed those false positives, slightly lowering the romance, therapy, and sex/ERP lines.",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Per-theme start dates",
    items: [
      "Each theme's line now begins only once its vocabulary was common enough to measure reliably. The consciousness line starts in 2025 rather than 2023 for this reason — a flat earlier line would imply absence where I simply couldn't measure it yet.",
    ],
    recent: false,
  },
  {
    date: "March 2026",
    title: "Daily collection began",
    items: [
      "The project moved from a one-time historical backfill to collecting posts fresh from Reddit every day. Comments were collected and keyword-tagged from this point on as well, but the published chart counts post text only — so this change adds no volume to any line.",
    ],
    recent: false,
  },
];
