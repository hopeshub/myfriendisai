"use client";

import { useMemo } from "react";
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

// ── Community activity chart ─────────────────────────────────────────────────
// The full-size version of the Communities-table sparkline: one community's
// monthly post volume, Jan 2023 to the last complete month. This is the
// longest-range data on the detail page — the daily-snapshot metric charts
// below it only reach back ~2 months.

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtMonth(m: string): string {
  const [y, mo] = m.split("-");
  return `${MONTH_NAMES[parseInt(mo, 10) - 1]} ${y}`;
}

function fmtCount(n: number): string {
  if (n >= 1000) return `${(n / 1000).toFixed(n >= 10000 ? 0 : 1)}k`;
  return String(n);
}

export default function CommunityActivityChart({
  months,
  values,
}: {
  months: string[];
  values: number[];
}) {
  const { rows, yearTicks } = useMemo(() => {
    const rows = months.map((m, i) => ({ month: m, value: values[i] ?? 0 }));
    const seen = new Set<string>();
    const yearTicks: string[] = [];
    for (const m of months) {
      const y = m.slice(0, 4);
      if (!seen.has(y)) {
        seen.add(y);
        yearTicks.push(m);
      }
    }
    return { rows, yearTicks };
  }, [months, values]);

  if (rows.length === 0 || values.every((v) => !v)) {
    return (
      <div
        style={{ height: 200 }}
        className="flex items-center justify-center text-sm text-[#6B7689]"
      >
        No monthly post data for this community yet.
      </div>
    );
  }

  return (
    <div style={{ height: 220 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={rows} margin={{ top: 8, right: 8, bottom: 2, left: 0 }}>
          <defs>
            <linearGradient id="community-activity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7C9CD0" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#7C9CD0" stopOpacity={0.04} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" vertical={false} />
          <XAxis
            dataKey="month"
            ticks={yearTicks}
            interval={0}
            tickFormatter={(m: string) => m.slice(0, 4)}
            stroke="#2A2D3A"
            tick={{ fill: "#6B7689", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#2A2D3A" }}
          />
          <YAxis
            width={44}
            stroke="transparent"
            tick={{ fill: "#6B7689", fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={fmtCount}
          />
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
                    fontSize: 11,
                    whiteSpace: "nowrap",
                  }}
                >
                  <span style={{ color: "#9AA7B8" }}>
                    {fmtMonth(label as string)}
                  </span>
                  <span style={{ color: "#9AA7B8" }}>{"  ·  "}</span>
                  <span style={{ color: "#F1F4F8", fontWeight: 600 }}>
                    {(payload[0].value as number).toLocaleString()}
                  </span>
                  <span style={{ color: "#9AA7B8" }}> posts</span>
                </div>
              );
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke="#7C9CD0"
            strokeWidth={2}
            fill="url(#community-activity)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
