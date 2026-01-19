"""
Async HTTP fetcher with security features.
"""

import aiohttp
from tenacity import (
    retry,
    stop_after_attempt,
    wait_fixed,
    retry_if_exception_type,
)
from url_utils import is_safe_url
from security import RobotsTxtChecker, RateLimiter


class AsyncFetcher:
    """
    Asynchronous HTTP fetcher with integrated security features.

    Combines rate limiting and robots.txt compliance for ethical crawling.
    """

    def __init__(
        self,
        rate_limiter: RateLimiter | None = None,
        robots_checker: RobotsTxtChecker | None = None,
        delay: float = 1.0,
        user_agent: str = "RespectfulBot"
    ):
        """
        Initialize the async fetcher.

        Args:
            rate_limiter: Optional rate limiter instance (created if not provided)
            robots_checker: Optional robots.txt checker (created if not provided)
            delay: Delay in seconds between requests (used if rate_limiter not provided)
            user_agent: User agent string for robots.txt checks
        """
        self.rate_limiter = rate_limiter if rate_limiter is not None else RateLimiter(delay=delay)
        self.robots_checker = robots_checker if robots_checker is not None else RobotsTxtChecker()
        self.user_agent = user_agent

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(aiohttp.ClientError),
        reraise=True,
    )
    async def _fetch_with_retry(self, url: str) -> str | None:
        """
        Internal method: Fetch a URL with retry logic.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if fetch fails

        Raises:
            aiohttp.ClientError: If the fetch fails after retries
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                return None

    async def fetch(self, url: str) -> str | None:
        """
        Fetch a URL asynchronously with security checks.

        Args:
            url: The URL to fetch

        Returns:
            HTML content as string, or None if fetch fails
        """
        # SSRF protection check
        if not is_safe_url(url):
            return None

        # Check robots.txt compliance
        if not self.robots_checker.can_fetch(self.user_agent, url):
            return None

        # Rate limit the request
        await self.rate_limiter.acquire()

        # Fetch the URL with retry logic
        try:
            return await self._fetch_with_retry(url)
        except aiohttp.ClientError:
            # Retries exhausted, return None
            return None
        except Exception:
            # Handle any other errors
            return None
