"use client";

import { useMemo } from "react";
import Link from "next/link";
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
import type { ThemeData } from "./themeData";
import { THEMES, EVENTS } from "./themes";

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
// Each panel is a link to that theme's own page (/theme/[id]) — the deeper
// "what is this and why" lives there, not in an overlay on this page.

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
// Compact single block above the grid. Events visible in the selected time
// range are numbered 1..n in chronological order, so the legend never shows a
// gap (e.g. "3, 4, 5"). Numbers re-index when the range changes — the legend
// and every panel update together, so within any view they stay consistent.
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
                fontSize: 11,
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

export default function TrendAtlas({
  themeData,
  timeRange,
  bp,
}: {
  themeData: ThemeData;
  timeRange: TimeRange;
  bp: Breakpoint;
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

  // Events that fall inside the visible window, numbered 1..n in order — so
  // the legend never shows a gap like "3, 4, 5".
  const numberedEvents: NumberedEvent[] = EVENTS.filter(
    (e) =>
      months.length > 0 &&
      e.date >= months[0] &&
      e.date <= months[months.length - 1],
  ).map((e, i) => ({ ...e, num: i + 1 }));

  return (
    <div>
      {numberedEvents.length > 0 && (
        <EventLegend events={numberedEvents} bp={bp} />
      )}

      <div
        className="grid gap-x-6 gap-y-4"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {THEMES.map((t) => {
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

          return (
            <Link
              key={t.id}
              href={`/theme/${t.id}`}
              aria-label={`${t.label} — open theme page`}
              className="group block min-w-0 rounded-lg transition-colors hover:bg-[#15171E] p-2"
            >
              {/* Panel header */}
              <div className="flex items-center gap-3">
                <span
                  className="flex items-center gap-2"
                  style={{ fontSize: 16, fontWeight: 600 }}
                >
                  <span aria-hidden>{t.emoji}</span>
                  <span style={{ color: t.color }}>{t.label}</span>
                </span>
              </div>

              {/* One-line reading of the theme's trend */}
              <p
                style={{
                  fontSize: bp === "mobile" ? 14 : 13,
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

              {/* Footer row: coverage note (left) + page affordance (right) */}
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
                  style={{ fontSize: labelFs, color: "#64748B" }}
                >
                  Explore {t.label} &rarr;
                </span>
              </div>
            </Link>
          );
        })}
      </div>
    </div>
  );
}
