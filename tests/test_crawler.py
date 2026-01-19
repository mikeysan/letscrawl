"""
Integration tests for the web crawler.
"""

import pytest
from aiohttp import web
from aiohttp.test_utils import TestClient, TestServer

from crawler import WebCrawler


@pytest.mark.asyncio
class TestWebCrawler:
    """Integration tests for WebCrawler."""

    async def test_crawler_visits_start_page(self):
        """Test that crawler visits the start page."""
        # Create test server
        async def handler(request):
            html = """
            <html>
                <body><h1>Test Page</h1></body>
            </html>
            """
            return web.Response(text=html)

        app = web.Application()
        app.router.add_get('/', handler)

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url('/'))

            # Create crawler with max_pages=1
            crawler = WebCrawler(start_url=url, max_pages=1, delay=0)

            # Mock is_safe_url to allow localhost
            from unittest.mock import patch
            with patch('fetcher.is_safe_url', return_value=True):
                results = await crawler.crawl()

            # Should have visited exactly 1 page
            assert len(results) == 1
            assert url in results
            assert "Test Page" in results[url]

        finally:
            await client.close()

    async def test_crawler_follows_links(self):
        """Test that crawler follows links to new pages."""
        # Create test server with two pages
        async def index_handler(request):
            html = """
            <html>
                <body>
                    <h1>Index Page</h1>
                    <a href="/page2">Page 2</a>
                </body>
            </html>
            """
            return web.Response(text=html)

        async def page2_handler(request):
            html = """
            <html>
                <body><h1>Page 2</h1></body>
            </html>
            """
            return web.Response(text=html)

        app = web.Application()
        app.router.add_get('/', index_handler)
        app.router.add_get('/page2', page2_handler)

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url('/'))

            # Create crawler with max_pages=2
            crawler = WebCrawler(start_url=url, max_pages=2, delay=0)

            # Mock is_safe_url to allow localhost
            from unittest.mock import patch
            with patch('fetcher.is_safe_url', return_value=True):
                results = await crawler.crawl()

            # Should have visited 2 pages
            assert len(results) == 2

            # Check that both pages were visited
            page_urls = list(results.keys())
            assert any('/page2' in u for u in page_urls)

        finally:
            await client.close()

    async def test_crawler_respects_max_pages(self):
        """Test that crawler stops after reaching max_pages limit."""
        # Create test server with multiple pages
        async def handler(request):
            page_num = request.path.strip('/') or '1'
            html = f"""
            <html>
                <body>
                    <h1>Page {page_num}</h1>
                    <a href="/page{int(page_num) + 1}">Next</a>
                </body>
            </html>
            """
            return web.Response(text=html)

        app = web.Application()
        app.router.add_get('/{tail:.*}', handler)

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url('/'))

            # Create crawler with max_pages=3
            crawler = WebCrawler(start_url=url, max_pages=3, delay=0)

            # Mock is_safe_url to allow localhost
            from unittest.mock import patch
            with patch('fetcher.is_safe_url', return_value=True):
                results = await crawler.crawl()

            # Should have visited exactly 3 pages
            assert len(results) == 3
            assert len(crawler.visited) == 3

        finally:
            await client.close()

    async def test_crawler_skips_visited_pages(self):
        """Test that crawler doesn't revisit pages."""
        # Create test server
        async def handler(request):
            html = """
            <html>
                <body>
                    <h1>Test</h1>
                    <a href="/">Self Link</a>
                </body>
            </html>
            """
            return web.Response(text=html)

        app = web.Application()
        app.router.add_get('/', handler)

        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()

        try:
            url = str(server.make_url('/'))

            # Create crawler
            crawler = WebCrawler(start_url=url, max_pages=10, delay=0)

            # Mock is_safe_url to allow localhost
            from unittest.mock import patch
            with patch('fetcher.is_safe_url', return_value=True):
                results = await crawler.crawl()

            # Should have visited only 1 page (despite self-link)
            assert len(results) == 1
            assert len(crawler.visited) == 1

        finally:
            await client.close()
