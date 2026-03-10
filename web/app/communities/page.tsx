import { getSubreddits } from "@/lib/data";
import type { SubredditSummary } from "@/lib/types";

function fmt(n: number | null, decimals = 0): string {
  if (n == null) return "—";
  return decimals > 0
    ? n.toLocaleString("en-US", { maximumFractionDigits: decimals })
    : n.toLocaleString("en-US");
}

function TierBadge({ tier }: { tier: number | null }) {
  const labels: Record<number, string> = {
    0: "Control",
    1: "Companion",
    2: "Platform",
    3: "Recovery",
  };
  const colors: Record<number, string> = {
    0: "bg-zinc-100 text-zinc-500",
    1: "bg-blue-50 text-blue-600",
    2: "bg-violet-50 text-violet-600",
    3: "bg-red-50 text-red-600",
  };
  if (tier == null) return null;
  return (
    <span
      className={`inline-flex text-xs font-medium px-2 py-0.5 rounded-full ${colors[tier] ?? "bg-zinc-100 text-zinc-500"}`}
    >
      {labels[tier] ?? `Tier ${tier}`}
    </span>
  );
}

function Row({ s }: { s: SubredditSummary }) {
  return (
    <tr className="border-t border-zinc-100 hover:bg-zinc-50 transition-colors">
      <td className="py-3 pr-4">
        <div className="font-medium text-sm">
          r/{s.subreddit}
        </div>
        {s.category && (
          <div className="text-xs text-zinc-400 mt-0.5">{s.category}</div>
        )}
      </td>
      <td className="py-3 pr-4">
        <TierBadge tier={s.tier} />
      </td>
      <td className="py-3 pr-4 text-sm tabular-nums text-right">
        {fmt(s.subscribers)}
      </td>
      <td className="py-3 pr-4 text-sm tabular-nums text-right">
        {fmt(s.posts_today)}
      </td>
      <td className="py-3 pr-4 text-sm tabular-nums text-right">
        {fmt(s.avg_comments_per_post, 1)}
      </td>
      <td className="py-3 text-sm tabular-nums text-right">
        {fmt(s.avg_score_per_post, 0)}
      </td>
    </tr>
  );
}

export default function Communities() {
  const subreddits = getSubreddits();

  return (
    <div className="py-8">
      <h1 className="text-3xl font-semibold tracking-tight mb-2">
        Communities
      </h1>
      <p className="text-zinc-500 text-sm mb-8">
        {subreddits.length} communities tracked. Data as of{" "}
        {subreddits[0]?.snapshot_date ?? "—"}.
      </p>

      <div className="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="text-xs text-zinc-400 uppercase tracking-wide">
              <th className="pb-3 pr-4 font-medium">Community</th>
              <th className="pb-3 pr-4 font-medium">Tier</th>
              <th className="pb-3 pr-4 font-medium text-right">Subscribers</th>
              <th className="pb-3 pr-4 font-medium text-right">Posts/day</th>
              <th className="pb-3 pr-4 font-medium text-right">Avg comments</th>
              <th className="pb-3 font-medium text-right">Avg score</th>
            </tr>
          </thead>
          <tbody>
            {subreddits
              .sort((a, b) => (b.subscribers ?? 0) - (a.subscribers ?? 0))
              .map((s) => (
                <Row key={s.subreddit} s={s} />
              ))}
          </tbody>
        </table>
      </div>

      <p className="mt-8 text-xs text-zinc-400">
        <strong>Subscribers</strong> — Direct (Reddit API).{" "}
        <strong>Posts/day</strong> — Inferred from posts in past 24h.{" "}
        <strong>Avg comments / Avg score</strong> — Inferred from most recent
        100 posts.
      </p>
    </div>
  );
}
