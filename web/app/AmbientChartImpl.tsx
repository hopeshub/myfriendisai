"use client";

import { useMemo, useState } from "react";
import {
  AreaChart,
  Area,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceDot,
} from "recharts";
import MeasuredChart from "@/app/MeasuredChart";
import type { AmbientTopPoint, AmbientStackPoint } from "./themeData";
import { measure } from "./styles";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

// ── §5 ambient-cluster chart ────────────────────────────────────────────────
// Two stacked panels, modeled on §1. Top: r/antiAI + r/aiwars — the two
// giants, within a couple percent of each other, both compounding fast since
// mid-2024. Bottom: a 5-band stacked composition of mid-tier subs that fills
// in around them — the cluster's organizing infrastructure forming room by
// room. r/trueantiAI (~50/mo) and r/ProAI (~40/mo) are too small to register
// as bands and are noted in the caption.
//
// Coloring is by sub identity (the §1 palette family), NOT by valence — the
// site doesn't score the culture war. The closer line under the chart lands
// the editorial point: the broad anti-AI movement is loud about everything
// except this site's subject.

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

// Companionship-discourse density from the 2026-05-20 scoping pass (50-post
// open-coding per sub). Shown in tooltip as a single italic line under each
// sub's monthly count — the editorial point that "% on companions" used to
// carry as a column.
const COMPANION_DENSITY: Record<string, number> = {
  antiAI: 6,
  aiwars: 2,
  ArtistHate: 2,
  AIDangers: 6,
  BetterOffline: 4,
  FuckAI: 0,
  DefendingAIArt: 0,
};

// Top panel — the two giants as parallel lines (not a stack; they're not
// composing a whole, they're independent communities tracking each other).
const TOP_LINES: { key: keyof AmbientTopPoint; label: string; color: string }[] = [
  { key: "antiAI", label: "r/antiAI", color: "#C99B5A" }, // warm tan
  { key: "aiwars", label: "r/aiwars", color: "#6E9BC4" }, // slate blue
];

// Bottom panel — declared bottom → top in the stacked composition. Largest
// & most-stable bands go on the bottom so the growing newer ones sit on top
// where they're easier to see.
type StackKey = keyof Omit<AmbientStackPoint, "month">;
const STACK_BANDS: { key: StackKey; label: string; color: string }[] = [
  { key: "ArtistHate",      label: "r/ArtistHate",      color: "#CC7E72" }, // coral
  { key: "DefendingAIArt",  label: "r/DefendingAIArt",  color: "#7BA98D" }, // sage
  { key: "BetterOffline",   label: "r/BetterOffline",   color: "#C77FA3" }, // pink
  { key: "FuckAI",          label: "r/FuckAI",          color: "#A98FC4" }, // lavender
  { key: "AIDangers",       label: "r/AIDangers",       color: "#D4A862" }, // amber
];
const STACK_LABEL: Record<string, string> = Object.fromEntries(
  STACK_BANDS.map((b) => [b.key, b.label]),
);

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

