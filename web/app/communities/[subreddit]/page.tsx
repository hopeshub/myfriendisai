import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getSubreddits,
  getCommunityActivity,
  getCommunityMetrics,
  getSnapshotsForSubreddit,
} from "@/lib/data";
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
    // Repeat the site card image: an openGraph/twitter block here replaces
    // the inherited one wholesale, so without this the route ships no image.
    openGraph: {
      title: `r/${subreddit} — My Friend Is AI`,
      description: ogDescription,
      images: ["/opengraph-image"],
    },
    twitter: {
      card: "summary_large_image",
      title: `r/${subreddit} — My Friend Is AI`,
      description: ogDescription,
      images: ["/opengraph-image"],
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

  // The tier label usually ends with the category name ("Tier 1 — Primary
  // Companionship" vs "Primary Companionship"), so only add the category when
  // it actually says something the tier label doesn't.
  const tierLabel = meta.tier != null ? TIER_LABELS[meta.tier] : "";
  const category = meta.category ?? "";
  const subtitle =
    category && !tierLabel.toLowerCase().includes(category.toLowerCase())
      ? [tierLabel, category].filter(Boolean).join(" · ")
      : tierLabel || category;

  const activity = getCommunityActivity();
  const activitySeries = activity.activity[subreddit] ?? [];
  // Loaded server-side and passed to Charts as a prop — the snapshot data is
  // baked into this statically-generated page, so there's no client-side
  // fetch (and no 6.5 MB API parse) on every visit.
  const snapshots = getSnapshotsForSubreddit(subreddit);
  const metrics = getCommunityMetrics();

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
          {subtitle && (
            <p className="text-[#9AA7B8] text-sm mt-1">{subtitle}</p>
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
          Posts per month, from this community&apos;s first month to the last
          complete one &mdash; the longest-range view of its activity.
        </p>
      </section>

      <Charts
        snapshots={snapshots}
        postsPerDay={metrics.postsPerDay7d[subreddit] ?? null}
        subscribersAsOf={metrics.subscribersAsOf[subreddit] ?? null}
      />

      <p className="mt-10 text-xs text-[#7E8B9E] border-t border-[#2A2D3A] pt-4">
        <strong>Subscribers and Avg score</strong> — Direct (Reddit API),
        frozen at the date shown since Reddit closed unauthenticated access in
        May 2026.{" "}
        <strong>Contributors/wk</strong>{" "}— counted from post and comment
        authors in the archive over the 7 days ending on the snapshot date; the
        historical series uses post authors only, with comment authors counted
        from 2026-03-12 onward, and more of them seen from June 2026, when
        comment collection became continuous &mdash; read it within an era, not
        across June 2026.{" "}
        <strong>Posts/day</strong> — mean of the last 7 complete days; the
        current day is still filling up, so it is left out.{" "}
        <strong>Avg comments</strong> — Derived from the comment threads this
        project collects (companionship communities only; since June 2026 those
        are gathered more completely than before, so read it within an era, not
        across June 2026).
      </p>
    </div>
  );
}
