"""
Tests for async fetcher.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from fetcher import AsyncFetcher
from security import RobotsTxtChecker, RateLimiter


@pytest.mark.asyncio
class TestAsyncFetcher:
    """Test suite for AsyncFetcher."""

    async def test_init_sets_attributes(self):
        """Test that AsyncFetcher.__init__ sets attributes correctly."""
        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_robots_checker = Mock(spec=RobotsTxtChecker)

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter,
            robots_checker=mock_robots_checker
        )

        assert fetcher.rate_limiter is mock_rate_limiter
        assert fetcher.robots_checker is mock_robots_checker

    async def test_init_with_default_values(self):
        """Test that AsyncFetcher can be initialized with defaults."""
        fetcher = AsyncFetcher()

        assert fetcher.rate_limiter is not None
        assert isinstance(fetcher.rate_limiter, RateLimiter)
        assert fetcher.robots_checker is not None
        assert isinstance(fetcher.robots_checker, RobotsTxtChecker)

    async def test_rate_limiter_delay_configurable(self):
        """Test that rate limiter delay can be configured."""
        custom_delay = 2.5
        fetcher = AsyncFetcher(delay=custom_delay)

        assert fetcher.rate_limiter.delay == custom_delay


@pytest.mark.asyncio
class TestAsyncFetcherFetch:
    """Test suite for AsyncFetcher.fetch() method."""

    async def test_fetch_returns_html_content(self):
        """Test that fetch() returns HTML content from the URL."""
        from aiohttp import web
        from aiohttp.test_utils import AioHTTPTestCase, unittest_run_loop

        # Create a simple test server
        async def handler(request):
            return web.Response(text="<html><body>Test Content</body></html>")

        app = web.Application()
        app.router.add_get('/', handler)

        from aiohttp.test_utils import TestServer, TestClient

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url('/'))

            mock_rate_limiter = Mock(spec=RateLimiter)
            mock_rate_limiter.acquire = AsyncMock()

            mock_robots_checker = Mock(spec=RobotsTxtChecker)
            mock_robots_checker.can_fetch.return_value = True

            fetcher = AsyncFetcher(
                rate_limiter=mock_rate_limiter,
                robots_checker=mock_robots_checker
            )

            result = await fetcher.fetch(url)

            assert result == "<html><body>Test Content</body></html>"
            mock_robots_checker.can_fetch.assert_called_once()
            mock_rate_limiter.acquire.assert_called_once()
        finally:
            await client.close()

    async def test_fetch_returns_none_on_network_error(self):
        """Test that fetch() returns None on network errors."""
        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_rate_limiter.acquire = AsyncMock()

        mock_robots_checker = Mock(spec=RobotsTxtChecker)
        mock_robots_checker.can_fetch.return_value = True

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter,
            robots_checker=mock_robots_checker
        )

        with patch('aiohttp.ClientSession', side_effect=Exception("Network error")):
            result = await fetcher.fetch("https://example.com")

            assert result is None
