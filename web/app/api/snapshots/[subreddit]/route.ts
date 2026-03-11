import { NextResponse } from "next/server";
import { getSnapshotsForSubreddit } from "@/lib/data";

export async function GET(
  _req: Request,
  { params }: { params: Promise<{ subreddit: string }> }
) {
  const { subreddit } = await params;
  const snapshots = getSnapshotsForSubreddit(subreddit);
  return NextResponse.json(snapshots);
}
