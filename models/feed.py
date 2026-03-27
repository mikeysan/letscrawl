"""
Feed discovery model for RSS and Atom feed finding.
"""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field

from .canonical import ScrapedItem


class FeedDiscovery(ScrapedItem):
    """
    Canonical model for RSS/Atom feed discovery results.

    Used when crawling websites to discover available feeds.
    """

    # Feed URLs
    site_url: str = Field(..., description="The homepage URL where the feed was discovered")
    feed_url: str = Field(..., description="The URL of the RSS/Atom feed")

    # Validation status
    feed_valid: bool = Field(..., description="Whether the feed URL is valid and accessible")

    # Optional feed metadata
    feed_title: Optional[str] = Field(None, description="Title of the feed (if available)")
    feed_type: Optional[str] = Field(
        None,
        description="Type of feed (rss, atom, etc.)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "source_name": "CNN",
                "source_type": "rss_discovery",
                "retrieved_at": "2026-03-27T10:30:00Z",
                "raw_url": "https://cnn.com",
                "site_url": "https://cnn.com",
                "feed_url": "https://cnn.com/rss",
                "feed_valid": True,
                "feed_title": "CNN Top Stories",
                "feed_type": "rss",
            }
        }
    }
