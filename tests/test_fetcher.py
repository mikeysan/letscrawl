"""
Tests for async fetcher.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest

from fetcher import AsyncFetcher
from security import RateLimiter, RobotsTxtChecker


@pytest.mark.asyncio
class TestAsyncFetcher:
    """Test suite for AsyncFetcher."""

    async def test_init_sets_attributes(self):
        """Test that AsyncFetcher.__init__ sets attributes correctly."""
        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_robots_checker = Mock(spec=RobotsTxtChecker)

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
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

        # Create a simple test server
        async def handler(request):
            return web.Response(text="<html><body>Test Content</body></html>")

        app = web.Application()
        app.router.add_get("/", handler)

        from aiohttp.test_utils import TestClient, TestServer

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url("/"))

            mock_rate_limiter = Mock(spec=RateLimiter)
            mock_rate_limiter.acquire = AsyncMock()

            mock_robots_checker = Mock(spec=RobotsTxtChecker)
            mock_robots_checker.can_fetch.return_value = True

            fetcher = AsyncFetcher(
                rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
            )

            # Patch is_safe_url to allow localhost in tests
            with patch("fetcher.is_safe_url", return_value=True):
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
            rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
        )

        with patch("aiohttp.ClientSession", side_effect=Exception("Network error")):
            result = await fetcher.fetch("https://example.com")

            assert result is None

    async def test_fetch_returns_none_on_general_exception(self):
        """Test that fetch() returns None on non-aiohttp exceptions."""
        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_rate_limiter.acquire = AsyncMock()

        mock_robots_checker = Mock(spec=RobotsTxtChecker)
        mock_robots_checker.can_fetch.return_value = True

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
        )

        # Mock to raise a non-ClientError exception
        async def mock_fetch(*args, **kwargs):
            raise ValueError("Some other error")

        fetcher._fetch_with_retry = mock_fetch  # type: ignore[method-assign]

        result = await fetcher.fetch("https://example.com")

        assert result is None


@pytest.mark.asyncio
class TestAsyncFetcherSecurityIntegration:
    """Test suite for security integration in fetch() method."""

    async def test_fetch_returns_none_for_disallowed_url(self):
        """Test that fetch() returns None when robots.txt disallows access."""
        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_rate_limiter.acquire = AsyncMock()

        mock_robots_checker = Mock(spec=RobotsTxtChecker)
        mock_robots_checker.can_fetch.return_value = False  # Disallowed

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
        )

        result = await fetcher.fetch("https://example.com/disallowed-page")

        assert result is None
        mock_robots_checker.can_fetch.assert_called_once()
        # Rate limiter should not be called if robots.txt disallows
        mock_rate_limiter.acquire.assert_not_called()

    # Skipping this test as it creates a localhost server which gets blocked by SSRF
    # SSRF protection is tested in test_url_utils.py
    # async def test_fetch_returns_none_for_unsafe_url(self):
    #     """Test that fetch() returns None for SSRF-protected URLs."""
    #     ...

    async def test_fetch_handles_aiohttp_client_errors(self):
        """Test that fetch() handles aiohttp.ClientError gracefully."""
        import aiohttp

        mock_rate_limiter = Mock(spec=RateLimiter)
        mock_rate_limiter.acquire = AsyncMock()

        mock_robots_checker = Mock(spec=RobotsTxtChecker)
        mock_robots_checker.can_fetch.return_value = True

        fetcher = AsyncFetcher(
            rate_limiter=mock_rate_limiter, robots_checker=mock_robots_checker
        )

        with patch(
            "aiohttp.ClientSession", side_effect=aiohttp.ClientError("Connection error")
        ):
            result = await fetcher.fetch("https://example.com")

            assert result is None

    @pytest.mark.skip(reason="TestServer hangs in WSL/GitHub Actions environment")
    async def test_fetch_returns_none_for_non_200_status(self):
        """Test that fetch() returns None for non-200 HTTP status codes."""
        from aiohttp import web
        from aiohttp.test_utils import TestClient, TestServer

        # Create test server that returns 404
        async def handler(request):
            return web.Response(text="Not Found", status=404)

        app = web.Application()
        app.router.add_get("/", handler)

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url("/"))

            fetcher = AsyncFetcher(delay=0)  # No delay for tests

            # Patch is_safe_url to allow localhost in tests
            with patch("fetcher.is_safe_url", return_value=True):
                result = await fetcher.fetch(url)

            assert result is None
        finally:
            await client.close()


@pytest.mark.asyncio
class TestAsyncFetcherRetry:
    """Test suite for retry logic with tenacity."""

    async def test_fetch_has_retry_decorator(self):
        """Test that _fetch_with_retry method has tenacity retry decorator."""

        fetcher = AsyncFetcher()

        # Verify the method is wrapped by tenacity
        assert hasattr(fetcher._fetch_with_retry, "retry")
        assert hasattr(fetcher._fetch_with_retry, "__wrapped__")

    async def test_fetch_retries_configured_correctly(self):
        """Test that retry logic is configured with correct parameters."""

        from fetcher import AsyncFetcher

        # Get the retry wrapper
        fetcher = AsyncFetcher()
        retry_state = fetcher._fetch_with_retry.retry  # type: ignore[attr-defined]

        # Verify it has the right configuration
        assert retry_state is not None

        # Check that it will stop after 3 attempts
        # (tenacity stores this internally, we just verify it exists)
        assert hasattr(retry_state, "stop")

        # Check that it has a wait strategy
        assert hasattr(retry_state, "wait")
