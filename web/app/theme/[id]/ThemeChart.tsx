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
import { EVENTS } from "../../themes";

// A single large line chart for one theme's page. Same honest series as the
// homepage atlas panel (validated-keyword mentions per 1,000 posts, monthly
// mean), just given room to breathe — full-size, with the events written out
// in words below the chart instead of squeezed onto it.

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

export default function ThemeChart({
  series,
  color,
}: {
  series: { date: string; hitsPerK: number }[];
  color: string;
}) {
  const monthly = useMemo(() => monthlySeries(series), [series]);

  const events = useMemo(() => {
    if (!monthly.length) return [];
    const first = monthly[0].date;
    const last = monthly[monthly.length - 1].date;
    return EVENTS.filter((e) => e.date >= first && e.date <= last).map(
      (e, i) => ({ ...e, num: i + 1 }),
    );
  }, [monthly]);

  if (!monthly.length) {
    return (
      <div className="h-[240px] flex items-center justify-center text-sm text-[#64748B]">
        No data in range yet.
      </div>
    );
  }

  const hasMethodology = events.some((e) => e.methodology);

  return (
    <div>
      <div className="h-[260px] sm:h-[360px] w-full">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={monthly}
            margin={{ top: 24, right: 14, bottom: 4, left: 0 }}
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
              tick={{ fill: "#64748B", fontSize: 12 }}
              tickLine={false}
              axisLine={{ stroke: "#2A2D3A" }}
              minTickGap={48}
            />
            <YAxis
              width={44}
              stroke="transparent"
              tick={{ fill: "#64748B", fontSize: 12 }}
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
              stroke={color}
              strokeWidth={2.5}
              dot={false}
              isAnimationActive={false}
              connectNulls={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div style={{ fontSize: 11, color: "#64748B", marginTop: 2 }}>
        Validated-keyword mentions per 1,000 posts · monthly average · post text
        only
      </div>

      {/* Events written out in words */}
      {events.length > 0 && (
        <div
          style={{
            marginTop: 14,
            paddingTop: 12,
            borderTop: "0.5px solid #1E293B",
          }}
        >
          <div
            style={{
              display: "flex",
              flexWrap: "wrap",
              gap: "8px 18px",
              alignItems: "center",
            }}
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
                style={{
                  display: "inline-flex",
                  alignItems: "center",
                  gap: 7,
                  fontSize: 13,
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
                    color: e.methodology ? "#D4A862" : "#0F1117",
                    backgroundColor: e.methodology ? "transparent" : "#C2974D",
                    border: e.methodology ? "1px dashed #C2974D" : "none",
                  }}
                >
                  {e.num}
                </span>
                <span style={{ color: "#CBD5E1" }}>{e.label}</span>
                <span style={{ color: "#64748B" }}>{fmtMonth(e.date)}</span>
              </span>
            ))}
          </div>
          {hasMethodology && (
            <div style={{ fontSize: 11, color: "#64748B", marginTop: 7 }}>
              A hollow marker is a change to our keyword set — a measurement
              change, not a real-world event.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
