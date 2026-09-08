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
// room. r/trueantiAI and r/ProAI (both under 200/mo) are too small to
// register as bands and are noted in the caption.
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

// Top panel — r/aiwars alone. It's the explicit all-sides debate floor,
// structurally different from the partisan rooms below: not a side, the
// arena. Splitting it off keeps that distinction visible.
const TOP_LINES: { key: keyof AmbientTopPoint; label: string; color: string }[] = [
  { key: "aiwars", label: "r/aiwars", color: "#6E9BC4" }, // slate blue
];

// Bottom panel — every partisan room, stacked. r/antiAI sits at the bottom
// because it's the largest current band (started 2025 from zero and is now
// the cluster's biggest single growth story); building the stack on top of
// it lets the smaller subs sit above its growth curve where they're legible.
type StackKey = keyof Omit<AmbientStackPoint, "month">;
const STACK_BANDS: { key: StackKey; label: string; color: string }[] = [
  { key: "antiAI",          label: "r/antiAI",          color: "#C99B5A" }, // warm tan
  { key: "ArtistHate",      label: "r/ArtistHate",      color: "#CC7E72" }, // coral
  { key: "DefendingAIArt",  label: "r/DefendingAIArt",  color: "#7BA98D" }, // sage
  { key: "BetterOffline",   label: "r/BetterOffline",   color: "#C77FA3" }, // pink
  { key: "FuckAI",          label: "r/FuckAI",          color: "#A98FC4" }, // lavender
  { key: "AIDangers",       label: "r/AIDangers",       color: "#D4A862" }, // amber
];
const STACK_LABEL: Record<string, string> = Object.fromEntries(
  STACK_BANDS.map((b) => [b.key, b.label]),
);

// ── In-band label geometry ───────────────────────────────────────────────────
// The stacked panel's fixed box, and the plot area inside it once the chart
// margins and the x-axis strip are taken out. Used to turn a pixel gap between
// two labels into the data-space distance a ReferenceDot needs.
const STACK_PANEL_HEIGHT = 240;
const STACK_PLOT_HEIGHT = 210;
const LABEL_LINE_PX = 13;
// Chart margins that bound the plot horizontally: the y-axis reserve on the
// left and the AreaChart's right margin.
const Y_AXIS_WIDTH = 40;
const PLOT_RIGHT_MARGIN = 12;
// Rough advance width of the 10px bold label face, per character.
const LABEL_CHAR_PX = 5.4;

/**
 * Where to hang one in-band label so it stays inside the plot. Recharts places
 * a ReferenceDot label from `position`: "center" centers it on the point,
 * "left"/"right" hang it off the point with the matching text anchor. A label
 * whose centered box would cross either edge of the plot gets hung inward
 * instead. `chartWidth` is the measured pixel width of the whole panel.
 */
function labelPosition(
  idx: number,
  lastIdx: number,
  label: string,
  chartWidth: number,
): "center" | "left" | "right" {
  const plotLeft = Y_AXIS_WIDTH;
  const plotRight = chartWidth - PLOT_RIGHT_MARGIN;
  const plotWidth = plotRight - plotLeft;
  if (plotWidth <= 0 || lastIdx <= 0) return "center";
  const x = plotLeft + (idx / lastIdx) * plotWidth;
  const halfLabel = (label.length * LABEL_CHAR_PX) / 2;
  if (x + halfLabel > plotRight) return "left";
  if (x - halfLabel < plotLeft) return "right";
  return "center";
}

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
  //
  // Three of the six bands are widest in the newest month, which put their
  // labels half off the right edge and stacked two of them on top of each
  // other. Two corrections below: `idx` travels with each anchor so the
  // renderer can right-anchor a label that would overflow, and labels that
  // land at nearly the same x are pushed apart vertically.
  const anchors = useMemo(() => {
    type Anchor = {
      x: string;
      idx: number;
      y: number;
      label: string;
      color: string;
    };
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
        idx: bestIdx,
        y: cumulative + bestVal / 2,
        label: b.label,
        color: b.color,
      });
    }

    // De-collide vertically. Labels far apart horizontally can never collide,
    // so only anchors within NEAR_X months of each other are compared. The
    // minimum gap is a pixel distance converted to data units through the
    // panel's plot height and the tallest stacked total — approximate (the
    // real axis rounds its max up to a tick), which errs toward more room.
    const NEAR_X = Math.max(2, Math.round(stack.length * 0.12));
    const tallest = Math.max(
      1,
      ...stack.map((p) => STACK_BANDS.reduce((s, b) => s + p[b.key], 0)),
    );
    const minGap = (LABEL_LINE_PX / STACK_PLOT_HEIGHT) * tallest;
    out.sort((a, b) => a.y - b.y);
    for (let i = 1; i < out.length; i++) {
      const prev = out[i - 1];
      if (
        Math.abs(out[i].idx - prev.idx) <= NEAR_X &&
        out[i].y - prev.y < minGap
      ) {
        out[i].y = prev.y + minGap;
      }
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
      {/* Top panel — r/aiwars alone (the explicit debate floor) */}
      <div style={{ fontSize: 14, fontWeight: 600, color: "#F1F4F8" }}>
        The debate floor
      </div>
      <div style={{ fontSize: 12, color: "#7E8B9E", marginBottom: 6 }}>
        r/aiwars &mdash; the only sub in the cluster whose charter is
        all-sides, not a side. Growing on the same curve as the partisans.
      </div>
      <MeasuredChart
        style={{ height: 200 }}
        role="img"
        ariaLabel="Line chart: r/aiwars monthly post volume from 2023 to 2026, compounding past 3,000 posts per month."
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

      {/* Bottom panel — every partisan room, stacked */}
      <div
        style={{
          fontSize: 14,
          fontWeight: 600,
          color: "#F1F4F8",
          marginTop: 28,
        }}
      >
        The partisan rooms
      </div>
      <div style={{ fontSize: 12, color: "#7E8B9E", marginBottom: 6 }}>
        The cluster&apos;s six anti-AI and two pro-AI subs; the six largest
        are stacked here. r/antiAI (founded 2025) is now the largest; the
        others fill in around it.
      </div>
      <MeasuredChart
        style={{ height: STACK_PANEL_HEIGHT }}
        role="img"
        ariaLabel="Stacked area chart: monthly post volume of the partisan ambient subs — r/antiAI, r/ArtistHate, r/DefendingAIArt, r/BetterOffline, r/FuckAI, r/AIDangers — with r/antiAI as the dominant band growing from zero in early 2025."
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
                the colored band rather than at the boundary above it. A
                label whose box would cross the plot edge hangs inward from
                its point instead of straddling it. */}
            {anchors.map((a) => {
              const isSelected = selected != null;
              const matchKey = STACK_BANDS.find(
                (b) => b.label === a.label,
              )?.key;
              const dimmed = isSelected && matchKey !== selected;
              const position = labelPosition(
                a.idx,
                stack.length - 1,
                a.label,
                width,
              );
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
                    position,
                    offset: position === "center" ? 0 : 4,
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
        &mdash; r/trueantiAI and r/ProAI, both under 200 posts a month
        &mdash; are too small to register as bands here, but they are in the
        community list.
      </p>
    </div>
  );
}
