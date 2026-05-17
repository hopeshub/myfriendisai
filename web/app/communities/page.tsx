import type { Metadata } from "next";
import Link from "next/link";
import { getSubreddits } from "@/lib/data";
import CommunitiesTable from "./CommunitiesTable";

export const metadata: Metadata = {
  title: "Communities — My Friend Is AI",
  description:
    "Browse 26 Reddit communities tracked for AI companionship trends — sortable by subscribers, posts per day, and engagement metrics.",
  openGraph: {
    title: "Communities — My Friend Is AI",
    description:
      "Browse 26 Reddit communities tracked for AI companionship trends.",
  },
};

export default function Communities() {
  const subreddits = getSubreddits();
  const asOf = subreddits[0]?.snapshot_date ?? "—";

  return (
    <div className="max-w-[720px] mx-auto px-4 sm:px-8 py-8">
      <h1 className="text-3xl font-semibold tracking-tight mb-2 text-[#F8FAFC]">Communities</h1>
      <p className="text-[#9AA7B8] text-sm mb-2">
        {subreddits.length} communities tracked. Data as of {asOf}.
      </p>
      <p className="text-[#9AA7B8] text-sm mb-8 max-w-2xl">
        Size and activity for each tracked community &mdash; context, not the
        project&apos;s main measure. The actual instrument is the{" "}
        <Link
          href="/"
          className="underline underline-offset-2 text-[#C8D0DC] hover:text-[#F8FAFC]"
        >
          theme tracker
        </Link>
        .
      </p>
      <CommunitiesTable subreddits={subreddits} />
    </div>
  );
}
