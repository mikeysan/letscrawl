"""
RSS feed discovery source configurations.

This module defines typed source configurations for discovering RSS and Atom
feeds on websites.
"""

from models.source import (
    SourceConfig,
    ExtractionMode,
    SiteConfig,
    PaginationConfig,
    CrawlerBehaviorConfig,
    LLMExtractionConfig,
)

# RSS feed discovery selector
RSS_SELECTOR = (
    "link[type='application/rss+xml'], link[type='application/atom+xml'], "
    "a[href*='/rss'], a[href*='/feed'], a[href*='.rss'], a[href*='.xml']"
)

# RSS extraction instruction
RSS_INSTRUCTION = """
Find all RSS feed URLs on this page.
Extract the full URL for each RSS feed found. Look for:

1. <link> tags with type="application/rss+xml" or type="application/atom+xml"
2. Anchor tags (<a>) linking to /rss, /feed, .rss, or .xml files
3. Any other elements that typically contain RSS feed links

Extract ALL RSS feed URLs found on the page. Return only the URLs.
"""


def create_rss_config() -> SourceConfig:
    """
    Create an RSS feed discovery configuration.

    This configuration scans websites to discover RSS and Atom feed URLs.
    It's designed to work with multiple sites for batch feed discovery.

    Returns:
        SourceConfig: Typed RSS feed discovery configuration
    """
    return SourceConfig(
        name="rss",
        extraction_mode=ExtractionMode.LLM,
        required_keys=["url"],
        optional_keys=[],
        sites=[
            SiteConfig(
                name="CNN",
                base_url="https://cnn.com",
                css_selector=RSS_SELECTOR,
            ),
            SiteConfig(
                name="BBC",
                base_url="https://bbc.com",
                css_selector=RSS_SELECTOR,
            ),
            SiteConfig(
                name="NYTimes",
                base_url="https://nytimes.com",
                css_selector=RSS_SELECTOR,
            ),
        ],
        pagination=PaginationConfig(
            enabled=False,  # Single-page scanning
            max_pages=1,
            delay_between_pages=0,
        ),
        crawler_behavior=CrawlerBehaviorConfig(
            headless=True,
            cache_enabled=False,
            verbose_logging=True,
        ),
        llm_config=LLMExtractionConfig(
            provider="groq/llama-3.3-70b-versatile",
            extraction_type="schema",
            input_format="markdown",
            instruction=RSS_INSTRUCTION,
        ),
    )
