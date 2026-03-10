export default function About() {
  return (
    <div className="max-w-2xl py-8">
      <h1 className="text-3xl font-semibold tracking-tight mb-6">About</h1>
      <div className="prose prose-zinc text-zinc-600 space-y-4 text-base leading-relaxed">
        <p>
          <strong className="text-zinc-900">My Friend Is AI</strong> is a
          longitudinal research tracker documenting the growth of AI
          companionship communities on Reddit.
        </p>
        <p>
          The central thesis: AI companionship is proliferating, and Reddit
          community engagement is a meaningful proxy signal for that. The site
          makes this argument visually across a multi-year window.
        </p>
        <p>
          Communities are organized into four research tiers — from large
          general AI subreddits (baseline controls) to tiny recovery groups
          where AI attachment has become a problem users are trying to manage.
        </p>
        <p className="text-sm text-zinc-400 pt-4 border-t border-zinc-100">
          Data is collected daily from Reddit&apos;s public .json endpoints.
          Each metric is labeled by provenance: <em>Direct</em> (from
          Reddit&apos;s API response), <em>Inferred</em> (approximated from
          available data), or <em>Derived</em> (calculated from other metrics).
        </p>
      </div>
    </div>
  );
}
