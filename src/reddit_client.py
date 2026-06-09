"""HTTP client for Reddit.

Two access modes:
  - OAuth (preferred): app-only client_credentials grant against
    oauth.reddit.com. Activated automatically when credentials exist at
    ~/.config/myfriendisai-reddit.env (REDDIT_CLIENT_ID / REDDIT_CLIENT_SECRET).
    Rate limit ~100 req/min; we stay well under it.
  - Unauthenticated .json endpoints (legacy): Reddit globally disabled these
    on 2026-05-30 (all return 403). Kept as the no-creds fallback in case
    they ever come back; the daily pipeline falls back to Arctic Shift when
    this mode fails.
"""

import random
import time
import logging
from pathlib import Path
from typing import Optional

import requests

from src.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

USER_AGENT = "ai-companion-tracker/1.0 (research project; contact via github)"
BASE_URL = "https://www.reddit.com"
OAUTH_BASE_URL = "https://oauth.reddit.com"
TOKEN_URL = "https://www.reddit.com/api/v1/access_token"
CREDS_PATH = Path.home() / ".config" / "myfriendisai-reddit.env"

# Min seconds between requests per mode. OAuth allows ~100/min; 1.5s keeps a
# wide safety margin while cutting collection time ~4x vs the legacy 6s.
OAUTH_MIN_INTERVAL = 1.5
UNAUTH_MIN_INTERVAL = 6.0


def load_oauth_creds() -> Optional[tuple]:
    """Read (client_id, client_secret) from CREDS_PATH, or None if absent."""
    try:
        text = CREDS_PATH.read_text()
    except OSError:
        return None
    values = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        values[key.strip()] = val.strip().strip("'\"")
    client_id = values.get("REDDIT_CLIENT_ID")
    client_secret = values.get("REDDIT_CLIENT_SECRET")
    if client_id and client_secret:
        return client_id, client_secret
    return None

# HTTP errors that are worth retrying
RETRYABLE_STATUS = {429, 500, 502, 503, 504}

# Cap total backoff to avoid blocking launchd for hours on a persistent outage.
MAX_BACKOFF_SECONDS = 90.0


