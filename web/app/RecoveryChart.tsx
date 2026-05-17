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
import type { RecoveryVolumePoint } from "./themeData";
import { RECOVERY_COMMUNITIES } from "./recoveryData";

// Stacked monthly post volume across the four recovery / quitting communities.
// The shape — flat at zero through 2023, then a staggered climb as each
// community is founded — is the point of the chart.

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtMonth(m: string): string {
  const [y, mo] = m.split("-");
  return `${MONTH_NAMES[parseInt(mo, 10) - 1]} ${y}`;
}

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

export default function RecoveryChart({
  data,
}: {
  data: RecoveryVolumePoint[];
}) {
  const yearTicks = useMemo(() => {
    const seen = new Set<string>();
    const ticks: string[] = [];
    for (const d of data) {
      const y = d.month.slice(0, 4);
      if (!seen.has(y)) {
        seen.add(y);
        ticks.push(d.month);
      }
    }
    return ticks;
  }, [data]);

  if (data.length === 0) {
    return (
      <div
        style={{ height: 220 }}
        className="flex items-center justify-center text-sm text-[#64748B]"
      >
        No recovery-community data yet.
      </div>
    );
  }

  return (
    <div>
      <div
        className="flex flex-wrap gap-x-4 gap-y-1"
        style={{ fontSize: 12, color: "#94A3B8", marginBottom: 8 }}
      >
        {RECOVERY_COMMUNITIES.map((rc) => (
          <span key={rc.sub}>
            <Swatch color={rc.color} />
            {rc.label}
          </span>
        ))}
      </div>

      <div style={{ height: 230 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 8, right: 8, bottom: 2, left: 0 }}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#2A2D3A"
              vertical={false}
            />
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
              width={36}
              stroke="transparent"
              tick={{ fill: "#64748B", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              allowDecimals={false}
            />
            <Tooltip
              isAnimationActive={false}
              cursor={{ stroke: "#475569", strokeWidth: 1 }}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                const total = payload.reduce(
                  (s, p) => s + ((p.value as number) ?? 0),
                  0,
                );
                if (total === 0) return null;
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
                    {RECOVERY_COMMUNITIES.map((rc) => {
                      const v =
                        (payload.find((p) => p.dataKey === rc.sub)
                          ?.value as number) ?? 0;
                      return (
                        <div key={rc.sub} style={{ color: "#CBD5E1" }}>
                          <Swatch color={rc.color} />
                          {rc.label}&nbsp;&nbsp;
                          <span style={{ color: "#F8FAFC", fontWeight: 600 }}>
                            {v.toLocaleString()}
                          </span>
                        </div>
                      );
                    })}
                    <div style={{ color: "#64748B", marginTop: 2 }}>
                      total {total.toLocaleString()} posts
                    </div>
                  </div>
                );
              }}
            />
            {RECOVERY_COMMUNITIES.map((rc) => (
              <Area
                key={rc.sub}
                type="monotone"
                dataKey={rc.sub}
                stackId="recovery"
                stroke={rc.color}
                strokeWidth={1.5}
                fill={rc.color}
                fillOpacity={0.45}
                dot={false}
                activeDot={false}
                isAnimationActive={false}
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
