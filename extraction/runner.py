"""
Extraction runner for Crawl4AI.

This module provides a clean interface for executing Crawl4AI crawls with
proper error handling, logging, and result processing.
"""

import json
import asyncio
from typing import Optional, List, Dict, Any, Tuple
from crawl4ai import AsyncWebCrawler, CrawlResult

from utils.logger import logger
from extraction.browser import create_browser_config
from extraction.strategies import create_crawler_run_config, create_extraction_strategy
from models.source import SourceConfig, ExtractionMode


class ExtractionRunner:
    """
    High-level interface for running Crawl4AI extraction jobs.

    This class encapsulates Crawl4AI complexity and provides a simple
    interface for executing crawls with proper error handling.
    """

    def __init__(
        self,
        headless: bool = True,
        verbose: bool = True,
    ):
        """
        Initialize the extraction runner.

        Args:
            headless: Run browser in headless mode
            verbose: Enable verbose logging
        """
        self.headless = headless
        self.verbose = verbose
        self.crawler: Optional[AsyncWebCrawler] = None

    async def __aenter__(self):
        """Async context manager entry."""
        browser_config = create_browser_config(
            headless=self.headless,
            verbose=self.verbose,
        )
        self.crawler = AsyncWebCrawler(config=browser_config)
        await self.crawler.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.crawler:
            await self.crawler.__aexit__(exc_type, exc_val, exc_tb)

    async def check_no_results(
        self,
        url: str,
        session_id: str,
    ) -> bool:
        """
        Check if a "No Results Found" message is present on the page.

        Args:
            url: URL to check
            session_id: Session identifier

        Returns:
            bool: True if no results message found
        """
        if not self.crawler:
            raise RuntimeError("Runner not initialized. Use async context manager.")

        config = create_crawler_run_config(
            css_selector="body",  # Generic selector
            session_id=session_id,
        )

        result_container = await self.crawler.arun(url=url, config=config)
        result: CrawlResult = result_container[0]

        if result.success and result.cleaned_html:
            no_results_phrases = [
                "No Results Found",
                "No matches found",
                "Nothing found",
                "No items found",
                "0 results",
                "No results",
                "Empty",
            ]
            return any(
                phrase.lower() in result.cleaned_html.lower()
                for phrase in no_results_phrases
            )

        return False

    async def fetch_page(
        self,
        url: str,
        css_selector: str,
        source_config: SourceConfig,
        session_id: str,
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        Fetch and extract data from a single page.

        Args:
            url: URL to fetch
            css_selector: CSS selector for content elements
            source_config: Source configuration
            session_id: Session identifier

        Returns:
            Tuple of (extracted_items, no_results_flag)
        """
        if not self.crawler:
            raise RuntimeError("Runner not initialized. Use async context manager.")

        # Check for no results first
        no_results = await self.check_no_results(url, session_id)
        if no_results:
            logger.info("No results found on this page.")
            return [], True

        # Create extraction strategy
        extraction_strategy = create_extraction_strategy(
            source_config,
            source_config.translation,
        )

        # Create crawl config
        crawl_config = create_crawler_run_config(
            css_selector=css_selector,
            extraction_strategy=extraction_strategy,
            session_id=session_id,
        )

        # Fetch page
        logger.debug(f"Starting extraction for: {url}")
        result_container = await self.crawler.arun(url=url, config=crawl_config)
        result: CrawlResult = result_container[0]
        logger.debug("Extraction completed")

        if not result.success:
            logger.error(f"Error fetching page: {result.error_message}")
            return [], False

        if not result.extracted_content:
            logger.warning(
                f"No content extracted. CSS selector '{css_selector}' may have "
                f"found 0 elements."
            )
            return [], False

        # Parse extracted content
        try:
            extracted_data = json.loads(result.extracted_content)
            if not extracted_data:
                logger.info("No data found on page.")
                return [], False

            if self.verbose:
                logger.info(f"Extracted {len(extracted_data)} items")
                logger.debug(f"Raw data: {json.dumps(extracted_data, indent=2)[:200]}...")

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing JSON: {str(e)}")
            return [], False

        return extracted_data, False

    async def crawl_site(
        self,
        site_config: Any,
        source_config: SourceConfig,
        session_id: str,
        max_pages: int = 1,
        delay_between_pages: float = 2.0,
    ) -> List[Dict[str, Any]]:
        """
        Crawl a single site with pagination support.

        Args:
            site_config: Site configuration (dict or SiteConfig)
            source_config: Source configuration
            session_id: Session identifier
            max_pages: Maximum pages to crawl
            delay_between_pages: Delay between page requests

        Returns:
            List of extracted items from all pages
        """
        all_items = []

        # Handle both dict and SiteConfig
        if isinstance(site_config, dict):
            base_url = site_config["BASE_URL"]
            css_selector = site_config["CSS_SELECTOR"]
            site_name = site_config.get("name", "Unknown")
        else:
            base_url = site_config.base_url
            css_selector = site_config.css_selector
            site_name = site_config.name

        logger.info(f"Crawling: {site_name}")
        logger.info(f"URL: {base_url}")

        for page_number in range(1, max_pages + 1):
            # Construct URL for pagination
            url = base_url
            if page_number > 1:
                if "?" in base_url:
                    url = f"{base_url}&page={page_number}"
                else:
                    url = f"{base_url}?page={page_number}"

            logger.info(f"Processing page {page_number}: {url}")

            # Fetch and process page
            items, no_results = await self.fetch_page(
                url=url,
                css_selector=css_selector,
                source_config=source_config,
                session_id=session_id,
            )

            # Stop if no results found
            if no_results:
                logger.info("No more items found. Ending crawl.")
                break

            # Stop if no items extracted
            if not items:
                logger.warning(f"No items extracted from page {page_number}")
                break

            # Add site source to items
            for item in items:
                item["source_site"] = site_name

            all_items.extend(items)

            # Check if we should continue
            if page_number >= max_pages:
                logger.info(f"Reached page limit ({max_pages}).")
                break

            # Delay before next page
            if page_number < max_pages:
                await asyncio.sleep(delay_between_pages)

        logger.info(f"Completed crawling {site_name}. Total items: {len(all_items)}")
        return all_items
