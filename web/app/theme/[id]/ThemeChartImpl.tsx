"use client";

import { useMemo, useState } from "react";
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
import { EVENTS } from "../../themes";

// A single line chart for one theme's page. Same honest series as the homepage
// atlas panel (validated-keyword mentions per 1,000 posts, monthly mean), with
// a time-range selector so a reader can zoom in. Events are marked with
// numbered ticks and written out in full below the chart.

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

type TimeRange = "6M" | "1Y" | "2Y" | "ALL";
const RANGES: TimeRange[] = ["6M", "1Y", "2Y", "ALL"];

export default function ThemeChart({
  series,
  color,
}: {
  series: { date: string; hitsPerK: number }[];
  color: string;
}) {
  // Defaults to 1Y to match the homepage atlas, so clicking a theme open
  // doesn't silently change the time window the reader was looking at.
  const [range, setRange] = useState<TimeRange>("1Y");
  const monthly = useMemo(() => monthlySeries(series), [series]);

  // Apply the selected time window.
  const data = useMemo(() => {
    if (range === "ALL" || !monthly.length) return monthly;
    const back = range === "2Y" ? 24 : range === "1Y" ? 12 : 6;
    const last = new Date(monthly[monthly.length - 1].date + "T00:00:00Z");
    last.setUTCMonth(last.getUTCMonth() - back);
    const cutoff = last.toISOString().slice(0, 10);
    return monthly.filter((m) => m.date >= cutoff);
  }, [monthly, range]);

  // Events that fall inside the visible window, numbered in order.
  const events = useMemo(() => {
    if (!data.length) return [];
    const first = data[0].date;
    const last = data[data.length - 1].date;
    return EVENTS.filter((e) => e.date >= first && e.date <= last).map(
      (e, i) => ({ ...e, num: i + 1 }),
    );
  }, [data]);

  if (!monthly.length) {
    return (
      <div className="h-[240px] flex items-center justify-center text-sm text-[#7E8B9E]">
        No data yet.
      </div>
    );
  }

  const hasMethodology = events.some((e) => e.methodology);

  return (
    <div>
      {/* Time range selector */}
      <div className="flex gap-1 mb-3">
        {RANGES.map((r) => (
          <button
            key={r}
            onClick={() => setRange(r)}
            aria-pressed={range === r}
            aria-label={`Show ${r === "ALL" ? "all time" : `last ${r}`}`}
            className="px-3 h-11 sm:h-8 text-xs font-medium rounded-md transition-colors"
            style={{
              backgroundColor: range === r ? "#0F1117" : "transparent",
              color: range === r ? "#F8FAFC" : "#9AA7B8",
              border: `1px solid ${range === r ? "#2A2D3A" : "transparent"}`,
            }}
          >
            {r}
          </button>
        ))}
      </div>

      <div
        className="h-[240px] sm:h-[300px] w-full"
        role="img"
        aria-label="Line chart of this theme's validated-keyword mentions per 1,000 posts, monthly, with platform events marked."
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 30, right: 14, bottom: 4, left: 0 }}
            accessibilityLayer={false}
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
              tick={{ fill: "#7E8B9E", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "#2A2D3A" }}
              minTickGap={48}
            />
            <YAxis
              width={44}
              stroke="transparent"
              tick={{ fill: "#7E8B9E", fontSize: 12 }}
              tickLine={false}
              axisLine={false}
              domain={[0, "auto"]}
              tickCount={5}
              allowDecimals={false}
            />
            {events.map((e) => (
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
                  fontSize: 12,
                }}
              />
            ))}
            <Tooltip
              cursor={{ stroke: "#475569", strokeWidth: 1 }}
              animationDuration={140}
              animationEasing="ease-out"
              content={({ active, payload, label }) => {
                if (!active || !payload?.length || payload[0].value == null) {
                  return null;
                }
                return (
                  <div
                    style={{
                      backgroundColor: "#0F1117",
                      border: "1px solid #2A2D3A",
                      borderRadius: 6,
                      padding: "4px 8px",
                      fontSize: 12,
                      whiteSpace: "nowrap",
                    }}
                  >
                    <span style={{ color: "#9AA7B8" }}>
                      {fmtMonth(label as string)}
                    </span>
                    <span style={{ color: "#9AA7B8" }}>{"  ·  "}</span>
                    <span style={{ color: "#F1F4F8", fontWeight: 600 }}>
                      {(payload[0].value as number).toFixed(1)}
                    </span>
                    <span style={{ color: "#9AA7B8" }}> per 1k posts</span>
                  </div>
                );
              }}
            />
            <Line
              type="linear"
              dataKey="value"
              stroke={color}
              strokeWidth={2.5}
              dot={false}
              activeDot={{ r: 4, fill: color, stroke: color }}
              isAnimationActive={false}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 11, color: "#7E8B9E", marginTop: 8 }}>
        Validated-keyword mentions per 1,000 posts · monthly average · post text
        only
      </div>

      {/* Events — written out, one compact row */}
      {events.length > 0 && (
        <div
          style={{
            marginTop: 12,
            paddingTop: 10,
            borderTop: "1px solid #1E293B",
          }}
        >
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "6px 14px",
              alignItems: "center",
            }}
          >
            <span
              style={{
                fontSize: 11,
                color: "#7E8B9E",
                textTransform: "uppercase",
                letterSpacing: "0.05em",
              }}
            >
              Events
            </span>
            {events.map((e) => (
              <span
                key={e.date}
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 6,
                  fontSize: 13,
                  whiteSpace: "nowrap",
                }}
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
                <span style={{ color: "#C8D0DC" }}>{e.label}</span>
              </span>
            ))}
          </div>
          {hasMethodology && (
            <div style={{ fontSize: 11, color: "#7E8B9E", marginTop: 7 }}>
              A hollow marker is a change to our keyword set — a measurement
              change, not a real-world event.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
