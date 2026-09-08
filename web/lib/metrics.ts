// ── Metric display rules ─────────────────────────────────────────────────────
// Small pure helpers shared by the communities table and the per-community
// page, so both read the same numbers the same way. No file IO here — these
// run in client components too.

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

type CommentRow = {
  avg_comments_per_post: number | null;
  unique_comment_authors_7d: number | null;
};

/**
 * Was this row's comment average actually measured?
 *
 * The pipeline collects comment threads for the companionship communities
 * only; for the ambient tier and the three NSFW-scope subs it writes a 0
 * rather than a null. A 0 with no comment authors behind it means "not
 * collected", not "nobody replied" — so it must render as no data. A real
 * average, including a real 0 alongside counted comment authors, is kept.
 */
export function hasCommentAverage(row: CommentRow): boolean {
  if (row.avg_comments_per_post == null) return false;
  return row.avg_comments_per_post !== 0 || !!row.unique_comment_authors_7d;
}

/** "2026-05-28" + "2026-06-07" → "May–Jun 2026". One month → "May 2026". */
export function monthRange(from: string | null, to: string | null): string {
  if (!from || !to) return "";
  const label = (d: string) =>
    `${MONTH_NAMES[Number(d.slice(5, 7)) - 1]} ${d.slice(0, 4)}`;
  const a = label(from);
  const b = label(to);
  if (a === b) return a;
  return from.slice(0, 4) === to.slice(0, 4)
    ? `${a.split(" ")[0]}–${b}`
    : `${a}–${b}`;
}

/**
 * A community's monthly post volume before it existed is a run of zeros, which
 * plots as a flat line along the axis and then a cliff at its founding month.
 * Blank those leading months so the line simply starts when the community
 * does. Zeros after the first active month are real quiet months and stay.
 */
export function fromFirstActiveMonth(values: number[]): (number | null)[] {
  const first = values.findIndex((v) => v > 0);
  if (first <= 0) return values;
  return values.map((v, i) => (i < first ? null : v));
}

/** "2026-05" → "May 2026", for a chart caption. */
export function monthLabel(month: string): string {
  return `${MONTH_NAMES[Number(month.slice(5, 7)) - 1]} ${month.slice(0, 4)}`;
}
