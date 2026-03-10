import { getSubreddits } from "@/lib/data";
import CommunitiesTable from "./CommunitiesTable";

export default function Communities() {
  const subreddits = getSubreddits();
  const asOf = subreddits[0]?.snapshot_date ?? "—";

  return (
    <div className="py-8">
      <h1 className="text-3xl font-semibold tracking-tight mb-2">Communities</h1>
      <p className="text-zinc-500 text-sm mb-8">
        {subreddits.length} communities tracked. Data as of {asOf}.
      </p>
      <CommunitiesTable subreddits={subreddits} />
    </div>
  );
}
