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
};

// Colors tuned so value text passes WCAG AA on the card backgrounds.
export const THEMES: ThemeMeta[] = [
  { id: "romance",       label: "Romance",       emoji: "💕", color: "#FF69B4", detector: "narrow",   tagline: "Language of love, dating, and romantic attachment" },
  { id: "sexual_erp",    label: "Sex / ERP",     emoji: "🔞", color: "#f87171", detector: "moderate", tagline: "Language of sexual and erotic roleplay" },
  { id: "consciousness", label: "Consciousness", emoji: "🧠", color: "#C084FC", detector: "narrow",   tagline: "Language of sentience, awareness, and inner experience" },
  { id: "therapy",       label: "Therapy",       emoji: "🫂", color: "#60A5FA", detector: "moderate", tagline: "Language of mental health support and emotional care" },
  { id: "addiction",     label: "Addiction",     emoji: "💊", color: "#fd7112", detector: "broad",    tagline: "Language of dependency and compulsion" },
  { id: "rupture",       label: "Rupture",       emoji: "🥀", color: "#22C55E", detector: "narrow",   tagline: "Language of loss and grief" },
];

export const DETECTOR_LABEL: Record<Detector, string> = {
  narrow: "narrow detector",
  moderate: "moderate detector",
  broad: "broad detector",
};

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
