export type SubredditSummary = {
  subreddit: string;
  snapshot_date: string;
  subscribers: number | null;
  active_users: number | null;
  posts_today: number | null;
  avg_comments_per_post: number | null;
  avg_score_per_post: number | null;
  unique_authors: number | null;
  unique_post_authors_7d: number | null;
  unique_comment_authors_7d: number | null;
  unique_contributors_7d: number | null;
  category: string | null;
  tier: number | null;
  display_name: string | null;
};

export type Snapshot = {
  subreddit: string;
  snapshot_date: string;
  data_source: string;
  subscribers: number | null;
  active_users: number | null;
  visitors_7d: number | null;
  contributions_7d: number | null;
  posts_today: number | null;
  avg_comments_per_post: number | null;
  avg_score_per_post: number | null;
  unique_authors: number | null;
  unique_post_authors_7d: number | null;
  unique_comment_authors_7d: number | null;
  unique_contributors_7d: number | null;
};
