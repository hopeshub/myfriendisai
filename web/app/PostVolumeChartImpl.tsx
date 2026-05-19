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
import type { CaiPoint, CompositionPoint } from "./themeData";
import { measure } from "./styles";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

// ── §1 post-volume chart ─────────────────────────────────────────────────────
// Two stacked charts. Top: r/CharacterAI alone — it is 60-90% of all volume and
// would crush everything else on a shared scale. Bottom: every other
// companionship community as a stacked area, so the field's turnover is
// legible — r/replika's 2023 dominance collapsing while a new generation
// (Nomi, Kindroid, Chai, MyBoyfriendIsAI) rises to fill a roughly flat total.

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

// Stacked bands, declared bottom → top. r/replika sits at the bottom so its
// collapse reads against a clean baseline; "Other" is the catch-all on top.
type BandKey = keyof Omit<CompositionPoint, "month">;
type Band = { key: BandKey; label: string; color: string };
const BANDS: Band[] = [
  { key: "replika", label: "r/replika", color: "#C99B5A" },
  { key: "nomi", label: "r/NomiAI", color: "#7BA98D" },
  { key: "kindroid", label: "r/KindroidAI", color: "#A98FC4" },
  { key: "chai", label: "r/ChaiApp", color: "#6E9BC4" },
  { key: "chatgptcomplaints", label: "r/ChatGPTcomplaints", color: "#CC7E72" },
  { key: "myboyfriendisai", label: "r/MyBoyfriendIsAI", color: "#C77FA3" },
  { key: "other", label: "Other communities", color: "#525A6B" },
];
const BAND_LABEL: Record<string, string> = Object.fromEntries(
  BANDS.map((b) => [b.key, b.label]),
);

/** The first month of each calendar year — used for sparse x-axis ticks. */
function yearTicks(months: string[]): string[] {
  const seen = new Set<string>();
  const ticks: string[] = [];
  for (const m of months) {
    const y = m.slice(0, 4);
    if (!seen.has(y)) {
      seen.add(y);
      ticks.push(m);
    }
  }
  return ticks;
}

const tooltipBox: React.CSSProperties = {
  backgroundColor: "#0F1117",
  border: "1px solid #2A2D3A",
  borderRadius: 6,
  padding: "6px 9px",
  fontSize: 11,
};

