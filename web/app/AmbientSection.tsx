// ── Ambient / Discourse-climate section (homepage §5) ───────────────────────
// Server component. The section's eyebrow, heading, and intro live in
// page.tsx (matching §1/§2/§4); this renders the roster + closing note.
//
// The editorial point: the broad AI culture war on Reddit is loud, but
// almost none of it touches AI companionship. The companionship-density
// column shows that absence as the finding. The only place sustained
// critique of AI companions happens is in §4 above (the recovery cluster).
//
// Tracked as CONTEXT only — these subs are excluded from every keyword
// measurement (see the LOCKED criterion in CLAUDE.md §2.1 + the scoping
// doc). Read engagement, not opinion.

import { getCommunityActivity, getSubreddits } from "@/lib/data";
import type { SubredditSummary } from "@/lib/types";
import Sparkline from "./communities/Sparkline";
import { measure } from "./styles";

// Companionship-discourse density from the 2026-05-20 scoping pass
// (50-post open-coding per sub). The number is the editorial point: even
// the loudest anti-AI sub only touches AI companionship in ~6% of posts.
const COMPANIONSHIP_DENSITY: Record<string, number> = {
  antiAI: 6,
  aiwars: 2,
  ArtistHate: 2,
  AIDangers: 6,
  BetterOffline: 4,
  FuckAI: 0,
  trueantiAI: 0,
  DefendingAIArt: 0,
  ProAI: 2,
};

const GROUP_ORDER = [
  "Ambient — Anti-AI",
  "Ambient — Debate Arena",
  "Ambient — Pro-AI",
] as const;

const GROUP_LABEL: Record<string, string> = {
  "Ambient — Anti-AI": "Anti-AI",
  "Ambient — Debate Arena": "Debate arena",
  "Ambient — Pro-AI": "Pro-AI",
};

function fmtSubs(n: number | null): string {
  if (n == null) return "—";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 10_000) return `${Math.round(n / 1_000)}K`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return n.toLocaleString("en-US");
}

function densityCell(sub: string): { label: string; muted: boolean } {
  const v = COMPANIONSHIP_DENSITY[sub];
  if (v == null) return { label: "—", muted: true };
  return { label: `${v}%`, muted: v === 0 };
}

export default function AmbientSection() {
  const all = getSubreddits();
  const activity = getCommunityActivity();
  const t4 = all.filter((s) => s.tier === 4);

  // Group by category, sort by subscribers descending within each group.
  const byGroup = new Map<string, SubredditSummary[]>();
  for (const s of t4) {
    const cat = s.category ?? "Other";
    if (!byGroup.has(cat)) byGroup.set(cat, []);
    byGroup.get(cat)!.push(s);
  }
  for (const list of byGroup.values()) {
    list.sort((a, b) => (b.subscribers ?? 0) - (a.subscribers ?? 0));
  }

  return (
    <div>
      <div
        role="table"
        aria-label="Ambient AI discourse communities"
        style={{
          border: "1px solid #2A2D3A",
          borderRadius: 8,
          overflow: "hidden",
          marginBottom: 16,
        }}
      >
        {/* Column header */}
        <div
          role="row"
          style={{
            display: "grid",
            gridTemplateColumns: "minmax(0,1fr) 70px 90px 88px",
            gap: 12,
            padding: "10px 14px",
            fontSize: 11,
            textTransform: "uppercase",
            letterSpacing: "0.04em",
            color: "#7E8B9E",
            backgroundColor: "#15171E",
            borderBottom: "1px solid #2A2D3A",
          }}
        >
          <span>Community</span>
          <span style={{ textAlign: "right" }}>Subs</span>
          <span style={{ textAlign: "right" }} title="Share of recent posts where AI companionship was the primary topic (50-post sample per sub, May 2026)">
            % on companions
          </span>
          <span style={{ textAlign: "right" }}>Trend</span>
        </div>

        {GROUP_ORDER.map((groupKey) => {
          const subs = byGroup.get(groupKey) ?? [];
          if (subs.length === 0) return null;
          return (
            <div key={groupKey} role="rowgroup">
              {/* Group header */}
              <div
                role="row"
                style={{
                  padding: "10px 14px 6px",
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#C8D0DC",
                  backgroundColor: "#0F1117",
                  borderTop: "1px solid #2A2D3A",
                }}
              >
                {GROUP_LABEL[groupKey] ?? groupKey}
              </div>
              {subs.map((s) => {
                const series = activity.activity[s.subreddit] ?? [];
                const density = densityCell(s.subreddit);
                return (
                  <div
                    key={s.subreddit}
                    role="row"
                    style={{
                      display: "grid",
                      gridTemplateColumns: "minmax(0,1fr) 70px 90px 88px",
                      gap: 12,
                      alignItems: "center",
                      padding: "10px 14px",
                      borderTop: "1px solid #1A1D27",
                      fontSize: 13,
                    }}
                  >
                    <a
                      href={`/communities/${s.subreddit}`}
                      style={{
                        color: "#F1F4F8",
                        textDecoration: "none",
                        fontWeight: 500,
                      }}
                    >
                      r/{s.subreddit}
                    </a>
                    <span
                      style={{
                        textAlign: "right",
                        color: "#9AA7B8",
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {fmtSubs(s.subscribers)}
                    </span>
                    <span
                      style={{
                        textAlign: "right",
                        color: density.muted ? "#5A6478" : "#C8D0DC",
                        fontVariantNumeric: "tabular-nums",
                      }}
                    >
                      {density.label}
                    </span>
                    <span
                      style={{
                        display: "flex",
                        justifyContent: "flex-end",
                      }}
                    >
                      <Sparkline values={series} />
                    </span>
                  </div>
                );
              })}
            </div>
          );
        })}
      </div>

      {/* Closing editorial / disclosure paragraph */}
      <p
        style={{
          fontSize: 13,
          lineHeight: 1.7,
          color: "#9AA7B8",
          maxWidth: measure,
        }}
      >
        <span style={{ color: "#F1F4F8", fontWeight: 600 }}>
          What this is and isn&apos;t.
        </span>{" "}
        Engagement, not opinion &mdash; these communities take sides about AI
        as a cultural project; they are not a sample of mainstream AI
        sentiment. The <em>% on companions</em> column is the share of a
        50-post sample (May 2026) where AI companionship was the primary
        topic. Even the loudest anti-AI sub touched it in roughly one post
        in seventeen. The pro-AI side looks thin because most pro-AI energy on
        Reddit lives in product communities (r/ChatGPT, r/ClaudeAI,
        r/singularity) &mdash; people using the thing, not arguing for it.
        The fight against AI companionship, as far as Reddit shows it, is
        happening in §4 above: inside the communities themselves.
      </p>
    </div>
  );
}
