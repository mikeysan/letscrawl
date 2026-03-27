"""
Canonical data models for LetsCrawl research scraping platform.

This module defines the base models and shared metadata fields for all
scraped content types.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class ScrapedItem(BaseModel):
    """
    Base model for all scraped items with common metadata fields.

    All job-specific models (Article, FeedDiscovery, etc.) inherit from
    this base to ensure consistent metadata across all content types.
    """

    # Source metadata (required for all items)
    source_name: str = Field(..., description="Name of the source configuration or website")
    source_type: str = Field(..., description="Type of source (news, rss, product, etc.)")
    retrieved_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Timestamp when this item was retrieved"
    )
    raw_url: str = Field(..., description="The URL where this item was found")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }
