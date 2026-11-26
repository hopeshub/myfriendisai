"use client";

import { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";
import MeasuredChart from "@/app/MeasuredChart";
import { fromFirstActiveMonth } from "@/lib/metrics";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";
import { C, radius } from "@/app/styles";

// ── Community activity chart ─────────────────────────────────────────────────
// The full-size version of the Communities-table sparkline: one community's
// monthly post volume, Jan 2023 to the last complete month. It is counted
// from the posts themselves; the metric charts below it are monthly means of
// the daily snapshots, a separate series with its own start date.
//
// Months before the community's first post are drawn as gaps rather than as
// zeros, so the line starts where the community does.

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
  // No time-range toggle on this chart — it animates once on mount only.
  const reducedMotion = usePrefersReducedMotion();

  const { rows, yearTicks } = useMemo(() => {
    const active = fromFirstActiveMonth(values ?? []);
    const rows = months.map((m, i) => ({
      month: m,
      value: active[i] ?? null,
    }));
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
        className="flex items-center justify-center text-sm text-[var(--c-caption)]"
      >
        No monthly post data for this community yet.
      </div>
    );
  }

  return (
    <MeasuredChart
      style={{ height: 220 }}
      role="img"
      ariaLabel="Chart: this community's monthly post volume from 2023 to the latest complete month."
    >
      {({ width, height }) => (
        <AreaChart
          width={width}
          height={height}
          data={rows}
          margin={{ top: 8, right: 8, bottom: 2, left: 0 }}
          accessibilityLayer={false}
        >
          <defs>
            <linearGradient id="community-activity" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor={C.communityLine} stopOpacity={0.5} />
              <stop offset="100%" stopColor={C.communityLine} stopOpacity={0.04} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke={C.grid} vertical={false} />
          <XAxis
            dataKey="month"
            ticks={yearTicks}
            interval={0}
            tickFormatter={(m: string) => m.slice(0, 4)}
            stroke={C.grid}
            tick={{ fill: C.caption, fontSize: 11 }}
            tickLine={false}
            axisLine={{ stroke: C.grid }}
          />
          <YAxis
            width={44}
            stroke="transparent"
            tick={{ fill: C.caption, fontSize: 11 }}
            tickLine={false}
            axisLine={false}
            tickFormatter={fmtCount}
          />
          <Tooltip
            cursor={{ stroke: C.cursor, strokeWidth: 1 }}
            animationDuration={140}
            animationEasing="ease-out"
            content={({ active, payload, label }) => {
              if (!active || !payload?.length || payload[0].value == null) {
                return null;
              }
              return (
                <div
                  style={{
                    backgroundColor: C.bg,
                    border: `1px solid ${C.grid}`,
                    borderRadius: radius(6),
                    padding: "4px 8px",
                    fontSize: 11,
                    whiteSpace: "nowrap",
                  }}
                >
                  <span style={{ color: C.lead }}>
                    {fmtMonth(label as string)}
                  </span>
                  <span style={{ color: C.lead }}>{"  ·  "}</span>
                  <span style={{ color: C.heading, fontWeight: 600 }}>
                    {(payload[0].value as number).toLocaleString()}
                  </span>
                  <span style={{ color: C.lead }}> posts</span>
                </div>
              );
            }}
          />
          <Area
            type="monotone"
            dataKey="value"
            stroke={C.communityLine}
            strokeWidth={2}
            fill="url(#community-activity)"
            activeDot={{ r: 4, fill: C.communityLine, stroke: C.communityLine }}
            isAnimationActive={!reducedMotion}
            animationDuration={700}
            animationEasing="ease-out"
          />
        </AreaChart>
      )}
    </MeasuredChart>
  );
}
