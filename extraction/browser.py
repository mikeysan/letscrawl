"""
Browser configuration management for Crawl4AI.

This module handles the creation and configuration of BrowserConfig objects
for Crawl4AI's AsyncWebCrawler.
"""

from typing import Optional
from crawl4ai import BrowserConfig
from models.source import CrawlerBehaviorConfig


def create_browser_config(
    behavior: Optional[CrawlerBehaviorConfig] = None,
    headless: Optional[bool] = None,
    verbose: Optional[bool] = None,
) -> BrowserConfig:
    """
    Create a BrowserConfig for Crawl4AI from crawler behavior settings.

    Args:
        behavior: CrawlerBehaviorConfig with browser settings
        headless: Override headless setting
        verbose: Override verbose logging setting

    Returns:
        BrowserConfig: Configured browser settings for Crawl4AI
    """
    # Use provided behavior or defaults
    if behavior is None:
        behavior = CrawlerBehaviorConfig()

    # Allow overrides
    final_headless = headless if headless is not None else behavior.headless
    final_verbose = verbose if verbose is not None else behavior.verbose_logging

    return BrowserConfig(
        browser_type="chromium",
        headless=final_headless,
        verbose=final_verbose,
    )
