import { notFound } from "next/navigation";
import Link from "next/link";
import { getSubreddits, getSnapshotsForSubreddit } from "@/lib/data";
import Charts from "./Charts";

const TIER_LABELS: Record<number, string> = {
  0: "Tier 0 — Foundation / Control",
  1: "Tier 1 — Primary Companionship",
  2: "Tier 2 — Platform-Specific",
  3: "Tier 3 — Recovery & Dependency",
};

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return n.toLocaleString("en-US", { maximumFractionDigits: decimals });
}

export async function generateStaticParams() {
  const subreddits = getSubreddits();
  return subreddits.map((s) => ({ subreddit: s.subreddit }));
}

export default async function SubredditPage({
  params,
}: {
  params: Promise<{ subreddit: string }>;
}) {
  const { subreddit } = await params;
  const all = getSubreddits();
  const meta = all.find((s) => s.subreddit === subreddit);
  if (!meta) notFound();

  const snapshots = getSnapshotsForSubreddit(subreddit);
  const latest = snapshots.at(-1);

  return (
    <div className="py-8">
      <div className="mb-2">
        <Link href="/communities" className="text-sm text-zinc-400 hover:text-zinc-700 transition-colors">
          ← Communities
        </Link>
      </div>

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight">r/{subreddit}</h1>
          {meta.category && (
            <p className="text-zinc-400 text-sm mt-1">
              {meta.tier != null ? TIER_LABELS[meta.tier] : ""}{meta.category ? ` · ${meta.category}` : ""}
            </p>
          )}
        </div>
        <a
          href={`https://reddit.com/r/${subreddit}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-zinc-400 hover:text-zinc-700 border border-zinc-200 rounded-full px-3 py-1.5 transition-colors"
        >
          View on Reddit ↗
        </a>
      </div>

      {/* Stat row */}
      {latest && (
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mt-8 p-6 bg-zinc-50 rounded-xl">
          <div>
            <div className="text-2xl font-semibold tabular-nums">{fmt(latest.subscribers)}</div>
            <div className="text-xs text-zinc-400 mt-0.5">Subscribers</div>
          </div>
          <div>
            <div className="text-2xl font-semibold tabular-nums">{fmt(latest.posts_today)}</div>
            <div className="text-xs text-zinc-400 mt-0.5">Posts today</div>
          </div>
          <div>
            <div className="text-2xl font-semibold tabular-nums">{fmt(latest.avg_comments_per_post, 1)}</div>
            <div className="text-xs text-zinc-400 mt-0.5">Avg comments / post</div>
          </div>
          <div>
            <div className="text-2xl font-semibold tabular-nums">{fmt(latest.avg_score_per_post, 0)}</div>
            <div className="text-xs text-zinc-400 mt-0.5">Avg score / post</div>
          </div>
        </div>
      )}

      <div className="mt-8">
        <p className="text-sm text-zinc-500 mb-1">
          {snapshots.length} day{snapshots.length !== 1 ? "s" : ""} of data
          {snapshots.length === 1 && " — charts will grow as daily collection runs"}
        </p>
        <Charts snapshots={snapshots} />
      </div>

      <p className="mt-10 text-xs text-zinc-400 border-t border-zinc-100 pt-4">
        <strong>Subscribers</strong> — Direct (Reddit API).{" "}
        <strong>Posts/day</strong> — Inferred from posts created in past 24h.{" "}
        <strong>Avg comments / Avg score</strong> — Inferred from most recent 100 posts.
        Last snapshot: {latest?.snapshot_date ?? "—"}.
      </p>
    </div>
  );
}
