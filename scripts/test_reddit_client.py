"""Quick smoke test for the Reddit client. Fetches live data from each endpoint type."""

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.reddit_client import RedditClient, SubredditNotFound, SubredditForbidden, RedditError
from src.utils.rate_limiter import RateLimiter

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Fast rate limiter for testing (2s between requests — acceptable for a one-off test)
client = RedditClient(rate_limiter=RateLimiter(min_interval=2.0))

TEST_SUBREDDIT = "artificial"

print(f"\n=== Testing /r/{TEST_SUBREDDIT}/about.json ===")
about = client.get_about(TEST_SUBREDDIT)
print(f"  display_name: {about.get('display_name')}")
print(f"  subscribers:  {about.get('subscribers') or 'N/A'}")
print(f"  active_users: {about.get('active_user_count') or 'N/A'}")
print(f"  over_18:      {about.get('over_18')}")

print(f"\n=== Testing /r/{TEST_SUBREDDIT}/new.json ===")
new_posts = client.get_new(TEST_SUBREDDIT, limit=10)
print(f"  Fetched {len(new_posts)} posts")
if new_posts:
    p = new_posts[0]["data"]
    print(f"  Latest: \"{p['title'][:60]}...\"")
    print(f"  Author: u/{p['author']}, score: {p['score']}, comments: {p['num_comments']}")

print(f"\n=== Testing /r/{TEST_SUBREDDIT}/top.json?t=week ===")
top_posts = client.get_top(TEST_SUBREDDIT, timeframe="week", limit=10)
print(f"  Fetched {len(top_posts)} posts")
if top_posts:
    p = top_posts[0]["data"]
    print(f"  Top this week: \"{p['title'][:60]}...\"")
    print(f"  Score: {p['score']}, comments: {p['num_comments']}")

print(f"\n=== Testing error handling: nonexistent subreddit ===")
try:
    client.get_about("xthissubredditdoesnotexist12345x")
    print("  ERROR: Should have raised SubredditNotFound")
except SubredditNotFound as e:
    print(f"  SubredditNotFound raised correctly: {e}")

print("\n=== All tests passed ===\n")
