"""
Normalization layer for LetsCrawl.

This package normalizes extracted data to canonical schemas, adding
metadata and ensuring consistent field names across sources.
"""

from normalize.articles import (
    normalize_article,
    normalize_articles,
)
from normalize.feeds import (
    normalize_feed_discovery,
    normalize_feed_discoveries,
)

__all__ = [
    "normalize_article",
    "normalize_articles",
    "normalize_feed_discovery",
    "normalize_feed_discoveries",
]
