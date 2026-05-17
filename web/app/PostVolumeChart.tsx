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
// by month. It is a plain post count — no keyword judgement — but two honest
// caveats are built in visually:
//
//  1. Months with no archived data are rendered as a genuine break in the
//     area (connectNulls is off), so the 2017-2019 collection gap shows as
//     empty space, not a straight ramp across it.
//  2. The pre-2023 span is shaded: archive coverage there is patchy, so those
//     counts are a floor, not a true monthly volume.
//
// Note on what is NOT marked: the backfill→live-collector seam (March 2026)
// is a provenance change, not a volume artifact — the series is continuous
// across it — so it carries no marker here.

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

/** Every "YYYY-MM" from start to end inclusive, so gaps become explicit. */
function monthRange(start: string, end: string): string[] {
  const out: string[] = [];
  let [y, m] = start.split("-").map(Number);
  const [ey, em] = end.split("-").map(Number);
  while (y < ey || (y === ey && m <= em)) {
    out.push(`${y}-${String(m).padStart(2, "0")}`);
    m += 1;
    if (m > 12) {
      m = 1;
      y += 1;
    }
  }
  return out;
}

// First month from which archive coverage is dense enough to read counts at
// face value. Before this, the curve is a floor (see the About page).
const ARCHIVE_SEAM = "2023-01";

type Row = { month: string; posts: number | null };

export default function PostVolumeChart({ data }: { data: PostVolumePoint[] }) {
  const { series, yearTicks, firstMonth, hasEarly } = useMemo(() => {
    if (data.length === 0) {
      return { series: [] as Row[], yearTicks: [] as string[], firstMonth: "", hasEarly: false };
    }
    const lookup: Record<string, number> = {};
    for (const d of data) lookup[d.month] = d.posts;

    // Fill the whole span so missing months exist as null points — the area
    // then breaks over a gap instead of ramping straight across it.
    const months = monthRange(data[0].month, data[data.length - 1].month);
    const rows: Row[] = months.map((m) => ({ month: m, posts: lookup[m] ?? null }));

    // One tick per calendar year, anchored to that year's first month in the
    // axis — so labels read 2017, 2018, 2019 … once each, in order.
    const seen = new Set<string>();
    const ticks: string[] = [];
    for (const m of months) {
      const y = m.slice(0, 4);
      if (!seen.has(y)) {
        seen.add(y);
        ticks.push(m);
      }
    }

    return {
      series: rows,
      yearTicks: ticks,
      firstMonth: data[0].month,
      hasEarly: data[0].month < ARCHIVE_SEAM,
    };
  }, [data]);

  if (series.length === 0) {
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
        <AreaChart data={series} margin={{ top: 10, right: 8, bottom: 2, left: 0 }}>
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
              fillOpacity={0.09}
              label={{
                value: "patchy archive coverage — a floor, not a full count",
                position: "insideTop",
                fill: "#64748B",
                fontSize: 10,
              }}
            />
          )}
          <XAxis
            dataKey="month"
            ticks={yearTicks}
            interval={0}
            tickFormatter={(m: string) => m.slice(0, 4)}
            stroke="#2A2D3A"
            tick={{ fill: "#64748B", fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: "#2A2D3A" }}
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
            connectNulls={false}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