export default function AmbientChart({
  top,
  stack,
}: {
  top: AmbientTopPoint[];
  stack: AmbientStackPoint[];
}) {
  const reducedMotion = usePrefersReducedMotion();
  const animate = !reducedMotion;

  const [selected, setSelected] = useState<StackKey | null>(null);
  const toggle = (k: StackKey) => setSelected((s) => (s === k ? null : k));

  const ticks = useMemo(
    () => yearTicks(stack.map((d) => d.month)),
    [stack],
  );

  // Per-band label anchor: the data-space (x, y) point where the band's
  // in-chart label should sit. x = the month where the band is widest;
  // y = the cumulative midpoint of that band at that month (so the label
  // lands in the body of the colored band, not at the boundary above it).
  // Rendered via <ReferenceDot r={0} label={...} /> so Recharts handles
  // the data-to-pixel mapping.
  const anchors = useMemo(() => {
    type Anchor = { x: string; y: number; label: string; color: string };
    const out: Anchor[] = [];
    for (const b of STACK_BANDS) {
      let bestIdx = 0;
      let bestVal = -1;
      stack.forEach((p, i) => {
        const v = p[b.key];
        if (v > bestVal) {
          bestVal = v;
          bestIdx = i;
        }
      });
      if (bestVal <= 200) continue; // skip too-thin bands
      const point = stack[bestIdx];
      // Cumulative sum of all bands below b at this month, plus half of b.
      let cumulative = 0;
      for (const lower of STACK_BANDS) {
        if (lower.key === b.key) break;
        cumulative += point[lower.key];
      }
      out.push({
        x: point.month,
        y: cumulative + bestVal / 2,
        label: b.label,
        color: b.color,
      });
    }
    return out;
  }, [stack]);

  if (stack.length === 0 || top.length === 0) {
    return (
      <div
        style={{ height: 300 }}
        className="flex items-center justify-center text-sm text-[#7E8B9E]"
      >
        No ambient-cluster data yet.
      </div>
    );
  }

  const axisProps = {
    stroke: "#2A2D3A",
    tick: { fill: "#7E8B9E", fontSize: 11 },
    tickLine: false,
  };


  return (
    <div>
      {/* Top panel — the two giants, as parallel lines */}
      <div style={{ fontSize: 14, fontWeight: 600, color: "#F1F4F8" }}>
        The two giants
      </div>
      <div style={{ fontSize: 12, color: "#7E8B9E", marginBottom: 6 }}>
        r/antiAI and r/aiwars &mdash; the two largest, growing roughly in
        parallel since mid-2024.
      </div>
      <MeasuredChart
        style={{ height: 200 }}
        role="img"
        ariaLabel="Line chart: r/antiAI and r/aiwars monthly post volume from 2023 to 2026, both lines compounding past 3,000 posts per month."
      >
        {({ width, height }) => (
          <LineChart
            width={width}
            height={height}
            data={top}
            margin={{ top: 14, right: 12, bottom: 2, left: 0 }}
            accessibilityLayer={false}
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
              tick={{ fill: "#7E8B9E", fontSize: 11 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={fmtCount}
            />
            <Tooltip
              cursor={{ stroke: "#475569", strokeWidth: 1 }}
              animationDuration={140}
              content={({ active, payload, label }) => {
                if (!active || !payload?.length) return null;
                return (
                  <div style={tooltipBox}>
                    <div style={{ color: "#9AA7B8", marginBottom: 4 }}>
                      {fmtMonth(label as string)}
                    </div>
                    {payload.map((p) => {
                      const k = p.dataKey as string;
                      const density = COMPANION_DENSITY[k];
                      return (
                        <div
                          key={k}
                          style={{
                            color: "#C8D0DC",
                            lineHeight: 1.5,
                          }}
                        >
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
                          <span style={{ fontWeight: 600 }}>
                            r/{k}
                          </span>
                          <span style={{ color: "#9AA7B8" }}>{"  ·  "}</span>
                          <span style={{ fontWeight: 600 }}>
                            {((p.value as number) ?? 0).toLocaleString()}
                          </span>
                          <span style={{ color: "#9AA7B8" }}> posts</span>
                          {density != null && (
                            <div
                              style={{
                                color: "#7E8B9E",
                                fontStyle: "italic",
                                marginLeft: 13,
                                marginTop: 1,
                              }}
                            >
                              ~{density}% on AI companionship
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                );
              }}
            />
            {TOP_LINES.map((l) => (
              <Line
                key={l.key}
                type="monotone"
                dataKey={l.key}
                stroke={l.color}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 3, strokeWidth: 0 }}
                isAnimationActive={animate}
                animationDuration={700}
                animationEasing="ease-out"
              />
            ))}
          </LineChart>
        )}
      </MeasuredChart>
      {/* Top panel legend */}
      <div
        style={{
          fontSize: 11,
          color: "#7E8B9E",
          marginTop: 4,
          display: "flex",
          flexWrap: "wrap",
          gap: "4px 14px",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {TOP_LINES.map((l) => (
          <span
            key={l.key}
            style={{ display: "inline-flex", alignItems: "center", gap: 5 }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-block",
                width: 14,
                height: 2,
                backgroundColor: l.color,
              }}
            />
            <span style={{ color: "#C8D0DC" }}>{l.label}</span>
          </span>
        ))}
      </div>

      {/* Bottom panel — the rooms forming around them */}
      <div
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: "#F1F4F8",
          marginTop: 28,
        }}
      >
        The rooms forming around them
      </div>
      <div style={{ fontSize: 12, color: "#7E8B9E", marginBottom: 6 }}>
        Five smaller subs &mdash; some pre-existing, some founded mid-cluster
        &mdash; filling in below the giants.
      </div>
      <MeasuredChart
        style={{ height: 240 }}
        role="img"
        ariaLabel="Stacked area chart: monthly post volume of five mid-tier ambient subs — r/DefendingAIArt, r/BetterOffline, r/ArtistHate, r/AIDangers, r/FuckAI."
      >
        {({ width, height }) => (
          <AreaChart
            width={width}
            height={height}
            data={stack}
            margin={{ top: 6, right: 12, bottom: 2, left: 0 }}
            accessibilityLayer={false}
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
              tick={{ fill: "#7E8B9E", fontSize: 11 }}
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
                    {[...payload].reverse().map((p) => {
                      const k = p.dataKey as string;
                      const isSel = k === selected;
                      const density = COMPANION_DENSITY[k];
                      return (
                        <div
                          key={k}
                          style={{
                            color: isSel ? "#F1F4F8" : "#C8D0DC",
                            fontWeight: isSel ? 600 : 400,
                            opacity: selected !== null && !isSel ? 0.5 : 1,
                            lineHeight: 1.5,
                          }}
                        >
                          <div
                            style={{
                              display: "flex",
                              justifyContent: "space-between",
                              gap: 14,
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
                              {STACK_LABEL[k] ?? k}
                            </span>
                            <span style={{ fontWeight: 600 }}>
                              {((p.value as number) ?? 0).toLocaleString()}
                            </span>
                          </div>
                          {density != null && (
                            <div
                              style={{
                                color: "#7E8B9E",
                                fontStyle: "italic",
                                fontWeight: 400,
                                marginLeft: 13,
                                fontSize: 10,
                              }}
                            >
                              ~{density}% on AI companionship
                            </div>
                          )}
                        </div>
                      );
                    })}
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
            {STACK_BANDS.map((b) => {
              const dimmed = selected !== null && selected !== b.key;
              return (
                <Area
                  key={b.key}
                  type="monotone"
                  dataKey={b.key}
                  stackId="ambient"
                  stroke={b.color}
                  strokeWidth={selected === b.key ? 1.75 : 1}
                  strokeOpacity={dimmed ? 0.3 : 1}
                  fill={b.color}
                  fillOpacity={dimmed ? 0.08 : 0.82}
                  activeDot={false}
                  onClick={() => toggle(b.key)}
                  cursor="pointer"
                  isAnimationActive={animate}
                  animationDuration={700}
                  animationEasing="ease-out"
                />
              );
            })}
            {/* In-band labels: positioned at the data-space midpoint of each
                band at its widest month, so the label lands in the body of
                the colored band rather than at the boundary above it. */}
            {anchors.map((a) => {
              const isSelected = selected != null;
              const matchKey = STACK_BANDS.find(
                (b) => b.label === a.label,
              )?.key;
              const dimmed = isSelected && matchKey !== selected;
              return (
                <ReferenceDot
                  key={a.label}
                  x={a.x}
                  y={a.y}
                  r={0}
                  ifOverflow="extendDomain"
                  label={{
                    value: a.label,
                    fill: "#F8FAFC",
                    fontSize: 10,
                    fontWeight: 700,
                    stroke: "#0F1117",
                    strokeWidth: 3,
                    paintOrder: "stroke",
                    opacity: dimmed ? 0.15 : 0.95,
                    position: "center",
                  }}
                />
              );
            })}
          </AreaChart>
        )}
      </MeasuredChart>

      {/* Stack legend — click to isolate */}
      <div
        style={{
          marginTop: 10,
          display: "flex",
          flexWrap: "wrap",
          gap: "2px 8px",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        {STACK_BANDS.map((b) => {
          const dimmed = selected !== null && selected !== b.key;
          return (
            <button
              key={b.key}
              type="button"
              onClick={() => toggle(b.key)}
              aria-pressed={selected === b.key}
              style={{
                display: "inline-flex",
                alignItems: "center",
                gap: 5,
                fontSize: 11,
                color: "#9AA7B8",
                background: "none",
                border: "none",
                padding: "3px 4px",
                cursor: "pointer",
                opacity: dimmed ? 0.4 : 1,
                fontWeight: selected === b.key ? 600 : 400,
              }}
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
            </button>
          );
        })}
      </div>
      {selected !== null && (
        <div
          style={{
            marginTop: 2,
            textAlign: "center",
            fontSize: 11,
            color: "#7E8B9E",
          }}
        >
          Isolating {STACK_LABEL[selected]} &mdash;{" "}
          <button
            type="button"
            onClick={() => setSelected(null)}
            style={{
              background: "none",
              border: "none",
              color: "#9AA7B8",
              textDecoration: "underline",
              cursor: "pointer",
              fontSize: 11,
              padding: 0,
            }}
          >
            show all
          </button>
        </div>
      )}

      {/* Caption — the chart's editorial closer */}
      <p
        style={{
          fontSize: 13,
          lineHeight: 1.6,
          color: "#C8D0DC",
          marginTop: 16,
          textAlign: "center",
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
          fontStyle: "italic",
        }}
      >
        Half a million subscribers arguing about AI. Rarely about AI
        companionship &mdash; often about the kind of person who would.
      </p>

      <p
        style={{
          fontSize: 11,
          color: "#7E8B9E",
          marginTop: 8,
          textAlign: "center",
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        Monthly post volume. Each panel has its own scale; click a band to
        isolate it. The {"~"}% on AI companionship in each tooltip is from a
        50-post sample per sub (May 2026). Two small subs in the cluster
        &mdash; r/trueantiAI ({"~"}50 posts/mo) and r/ProAI ({"~"}40)
        &mdash; are too small to register as bands here but are in the
        community list.
      </p>
    </div>
  );
}
