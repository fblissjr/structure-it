"""Safety utilities for scraping."""

import logging
import time
from typing import Any, Optional

import requests
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)

class RateLimiter:
    """Token-bucket style rate limiter (interval based)."""

    def __init__(self, requests_per_minute: int = 10):
        self.delay = 60.0 / requests_per_minute
        self.last_request = 0.0

    def wait(self) -> None:
        """Sleep until the next request is allowed."""
        elapsed = time.time() - self.last_request
        if elapsed < self.delay:
            sleep_time = self.delay - elapsed
            time.sleep(sleep_time)
        self.last_request = time.time()


class SafeSession:
    """A requests-like object that enforces rate limits and retries.
    
    Can be used to monkeypatch requests or as a standalone session.
    """

    def __init__(self, requests_per_minute: int = 10, user_agent: str = "structure-it/research-bot"):
        self.limiter = RateLimiter(requests_per_minute)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": user_agent})

    @retry(
        reraise=True,
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=2, max=60),
        retry=retry_if_exception_type((requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.HTTPError)),
        before_sleep=before_sleep_log(logger, logging.WARNING)
    )
    def request(self, method: str, url: str, **kwargs: Any) -> requests.Response:
        """Execute a request with safety controls."""
        self.limiter.wait()
        
        response = self.session.request(method, url, **kwargs)
        
        # Raise for status to trigger retry on 5xx/429
        # We handle 429 specifically if needed, but raise_for_status covers it
        if response.status_code == 429:
            # If we hit a 429, the backoff decorator will handle the wait,
            # but we should probably explicitly log it.
            logger.warning(f"Rate limit hit (429) for {url}")
            
        response.raise_for_status()
        return response

    def get(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("POST", url, **kwargs)

    def head(self, url: str, **kwargs: Any) -> requests.Response:
        return self.request("HEAD", url, **kwargs)

# Global safe session singleton for monkeypatching
DEFAULT_SAFE_SESSION = SafeSession(requests_per_minute=10)
