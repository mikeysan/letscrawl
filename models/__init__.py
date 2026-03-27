"""
Canonical data models for LetsCrawl.

This package defines the canonical schemas for different content types
scraped by the platform. All models inherit from ScrapedItem base class
to ensure consistent metadata across sources.
"""

from .canonical import ScrapedItem
from .news import Article
from .feed import FeedDiscovery

__all__ = [
    "ScrapedItem",
    "Article",
    "FeedDiscovery",
]
