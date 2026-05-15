"use client";

import { Fragment, useEffect, useMemo, useRef } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  ReferenceLine,
  Tooltip,
  CartesianGrid,
} from "recharts";
import type { ThemeData } from "./page";
import { THEMES, EVENTS, DETECTOR_LABEL } from "./themes";
import type { ThemeMeta } from "./themes";
import {
  KeywordsSection,
  CommunitiesSection,
  SamplePostsSection,
  pickSamples,
} from "./TransparencyPanel";
import type { CategoryDetail, KeywordDetailsData } from "./TransparencyPanel";

// ── Trend Atlas ──────────────────────────────────────────────────────────────
// One panel per theme, each on its OWN y-axis — detection sensitivity differs
// ~10x between themes, so line heights are not comparable between panels.
// Compare each theme's shape and timing over time; that comparison is honest.
//
// Panels are kept compact so all six tile into roughly one viewport (a true
// "atlas" glance, not a scroll of paragraphs). Events are shared across themes,
// so they're labelled once in a legend; each panel carries a numbered tick.
// THEMES order is fixed and intentional — panels are never sorted by value
// (sorting by value would itself imply the cross-theme ranking we forbid).
//
// Clicking a panel expands a full-width detail row IN PLACE, directly beneath
// that panel's row — the grid stays visible and the clicked panel is never
// covered (unlike a modal or an edge slideout). Mobile uses a bottom sheet.

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";
type Breakpoint = "mobile" | "tablet" | "desktop";
type NumberedEvent = (typeof EVENTS)[number] & { num: number };

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtMonth(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;
}

function fmtMonthShort(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTH_NAMES[dt.getUTCMonth()]} '${String(dt.getUTCFullYear()).slice(2)}`;
}

/** Monthly mean of the daily per-1k rate. */
function monthlySeries(
  points: { date: string; hitsPerK: number }[],
): { date: string; value: number }[] {
  const buckets: Record<string, { sum: number; n: number }> = {};
  for (const p of points) {
    const m = p.date.slice(0, 7) + "-01";
    if (!buckets[m]) buckets[m] = { sum: 0, n: 0 };
    buckets[m].sum += p.hitsPerK;
    buckets[m].n += 1;
  }
  return Object.keys(buckets)
    .sort()
    .map((m) => ({ date: m, value: buckets[m].sum / buckets[m].n }));
}

// ── Event legend ─────────────────────────────────────────────────────────────
// Compact single block above the grid. Event numbers are STABLE — assigned by
// fixed chronological order over the full event set — so a given number always
// means the same event regardless of the selected time range.
function EventLegend({
  events,
  bp,
}: {
  events: NumberedEvent[];
  bp: Breakpoint;
}) {
  const hasMethodology = events.some((e) => e.methodology);
  const fs = bp === "mobile" ? 14 : 12;
  return (
    <div style={{ marginBottom: 16 }}>
      <div
        style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", alignItems: "center" }}
      >
        <span
          style={{
            fontSize: 11,
            color: "#64748B",
            textTransform: "uppercase",
            letterSpacing: "0.05em",
          }}
        >
          Events
        </span>
        {events.map((e) => (
          <span
            key={e.date}
            style={{ display: "inline-flex", alignItems: "center", gap: 6, fontSize: fs }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: 16,
                height: 16,
                borderRadius: 999,
                fontSize: 9.5,
                fontWeight: 700,
                flexShrink: 0,
                color: e.methodology ? "#D4A862" : "#0F1117",
                backgroundColor: e.methodology ? "transparent" : "#C2974D",
                border: e.methodology ? "1px dashed #C2974D" : "none",
              }}
            >
              {e.num}
            </span>
            <span style={{ color: "#CBD5E1" }}>{e.label}</span>
            <span style={{ color: "#64748B" }}>{fmtMonthShort(e.date)}</span>
          </span>
        ))}
      </div>
      {hasMethodology && (
        <div style={{ fontSize: bp === "mobile" ? 14 : 11, color: "#64748B", marginTop: 6 }}>
          A hollow marker is a change to our keyword set — a measurement
          change, not a real-world event.
        </div>
      )}
    </div>
  );
}

