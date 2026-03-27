"""
News source configurations for multi-site African news scraping.

This module defines typed source configurations for news article extraction
from multiple African news websites.
"""

from models.source import (
    SourceConfig,
    ExtractionMode,
    SiteConfig,
    PaginationConfig,
    CrawlerBehaviorConfig,
    LLMExtractionConfig,
)

# News extraction instruction
NEWS_INSTRUCTION = """
Extract news article information from each article element:
- Title: The headline/title of the news article
- Content: The main article text or summary description
- Date Published: The publication date (in any recognizable format)

Focus on extracting clean, readable text content for each field.
"""


def create_news_config() -> SourceConfig:
    """
    Create a multi-site news scraping configuration.

    This configuration scrapes news articles from multiple African news sites:
    - Seneweb (Senegal)
    - The Namibian (Namibia)
    - New Times (Rwanda)

    Returns:
        SourceConfig: Typed news scraping configuration
    """
    return SourceConfig(
        name="news",
        extraction_mode=ExtractionMode.LLM,
        required_keys=["title", "date_published"],
        optional_keys=["content"],
        sites=[
            SiteConfig(
                name="Seneweb (Senegal)",
                base_url="https://www.seneweb.com",
                css_selector="div.post-sidebar-big",
            ),
            SiteConfig(
                name="The Namibian (Namibia)",
                base_url="https://www.namibian.com.na",
                css_selector="article, .news-article, .post-item",
            ),
            SiteConfig(
                name="New Times (Rwanda)",
                base_url="https://www.newtimes.co.rw",
                css_selector=".article",
            ),
        ],
        pagination=PaginationConfig(
            enabled=True,
            max_pages=3,
            delay_between_pages=5.0,
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
            instruction=NEWS_INSTRUCTION,
        ),
    )
