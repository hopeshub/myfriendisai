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
  ReferenceArea,
} from "recharts";
import type { PostVolumePoint } from "./themeData";

// ── Post-volume chart ────────────────────────────────────────────────────────
// The orientation chart: how much the committed-core communities post, month
// by month. It needs no keyword caveats — it is a plain post count — but it
// does need one: public archives captured less of the pre-2023 years, so the
// early part of the curve runs low. That region is shaded, not hidden.

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

// First month from which archive coverage is dense enough to read counts at
// face value. Before this, the curve is a floor (see the About page).
const ARCHIVE_SEAM = "2023-01";

export default function PostVolumeChart({ data }: { data: PostVolumePoint[] }) {
  const { firstMonth, hasEarly } = useMemo(
    () => ({
      firstMonth: data[0]?.month ?? "",
      hasEarly: data.length > 0 && data[0].month < ARCHIVE_SEAM,
    }),
    [data],
  );

  if (data.length === 0) {
    return (
      <div
        style={{ height: 240 }}
        className="flex items-center justify-center text-sm text-[#64748B]"
      >
        No post-volume data yet.
      </div>
    );
  }

  return (
    <div style={{ height: 260 }}>
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart data={data} margin={{ top: 10, right: 8, bottom: 2, left: 0 }}>
          <defs>
            <linearGradient id="pv-fill" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#7C9CD0" stopOpacity={0.5} />
              <stop offset="100%" stopColor="#7C9CD0" stopOpacity={0.03} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="#2A2D3A"
            vertical={false}
          />
          {hasEarly && (
            <ReferenceArea
              x1={firstMonth}
              x2={ARCHIVE_SEAM}
              fill="#64748B"
              fillOpacity={0.08}
              label={{
                value: "archives thinner — counts run low",
                position: "insideTop",
                fill: "#64748B",
                fontSize: 10,
              }}
            />
          )}
          <XAxis
            dataKey="month"
            tickFormatter={(m: string) => m.slice(0, 4)}
            stroke="#2A2D3A"
            tick={{ fill: "#64748B", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#2A2D3A" }}
            minTickGap={28}
          />
          <YAxis
            width={40}
            stroke="transparent"
            tick={{ fill: "#64748B", fontSize: 11 }}
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
                  <span style={{ color: "#94A3B8" }}>
                    {fmtMonth(label as string)}
                  </span>
                  <span style={{ color: "#94A3B8" }}>{"  ·  "}</span>
                  <span style={{ color: "#F8FAFC", fontWeight: 600 }}>
                    {(payload[0].value as number).toLocaleString()}
                  </span>
                  <span style={{ color: "#94A3B8" }}> posts</span>
                </div>
              );
            }}
          />
          <Area
            type="monotone"
            dataKey="posts"
            stroke="#7C9CD0"
            strokeWidth={2}
            fill="url(#pv-fill)"
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
