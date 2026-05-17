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
// Two panels, each on its OWN y-scale: r/CharacterAI, and every other tracked
// community. They are deliberately not stacked or on a shared axis — CharacterAI
// is so much larger that a shared scale flattens the second panel into an
// unreadable sliver. Separate scales let each be read on its own terms: one
// surged and crashed on a platform lifecycle, the other held roughly steady.
//
// Honest caveats stay built in: missing months render as a real break
// (connectNulls off — the 2017-2019 collection gap), and the pre-2023 span is
// shaded for patchy archive coverage.
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

type PanelRow = { month: string; value: number | null };

function VolumePanel({
  title,
  caption,
  rows,
  yearTicks,
  firstMonth,
  hasEarly,
  color,
  gradientId,
  showSeamLabel,
}: {
  title: string;
  caption: string;
  rows: PanelRow[];
  yearTicks: string[];
  firstMonth: string;
  hasEarly: boolean;
  color: string;
  gradientId: string;
  showSeamLabel?: boolean;
}) {
  return (
    <div>
      <div style={{ fontSize: 14, fontWeight: 600, color: "#E2E8F0" }}>
        {title}
      </div>
      <div style={{ fontSize: 12, color: "#94A3B8", marginBottom: 6 }}>
        {caption}
      </div>
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={rows} margin={{ top: 8, right: 8, bottom: 2, left: 0 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.5} />
                <stop offset="100%" stopColor={color} stopOpacity={0.04} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" vertical={false} />
            {hasEarly && (
              <ReferenceArea
                x1={firstMonth}
                x2={ARCHIVE_SEAM}
                fill="#64748B"
                fillOpacity={0.09}
                label={
                  showSeamLabel
                    ? {
                        value: "patchy archive coverage",
                        position: "insideTop",
                        fill: "#94A3B8",
                        fontSize: 11,
                      }
                    : undefined
                }
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
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              fill={`url(#${gradientId})`}
              connectNulls={false}
              isAnimationActive={false}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default function PostVolumeChart({
  data,
}: {
  data: PostVolumeSplitPoint[];
}) {
  const { caiRows, otherRows, yearTicks, firstMonth, hasEarly } = useMemo(() => {
    if (data.length === 0) {
      return {
        caiRows: [] as PanelRow[],
        otherRows: [] as PanelRow[],
        yearTicks: [] as string[],
        firstMonth: "",
        hasEarly: false,
      };
    }
    const lookup: Record<string, PostVolumeSplitPoint> = {};
    for (const d of data) lookup[d.month] = d;

    // Fill the whole span so missing months exist as null points — the area
    // breaks over a gap instead of ramping straight across it.
    const months = monthRange(data[0].month, data[data.length - 1].month);
    const caiRows: PanelRow[] = months.map((m) => ({
      month: m,
      value: lookup[m] ? lookup[m].characterai : null,
    }));
    const otherRows: PanelRow[] = months.map((m) => ({
      month: m,
      value: lookup[m] ? lookup[m].other : null,
    }));

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
      caiRows,
      otherRows,
      yearTicks: ticks,
      firstMonth: data[0].month,
      hasEarly: data[0].month < ARCHIVE_SEAM,
    };
  }, [data]);

  if (caiRows.length === 0) {
    return (
      <div
        style={{ height: 220 }}
        className="flex items-center justify-center text-sm text-[#64748B]"
      >
        No post-volume data yet.
      </div>
    );
  }

  return (
    <div>
      <div className="grid gap-x-6 gap-y-5 sm:grid-cols-2">
        <VolumePanel
          title="r/CharacterAI"
          caption="Surged, then contracted — one platform's lifecycle."
          rows={caiRows}
          yearTicks={yearTicks}
          firstMonth={firstMonth}
          hasEarly={hasEarly}
          color="#566173"
          gradientId="pv-cai"
          showSeamLabel
        />
        <VolumePanel
          title="Every other tracked community"
          caption="Held roughly steady, with spikes at platform events."
          rows={otherRows}
          yearTicks={yearTicks}
          firstMonth={firstMonth}
          hasEarly={hasEarly}
          color="#7C9CD0"
          gradientId="pv-other"
        />
      </div>
      <p
        style={{
          fontSize: 11,
          color: "#64748B",
          marginTop: 8,
          textAlign: "center",
        }}
      >
        Each panel has its own scale &mdash; at its 2024 peak r/CharacterAI was
        roughly five times the size of every other tracked community combined.
      </p>
    </div>
  );
}
