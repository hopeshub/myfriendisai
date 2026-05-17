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
import type { PostVolumeSplitPoint } from "./themeData";

// ── Post-volume chart ────────────────────────────────────────────────────────
// How much the committed-core communities post, month by month — split into
// r/CharacterAI and everything else. CharacterAI is a mass-market roleplay
// platform that has been 75-90% of all post volume; stacking it separately
// keeps its own boom-and-bust from being read as the whole category's. The
// lower band (dedicated companion communities) is the signal that matters.
//
// Honest caveats are built in: months with no archived data render as a real
// break (connectNulls off — the 2017-2019 collection gap), and the pre-2023
// span is shaded because archive coverage there is patchy.
// See docs/characterai_composition_fault_2026-05-16.md.

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

const ARCHIVE_SEAM = "2023-01";
const CAI_COLOR = "#566173"; // r/CharacterAI — muted slate, the big confounder
const OTHER_COLOR = "#7C9CD0"; // dedicated communities — the signal

type Row = { month: string; other: number | null; characterai: number | null };

function Swatch({ color }: { color: string }) {
  return (
    <span
      aria-hidden
      style={{
        display: "inline-block",
        width: 9,
        height: 9,
        borderRadius: 2,
        backgroundColor: color,
        marginRight: 5,
        verticalAlign: "baseline",
      }}
    />
  );
}

export default function PostVolumeChart({
  data,
}: {
  data: PostVolumeSplitPoint[];
}) {
  const { series, yearTicks, firstMonth, hasEarly } = useMemo(() => {
    if (data.length === 0) {
      return { series: [] as Row[], yearTicks: [] as string[], firstMonth: "", hasEarly: false };
    }
    const lookup: Record<string, PostVolumeSplitPoint> = {};
    for (const d of data) lookup[d.month] = d;

    // Fill the whole span so missing months exist as null points — the area
    // then breaks over a gap instead of ramping straight across it.
    const months = monthRange(data[0].month, data[data.length - 1].month);
    const rows: Row[] = months.map((m) => {
      const d = lookup[m];
      return {
        month: m,
        other: d ? d.other : null,
        characterai: d ? d.characterai : null,
      };
    });

    // One tick per calendar year, anchored to that year's first month.
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
    <div>
      {/* Legend */}
      <div
        className="flex flex-wrap gap-x-4 gap-y-1"
        style={{ fontSize: 12, color: "#94A3B8", marginBottom: 8 }}
      >
        <span>
          <Swatch color={OTHER_COLOR} />
          dedicated companion communities
        </span>
        <span>
          <Swatch color={CAI_COLOR} />
          r/CharacterAI
        </span>
      </div>

      <div style={{ height: 252 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={series} margin={{ top: 10, right: 8, bottom: 2, left: 0 }}>
            <defs>
              <linearGradient id="pv-other" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={OTHER_COLOR} stopOpacity={0.6} />
                <stop offset="100%" stopColor={OTHER_COLOR} stopOpacity={0.15} />
              </linearGradient>
              <linearGradient id="pv-cai" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={CAI_COLOR} stopOpacity={0.55} />
                <stop offset="100%" stopColor={CAI_COLOR} stopOpacity={0.15} />
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
                if (!active || !payload?.length) return null;
                const get = (k: string) =>
                  payload.find((p) => p.dataKey === k)?.value as
                    | number
                    | null
                    | undefined;
                const o = get("other");
                const c = get("characterai");
                if (o == null && c == null) return null;
                const total = (o ?? 0) + (c ?? 0);
                return (
                  <div
                    style={{
                      backgroundColor: "#0F1117",
                      border: "1px solid #2A2D3A",
                      borderRadius: 6,
                      padding: "6px 9px",
                      fontSize: 11,
                      lineHeight: 1.6,
                    }}
                  >
                    <div style={{ color: "#94A3B8", marginBottom: 2 }}>
                      {fmtMonth(label as string)}
                    </div>
                    <div style={{ color: "#CBD5E1" }}>
                      <Swatch color={OTHER_COLOR} />
                      dedicated&nbsp;&nbsp;
                      <span style={{ color: "#F8FAFC", fontWeight: 600 }}>
                        {(o ?? 0).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ color: "#CBD5E1" }}>
                      <Swatch color={CAI_COLOR} />
                      r/CharacterAI&nbsp;&nbsp;
                      <span style={{ color: "#F8FAFC", fontWeight: 600 }}>
                        {(c ?? 0).toLocaleString()}
                      </span>
                    </div>
                    <div style={{ color: "#64748B", marginTop: 2 }}>
                      total {total.toLocaleString()} posts
                    </div>
                  </div>
                );
              }}
            />
            {/* Bottom band = the signal; CharacterAI stacked on top. */}
            <Area
              type="monotone"
              dataKey="other"
              stackId="v"
              stroke={OTHER_COLOR}
              strokeWidth={2}
              fill="url(#pv-other)"
              connectNulls={false}
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="characterai"
              stackId="v"
              stroke={CAI_COLOR}
              strokeWidth={1.5}
              fill="url(#pv-cai)"
              connectNulls={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
