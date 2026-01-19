"""
Simple async web crawler with security features.
"""

import asyncio
from collections import deque
from typing import Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from fetcher import AsyncFetcher
from url_utils import normalize_url, is_safe_url


class WebCrawler:
    """
    Async web crawler with security features and queue-based orchestration.
    """

    def __init__(
        self,
        start_url: str,
        max_pages: int = 10,
        delay: float = 1.0,
        user_agent: str = "RespectfulBot"
    ):
        """
        Initialize the web crawler.

        Args:
            start_url: The URL to start crawling from
            max_pages: Maximum number of pages to crawl
            delay: Delay in seconds between requests
            user_agent: User agent string for robots.txt checks
        """
        self.start_url = start_url
        self.max_pages = max_pages
        self.fetcher = AsyncFetcher(delay=delay, user_agent=user_agent)
        self.frontier: deque[str] = deque()
        self.visited: Set[str] = set()
        self.base_url = f"{urlparse(start_url).scheme}://{urlparse(start_url).netloc}"

    def _extract_links(self, html: str, current_url: str) -> list[str]:
        """
        Extract links from HTML content.

        Args:
            html: HTML content
            current_url: URL of the current page

        Returns:
            List of normalized absolute URLs
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = []

        for tag in soup.find_all('a', href=True):
            href = tag['href']
            # Normalize the URL
            absolute_url = normalize_url(href, current_url)
            links.append(absolute_url)

        return links

    def _should_crawl(self, url: str) -> bool:
        """
        Check if a URL should be crawled.

        Args:
            url: URL to check

        Returns:
            True if the URL should be crawled, False otherwise
        """
        # Check if already visited
        if url in self.visited:
            return False

        # Check if same domain
        parsed = urlparse(url)
        if parsed.netloc != urlparse(self.start_url).netloc:
            return False

        return True

    async def crawl(self) -> dict[str, str]:
        """
        Run the crawler.

        Returns:
            Dictionary mapping URLs to their HTML content
        """
        # Add start URL to frontier
        self.frontier.append(self.start_url)
        results = {}

        while self.frontier and len(self.visited) < self.max_pages:
            # Get next URL from frontier
            url = self.frontier.popleft()

            # Skip if already visited
            if url in self.visited:
                continue

            # Fetch the page
            print(f"Crawling: {url}")
            html = await self.fetcher.fetch(url)

            if html is None:
                print(f"Failed to fetch: {url}")
                continue

            # Mark as visited
            self.visited.add(url)
            results[url] = html

            # Extract and enqueue links
            links = self._extract_links(html, url)
            for link in links:
                if self._should_crawl(link):
                    self.frontier.append(link)

        print(f"\nCrawling complete. Visited {len(self.visited)} pages.")
        return results


async def main():
    """Example usage of the web crawler."""
    crawler = WebCrawler(
        start_url="https://example.com",
        max_pages=5,
        delay=1.0
    )

    results = await crawler.crawl()

    print(f"\nCrawled {len(results)} pages:")
    for url in results.keys():
        print(f"  - {url}")


if __name__ == "__main__":
    asyncio.run(main())
