// Shared theme + event metadata for the chart (used by TrendsExplorer and
// TrendAtlas). Kept in one place so the two components cannot drift apart.

export type ThemeId =
  | "romance"
  | "sexual_erp"
  | "consciousness"
  | "therapy"
  | "addiction"
  | "rupture";

// `detector` is a coarse description of how much theme-relevant discourse the
// keyword set actually catches — from the comprehensiveness audit's recall
// estimate: narrow < ~10%, moderate ~10-25%, broad > ~25%. It is intentionally
// coarse; the recall figures have wide confidence intervals. It tells a reader
// not to compare line heights between a "narrow" and a "broad" theme.
export type Detector = "narrow" | "moderate" | "broad";

export type ThemeMeta = {
  id: ThemeId;
  label: string;
  emoji: string;
  color: string;
  tagline: string;
  detector: Detector;
  // A short, durable reading of the theme's trend shape — what the panel
  // shows. Kept to structural observations (not last-week's number) so it
  // stays true as the data updates.
  blurb: string;
  // A longer plain-language story for the theme's own page: what the line
  // does and why, anchored to events. Also kept durable — no week-specific
  // numbers — so it stays true as the data updates.
  story: string;
};

export const THEMES: ThemeMeta[] = [
  {
    id: "romance",
    label: "Romance",
    emoji: "💕",
    color: "#FF69B4",
    detector: "narrow",
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
    color: "#f87171",
    detector: "moderate",
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
    color: "#C084FC",
    detector: "narrow",
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
    color: "#60A5FA",
    detector: "moderate",
    tagline: "Language of mental health support and emotional care",
    blurb:
      "Gradually rising — and the noisiest theme, catching complaint alongside genuine use.",
    story:
      "Therapy language has risen gradually, as more people describe an AI as emotional support or a substitute for a therapist. It is the noisiest theme to measure: the same phrases that mark genuine therapeutic use also catch people arguing about it — “it’s not a real therapist” — so trust the overall direction more than the exact height.",
  },
  {
    id: "addiction",
    label: "Addiction",
    emoji: "💊",
    color: "#fd7112",
    detector: "broad",
    tagline: "Language of dependency and compulsion",
    blurb:
      "A steady climb, not an event spike — dependency language growing over time.",
    story:
      "Addiction is a steady climb rather than an event spike. Unlike themes that jump on a single platform change, dependency language grows slowly and continuously — a rising number of people describing compulsive use, lost time, and attempts to cut back.",
  },
  {
    id: "rupture",
    label: "Rupture",
    emoji: "🥀",
    color: "#22C55E",
    detector: "narrow",
    tagline: "Language of loss and grief",
    blurb:
      "The sharpest signal here — spikes on platform-loss events; the 2026 surge is the 4o retirement.",
    story:
      "Rupture is the sharpest signal here: it jumps hard whenever a platform change takes someone’s AI companion away — a shutdown, a personality change, a model retirement. The large 2026 rise follows the retirement of OpenAI’s 4o model, which many people had grown attached to. Where this line has a cliff, a product changed underneath its users.",
  },
];

export const DETECTOR_LABEL: Record<Detector, string> = {
  narrow: "coverage: narrow",
  moderate: "coverage: moderate",
  broad: "coverage: broad",
};

// Explanation shown in the hover popover on the detector chip.
export const DETECTOR_EXPLAINER =
  "How much of this theme’s real discussion the keywords catch — narrow, moderate, or broad. A narrower detector means the line undercounts more, so line heights aren’t comparable between themes.";

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
  { date: "2025-04-01", label: "Sycophancy update", shortLabel: "Syco. update" },
  { date: "2025-08-01", label: "4o 1st sunset", shortLabel: "4o sunset" },
  { date: "2026-02-01", label: "4o retired", shortLabel: "4o ret." },
  { date: "2026-05-12", label: "Rupture keywords expanded", shortLabel: "Rupture keywords", methodology: true },
];
