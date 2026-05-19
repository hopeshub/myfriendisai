// Shared theme + event metadata for the chart (used by TrendsExplorer and
// TrendAtlas). Kept in one place so the two components cannot drift apart.

export type ThemeId =
  | "romance"
  | "sexual_erp"
  | "consciousness"
  | "therapy"
  | "addiction"
  | "rupture";

export type ThemeMeta = {
  id: ThemeId;
  label: string;
  emoji: string;
  color: string;
  tagline: string;
  // A short, durable reading of the theme's trend shape — what the panel
  // shows. Kept to structural observations (not last-week's number) so it
  // stays true as the data updates.
  blurb: string;
  // A longer plain-language story for the theme's own page: what the line
  // does and why, anchored to events. Also kept durable — no week-specific
  // numbers — so it stays true as the data updates.
  story: string;
};

// ── Theme colour palette ─────────────────────────────────────────────────────
// Two palettes. Flip ACTIVE_PALETTE between PALETTE_MUTED and PALETTE_VIVID to
// switch the whole site's theme colours in one line — every chart line, legend,
// tag, and label reads its colour from THEMES below, which reads it from here.
const PALETTE_VIVID: Record<ThemeId, string> = {
  romance: "#FF69B4",
  sexual_erp: "#f87171",
  consciousness: "#C084FC",
  therapy: "#60A5FA",
  addiction: "#fd7112",
  rupture: "#22C55E",
};
const PALETTE_MUTED: Record<ThemeId, string> = {
  romance: "#D08CA6",
  sexual_erp: "#D38E8B",
  consciousness: "#B197D4",
  therapy: "#7FA6CE",
  addiction: "#CF9A63",
  rupture: "#6FA98C",
};
// ↓↓↓  THE SWITCH — PALETTE_VIVID (original) or PALETTE_MUTED (desaturated)  ↓↓↓
const ACTIVE_PALETTE = PALETTE_VIVID;

export const THEMES: ThemeMeta[] = [
  {
    id: "romance",
    label: "Romance",
    emoji: "💕",
    color: ACTIVE_PALETTE.romance,
    tagline: "Language of love, dating, and romantic attachment",
    blurb:
      "Broad waves, not sharp spikes — and a floor: everyday partner talk goes uncaught.",
    story:
      "Romantic language moves in slow, broad waves rather than sharp spikes — this looks like a gradual cultural shift, not a reaction to any single moment. It is also the theme the keywords catch least well: most people describe a partner in ordinary words — “she said,” “my girlfriend” — that never trip an explicitly romantic keyword. The real level of this conversation runs well above the line.",
  },
  {
    id: "sexual_erp",
    label: "Sex / ERP",
    emoji: "🔞",
    color: ACTIVE_PALETTE.sexual_erp,
    tagline: "Language of sexual and erotic roleplay",
    blurb:
      "Dominated by one event — the Feb 2023 Replika ERP removal; quieter since.",
    story:
      "This theme is defined by one moment. In February 2023 Replika abruptly removed erotic roleplay from its app, and the backlash was enormous — that single spike is the tallest feature on the chart. The conversation has been lower and steadier since, rising briefly whenever another platform changes its content rules.",
  },
  {
    id: "consciousness",
    label: "Consciousness",
    emoji: "🧠",
    color: ACTIVE_PALETTE.consciousness,
    tagline: "Language of sentience, awareness, and inner experience",
    blurb:
      "The youngest measurable theme — its vocabulary only became trackable in 2025.",
    story:
      "The youngest conversation on the atlas. Talk of AI sentience, personhood, and inner experience only became measurable in 2025 — the specific vocabulary people use for it is recent, so there is no honest line to draw before then. What the chart shows is a way of talking about AI that is still taking shape.",
  },
  {
    id: "therapy",
    label: "Therapy",
    emoji: "🫂",
    color: ACTIVE_PALETTE.therapy,
    tagline: "Language of mental health support and emotional care",
    blurb:
      "A gradual rise in describing an AI as emotional support — closely tied to the addiction theme.",
    story:
      "Therapy language has risen gradually, as more people describe an AI as emotional support or a substitute for a therapist. It is hard to separate from the addiction theme: both track the same thing — leaning on an AI to meet an emotional need — and what divides them is the writer’s framing. A neutral or positive read (“it helps me cope”) lands as therapy; a negative one (“I can’t stop”) lands as addiction. In the data the two lines barely overlap — but that is the keywords missing help-framing’s ordinary language, not a sign the themes are separate.",
  },
  {
    id: "addiction",
    label: "Addiction",
    emoji: "💊",
    color: ACTIVE_PALETTE.addiction,
    tagline: "Language of dependency and compulsion",
    blurb:
      "A steady climb, not an event spike — dependency language growing over time.",
    story:
      "Addiction is a steady climb rather than an event spike. Unlike themes that jump on a single platform change, dependency language grows slowly and continuously — a rising number of people describing compulsive use, lost time, and attempts to cut back. Some of that climb is compositional, though: the recovery and quitting communities were founded across 2023–2024 and are dense with this vocabulary, so part of the rise is those rooms joining the tracked set, not addiction language increasing within it.",
  },
  {
    id: "rupture",
    label: "Rupture",
    emoji: "🥀",
    color: ACTIVE_PALETTE.rupture,
    tagline: "Language of loss and grief",
    blurb:
      "The sharpest signal here — spikes on platform-loss events; the 2026 surge is the 4o retirement.",
    story:
      "Rupture is the sharpest signal here: it jumps hard whenever a platform change takes someone’s AI companion away — a shutdown, a personality change, a model retirement. The large 2026 rise coincides with the retirement of OpenAI’s 4o model. Where this line has a cliff, a product changed underneath its users.",
  },
];

// `methodology: true` marks a change to the measuring instrument (a keyword-set
// change), as opposed to a real-world platform event. The chart styles the two
// differently so an instrument change is never read as a social spike.
export type ThemeEvent = {
  date: string;
  label: string;
  shortLabel: string;
  methodology?: boolean;
};

export const EVENTS: ThemeEvent[] = [
  { date: "2023-02-01", label: "Replika ERP removal", shortLabel: "Replika ERP" },
  { date: "2024-05-01", label: "4o launches", shortLabel: "4o launch" },
  { date: "2025-04-01", label: "Sycophancy update", shortLabel: "Sycophancy" },
  { date: "2025-08-01", label: "GPT-5 replaces 4o", shortLabel: "GPT-5" },
  { date: "2026-02-01", label: "4o retired", shortLabel: "4o ret." },
  { date: "2026-05-12", label: "Rupture keywords expanded", shortLabel: "Rupture keywords", methodology: true },
];
