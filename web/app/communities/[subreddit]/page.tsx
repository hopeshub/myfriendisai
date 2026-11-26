import type { Metadata } from "next";
import { notFound } from "next/navigation";
import Link from "next/link";
import {
  getSubreddits,
  getCommunityActivity,
  getCommunityMetrics,
  getSnapshotsForSubreddit,
} from "@/lib/data";
import { buildCommunityChartData } from "@/lib/communityCharts";
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
    // Repeat the card image + url/siteName/type: an openGraph/twitter block here replaces
    // the inherited one wholesale, so without this the route ships none of them.
    openGraph: {
      title: `r/${subreddit} — My Friend Is AI`,
      description: ogDescription,
      url: `/communities/${subreddit}`,
      siteName: "My Friend Is AI",
      type: "website",
      locale: "en_US",
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

// Unknown slugs get the real 404 page at build time instead of an on-demand
// render that came back blank without JavaScript (2026-10-24 site audit).
export const dynamicParams = false;

export async function generateStaticParams() {
  const subreddits = getSubreddits();
  return subreddits.map((s) => ({ subreddit: s.subreddit }));
}

// Reading notes for the few community pages whose chart would mislead on its
// own. Figures checked against the database 2026-11-20.
const COMMUNITY_NOTES: Record<string, string> = {
  ChaiApp:
    "Read this chart with care. Most posts here are recorded as removed or deleted before the archive can read them: about three in four from 2024 to early 2026, and more than 80% every month since May 2026 (90% in October). This site counts only posts whose text survived, so the line shows a few hundred posts a month, lately a few dozen, while people still submit about 2,000. Since late 2026 the community is close to unmeasurable here.",
  therapyGPT:
    "Tracked as context only. People here use general chatbots as a confidant or therapist, and therapy language is so dense that this one community, under 2% of the posts, would supply about 40% of the therapy line. It is kept out of the theme lines so that line does not follow one community's posting volume.",
};

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
  // it actually says something the tier label doesn't. T4 categories carry
  // their own "Ambient — " prefix ("Ambient — Anti-AI"), which the tier label
  // already says, so drop that prefix rather than print "Ambient" twice.
  const tierLabel = meta.tier != null ? TIER_LABELS[meta.tier] : "";
  const rawCategory = meta.category ?? "";
  const [categoryHead, ...categoryRest] = rawCategory.split(" — ");
  const category =
    categoryRest.length > 0 &&
    tierLabel.toLowerCase().includes(categoryHead.toLowerCase())
      ? categoryRest.join(" — ")
      : rawCategory;
  const subtitle =
    category && !tierLabel.toLowerCase().includes(category.toLowerCase())
      ? [tierLabel, category].filter(Boolean).join(" · ")
      : tierLabel || category;

  const activity = getCommunityActivity();
  const activitySeries = activity.activity[subreddit] ?? [];
  // Loaded and aggregated server-side, then passed to Charts as a prop. Only
  // the monthly means and latest-known card values the client renders are
  // baked into this statically-generated page — not the ~1,300 daily rows
  // (which made each page ~400 KB) — and there's no client-side fetch.
  const chartData = buildCommunityChartData(getSnapshotsForSubreddit(subreddit));
  const metrics = getCommunityMetrics();

  return (
    <div className="max-w-[1080px] mx-auto px-4 sm:px-8 py-8">
      <div className="mb-2">
        <Link href="/communities" className="text-sm text-[var(--c-lead)] hover:text-[var(--c-title)] transition-colors">
          ← Communities
        </Link>
      </div>

      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <h1 className="font-display text-3xl font-semibold tracking-tight text-[var(--c-title)]">r/{subreddit}</h1>
          {subtitle && (
            <p className="text-[var(--c-lead)] text-sm mt-1">{subtitle}</p>
          )}
        </div>
        <a
          href={`https://reddit.com/r/${subreddit}`}
          target="_blank"
          rel="noopener noreferrer"
          className="text-xs text-[var(--c-lead)] hover:text-[var(--c-title)] border border-[var(--c-border)] rounded-full px-3 py-1.5 transition-colors"
        >
          View on Reddit ↗
        </a>
      </div>

      <p className="text-[var(--c-lead)] text-sm mt-3 max-w-2xl">
        Engagement metrics for a single community &mdash; size and activity over
        time, shown as context.
      </p>

      <section id="activity" className="mt-8 scroll-mt-8">
        <p className="text-xs text-[var(--c-caption)] mb-3">
          Monthly post volume
        </p>
        <CommunityActivityChart months={activity.months} values={activitySeries} />
        <p className="text-xs text-[var(--c-caption)] mt-2 max-w-2xl">
          Posts per month, from this community&apos;s first month to the last
          complete one &mdash; the longest-range view of its activity.
        </p>
        {COMMUNITY_NOTES[subreddit] && (
          <p className="text-sm text-[var(--c-body)] mt-4 max-w-2xl border-l-2 border-[var(--c-border)] pl-3">
            {COMMUNITY_NOTES[subreddit]}
          </p>
        )}
      </section>

      <Charts
        data={chartData}
        postsPerDay={metrics.postsPerDay7d[subreddit] ?? null}
        subscribersAsOf={metrics.subscribersAsOf[subreddit] ?? null}
      />

      <p className="mt-10 text-xs text-[var(--c-caption)] border-t border-[var(--c-border)] pt-4">
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
        across June 2026). On the comment and score charts, the shaded band
        (March–May 2026) came from
        Reddit&apos;s live listing, which leaves out removed posts, so
        communities that remove many posts read high there.
      </p>
    </div>
  );
}
