"""
Security utilities for ethical web crawling.
"""

import asyncio
import time
import urllib.robotparser
from urllib.parse import urlparse


class RobotsTxtChecker:
    """
    Checks robots.txt compliance for web crawling.

    Caches robots.txt files per domain to avoid repeated fetches.
    """

    def __init__(self) -> None:
        """Initialize the robots.txt checker with an empty cache."""
        self._cache: dict[str, urllib.robotparser.RobotFileParser] = {}

    def can_fetch(self, user_agent: str, url: str) -> bool:
        """
        Check if a user agent is allowed to fetch a URL according to robots.txt.

        Args:
            user_agent: The user agent string to check
            url: The URL to check

        Returns:
            True if the user agent is allowed to fetch the URL, False otherwise
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc

        # Check if we have a cached robot file parser for this domain
        if domain not in self._cache:
            robots_url = f"{parsed_url.scheme}://{domain}/robots.txt"
            rp = urllib.robotparser.RobotFileParser()
            rp.set_url(robots_url)
            rp.read()
            self._cache[domain] = rp
        else:
            rp = self._cache[domain]

        return rp.can_fetch(user_agent, url)


class RateLimiter:
    """
    Rate limiter to control request frequency.

    Ensures a minimum delay between requests to be respectful to servers.
    """

    def __init__(self, delay: float = 1.0):
        """
        Initialize the rate limiter.

        Args:
            delay: Minimum delay in seconds between requests (default: 1.0)
        """
        self.delay: float = delay
        self._lock = asyncio.Lock()
        self._last_fetch_time: float = 0.0

    async def acquire(self) -> None:
        """
        Acquire permission to make a request.

        Will wait if necessary to ensure the minimum delay between requests.
        """
        async with self._lock:
            current_time = time.time()
            time_since_last_fetch = current_time - self._last_fetch_time

            if time_since_last_fetch < self.delay:
                wait_time = self.delay - time_since_last_fetch
                await asyncio.sleep(wait_time)

            self._last_fetch_time = time.time()
