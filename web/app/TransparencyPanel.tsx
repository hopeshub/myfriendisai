"use client";

import { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────

type SamplePost = { title: string; subreddit: string; date: string };
type KeywordEntry = {
  term: string;
  hits: number;
  precision: number | null;
  sample_posts: SamplePost[];
};
type SubredditEntry = { name: string; hits: number; pct: number };

export type CategoryDetail = {
  keywords: KeywordEntry[];
  subreddits: SubredditEntry[];
  total_hits: number;
  unique_posts: number;
};

export type KeywordDetailsData = Record<string, CategoryDetail>;

type Props = {
  themeId: string;
  themeLabel: string;
  themeColor: string;
  data: CategoryDetail;
  breakpoint: "mobile" | "tablet" | "desktop";
  onClose: () => void;
};

// ─── Helpers ──────────────────────────────────────────────────────────────

const MONTH_NAMES = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function formatDate(dateStr: string): string {
  const d = new Date(dateStr + "T00:00:00Z");
  return `${MONTH_NAMES[d.getUTCMonth()]} ${d.getUTCFullYear()}`;
}

function truncate(str: string, max: number): string {
  return str.length > max ? str.slice(0, max).trimEnd() + "\u2026" : str;
}

/** Pick up to 3 diverse sample posts, one from each keyword where possible */
function pickSamples(keywords: KeywordEntry[]): SamplePost[] {
  const samples: SamplePost[] = [];
  const seen = new Set<string>();
  // First pass: one per keyword
  for (const kw of keywords) {
    if (samples.length >= 3) break;
    for (const sp of kw.sample_posts) {
      if (!seen.has(sp.title)) {
        samples.push(sp);
        seen.add(sp.title);
        break;
      }
    }
  }
  // Second pass: fill remaining from any keyword
  if (samples.length < 3) {
    for (const kw of keywords) {
      for (const sp of kw.sample_posts) {
        if (samples.length >= 3) break;
        if (!seen.has(sp.title)) {
          samples.push(sp);
          seen.add(sp.title);
        }
      }
      if (samples.length >= 3) break;
    }
  }
  return samples;
}

// ─── Subcomponents ────────────────────────────────────────────────────────

function KeywordsColumn({
  keywords,
  color,
}: {
  keywords: KeywordEntry[];
  color: string;
}) {
  const [expanded, setExpanded] = useState(false);
  const maxHits = keywords.length > 0 ? keywords[0].hits : 1;
  const visible = expanded ? keywords : keywords.slice(0, 8);
  const hasMore = keywords.length > 8;

  return (
    <div>
      <div
        className="text-[12px] font-medium mb-3"
        style={{
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "#64748B",
        }}
      >
        Tracked keywords
      </div>
      <div className="space-y-2">
        {visible.map((kw) => (
          <div key={kw.term}>
            <div className="flex items-baseline justify-between mb-0.5">
              <span className="text-[14px]" style={{ color }}>
                {kw.term}
              </span>
              <span
                className="text-[13px] ml-2 flex-shrink-0"
                style={{ color: "#94A3B8" }}
              >
                {kw.hits.toLocaleString()}
              </span>
            </div>
            <div
              className="rounded-full"
              style={{ height: 6, backgroundColor: "#0F1117" }}
            >
              <div
                className="rounded-full"
                style={{
                  height: 6,
                  width: `${(kw.hits / maxHits) * 100}%`,
                  backgroundColor: color,
                  opacity: 0.3,
                }}
              />
            </div>
          </div>
        ))}
      </div>
      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="text-[12px] mt-2 hover:text-foreground transition-colors"
          style={{ color: "#64748B" }}
        >
          {expanded
            ? "Show fewer"
            : `Show all ${keywords.length} keywords`}
        </button>
      )}
    </div>
  );
}

function CommunitiesColumn({
  subreddits,
  color,
}: {
  subreddits: SubredditEntry[];
  color: string;
}) {
  const visible = subreddits.slice(0, 6);
  const remaining = subreddits.length - 6;

  return (
    <div>
      <div
        className="text-[12px] font-medium mb-3"
        style={{
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "#64748B",
        }}
      >
        Top communities
      </div>
      <div className="space-y-2.5">
        {visible.map((sub) => (
          <div key={sub.name}>
            <div className="flex items-baseline justify-between mb-0.5">
              <span className="text-[13px]" style={{ color: "#CBD5E1" }}>
                r/{sub.name}
              </span>
              <span
                className="text-[12px] ml-2 flex-shrink-0"
                style={{ color: "#94A3B8" }}
              >
                {sub.pct}%
              </span>
            </div>
            <div
              className="rounded-full"
              style={{ height: 4, backgroundColor: "#0F1117" }}
            >
              <div
                className="rounded-full"
                style={{
                  height: 4,
                  width: `${sub.pct}%`,
                  backgroundColor: color,
                  opacity: 0.2,
                }}
              />
            </div>
          </div>
        ))}
      </div>
      {remaining > 0 && (
        <div className="text-[12px] mt-2" style={{ color: "#64748B" }}>
          and {remaining} more communities
        </div>
      )}
    </div>
  );
}

