"use client";

import { useMemo } from "react";
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

// ── Trend Atlas ──────────────────────────────────────────────────────────────
// Small-multiples grid: one panel per theme, each on its OWN y-axis. The axes
// deliberately do not match — detection sensitivity differs ~10x between themes,
// so line heights are not comparable between panels. Compare each theme's shape
// and timing over time; that comparison is honest. A shared y-axis would not be.
//
// Events are shared across all themes, so they are labelled once in a legend
// above the grid; each panel carries only a faint numbered tick.

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
// Shown once above the grid. Each panel then only needs a numbered tick.
function EventLegend({ events }: { events: NumberedEvent[] }) {
  const hasMethodology = events.some((e) => e.methodology);
  return (
    <div style={{ marginBottom: 14 }}>
      <div
        style={{
          fontSize: 11,
          color: "#64748B",
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          marginBottom: 7,
        }}
      >
        Events
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: "7px 18px" }}>
        {events.map((e) => (
          <span
            key={e.date}
            style={{
              display: "inline-flex",
              alignItems: "center",
              gap: 7,
              fontSize: 12.5,
            }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: 17,
                height: 17,
                borderRadius: 999,
                fontSize: 10,
                fontWeight: 700,
                flexShrink: 0,
                color: e.methodology ? "#94A3B8" : "#0F1117",
                backgroundColor: e.methodology ? "transparent" : "#94A3B8",
                border: e.methodology ? "1px dashed #5B6472" : "none",
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
        <div style={{ fontSize: 10.5, color: "#64748B", marginTop: 6 }}>
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
  onOpenDetail,
}: {
  themeData: ThemeData;
  timeRange: TimeRange;
  bp: Breakpoint;
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

  const cols = bp === "mobile" ? 1 : bp === "tablet" ? 2 : 3;
  const panelHeight = bp === "mobile" ? 178 : 204;

  // Events within the visible window, numbered left-to-right by date.
  const numberedEvents: NumberedEvent[] = months.length
    ? EVENTS.filter(
        (e) => e.date >= months[0] && e.date <= months[months.length - 1],
      ).map((e, i) => ({ ...e, num: i + 1 }))
    : [];

  return (
    <div>
      {numberedEvents.length > 0 && <EventLegend events={numberedEvents} />}

      <div
        className="grid gap-3"
        style={{ gridTemplateColumns: `repeat(${cols}, minmax(0, 1fr))` }}
      >
        {THEMES.map((t) => {
          const series = perTheme[t.id] ?? [];
          const byDate: Record<string, number> = {};
          for (const r of series) byDate[r.date] = r.value;
          const themeStart = series[0]?.date;

          // Render the full shared month domain; null before the theme's own
          // start so the line simply begins at its coverage_start.
          const data = months.map((m) => ({
            date: m,
            value: themeStart && m >= themeStart ? byDate[m] ?? 0 : null,
          }));
          const startsLate =
            themeStart && months.length > 0 && themeStart > months[0];

          return (
            <div
              key={t.id}
              role="button"
              tabIndex={0}
              data-theme-trigger={t.id}
              onClick={() => onOpenDetail(t.id)}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") {
                  e.preventDefault();
                  onOpenDetail(t.id);
                }
              }}
              aria-label={`${t.label} — open theme detail`}
              className="rounded-lg cursor-pointer transition-colors"
              style={{
                backgroundColor: "#1A1D27",
                border: "1px solid #2A2D3A",
                borderLeft: `3px solid ${t.color}`,
                padding: "10px 12px 8px",
              }}
            >
              {/* Panel header */}
              <div className="flex items-center justify-between gap-2 mb-1">
                <span
                  className="flex items-center gap-1.5"
                  style={{ fontSize: 13 }}
                >
                  <span aria-hidden>{t.emoji}</span>
                  <span style={{ color: t.color, fontWeight: 600 }}>
                    {t.label}
                  </span>
                </span>
                <span
                  title="How much theme-relevant discourse the keyword set catches. Heights are not comparable between detectors of different width."
                  style={{
                    fontSize: 10,
                    color: "#8293A6",
                    border: "1px solid #2A2D3A",
                    borderRadius: 4,
                    padding: "1px 6px",
                    whiteSpace: "nowrap",
                  }}
                >
                  {DETECTOR_LABEL[t.detector]}
                </span>
              </div>

              <div style={{ height: panelHeight }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={data}
                    margin={{ top: 14, right: 8, bottom: 2, left: 0 }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#23262F"
                      vertical={false}
                    />
                    <XAxis
                      dataKey="date"
                      tickFormatter={fmtMonthShort}
                      stroke="#2A2D3A"
                      tick={{ fill: "#64748B", fontSize: 10 }}
                      tickLine={false}
                      axisLine={{ stroke: "#2A2D3A" }}
                      minTickGap={36}
                    />
                    <YAxis
                      width={34}
                      stroke="transparent"
                      tick={{ fill: "#64748B", fontSize: 10 }}
                      tickLine={false}
                      axisLine={false}
                      tickCount={3}
                      allowDecimals={false}
                    />
                    {numberedEvents.map((e) => (
                      <ReferenceLine
                        key={e.date}
                        x={e.date}
                        stroke="#6B7280"
                        strokeDasharray={e.methodology ? "2 3" : "5 3"}
                        strokeWidth={1}
                        label={{
                          value: String(e.num),
                          position: "insideTop",
                          fill: "#94A3B8",
                          fontSize: 9.5,
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
                            <span style={{ color: "#94A3B8" }}> per 1k</span>
                          </div>
                        );
                      }}
                    />
                    <Line
                      type="monotone"
                      dataKey="value"
                      stroke={t.color}
                      strokeWidth={1.8}
                      dot={false}
                      isAnimationActive={false}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>

              {startsLate && (
                <div style={{ fontSize: 10, color: "#64748B", marginTop: 2 }}>
                  measurable from {fmtMonthShort(themeStart!)}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
