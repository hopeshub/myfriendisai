// ── Shared style constants ───────────────────────────────────────────────────
// One home for the type scale and the style objects that were previously
// re-defined (with slight drift) across page.tsx, about/page.tsx, and
// theme/[id]/page.tsx. Import from here instead of redefining locally.
//
// The styling mechanism stays as plain inline style objects — this module only
// unifies the values, it is not an inline-style → Tailwind migration.

import type { CSSProperties } from "react";

// ── Site theme: the one switch ───────────────────────────────────────────────
// Every neutral and accent colour on the site is a role in one of these two
// palettes. Components read roles from `C` (inline styles, SVG attributes) or
// from the matching CSS variables `--c-<role>` (Tailwind classes, globals.css),
// which layout.tsx writes onto <html> from the same object. Categorical
// colours (community bands) stay literal in their components; theme colours
// live in themes.ts and follow this switch too.
//
//   "dark"  — the original slate site (Inter + Newsreader).
//   "paper" — design step 3c, chart-recorder paper: a near-white sheet, navy
//             ink, salmon grid, red ink for platform events; IBM Plex Sans
//             Condensed for headings and labels, Literata for prose.
//
// Revert to the dark site by changing this one line.
export type SiteTheme = "dark" | "paper";
export const SITE_THEME = "dark" as SiteTheme;

export type Palette = {
  bg: string; surface: string; surface2: string;
  border: string; borderSoft: string; borderStrong: string; grid: string;
  cursor: string; neutralSeries: string; otherBand: string;
  title: string; heading: string; body: string; body2: string;
  lead: string; leadAlt: string; muted2: string; eyebrow: string; caption: string;
  event: string; eventText: string; onEvent: string; highlight: string;
  communityLine: string; metricA: string; metricB: string;
  alertBg: string; alertText: string;
  bandLabel: string; bandHalo: string;
};

const DARK: Palette = {
  bg: "#0F1117", surface: "#15171E", surface2: "#1A1D27",
  border: "#2A2D3A", borderSoft: "#1E293B", borderStrong: "#334155", grid: "#2A2D3A",
  cursor: "#475569", neutralSeries: "#566173", otherBand: "#525A6B",
  title: "#F8FAFC", heading: "#F1F4F8", body: "#C8D0DC", body2: "#CBD5E1",
  lead: "#9AA7B8", leadAlt: "#94A3B8", muted2: "#8A93A3", eyebrow: "#8293A6", caption: "#7E8B9E",
  event: "#C2974D", eventText: "#D4A862", onEvent: "#0F1117", highlight: "#F59E0B",
  communityLine: "#7C9CD0", metricA: "#e8692a", metricB: "#8b5cf6",
  alertBg: "#7f1d1d", alertText: "#fef2f2",
  bandLabel: "#F8FAFC", bandHalo: "#0F1117",
};

// Chart-recorder paper. Ink is navy-black (#1F2433), never pure black; the
// grid is the salmon of strip-chart paper; red ink is reserved for platform
// events and warnings. Every text role clears WCAG AA (4.5:1) on the sheet.
const PAPER: Palette = {
  bg: "#FCFBF8", surface: "#F7F5F0", surface2: "#F1EEE7",
  border: "#DCD7CD", borderSoft: "#E7E3DA", borderStrong: "#C8C1B4", grid: "#EDBFB8",
  cursor: "#9A9184", neutralSeries: "#8E8A86", otherBand: "#B7B1A6",
  title: "#1F2433", heading: "#1F2433", body: "#2E3342", body2: "#2E3342",
  lead: "#454B59", leadAlt: "#454B59", muted2: "#575D6B", eyebrow: "#575D6B", caption: "#5C6270",
  event: "#A8261F", eventText: "#A8261F", onEvent: "#FCFBF8", highlight: "#A8261F",
  communityLine: "#1F2433", metricA: "#1F2433", metricB: "#1F2433",
  alertBg: "#A8261F", alertText: "#FCFBF8",
  bandLabel: "#1F2433", bandHalo: "#FCFBF8",
};

/** The active palette. */
export const C: Palette = SITE_THEME === "paper" ? PAPER : DARK;

/** CSS custom properties for every role (`--c-bg`, `--c-lead`, …), written
 *  onto <html> by layout.tsx so Tailwind classes and globals.css can use them. */
export const paletteCssVars: Record<string, string> = Object.fromEntries(
  Object.entries(C).map(([k, v]) => [`--c-${k}`, v]),
);

/**
 * Named modular type scale. Every ad-hoc / half-pixel font size in the app
 * snaps to one of these steps.
 *
 *   micro  11 — dense chart axis ticks and micro-labels ONLY
 *   xs     12 — captions, eyebrows, fine print
 *   sm     13 — secondary body, dense notes
 *   base   14 — default body text, UI controls
 *   md     16 — intro / lead paragraphs
 *   lg     18 — card titles, small headings
 *   xl     21 — stat figures
 *   xxl    26 — section / page headings
 *   xxxl   32 — page titles
 */
export const fontSize = {
  micro: 11,
  xs: 12,
  sm: 13,
  base: 14,
  md: 16,
  lg: 18,
  xl: 21,
  xxl: 26,
  xxxl: 32,
} as const;

// ── Canonical text-color set ─────────────────────────────────────────────────
// The one role-based text-color ladder for the site: brighter = more important.
// Use these roles instead of picking a near-grey by component habit.
export const textColor = {
  title: C.title,
  heading: C.heading,
  body: C.body,
  lead: C.lead,
  caption: C.caption,
  eyebrow: C.eyebrow,
} as const;

// ── Shared style objects ─────────────────────────────────────────────────────

/** The reading measure — max line length (px) for all running text. */
export const measure = 680;

/** Small sentence-case label for a block that has no heading of its own
 *  (the theme list in the masthead, "The keywords" on a theme page). Not for
 *  use above a heading: a label that only restates the heading is dropped.
 *  Size comes from the `--eyebrow-size` CSS variable (globals.css): fontSize.xs
 *  (12px) on desktop, 14px at ≤768px to hold the mobile font floor. */
export const sectionEyebrow: CSSProperties = {
  fontSize: `var(--eyebrow-size, ${fontSize.xs}px)`,
  fontWeight: 500,
  color: C.eyebrow,
  marginBottom: 8,
};

/** Section / sub-section heading, sentence case (About page sections). */
export const sectionHeading: CSSProperties = {
  fontSize: fontSize.base,
  fontWeight: 500,
  color: C.eyebrow,
  marginBottom: 16,
};

/** Small square colour key for a theme, shown beside a theme name that is not
 *  itself set in the theme's colour. (Replaced the per-theme emoji icons.) */
export function themeKey(color: string): CSSProperties {
  // On paper every theme is drawn in the same navy ink and told apart by its
  // name, so a colour key would only be a bullet: hide it.
  if (SITE_THEME === "paper") return { display: "none" };
  return {
    display: "inline-block",
    width: 8,
    height: 8,
    backgroundColor: color,
    flexShrink: 0,
  };
}

/** Intro / lead paragraph — the larger paragraph that opens a section. */
export const introParagraph: CSSProperties = {
  fontSize: fontSize.md,
  lineHeight: 1.7,
  color: C.lead,
  maxWidth: measure,
};

/** Standard body paragraph. */
export const bodyParagraph: CSSProperties = {
  fontSize: fontSize.base,
  lineHeight: 1.8,
  color: C.body,
  maxWidth: measure,
};
