"""HTTP client for Reddit's public .json endpoints.

No OAuth credentials required. Uses unauthenticated access with a custom
User-Agent. Respects Reddit's ~10 req/min rate limit with exponential backoff
on 429 responses.
"""

import time
import logging
from typing import Optional

import requests

from src.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

USER_AGENT = "ai-companion-tracker/1.0 (research project; contact via github)"
BASE_URL = "https://www.reddit.com"

# HTTP errors that are worth retrying
RETRYABLE_STATUS = {429, 500, 502, 503, 504}


class RedditError(Exception):
    pass


class SubredditNotFound(RedditError):
    pass


class SubredditForbidden(RedditError):
    """Returned for private or NSFW-blocked subreddits."""
    pass


class RedditClient:
    def __init__(self, rate_limiter: Optional[RateLimiter] = None, max_retries: int = 4):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        self.rate_limiter = rate_limiter or RateLimiter()
        self.max_retries = max_retries

    def _get(self, url: str, params: Optional[dict] = None) -> dict:
        """Make a rate-limited GET request with exponential backoff on failure."""
        self.rate_limiter.wait()

        backoff = 10.0
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise RedditError(f"Network error after {self.max_retries} attempts: {e}") from e
                logger.warning("Network error (attempt %d/%d): %s", attempt + 1, self.max_retries, e)
                time.sleep(backoff)
                backoff *= 2
                continue

            if response.status_code == 200:
                return response.json()

            if response.status_code == 404:
                raise SubredditNotFound(f"Subreddit not found: {url}")

            if response.status_code == 403:
                raise SubredditForbidden(f"Access forbidden (private or NSFW): {url}")

            if response.status_code in RETRYABLE_STATUS:
                if attempt == self.max_retries - 1:
                    raise RedditError(f"HTTP {response.status_code} after {self.max_retries} attempts: {url}")
                logger.warning(
                    "HTTP %d (attempt %d/%d), backing off %.0fs",
                    response.status_code, attempt + 1, self.max_retries, backoff
                )
                time.sleep(backoff)
                backoff *= 2
                continue

            raise RedditError(f"Unexpected HTTP {response.status_code}: {url}")

        raise RedditError(f"Exhausted retries for {url}")

    def get_about(self, subreddit: str) -> dict:
        """Fetch subreddit metadata from /r/{subreddit}/about.json."""
        url = f"{BASE_URL}/r/{subreddit}/about.json"
        data = self._get(url)
        return data.get("data", {})

    def get_new(self, subreddit: str, limit: int = 100) -> list[dict]:
        """Fetch recent posts from /r/{subreddit}/new.json."""
        url = f"{BASE_URL}/r/{subreddit}/new.json"
        data = self._get(url, params={"limit": limit})
        return data.get("data", {}).get("children", [])

    def get_top(self, subreddit: str, timeframe: str = "week", limit: int = 100) -> list[dict]:
        """Fetch top posts from /r/{subreddit}/top.json."""
        url = f"{BASE_URL}/r/{subreddit}/top.json"
        data = self._get(url, params={"t": timeframe, "limit": limit})
        return data.get("data", {}).get("children", [])

    def search(self, subreddit: str, query: str, timeframe: str = "day", limit: int = 100) -> list[dict]:
        """Search within a subreddit. Phase 2 only."""
        url = f"{BASE_URL}/r/{subreddit}/search.json"
        data = self._get(url, params={
            "q": query,
            "restrict_sr": "on",
            "t": timeframe,
            "limit": limit,
        })
        return data.get("data", {}).get("children", [])
