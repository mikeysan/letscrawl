"""
Source configurations for LetsCrawl.

This package provides typed, validated source configurations for different
scraping jobs (news, RSS feeds, etc.).
"""

from sources.registry import (
    SourceRegistry,
    register_source,
    get_source,
    list_sources,
    has_source,
    get_registry,
)

# Import and register typed sources
from sources.news import create_news_config
from sources.rss import create_rss_config


def _register_default_sources() -> None:
    """Register default typed sources (news, rss)."""
    registry = get_registry()

    # Register news source
    if not registry.has_source("news"):
        news_config = create_news_config()
        register_source(news_config)

    # Register rss source
    if not registry.has_source("rss"):
        rss_config = create_rss_config()
        register_source(rss_config)


# Auto-register default sources on import
_register_default_sources()

__all__ = [
    "SourceRegistry",
    "register_source",
    "get_source",
    "list_sources",
    "has_source",
    "get_registry",
    "_register_default_sources",
]
