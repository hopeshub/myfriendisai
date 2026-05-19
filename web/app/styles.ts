// ── Shared style constants ───────────────────────────────────────────────────
// One home for the type scale and the style objects that were previously
// re-defined (with slight drift) across page.tsx, about/page.tsx, and
// theme/[id]/page.tsx. Import from here instead of redefining locally.
//
// The styling mechanism stays as plain inline style objects — this module only
// unifies the values, it is not an inline-style → Tailwind migration.

import type { CSSProperties } from "react";

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
  title: "#F8FAFC",
  heading: "#F1F4F8",
  body: "#C8D0DC",
  lead: "#9AA7B8",
  caption: "#7E8B9E",
  eyebrow: "#8293A6",
} as const;

// ── Shared style objects ─────────────────────────────────────────────────────

/** The reading measure — max line length (px) for all running text. */
export const measure = 680;

/** Small uppercase "eyebrow" label that sits above a section heading. */
export const sectionEyebrow: CSSProperties = {
  fontSize: fontSize.xs,
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "#8293A6",
  marginBottom: 8,
};

/** Section / sub-section heading (the line under the eyebrow). */
export const sectionHeading: CSSProperties = {
  fontSize: fontSize.base,
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "#8293A6",
  marginBottom: 16,
};

/** Intro / lead paragraph — the larger paragraph that opens a section. */
export const introParagraph: CSSProperties = {
  fontSize: fontSize.md,
  lineHeight: 1.7,
  color: "#9AA7B8",
  maxWidth: measure,
};

/** Standard body paragraph. */
export const bodyParagraph: CSSProperties = {
  fontSize: fontSize.base,
  lineHeight: 1.8,
  color: "#C8D0DC",
  maxWidth: measure,
};