function SamplePostsColumn({ samples }: { samples: SamplePost[] }) {
  return (
    <div>
      <div
        className="text-[12px] font-medium mb-3"
        style={{
          textTransform: "uppercase",
          letterSpacing: "0.05em",
          color: "#64748B",
        }}
      >
        Example posts
      </div>
      <div>
        {samples.map((sp, i) => (
          <div
            key={i}
            className="py-2.5"
            style={
              i > 0
                ? { borderTop: "0.5px solid #1E293B" }
                : undefined
            }
          >
            <div className="text-[13px]" style={{ color: "#CBD5E1" }}>
              {truncate(sp.title, 80)}
            </div>
            <div className="text-[11px] mt-1" style={{ color: "#64748B" }}>
              r/{sp.subreddit} &middot; {formatDate(sp.date)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

function PanelFooter({ data }: { data: CategoryDetail }) {
  return (
    <div
      className="text-[11px] mt-4 pt-3"
      style={{ color: "#64748B", borderTop: "0.5px solid #1E293B" }}
    >
      Showing {data.keywords.length} keywords across{" "}
      {data.subreddits.length} communities &middot;{" "}
      {data.unique_posts.toLocaleString()} total posts matched &middot; All
      keywords validated at &ge;80% precision
    </div>
  );
}

// ─── Panel content (shared between desktop/tablet inline and mobile drawer) ─

function PanelContent({
  data,
  color,
  breakpoint,
}: {
  data: CategoryDetail;
  color: string;
  breakpoint: "mobile" | "tablet" | "desktop";
}) {
  const samples = pickSamples(data.keywords);

  if (breakpoint === "mobile") {
    return (
      <div className="space-y-6">
        <KeywordsColumn keywords={data.keywords} color={color} />
        <CommunitiesColumn subreddits={data.subreddits} color={color} />
        <SamplePostsColumn samples={samples} />
        <PanelFooter data={data} />
      </div>
    );
  }

  if (breakpoint === "tablet") {
    return (
      <>
        <div className="grid grid-cols-2 gap-6">
          <div className="space-y-6">
            <KeywordsColumn keywords={data.keywords} color={color} />
            <CommunitiesColumn subreddits={data.subreddits} color={color} />
          </div>
          <SamplePostsColumn samples={samples} />
        </div>
        <PanelFooter data={data} />
      </>
    );
  }

  // Desktop: three columns
  return (
    <>
      <div className="grid grid-cols-3 gap-6">
        <KeywordsColumn keywords={data.keywords} color={color} />
        <CommunitiesColumn subreddits={data.subreddits} color={color} />
        <SamplePostsColumn samples={samples} />
      </div>
      <PanelFooter data={data} />
    </>
  );
}

// ─── Main component ───────────────────────────────────────────────────────

export default function TransparencyPanel({
  themeId,
  themeLabel,
  themeColor,
  data,
  breakpoint,
  onClose,
}: Props) {
  // Mobile: bottom drawer with overlay
  if (breakpoint === "mobile") {
    return (
      <div className="fixed inset-0 z-50">
        {/* Backdrop */}
        <div
          className="absolute inset-0"
          style={{ backgroundColor: "rgba(0,0,0,0.4)" }}
          onClick={onClose}
        />
        {/* Drawer */}
        <div
          className="absolute bottom-0 left-0 right-0 rounded-t-xl overflow-y-auto"
          style={{
            backgroundColor: "#1A1D27",
            borderTop: "1px solid #2A2D3A",
            borderLeft: `3px solid ${themeColor}`,
            maxHeight: "70vh",
            animation: "slideUp 200ms ease-out",
          }}
        >
          {/* Fixed header */}
          <div
            className="sticky top-0 flex items-center justify-between px-4 py-3 z-10"
            style={{
              backgroundColor: "#1A1D27",
              borderBottom: "0.5px solid #1E293B",
            }}
          >
            <span
              className="text-[14px] font-medium"
              style={{ color: themeColor }}
            >
              {themeLabel}
            </span>
            <button
              onClick={onClose}
              className="text-[18px] leading-none px-1 hover:text-foreground transition-colors"
              style={{ color: "#64748B" }}
              aria-label="Close panel"
            >
              &times;
            </button>
          </div>
          <div className="px-4 py-4">
            <PanelContent
              data={data}
              color={themeColor}
              breakpoint={breakpoint}
            />
          </div>
        </div>
      </div>
    );
  }

  // Desktop / Tablet: inline panel
  return (
    <div
      className="rounded-lg overflow-hidden mb-4"
      style={{
        backgroundColor: "#1A1D27",
        border: "0.5px solid #2A2D3A",
        borderLeft: `3px solid ${themeColor}`,
      }}
    >
      <div className="relative px-5 py-4" style={{ maxHeight: breakpoint === "tablet" ? 400 : 320, overflowY: "auto" }}>
        {/* Close button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 text-[16px] leading-none px-1 hover:text-foreground transition-colors"
          style={{ color: "#64748B" }}
          aria-label="Close panel"
        >
          &times;
        </button>
        <PanelContent
          data={data}
          color={themeColor}
          breakpoint={breakpoint}
        />
      </div>
    </div>
  );
}
