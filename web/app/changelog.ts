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
    title: "Smoothing corrected — the theme lines were recomputed",
    items: [
      "Each theme's rate is a 7-day trailing mean of keyword hits divided by a 7-day trailing mean of posts. A review found the two means did not share a window: the hit-count mean skipped days with no hits, so in sparse stretches it reached back weeks or months and inflated the line, while the days after a spike were treated as zero. Both are now computed over the same seven days of the corpus calendar, with a day that has posts but no hits counting as zero. 45 of 244 monthly values changed by more than 10% (the largest by 54%, therapy in February 2024), almost all in 2023–2024; no 2026 month moved more than 8%. The downloadable dataset was regenerated; its plain monthly rates (rate_per_1k) were never affected.",
      "Corrected in the same pass: the therapy precision figure quoted as ~80% belongs to a rebuilt keyword set that never shipped — the set in use measures ~68%, below the project's own 80% gate, and is published with that caveat; the 400-post recall audit was classified by a language model and spot-checked by hand, not hand-coded, and recall runs from 0% (consciousness) to 32%, not 3–32%; and the download links on the dataset page, which had been broken by a redirect, now work.",
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
    date: "June 2026",
    title: "Collection moved to the Arctic Shift archive",
    items: [
      "Reddit ended unauthenticated data access without notice on May 30, 2026, which paused daily collection from May 29 to June 9. Posts and comments for those days were recovered from the Arctic Shift archive, so post volume and theme lines are complete across the gap. Daily collection has run on the archive since; per-day subscriber and active-user figures cannot be collected that way, so subscriber counts are frozen at their last snapshot (late May–early June 2026). The published theme lines count post text only and are unaffected by the change of source.",
    ],
    recent: true,
  },
  {
    date: "May 2026",
    title: "How to read the therapy and addiction lines",
    items: [
      "A hand-check of 90 posts the keywords had filed as addiction tested how cleanly the two lines separate help from harm. About a quarter of them also carried a help framing the keywords had missed — help language hides in ordinary words (\"it got me through\"), while problem language announces itself (\"relapse,\" \"days clean\"). So the therapy and addiction lines can't be read against each other as a balance: the instrument hears the problem framing far more clearly than the help one. The homepage and About page were corrected to say this plainly.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Five communities added",
    items: [
      "Five more AI-companionship communities joined the tracked set — r/aipartners, r/ReplikaLovers, r/ILoveMyReplika, r/MyBoyfriendIsAI_Open and r/NectarAI. They were picked from a wider candidate list by reading post samples and keeping only those genuinely centered on companionship discourse rather than tech support or platform-migration chatter. They are small communities, so they add little to overall post volume; their theme lines begin only once enough of their posts have been collected, so they appear gradually rather than all at once.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Three communities removed from the theme charts",
    items: [
      "r/AIGirlfriend, r/ChatGPTNSFW and r/SpicyChatAI were dropped from the keyword theme lines. Two are mostly noise — affiliate-spam image posts (r/AIGirlfriend) and bot-card listings (r/SpicyChatAI). r/ChatGPTNSFW is a real erotica-writing and jailbreak community, but not a companionship one, so it sits outside what the themes measure. All three remain in the community explorer as context. The sex/ERP line steps down from this point — most visibly across 2024–2025 — because r/ChatGPTNSFW had been a large share of it.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Theme accuracy re-checked",
    items: [
      "Re-checked that keywords land on the theme they claim — about 1,800 tagged posts re-read by a separate automated check, then a sample re-coded by hand. Keywords reliably identify AI-companion discourse; sorting it into the right theme is tightest for sex/ERP and addiction, and holds up better for therapy and consciousness than that first automated pass suggested. The re-check also confirmed that therapy and addiction are largely one subject — the same reliance on an AI, framed once as help and once as a problem. No keywords changed: the response to a fast-moving vocabulary is disclosure, not constant edits.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Post corpus extended back to 2017",
    items: [
      "The post corpus was backfilled from public archives back to 2017. In practice this moved the earliest theme lines from a 2023 start back a few months, into the second half of 2022 — as far back as monthly volume stays reliable enough to chart. The 2017–2021 years exist in the corpus but are too sparse to draw as theme lines, so the early-Replika era is not itself visible on the chart.",
    ],
    recent: false,
  },
  {
    date: "May 2026",
    title: "Rupture vocabulary expanded",
    items: [
      "Added grief-and-farewell language; the earlier keywords caught only metaphors like \"lobotomized.\" The rupture line steps up in mid-May 2026 — that part of the rise reflects the wider net, not a sudden change in the discourse itself.",
    ],
    recent: false,
  },
  {
    date: "April 2026",
    title: "Keyword set revalidated",
    items: [
      "Every high-volume keyword was re-checked against recent posts. Six were dropped — notably \"sentient,\" which had drifted into meme and roleplay use — so the consciousness line is thinner from this point on.",
    ],
    recent: false,
  },
  {
    date: "April 2026",
    title: "Keyword-matching bug fixed",
    items: [
      "Multi-word keywords had been matching inside unrelated words (\"dating my\" caught inside \"updating my\"). Fixing it removed those false positives, slightly lowering the romance, therapy, and sex/ERP lines.",
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
      "The project moved from a one-time historical backfill to collecting posts from Reddit every day (moved to the Arctic Shift archive in June 2026). Comments were collected and keyword-tagged from this point on as well, but the published chart counts post text only — so this change adds no volume to any line.",
    ],
    recent: false,
  },
];
