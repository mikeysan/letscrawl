"""
Canonical data models for LetsCrawl.

This package defines the canonical schemas for different content types
scraped by the platform. All models inherit from ScrapedItem base class
to ensure consistent metadata across sources.
"""

from .canonical import ScrapedItem
from .news import Article
from .feed import FeedDiscovery
from .item import ScrapedItem as LegacyScrapedItem
from .source import (
    SourceConfig,
    ExtractionMode,
    SiteConfig,
    PaginationConfig,
    CrawlerBehaviorConfig,
    LLMExtractionConfig,
    TranslationConfig,
)

__all__ = [
    # Canonical models
    "ScrapedItem",
    "Article",
    "FeedDiscovery",
    # Legacy model (for backward compatibility)
    "LegacyScrapedItem",
    # Source configuration models
    "SourceConfig",
    "ExtractionMode",
    "SiteConfig",
    "PaginationConfig",
    "CrawlerBehaviorConfig",
    "LLMExtractionConfig",
    "TranslationConfig",
]
