// ── Recovery section (homepage §4) ───────────────────────────────────────────
// Server component. The section's eyebrow, heading, and intro live in
// page.tsx (matching §1/§2); this renders the chart, the curated posts, and
// the closing scale caveat.

import RecoveryChart from "./RecoveryChart";
import { RECOVERY_POSTS, type RecoveryPost } from "./recoveryData";
import type { RecoveryVolumePoint } from "./themeData";

const MONTHS = [
  "Jan", "Feb", "Mar", "Apr", "May", "Jun",
  "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];

function fmtDate(d: string): string {
  const dt = new Date(d + "T00:00:00Z");
  return `${MONTHS[dt.getUTCMonth()]} ${dt.getUTCFullYear()}`;
}

function permalink(p: RecoveryPost): string {
  return `https://www.reddit.com/r/${p.subreddit}/comments/${p.id}/`;
}

export default function RecoverySection({
  data,
}: {
  data: RecoveryVolumePoint[];
}) {
  return (
    <div>
      <RecoveryChart data={data} />
      <p
        style={{
          fontSize: 12,
          color: "#64748B",
          marginTop: 8,
          marginBottom: 28,
        }}
      >
        Monthly posts across the two recovery communities, with key
        Character.AI moments marked. The shape is the finding: near nothing
        through 2023, then a steady climb.
      </p>

      <div className="grid gap-3 sm:grid-cols-3" style={{ marginBottom: 24 }}>
        {RECOVERY_POSTS.map((p) => (
          <a
            key={p.id}
            href={permalink(p)}
            target="_blank"
            rel="noopener noreferrer"
            className="group block rounded-lg transition-colors hover:bg-[#1A1D27]"
            style={{
              backgroundColor: "#15171E",
              border: "1px solid #2A2D3A",
              padding: 14,
            }}
          >
            <div
              className="line-clamp-2"
              style={{
                fontSize: 13,
                fontWeight: 600,
                color: "#E2E8F0",
                lineHeight: 1.4,
              }}
            >
              {p.title}
            </div>
            <p
              className="line-clamp-4"
              style={{
                fontSize: 13,
                lineHeight: 1.6,
                color: "#94A3B8",
                marginTop: 8,
                fontStyle: "italic",
              }}
            >
              &ldquo;{p.excerpt}&rdquo;
            </p>
            <div
              style={{
                fontSize: 11,
                color: "#64748B",
                marginTop: 10,
                display: "flex",
                gap: 8,
                flexWrap: "wrap",
              }}
            >
              <span className="group-hover:text-[#94A3B8] transition-colors">
                r/{p.subreddit}
              </span>
              <span>·</span>
              <span>{fmtDate(p.date)}</span>
              <span>·</span>
              <span>
                <span aria-hidden>&uarr;</span>{" "}
                <span className="sr-only">score </span>
                {p.score.toLocaleString()}
              </span>
            </div>
          </a>
        ))}
      </div>

      <p
        style={{
          fontSize: 13,
          lineHeight: 1.7,
          color: "#94A3B8",
          maxWidth: 700,
        }}
      >
        <span style={{ color: "#E2E8F0", fontWeight: 600 }}>
          A note on scale.
        </span>{" "}
        These are small communities &mdash; together a few thousand posts a
        year, a rounding error against CharacterAI&apos;s millions. This is a
        qualitative finding, not a measured prevalence: not how many people,
        but the plain fact that a recovery infrastructure now exists where
        three years ago there was none.
      </p>
    </div>
  );
}