def _next_backoff(current: float) -> float:
    # Exponential with ±25% jitter; clamped at MAX_BACKOFF_SECONDS so a
    # prolonged 429 streak can't stall the whole daily pipeline.
    jittered = current * random.uniform(0.75, 1.25)
    return min(jittered * 2, MAX_BACKOFF_SECONDS)


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
        self.max_retries = max_retries

        self._creds = load_oauth_creds()
        self._token: Optional[str] = None
        self._token_expiry: float = 0.0
        if self._creds:
            self.base_url = OAUTH_BASE_URL
            logger.info("Reddit client: OAuth mode (creds from %s)", CREDS_PATH)
        else:
            self.base_url = BASE_URL
            logger.info("Reddit client: unauthenticated mode (no creds at %s)", CREDS_PATH)

        default_interval = OAUTH_MIN_INTERVAL if self._creds else UNAUTH_MIN_INTERVAL
        self.rate_limiter = rate_limiter or RateLimiter(min_interval=default_interval)

    @property
    def is_authenticated(self) -> bool:
        return self._creds is not None

    def _refresh_token(self) -> None:
        """Fetch an app-only bearer token via the client_credentials grant."""
        client_id, client_secret = self._creds
        try:
            resp = requests.post(
                TOKEN_URL,
                auth=(client_id, client_secret),
                data={"grant_type": "client_credentials"},
                headers={"User-Agent": USER_AGENT},
                timeout=15,
            )
        except requests.RequestException as e:
            raise RedditError(f"OAuth token request failed: {e}") from e
        if resp.status_code != 200:
            raise RedditError(f"OAuth token request returned HTTP {resp.status_code}: {resp.text[:200]}")
        payload = resp.json()
        token = payload.get("access_token")
        if not token:
            raise RedditError(f"OAuth token response missing access_token: {payload}")
        # Refresh 5 minutes early so a token never expires mid-pagination.
        self._token = token
        self._token_expiry = time.monotonic() + float(payload.get("expires_in", 3600)) - 300
        self.session.headers["Authorization"] = f"bearer {token}"
        logger.info("Obtained Reddit OAuth token (expires_in=%ss)", payload.get("expires_in"))

    def _ensure_token(self) -> None:
        if self._creds and (self._token is None or time.monotonic() >= self._token_expiry):
            self._refresh_token()

    def _get(self, url: str, params: Optional[dict] = None) -> dict:
        """Make a rate-limited GET request with exponential backoff on failure."""
        self.rate_limiter.wait()
        self._ensure_token()

        backoff = 10.0
        token_retried = False
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, params=params, timeout=15)
            except requests.RequestException as e:
                if attempt == self.max_retries - 1:
                    raise RedditError(f"Network error after {self.max_retries} attempts: {e}") from e
                logger.warning("Network error (attempt %d/%d): %s", attempt + 1, self.max_retries, e)
                time.sleep(backoff)
                backoff = _next_backoff(backoff)
                continue

            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as e:
                    # Reddit occasionally returns an HTML error/interstitial page with a 200 status.
                    if attempt == self.max_retries - 1:
                        raise RedditError(f"Invalid JSON response after {self.max_retries} attempts: {url}") from e
                    logger.warning(
                        "Invalid JSON at %s (attempt %d/%d), backing off %.0fs",
                        url, attempt + 1, self.max_retries, backoff,
                    )
                    time.sleep(backoff)
                    backoff *= 2
                    continue

            if response.status_code == 404:
                raise SubredditNotFound(f"Subreddit not found: {url}")

            if response.status_code == 401 and self._creds:
                if token_retried:
                    raise RedditError(f"HTTP 401 persisted after token refresh: {url}")
                logger.warning("HTTP 401 — refreshing OAuth token and retrying")
                token_retried = True
                self._refresh_token()
                continue

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
                backoff = _next_backoff(backoff)
                continue

            raise RedditError(f"Unexpected HTTP {response.status_code}: {url}")

        raise RedditError(f"Exhausted retries for {url}")

    def get_about(self, subreddit: str) -> dict:
        """Fetch subreddit metadata from /r/{subreddit}/about.json."""
        url = f"{self.base_url}/r/{subreddit}/about.json"
        data = self._get(url)
        return data.get("data", {})

    def get_new(self, subreddit: str, limit: int = 100) -> list[dict]:
        """Fetch recent posts from /r/{subreddit}/new.json."""
        url = f"{self.base_url}/r/{subreddit}/new.json"
        data = self._get(url, params={"limit": limit})
        return data.get("data", {}).get("children", [])

    def get_top(self, subreddit: str, timeframe: str = "week", limit: int = 100) -> list[dict]:
        """Fetch top posts from /r/{subreddit}/top.json."""
        url = f"{self.base_url}/r/{subreddit}/top.json"
        data = self._get(url, params={"t": timeframe, "limit": limit})
        return data.get("data", {}).get("children", [])

    def get_new_paginated(self, subreddit: str, target: int = 500) -> list[dict]:
        """Fetch up to `target` recent posts using pagination."""
        all_children = []
        after = None
        while len(all_children) < target:
            batch_size = min(100, target - len(all_children))
            url = f"{self.base_url}/r/{subreddit}/new.json"
            params = {"limit": batch_size}
            if after:
                params["after"] = after
            data = self._get(url, params=params)
            children = data.get("data", {}).get("children", [])
            if not children:
                break
            all_children.extend(children)
            after = data.get("data", {}).get("after")
            if not after:
                break
        return all_children

    def get_new_until(self, subreddit: str, since_epoch: float, max_posts: int = 1000) -> list[dict]:
        """Fetch recent posts, paginating until coverage reaches `since_epoch`.

        Used by the daily collector to capture full daily volume for high-volume
        subs (CharacterAI, etc.) that exceed Reddit's 100-post-per-listing cap.
        Low-volume subs naturally stop after page 1 because their 100th-most-
        recent post is already past the cutoff.

        Stops when:
          - oldest post in the latest page is older than since_epoch, OR
          - listing is exhausted (no `after` token), OR
          - max_posts safety cap reached
        """
        all_children: list[dict] = []
        after: Optional[str] = None
        while len(all_children) < max_posts:
            batch_size = min(100, max_posts - len(all_children))
            url = f"{self.base_url}/r/{subreddit}/new.json"
            params: dict = {"limit": batch_size}
            if after:
                params["after"] = after
            data = self._get(url, params=params)
            children = data.get("data", {}).get("children", [])
            if not children:
                break
            all_children.extend(children)

            oldest_ts = min(
                (c.get("data", {}).get("created_utc") or 0) for c in children
            )
            if oldest_ts and oldest_ts <= since_epoch:
                break

            after = data.get("data", {}).get("after")
            if not after:
                break
        return all_children

    def get_post_comments(self, subreddit: str, post_id: str, limit: int = 20) -> list[dict]:
        """Fetch top comments for a post. Returns list of comment dicts."""
        url = f"{self.base_url}/r/{subreddit}/comments/{post_id}.json"
        data = self._get(url, params={"limit": limit, "sort": "top"})
        comments = []
        if isinstance(data, list) and len(data) > 1:
            for child in data[1].get("data", {}).get("children", []):
                if child.get("kind") == "t1":
                    comments.append(child.get("data", {}))
        return comments

    def search(self, subreddit: str, query: str, timeframe: str = "day", limit: int = 100) -> list[dict]:
        """Search within a subreddit. Phase 2 only."""
        url = f"{self.base_url}/r/{subreddit}/search.json"
        data = self._get(url, params={
            "q": query,
            "restrict_sr": "on",
            "t": timeframe,
            "limit": limit,
        })
        return data.get("data", {}).get("children", [])
