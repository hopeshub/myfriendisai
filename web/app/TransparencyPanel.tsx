"use client";

import { useState } from "react";

// ─── Types ────────────────────────────────────────────────────────────────

type SamplePost = { title: string; subreddit: string; date: string; id: string };
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
  themeEmoji: string;
  themeTagline: string;
  themeColor: string;
  data: CategoryDetail;
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

function redditUrl(postId: string): string {
  return `https://www.reddit.com/comments/${postId}`;
}

/** Pick up to 3 diverse sample posts, one from each keyword where possible */
function pickSamples(keywords: KeywordEntry[]): SamplePost[] {
  const samples: SamplePost[] = [];
  const seen = new Set<string>();
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

// ─── Section header style ─────────────────────────────────────────────────

export { pickSamples };
export type { KeywordEntry, SamplePost, SubredditEntry };

export const sectionHeaderStyle: React.CSSProperties = {
  fontSize: 11,
  fontWeight: 500,
  textTransform: "uppercase",
  letterSpacing: "0.05em",
  color: "#8293A6",
  marginBottom: 8,
};

// ─── Sections ─────────────────────────────────────────────────────────────

export function KeywordsSection({
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
      <div style={sectionHeaderStyle}>Tracked keywords</div>
      <div className="space-y-1.5">
        {visible.map((kw) => (
          <div key={kw.term}>
            <div className="flex items-baseline justify-between mb-0.5">
              <span className="text-[13px]" style={{ color }}>
                {kw.term}
              </span>
              <span
                className="text-[12px] ml-2 flex-shrink-0"
                style={{ color: "#94A3B8" }}
              >
                {kw.hits.toLocaleString()}
              </span>
            </div>
            <div
              className="rounded-full"
              style={{ height: 5, backgroundColor: "#0F1117" }}
            >
              <div
                className="rounded-full"
                style={{
                  height: 5,
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
          style={{ color: "#8293A6" }}
        >
          {expanded ? "Show fewer" : `Show all ${keywords.length} keywords`}
        </button>
      )}
    </div>
  );
}

export function CommunitiesSection({
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
      <div style={sectionHeaderStyle}>Top communities</div>
      <div className="space-y-2">
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
        <div className="text-[12px] mt-2" style={{ color: "#8293A6" }}>
          and {remaining} more communities
        </div>
      )}
    </div>
  );
}

export function SamplePostsSection({ samples }: { samples: SamplePost[] }) {
  return (
    <div>
      <div style={sectionHeaderStyle}>Example posts</div>
      <div>
        {samples.map((sp, i) => (
          <div
            key={i}
            className="py-2"
            style={i > 0 ? { borderTop: "0.5px solid #1E293B" } : undefined}
          >
            <a
              href={redditUrl(sp.id)}
              target="_blank"
              rel="noopener noreferrer"
              className="text-[13px] hover:underline underline-offset-2 transition-colors"
              style={{ color: "#CBD5E1" }}
            >
              {truncate(sp.title, 100)}
            </a>
            <div className="text-[11px] mt-1" style={{ color: "#8293A6" }}>
              r/{sp.subreddit} &middot; {formatDate(sp.date)}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

// ─── Main component: right-edge side panel ────────────────────────────────

export default function TransparencyPanel({
  themeLabel,
  themeEmoji,
  themeTagline,
  themeColor,
  data,
  onClose,
}: Props) {
  const samples = pickSamples(data.keywords);

  return (
    <div
      className="side-panel fixed top-0 right-0 bottom-0 flex flex-col z-40"
      style={{
        width: "min(400px, 100vw)",
        backgroundColor: "#1A1D27",
        borderLeft: `3px solid ${themeColor}`,
        boxShadow: "-8px 0 24px rgba(0,0,0,0.4)",
      }}
    >
      {/* Header — sticky at top */}
      <div
        className="flex items-center justify-between px-5 py-3 flex-shrink-0"
        style={{ borderBottom: "0.5px solid #1E293B" }}
      >
        <div>
          <div className="text-[15px] font-medium" style={{ color: themeColor }}>
            {themeEmoji} {themeLabel}
          </div>
          <div className="text-[11px] mt-0.5" style={{ color: "#8293A6" }}>
            {themeTagline}
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-[20px] leading-none w-8 h-8 flex items-center justify-center rounded hover:text-foreground transition-colors"
          style={{ color: "#8293A6" }}
          aria-label="Close panel"
        >
          &times;
        </button>
      </div>

      {/* Scrollable content */}
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-5">
        <KeywordsSection keywords={data.keywords} color={themeColor} />
        <CommunitiesSection subreddits={data.subreddits} color={themeColor} />
        <SamplePostsSection samples={samples} />

        {/* Footer */}
        <div
          className="text-[11px] pt-2"
          style={{ color: "#8293A6", borderTop: "0.5px solid #1E293B" }}
        >
          {data.keywords.length} keywords across{" "}
          {data.subreddits.length} communities &middot;{" "}
          {data.unique_posts.toLocaleString()} posts matched &middot; All
          keywords validated at &ge;80% precision
        </div>
      </div>
    </div>
  );
}
