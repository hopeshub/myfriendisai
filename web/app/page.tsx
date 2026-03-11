import { getSubreddits, getSnapshots } from "@/lib/data";
import HeroChart from "./HeroChart";

export default function Home() {
  const subreddits = getSubreddits();
  const snapshots = getSnapshots();

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 py-8 sm:py-16">
      {/* Minimal header text */}
      <div className="mb-8">
        <h1 className="text-2xl sm:text-3xl font-semibold tracking-tight text-foreground mb-2">
          AI companionship is proliferating.
        </h1>
        <p className="text-sm text-muted max-w-xl">
          Tracking Reddit communities where people form emotional attachments to
          AI — updated daily.
        </p>
      </div>

      {/* Hero chart */}
      <div className="rounded-xl border border-border bg-card p-4 sm:p-6">
        <HeroChart snapshots={snapshots} subreddits={subreddits} />
      </div>
    </div>
  );
}
