import Link from "next/link";
import { getSubreddits, getSnapshots } from "@/lib/data";
import HeroChart from "./HeroChart";

export default function Home() {
  const subreddits = getSubreddits();
  const snapshots = getSnapshots();
  const totalSubscribers = subreddits.reduce((sum, s) => sum + (s.subscribers ?? 0), 0);

  return (
    <div className="py-16">
      <div className="max-w-2xl">
        <p className="text-sm font-mono text-zinc-400 mb-4 uppercase tracking-widest">
          Research Tracker
        </p>
        <h1 className="text-4xl font-semibold tracking-tight leading-tight mb-6">
          AI companionship is proliferating.
          <br />
          Here&apos;s the data.
        </h1>
        <p className="text-lg text-zinc-600 leading-relaxed mb-8">
          This site tracks Reddit communities where people form emotional
          attachments to AI — chatbots, virtual companions, and AI friends.
          Community engagement is a meaningful proxy for the growth and cultural
          dynamics of AI companionship over time.
        </p>
        <Link
          href="/communities"
          className="inline-flex items-center gap-2 bg-zinc-900 text-white text-sm font-medium px-5 py-2.5 rounded-full hover:bg-zinc-700 transition-colors"
        >
          Browse communities →
        </Link>
      </div>

      {/* Hero chart */}
      <div className="mt-16 border border-zinc-100 rounded-2xl p-6">
        <HeroChart snapshots={snapshots} />
      </div>

      {/* Stats row */}
      <div className="mt-12 grid grid-cols-2 sm:grid-cols-4 gap-6">
        <div>
          <div className="text-2xl font-semibold tabular-nums">
            {subreddits.length}
          </div>
          <div className="text-sm text-zinc-500 mt-0.5">Communities tracked</div>
        </div>
        <div>
          <div className="text-2xl font-semibold tabular-nums">
            {totalSubscribers >= 1_000_000
              ? `${(totalSubscribers / 1_000_000).toFixed(1)}M`
              : `${(totalSubscribers / 1_000).toFixed(0)}K`}
          </div>
          <div className="text-sm text-zinc-500 mt-0.5">Total subscribers</div>
        </div>
        <div>
          <div className="text-2xl font-semibold">Daily</div>
          <div className="text-sm text-zinc-500 mt-0.5">Snapshot cadence</div>
        </div>
        <div>
          <div className="text-2xl font-semibold">Open</div>
          <div className="text-sm text-zinc-500 mt-0.5">
            Metrics labeled by provenance
          </div>
        </div>
      </div>

      {/* Tier explainer */}
      <div className="mt-16 border-t border-zinc-100 pt-12">
        <p className="text-xs text-zinc-400 uppercase tracking-widest mb-6">
          Four research tiers
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          {[
            {
              label: "Tier 0 — Control",
              color: "bg-zinc-100 text-zinc-500",
              desc: "Large general AI communities (r/ChatGPT, r/singularity). Baseline for measuring how much companionship language bleeds into tool-use contexts.",
            },
            {
              label: "Tier 1 — Primary Companionship",
              color: "bg-blue-50 text-blue-600",
              desc: "Communities where AI companionship is the central topic (r/replika, r/CharacterAI). Highest concentration of emotionally revealing discourse.",
            },
            {
              label: "Tier 2 — Platform-Specific",
              color: "bg-violet-50 text-violet-600",
              desc: "Subreddits for specific companion products (Kindroid, Nomi, SillyTavern). Higher signal-to-noise for studying how product design affects attachment.",
            },
            {
              label: "Tier 3 — Recovery",
              color: "bg-red-50 text-red-600",
              desc: "Recovery and dependency communities. The smallest and most emotionally saturated — the outer edge of the AI attachment spectrum.",
            },
          ].map((t) => (
            <div key={t.label} className="flex gap-3 p-4 rounded-xl border border-zinc-100">
              <span className={`text-xs font-medium px-2 py-0.5 rounded-full h-fit whitespace-nowrap ${t.color}`}>
                {t.label}
              </span>
              <p className="text-sm text-zinc-500 leading-relaxed">{t.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