export default function PostVolumeChart({
  characterai,
  composition,
}: {
  characterai: CaiPoint[];
  composition: CompositionPoint[];
}) {
  // Static chart — animates once on mount only.
  const reducedMotion = usePrefersReducedMotion();
  const animate = !reducedMotion;

  const ticks = useMemo(
    () => yearTicks(composition.map((d) => d.month)),
    [composition],
  );

  if (composition.length === 0) {
    return (
      <div
        style={{ height: 300 }}
        className="flex items-center justify-center text-sm text-[#6B7689]"
      >
        No post-volume data yet.
      </div>
    );
  }

  const axisProps = {
    stroke: "#2A2D3A",
    tick: { fill: "#6B7689", fontSize: 11 },
    tickLine: false,
  };

  return (
    <div>
      {/* r/CharacterAI — on its own scale */}
      <div style={{ fontSize: 14, fontWeight: 600, color: "#F1F4F8" }}>
        r/CharacterAI
      </div>
      <div style={{ fontSize: 12, color: "#6B7689", marginBottom: 6 }}>
        The mass-market giant — boomed past 40k posts a month, then receded.
      </div>
      <div style={{ height: 132 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={characterai}
            margin={{ top: 6, right: 8, bottom: 2, left: 0 }}
          >
            <defs>
              <linearGradient id="pv-cai" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor="#566173" stopOpacity={0.45} />
                <stop offset="100%" stopColor="#566173" stopOpacity={0.04} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" vertical={false} />
            <XAxis
              dataKey="month"
              ticks={ticks}
              interval={0}
              tickFormatter={(m: string) => m.slice(0, 4)}
              axisLine={{ stroke: "#2A2D3A" }}
              {...axisProps}
            />
            <YAxis
              width={40}
              stroke="transparent"
              tick={{ fill: "#6B7689", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={fmtCount}
            />
            <Tooltip
              cursor={{ stroke: "#475569", strokeWidth: 1 }}
              animationDuration={140}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length || payload[0].value == null) {
                  return null;
                }
                return (
                  <div style={{ ...tooltipBox, whiteSpace: "nowrap" }}>
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
              stroke="#566173"
              strokeWidth={2}
              fill="url(#pv-cai)"
              isAnimationActive={animate}
              animationDuration={700}
              animationEasing="ease-out"
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Every other community — stacked composition */}
      <div
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: "#F1F4F8",
          marginTop: 20,
        }}
      >
        Every other community
      </div>
      <div style={{ fontSize: 12, color: "#6B7689", marginBottom: 6 }}>
        A roughly flat total &mdash; but watch r/replika give way to a new
        generation.
      </div>
      <div style={{ height: 264 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart
            data={composition}
            margin={{ top: 6, right: 8, bottom: 2, left: 0 }}
          >
            <CartesianGrid strokeDasharray="3 3" stroke="#2A2D3A" vertical={false} />
            <XAxis
              dataKey="month"
              ticks={ticks}
              interval={0}
              tickFormatter={(m: string) => m.slice(0, 4)}
              axisLine={{ stroke: "#2A2D3A" }}
              {...axisProps}
            />
            <YAxis
              width={40}
              stroke="transparent"
              tick={{ fill: "#6B7689", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={fmtCount}
            />
            <Tooltip
              cursor={{ stroke: "#475569", strokeWidth: 1 }}
              animationDuration={140}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                const total = payload.reduce(
                  (s, p) => s + ((p.value as number) ?? 0),
                  0,
                );
                return (
                  <div style={tooltipBox}>
                    <div style={{ color: "#9AA7B8", marginBottom: 4 }}>
                      {fmtMonth(label as string)}
                    </div>
                    {[...payload].reverse().map((p) => (
                      <div
                        key={p.dataKey as string}
                        style={{
                          display: "flex",
                          justifyContent: "space-between",
                          gap: 14,
                          color: "#C8D0DC",
                          lineHeight: 1.5,
                        }}
                      >
                        <span>
                          <span
                            style={{
                              display: "inline-block",
                              width: 8,
                              height: 8,
                              borderRadius: 2,
                              backgroundColor: p.color,
                              marginRight: 5,
                            }}
                          />
                          {BAND_LABEL[p.dataKey as string] ?? p.dataKey}
                        </span>
                        <span style={{ fontWeight: 600 }}>
                          {((p.value as number) ?? 0).toLocaleString()}
                        </span>
                      </div>
                    ))}
                    <div
                      style={{
                        borderTop: "1px solid #2A2D3A",
                        marginTop: 4,
                        paddingTop: 4,
                        display: "flex",
                        justifyContent: "space-between",
                        gap: 14,
                        color: "#9AA7B8",
                      }}
                    >
                      <span>Total</span>
                      <span>{total.toLocaleString()}</span>
                    </div>
                  </div>
                );
              }}
            />
            {BANDS.map((b) => (
              <Area
                key={b.key}
                type="monotone"
                dataKey={b.key}
                stackId="composition"
                stroke={b.color}
                strokeWidth={1}
                fill={b.color}
                fillOpacity={0.8}
                isAnimationActive={animate}
                animationDuration={700}
                animationEasing="ease-out"
              />
            ))}
          </AreaChart>
        </ResponsiveContainer>
      </div>

      {/* Legend for the stacked bands */}
      <div
        style={{
          marginTop: 10,
          display: "flex",
          flexWrap: "wrap",
          gap: "4px 14px",
          justifyContent: "center",
          fontSize: 11,
          color: "#9AA7B8",
        }}
      >
        {BANDS.map((b) => (
          <span
            key={b.key}
            style={{ display: "inline-flex", alignItems: "center", gap: 5 }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-block",
                width: 9,
                height: 9,
                borderRadius: 2,
                backgroundColor: b.color,
              }}
            />
            {b.label}
          </span>
        ))}
      </div>

      <p
        style={{
          fontSize: 11,
          color: "#6B7689",
          marginTop: 8,
          textAlign: "center",
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        Monthly post volume, from 2023 onward (where monthly counts become
        reliable). Each chart has its own scale.
      </p>
    </div>
  );
}
