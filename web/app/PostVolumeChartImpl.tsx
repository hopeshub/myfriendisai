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
  ReferenceLine,
} from "recharts";
import type { PostVolumeSplitPoint } from "./themeData";
import { measure } from "./styles";
import { usePrefersReducedMotion } from "@/lib/usePrefersReducedMotion";

// ── Post-volume chart ────────────────────────────────────────────────────────
// Two panels, each on its OWN y-scale: r/CharacterAI, and every other tracked
// community. They are deliberately not stacked or on a shared axis —
// CharacterAI is so much larger that a shared scale flattens the second panel
// into an unreadable sliver. Separate scales let each be read on its own terms.
//
// The chart begins in 2023. The post corpus reaches back to 2017, but the
// 2017-2022 years are sparse and partly archive-gapped — shown earlier as a
// large shaded "patchy coverage" block that dominated the chart. Cropping to
// the reliable era is cleaner and more honest than rendering two-thirds of the
// chart as untrustworthy; the corpus extent is noted in the caption instead.
//
// The CharacterAI panel carries numbered event markers — the platform changes
// behind its surge and fall — so the §1 thesis ("one platform's lifecycle, not
// the category's") is legible on the chart itself, not only in the prose.

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

/** Every "YYYY-MM" from start to end inclusive. */
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

// The chart starts here — the first month from which monthly post counts are
// reliable. Earlier data exists in the corpus but is sparse / archive-gapped.
const CHART_START = "2023-01";

// r/CharacterAI's platform timeline — the events behind the surge and fall.
type ChartEvent = { month: string; label: string };
const CAI_EVENTS: ChartEvent[] = [
  { month: "2024-10", label: "Lawsuit filed" },
  { month: "2025-10", label: "New under-18 limits" },
];

type PanelRow = { month: string; value: number | null };

function VolumePanel({
  title,
  caption,
  rows,
  yearTicks,
  color,
  gradientId,
  events,
  animate,
}: {
  title: string;
  caption: string;
  rows: PanelRow[];
  yearTicks: string[];
  color: string;
  gradientId: string;
  events?: ChartEvent[];
  animate: boolean;
}) {
  return (
    <div>
      <div style={{ fontSize: 14, fontWeight: 600, color: "#F1F4F8" }}>
        {title}
      </div>
      <div style={{ fontSize: 12, color: "#6B7689", marginBottom: 6 }}>
        {caption}
      </div>
      <div style={{ height: 200 }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={rows} margin={{ top: 20, right: 8, bottom: 2, left: 0 }}>
            <defs>
              <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stopColor={color} stopOpacity={0.5} />
                <stop offset="100%" stopColor={color} stopOpacity={0.04} />
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
              animationEasing="ease-out"
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
              stroke={color}
              strokeWidth={2}
              fill={`url(#${gradientId})`}
              connectNulls={false}
              isAnimationActive={animate}
              animationDuration={700}
              animationEasing="ease-out"
            />
            {/* Numbered platform-event markers — named in the legend below. */}
            {events?.map((ev, i) => (
              <ReferenceLine
                key={ev.month}
                x={ev.month}
                stroke="#C2974D"
                strokeOpacity={0.55}
                strokeDasharray="4 3"
                strokeWidth={1}
                label={{
                  value: String(i + 1),
                  position: "top",
                  fill: "#D4A862",
                  fontSize: 11,
                  fontWeight: 700,
                }}
              />
            ))}
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
  // No time-range/scope toggle on this chart — animates once on mount only.
  const reducedMotion = usePrefersReducedMotion();

  const { caiRows, otherRows, yearTicks } = useMemo(() => {
    // Crop to the reliable era — 2023 onward.
    const cropped = data.filter((d) => d.month >= CHART_START);
    if (cropped.length === 0) {
      return {
        caiRows: [] as PanelRow[],
        otherRows: [] as PanelRow[],
        yearTicks: [] as string[],
      };
    }
    const lookup: Record<string, PostVolumeSplitPoint> = {};
    for (const d of cropped) lookup[d.month] = d;

    const months = monthRange(cropped[0].month, cropped[cropped.length - 1].month);
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

    return { caiRows, otherRows, yearTicks: ticks };
  }, [data]);

  if (caiRows.length === 0) {
    return (
      <div
        style={{ height: 220 }}
        className="flex items-center justify-center text-sm text-[#6B7689]"
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
          color="#566173"
          gradientId="pv-cai"
          events={CAI_EVENTS}
          animate={!reducedMotion}
        />
        <VolumePanel
          title="Every other tracked community"
          caption="Held roughly steady, with spikes at platform events."
          rows={otherRows}
          yearTicks={yearTicks}
          color="#7C9CD0"
          gradientId="pv-other"
          animate={!reducedMotion}
        />
      </div>

      {/* Legend for the r/CharacterAI panel's numbered event markers. */}
      <div
        style={{
          fontSize: 11,
          color: "#6B7689",
          marginTop: 10,
          display: "flex",
          flexWrap: "wrap",
          gap: "4px 14px",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <span style={{ textTransform: "uppercase", letterSpacing: "0.05em" }}>
          r/CharacterAI
        </span>
        {CAI_EVENTS.map((ev, i) => (
          <span
            key={ev.month}
            style={{ display: "inline-flex", alignItems: "center", gap: 5 }}
          >
            <span
              aria-hidden
              style={{
                display: "inline-flex",
                alignItems: "center",
                justifyContent: "center",
                width: 15,
                height: 15,
                borderRadius: 999,
                fontSize: 10,
                fontWeight: 700,
                color: "#0F1117",
                backgroundColor: "#C2974D",
              }}
            >
              {i + 1}
            </span>
            <span style={{ color: "#C8D0DC" }}>{ev.label}</span>
            <span>{fmtMonth(ev.month)}</span>
          </span>
        ))}
      </div>

      <p
        style={{
          fontSize: 11,
          color: "#6B7689",
          marginTop: 6,
          textAlign: "center",
          maxWidth: measure,
          marginLeft: "auto",
          marginRight: "auto",
        }}
      >
        The chart begins in 2023, where monthly counts become reliable &mdash;
        the post record itself reaches back to 2017. Each panel has its own
        scale: for years, r/CharacterAI alone was 75&ndash;90% of every post
        counted here.
      </p>
    </div>
  );
}
