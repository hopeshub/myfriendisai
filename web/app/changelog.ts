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
    recent: true,
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
      "The project moved from a one-time historical backfill to collecting posts fresh from Reddit every day. Comments were collected and keyword-tagged from this point on as well, but the published chart counts post text only — so this change adds no volume to any line.",
    ],
    recent: false,
  },
];
