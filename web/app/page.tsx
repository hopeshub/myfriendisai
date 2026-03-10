import Link from "next/link";

export default function Home() {
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

      <div className="mt-20 border-t border-zinc-100 pt-12">
        <p className="text-xs text-zinc-400 uppercase tracking-widest mb-6">
          What we track
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-8">
          <div>
            <div className="text-2xl font-semibold mb-1">~20</div>
            <div className="text-sm text-zinc-500">
              Reddit communities across 4 research tiers — from general AI to
              recovery groups
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold mb-1">Daily</div>
            <div className="text-sm text-zinc-500">
              Snapshots of subscribers, post activity, and engagement depth
            </div>
          </div>
          <div>
            <div className="text-2xl font-semibold mb-1">Open</div>
            <div className="text-sm text-zinc-500">
              All metrics labeled by provenance — direct, inferred, or derived
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
