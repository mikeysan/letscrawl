"""
Feed discovery normalization for RSS and Atom feeds.

This module normalizes RSS feed discovery results to the canonical
FeedDiscovery schema, adding metadata and validation.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from models.feed import FeedDiscovery


def normalize_feed_discovery(
    raw_item: Dict[str, Any],
    source_name: str,
    site_url: str,
    retrieved_at: Optional[datetime] = None,
) -> FeedDiscovery:
    """
    Normalize raw RSS feed discovery data to canonical FeedDiscovery schema.

    Args:
        raw_item: Raw extracted feed data from crawler
        source_name: Name of the source configuration
        site_url: URL of the website where feed was found
        retrieved_at: Timestamp when item was retrieved (defaults to now)

    Returns:
        FeedDiscovery: Normalized feed discovery with canonical schema
    """
    # Set retrieval timestamp
    if retrieved_at is None:
        retrieved_at = datetime.utcnow()

    # Extract feed URL
    feed_url = raw_item.get("url", "")
    if not feed_url:
        raise ValueError("Feed discovery must have a URL")

    # Get validation status (if already validated)
    feed_valid = raw_item.get("feed_valid", True)

    # Create normalized FeedDiscovery
    discovery = FeedDiscovery(
        # Required metadata
        source_name=source_name,
        source_type="rss_discovery",
        retrieved_at=retrieved_at,
        raw_url=site_url,

        # Feed-specific fields
        site_url=site_url,
        feed_url=feed_url,
        feed_valid=feed_valid,

        # Optional metadata
        feed_title=raw_item.get("feed_title"),
        feed_type=raw_item.get("feed_type"),
    )

    return discovery


def normalize_feed_discoveries(
    raw_items: List[Dict[str, Any]],
    source_name: str,
    site_url: str,
) -> List[FeedDiscovery]:
    """
    Normalize multiple raw feed discoveries to canonical schema.

    Args:
        raw_items: List of raw extracted feed URLs
        source_name: Name of the source configuration
        site_url: URL of the website

    Returns:
        List of normalized FeedDiscovery objects
    """
    normalized = []
    errors = []

    for i, raw_item in enumerate(raw_items):
        try:
            discovery = normalize_feed_discovery(raw_item, source_name, site_url)
            normalized.append(discovery)
        except ValueError as e:
            errors.append((i, str(e)))

    if errors:
        from utils.logger import logger
        logger.warning(f"Failed to normalize {len(errors)} feed discoveries:")
        for i, error in errors:
            logger.warning(f"  Item {i}: {error}")

    return normalized
