"""
Tests for security utilities.
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from security import RobotsTxtChecker, RateLimiter


class TestRobotsTxtChecker:
    """Test suite for robots.txt compliance checker."""

    def test_can_fetch_allows_valid_user_agent(self):
        """Test that can_fetch returns True when robots.txt allows access."""
        mock_robot_parser = Mock()
        mock_robot_parser.can_fetch.return_value = True

        with patch('security.urllib.robotparser.RobotFileParser', return_value=mock_robot_parser):
            checker = RobotsTxtChecker()
            result = checker.can_fetch('MyBot', 'https://example.com/page')

            assert result is True
            mock_robot_parser.set_url.assert_called_once()
            mock_robot_parser.read.assert_called_once()
            mock_robot_parser.can_fetch.assert_called_once_with('MyBot', 'https://example.com/page')

    def test_can_fetch_blocks_disallowed_path(self):
        """Test that can_fetch returns False when robots.txt disallows access."""
        mock_robot_parser = Mock()
        mock_robot_parser.can_fetch.return_value = False

        with patch('security.urllib.robotparser.RobotFileParser', return_value=mock_robot_parser):
            checker = RobotsTxtChecker()
            result = checker.can_fetch('MyBot', 'https://example.com/admin')

            assert result is False
            mock_robot_parser.can_fetch.assert_called_once_with('MyBot', 'https://example.com/admin')

    def test_can_fetch_caches_robots_txt_per_domain(self):
        """Test that robots.txt is cached per domain."""
        mock_robot_parser = Mock()
        mock_robot_parser.can_fetch.return_value = True

        with patch('security.urllib.robotparser.RobotFileParser', return_value=mock_robot_parser):
            checker = RobotsTxtChecker()

            # Fetch from same domain twice
            checker.can_fetch('MyBot', 'https://example.com/page1')
            checker.can_fetch('MyBot', 'https://example.com/page2')

            # Should only set URL and read once (cached)
            assert mock_robot_parser.set_url.call_count == 1
            assert mock_robot_parser.read.call_count == 1

    def test_can_fetch_fetches_new_robots_txt_for_different_domain(self):
        """Test that different domains trigger separate robots.txt fetches."""
        mock_robot_parser = Mock()
        mock_robot_parser.can_fetch.return_value = True

        with patch('security.urllib.robotparser.RobotFileParser', return_value=mock_robot_parser):
            checker = RobotsTxtChecker()

            # Fetch from different domains
            checker.can_fetch('MyBot', 'https://example.com/page')
            checker.can_fetch('MyBot', 'https://another.com/page')

            # Should fetch robots.txt twice (different domains)
            assert mock_robot_parser.set_url.call_count == 2
            assert mock_robot_parser.read.call_count == 2


@pytest.mark.asyncio
class TestRateLimiter:
    """Test suite for rate limiting functionality."""

    async def test_rate_limiter_enforces_delay(self):
        """Test that rate limiter enforces delay between requests."""
        limiter = RateLimiter(delay=0.5)  # 0.5 second delay

        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        elapsed_time = time.time() - start_time

        # Should take at least 0.5 seconds
        assert elapsed_time >= 0.5

    async def test_rate_limiter_allows_concurrent_acquires(self):
        """Test that rate limiter handles concurrent acquires correctly."""
        limiter = RateLimiter(delay=0.2)  # 0.2 second delay

        start_time = time.time()

        # Launch concurrent acquires
        tasks = [limiter.acquire() for _ in range(3)]
        await asyncio.gather(*tasks)

        elapsed_time = time.time() - start_time

        # Should take at least 0.4 seconds (2 delays for 3 acquires)
        assert elapsed_time >= 0.4

    async def test_rate_limiter_zero_delay(self):
        """Test that rate limiter with zero delay doesn't slow down requests."""
        limiter = RateLimiter(delay=0)

        start_time = time.time()
        await limiter.acquire()
        await limiter.acquire()
        elapsed_time = time.time() - start_time

        # Should be nearly instantaneous
        assert elapsed_time < 0.1
