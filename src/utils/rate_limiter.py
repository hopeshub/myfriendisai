"""Token bucket rate limiter for Reddit .json endpoint requests."""

import time


class RateLimiter:
    """Ensures we don't exceed Reddit's ~10 req/min unauthenticated limit.

    Conservative default: 1 request per 6 seconds = 10/min.
    """

    def __init__(self, min_interval: float = 6.0):
        self.min_interval = min_interval
        self._last_request: float = 0.0

    def wait(self):
        elapsed = time.monotonic() - self._last_request
        wait_time = self.min_interval - elapsed
        if wait_time > 0:
            time.sleep(wait_time)
        self._last_request = time.monotonic()