// ── Inline detail row ────────────────────────────────────────────────────────
// A full-width region injected into the grid (gridColumn 1 / -1) directly under
// the clicked panel's row. It pushes the rows below it down — nothing is
// overlaid, the grid stays in context, and the clicked panel sits right above
// its own detail. The three sections are laid out as a responsive band so the
// detail reads short and wide rather than as a tall scrolling column.
function ThemeDetailRow({
  theme,
  data,
  onClose,
}: {
  theme: ThemeMeta;
  data: CategoryDetail;
  onClose: () => void;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const samples = pickSamples(data.keywords);

  useEffect(() => {
    // Bring the detail into view — handles a bottom-row panel whose detail
    // would otherwise open below the fold.
    ref.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, []);

  return (
    <div
      ref={ref}
      role="region"
      aria-label={`${theme.label} — theme detail`}
      className="detail-row-in"
      style={{
        gridColumn: "1 / -1",
        backgroundColor: "#1A1D27",
        border: "1px solid #2A2D3A",
        borderTop: `2px solid ${theme.color}`,
        borderRadius: 8,
        padding: "16px 20px 18px",
      }}
    >
      {/* Header — theme identity + close */}
      <div
        className="flex items-start justify-between gap-4"
        style={{ marginBottom: 14 }}
      >
        <div>
          <div style={{ fontSize: 16, fontWeight: 600, color: theme.color }}>
            <span aria-hidden>{theme.emoji}</span> {theme.label}
          </div>
          <div style={{ fontSize: 12, color: "#8293A6", marginTop: 2 }}>
            {theme.tagline}
          </div>
        </div>
        <button
          onClick={onClose}
          aria-label="Close theme detail"
          className="leading-none flex items-center justify-center rounded hover:text-foreground transition-colors"
          style={{
            fontSize: 20,
            color: "#8293A6",
            minWidth: 32,
            minHeight: 32,
            flexShrink: 0,
          }}
        >
          &times;
        </button>
      </div>

      {/* Detail band — keywords | communities | example posts.
          auto-fit collapses to 2 then 1 column as width tightens. */}
      <div
        className="grid gap-x-8 gap-y-5"
        style={{ gridTemplateColumns: "repeat(auto-fit, minmax(240px, 1fr))" }}
      >
        <KeywordsSection keywords={data.keywords} color={theme.color} />
        <CommunitiesSection subreddits={data.subreddits} color={theme.color} />
        <SamplePostsSection samples={samples} />
      </div>

      {/* Footer — provenance line */}
      <div
        style={{
          fontSize: 11,
          color: "#8293A6",
          marginTop: 14,
          paddingTop: 10,
          borderTop: "0.5px solid #1E293B",
        }}
      >
        {data.keywords.length} keywords across {data.subreddits.length}{" "}
        communities &middot; {data.unique_posts.toLocaleString()} posts matched
        &middot; all keywords manually validated
      </div>
    </div>
  );
}

export default function TrendAtlas({
  themeData,
  timeRange,
  bp,
  selected,
  keywordDetails,
  onOpenDetail,
}: {
  themeData: ThemeData;
  timeRange: TimeRange;
  bp: Breakpoint;
  selected: string | null;
  keywordDetails: KeywordDetailsData;
  onOpenDetail: (id: string) => void;
}) {
  // Build each theme's monthly series and the shared month domain.
  const { perTheme, months } = useMemo(() => {
    const series: Record<string, { date: string; value: number }[]> = {};
    const monthSet = new Set<string>();
    for (const t of THEMES) {
      const s = monthlySeries(themeData[t.id] ?? []);
      series[t.id] = s;
      for (const r of s) monthSet.add(r.date);
    }
    let domain = [...monthSet].sort();
    if (timeRange !== "ALL" && domain.length) {
      const back = timeRange === "2Y" ? 24 : timeRange === "1Y" ? 12 : 6;
      const last = new Date(domain[domain.length - 1] + "T00:00:00Z");
      last.setUTCMonth(last.getUTCMonth() - back);
      const cutoff = last.toISOString().slice(0, 10);
      domain = domain.filter((m) => m >= cutoff);
    }
    return { perTheme: series, months: domain };
  }, [themeData, timeRange]);

  // 3 columns on desktop (2 rows → all six panels fit one screen), 2 on
  // tablet, 1 on mobile.
  const cols = bp === "mobile" ? 1 : bp === "tablet" ? 2 : 3;
  const panelHeight = bp === "mobile" ? 210 : 240;
  const labelFs = bp === "mobile" ? 14 : 11;

  // Events numbered by FIXED chronological order over the full set (stable
  // identifiers), then filtered to the visible window.
  const numberedEvents: NumberedEvent[] = EVENTS.map((e, i) => ({
    ...e,
    num: i + 1,
  })).filter(
    (e) =>
      months.length > 0 &&
      e.date >= months[0] &&
      e.date <= months[months.length - 1],
  );

  // Inline detail: which panel is expanded, and after which grid index the
  // full-width detail row is injected (the last panel of the clicked row).
  const selectedIdx = selected
    ? THEMES.findIndex((t) => t.id === selected)
    : -1;
  const selectedTheme = selectedIdx >= 0 ? THEMES[selectedIdx] : null;
  const selectedData =
    selected && keywordDetails[selected] ? keywordDetails[selected] : null;
  // Inline expansion on tablet/desktop; mobile uses a bottom sheet instead.
  const showInline = bp !== "mobile" && !!selectedTheme && !!selectedData;
  const detailAfterIdx = showInline
    ? Math.min(
        Math.floor(selectedIdx / cols) * cols + cols - 1,
        THEMES.length - 1,
      )
    : -1;

  return (
    <div>
      {numberedEvents.length > 0 && (
        <EventLegend events={numberedEvents} bp={bp} />
      )}

      <div
        className="grid gap-x-6 gap-y-4"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {THEMES.map((t, i) => {
          const series = perTheme[t.id] ?? [];
          const byDate: Record<string, number> = {};
          for (const r of series) byDate[r.date] = r.value;
          const themeStart = series[0]?.date;

          const data = months.map((m) => ({
            date: m,
            value: themeStart && m >= themeStart ? byDate[m] ?? 0 : null,
          }));
          const startsLate =
            themeStart && months.length > 0 && themeStart > months[0];
          const isOpen = selected === t.id;

          return (
            <Fragment key={t.id}>
              <div
                role="button"
                tabIndex={0}
                data-theme-trigger={t.id}
                aria-expanded={isOpen}
                onClick={() => onOpenDetail(t.id)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onOpenDetail(t.id);
                  }
                }}
                aria-label={`${t.label} — ${isOpen ? "collapse" : "expand"} theme detail`}
                className="group min-w-0 cursor-pointer rounded-lg transition-colors hover:bg-[#15171E] p-2"
                style={
                  isOpen
                    ? {
                        backgroundColor: "#15171E",
                        boxShadow: `0 0 0 1.5px ${t.color}`,
                      }
                    : undefined
                }
              >
                {/* Panel header */}
                <div className="flex items-center justify-between gap-3">
                  <span
                    className="flex items-center gap-2"
                    style={{ fontSize: 16, fontWeight: 600 }}
                  >
                    <span aria-hidden>{t.emoji}</span>
                    <span style={{ color: t.color }}>{t.label}</span>
                  </span>
                  {/* Detector chip — the key "heights aren't comparable" signal,
                      given real visible weight rather than a faint corner tag. */}
                  <span
                    title="How much theme-relevant discourse the keyword set catches. Line heights are NOT comparable between panels of different detector width."
                    style={{
                      fontSize: labelFs,
                      color: "#AEB9C7",
                      backgroundColor: "#20242F",
                      border: "1px solid #2F3441",
                      borderRadius: 5,
                      padding: "1.5px 8px",
                      whiteSpace: "nowrap",
                    }}
                  >
                    {DETECTOR_LABEL[t.detector]}
                  </span>
                </div>

                {/* One-line reading of the theme's trend */}
                <p
                  style={{
                    fontSize: bp === "mobile" ? 14 : 12.5,
                    lineHeight: 1.45,
                    color: "#94A3B8",
                    marginTop: 3,
                    marginBottom: 6,
                  }}
                >
                  {t.blurb}
                </p>

                <div style={{ height: panelHeight }}>
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={data}
                      margin={{ top: 24, right: 8, bottom: 2, left: 0 }}
                    >
                      <CartesianGrid
                        strokeDasharray="3 3"
                        stroke="#2A2D3A"
                        vertical={false}
                      />
                      <XAxis
                        dataKey="date"
                        tickFormatter={fmtMonthShort}
                        stroke="#2A2D3A"
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        tickLine={false}
                        axisLine={{ stroke: "#2A2D3A" }}
                        minTickGap={44}
                      />
                      <YAxis
                        width={36}
                        stroke="transparent"
                        tick={{ fill: "#64748B", fontSize: 11 }}
                        tickLine={false}
                        axisLine={false}
                        domain={[0, "auto"]}
                        tickCount={4}
                        allowDecimals={false}
                      />
                      {numberedEvents.map((e) => (
                        <ReferenceLine
                          key={e.date}
                          x={e.date}
                          stroke="#C2974D"
                          strokeOpacity={0.7}
                          strokeDasharray={e.methodology ? "2 3" : "5 3"}
                          strokeWidth={1}
                          label={{
                            value: String(e.num),
                            position: "top",
                            fill: "#D4A862",
                            fontSize: 11,
                          }}
                        />
                      ))}
                      <Tooltip
                        cursor={{ stroke: "#475569", strokeWidth: 1 }}
                        content={({ active, payload, label }) => {
                          if (
                            !active ||
                            !payload?.length ||
                            payload[0].value == null
                          ) {
                            return null;
                          }
                          return (
                            <div
                              style={{
                                backgroundColor: "#0F1117",
                                border: "1px solid #2A2D3A",
                                borderRadius: 6,
                                padding: "4px 8px",
                                fontSize: 11,
                                whiteSpace: "nowrap",
                              }}
                            >
                              <span style={{ color: "#94A3B8" }}>
                                {fmtMonth(label as string)}
                              </span>
                              <span style={{ color: "#94A3B8" }}>{"  ·  "}</span>
                              <span style={{ color: "#F8FAFC", fontWeight: 600 }}>
                                {(payload[0].value as number).toFixed(1)}
                              </span>
                              <span style={{ color: "#94A3B8" }}> per 1k posts</span>
                            </div>
                          );
                        }}
                      />
                      <Line
                        type="linear"
                        dataKey="value"
                        stroke={t.color}
                        strokeWidth={2}
                        dot={false}
                        isAnimationActive={false}
                        connectNulls={false}
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>

                {/* Footer row: coverage note (left) + detail affordance (right) */}
                <div
                  className="flex items-center justify-between"
                  style={{ marginTop: 2, minHeight: 16 }}
                >
                  <span style={{ fontSize: labelFs, color: "#64748B" }}>
                    {startsLate
                      ? `measurable from ${fmtMonthShort(themeStart!)}`
                      : ""}
                  </span>
                  <span
                    className="transition-colors group-hover:text-[#94A3B8]"
                    style={{
                      fontSize: labelFs,
                      color: isOpen ? "#94A3B8" : "#64748B",
                    }}
                  >
                    {isOpen ? "Hide detail" : "Details →"}
                  </span>
                </div>
              </div>

              {/* Inline detail row — injected after the clicked panel's row */}
              {showInline && i === detailAfterIdx && (
                <ThemeDetailRow
                  key={selected ?? "detail"}
                  theme={selectedTheme!}
                  data={selectedData!}
                  onClose={() => onOpenDetail(selected!)}
                />
              )}
            </Fragment>
          );
        })}
      </div>
    </div>
  );
}
