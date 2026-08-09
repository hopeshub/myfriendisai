import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import { getSubreddits, getCommunityActivity, getSnapshotsForSubreddit } from "@/lib/data";
import Charts from "./Charts";
import CommunityActivityChart from "./CommunityActivityChart";

const TIER_LABELS: Record<number, string> = {
  0: "Tier 0 — General AI",
  1: "Tier 1 — Primary Companionship",
  2: "Tier 2 — Platform-Specific",
  3: "Tier 3 — Recovery & Dependency",
  4: "Tier 4 — Ambient / Discourse Climate",
};

export async function generateMetadata({
  params,
}: {
  params: Promise<{ subreddit: string }>;
}): Promise<Metadata> {
  const { subreddit } = await params;
  const all = getSubreddits();
  const meta = all.find((s) => s.subreddit === subreddit);
  // The page itself 404s on an unknown slug — don't emit real-looking
  // metadata for it.
  if (!meta) return { title: "Community not found" };
  const tierLabel = meta.tier != null ? TIER_LABELS[meta.tier] : "";
  const ogDescription = `Engagement trends for r/${subreddit} on Reddit.`;
  return {
    title: `r/${subreddit}`,
    description: `Engagement trends for r/${subreddit}${tierLabel ? ` (${tierLabel})` : ""} — subscribers, posts per day, and comment activity over time.`,
    alternates: { canonical: `/communities/${subreddit}` },
    openGraph: {
      title: `r/${subreddit} — My Friend Is AI`,
      description: ogDescription,
    },
    twitter: {
      title: `r/${subreddit} — My Friend Is AI`,
      description: ogDescription,
    },
  };
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

  const activity = getCommunityActivity();
  const activitySeries = activity.activity[subreddit] ?? [];
  // Loaded server-side and passed to Charts as a prop — the snapshot data is
  // baked into this statically-generated page, so there's no client-side
  // fetch (and no 6.5 MB API parse) on every visit.
  const snapshots = getSnapshotsForSubreddit(subreddit);

  return (
    <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-8">
      <div className="mb-2">
        <Link href="/communities" className="text-sm text-[#9AA7B8] hover:text-[#F8FAFC] transition-colors">
          ← Communities
        </Link>
      </div>

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-[#F8FAFC]">r/{subreddit}</h1>
          {meta.category && (
            <p className="text-[#9AA7B8] text-sm mt-1">
              {meta.tier != null ? TIER_LABELS[meta.tier] : ""}{meta.category ? ` · ${meta.category}` : ""}
            </p>
          )}
        </div>
        <a
          href={`https://reddit.com/r/${subreddit}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-[#9AA7B8] hover:text-[#F8FAFC] border border-[#2A2D3A] rounded-full px-3 py-1.5 transition-colors"
        >
          View on Reddit ↗
        </a>
      </div>

      <p className="text-[#9AA7B8] text-sm mt-3 max-w-2xl">
        Engagement metrics for a single community &mdash; size and activity over
        time, shown as context.
      </p>

      <section id="activity" className="mt-8 scroll-mt-8">
        <p className="text-xs text-[#7E8B9E] uppercase tracking-widest mb-3">
          Monthly post volume
        </p>
        <CommunityActivityChart months={activity.months} values={activitySeries} />
        <p className="text-xs text-[#7E8B9E] mt-2 max-w-2xl">
          Posts per month since January 2023, to the last complete month &mdash;
          the longest-range view of this community&apos;s activity.
        </p>
      </section>

      <Charts snapshots={snapshots} />

      <p className="mt-10 text-xs text-[#7E8B9E] border-t border-[#2A2D3A] pt-4">
        <strong>Subscribers</strong> — Direct (Reddit API), last collected
        2026-06-07; Reddit closed unauthenticated API access in May 2026, so
        subscriber counts are frozen at that date. Other metrics come from
        post/comment archives and stay current.{" "}
        <strong>Contributors / week</strong> — Derived: distinct authors of posts +
        comments in the 7 days ending on the snapshot date. Historical series uses
        post authors only; comment authors are counted from 2026-03-10 forward.{" "}
        <strong>Posts/day</strong> — Inferred from posts created in past 24h.{" "}
        <strong>Avg comments / Avg score</strong> — Inferred from most recent 100 posts.
      </p>
    </div>
  );
}
