"""
Article normalization for news and blog content.

This module normalizes extracted article data to the canonical Article schema,
adding metadata and ensuring consistent field names across sources.
"""

from datetime import datetime
from typing import Dict, Any, List, Optional
from models.news import Article
from models.item import ScrapedItem


def normalize_article(
    raw_item: Dict[str, Any],
    source_name: str,
    source_type: str = "news",
    retrieved_at: Optional[datetime] = None,
) -> Article:
    """
    Normalize raw extracted article data to canonical Article schema.

    Args:
        raw_item: Raw extracted data from crawler
        source_name: Name of the source configuration
        source_type: Type of source (news, rss, etc.)
        retrieved_at: Timestamp when item was retrieved (defaults to now)

    Returns:
        Article: Normalized article with canonical schema

    Raises:
        ValueError: If required fields are missing
    """
    # Set retrieval timestamp
    if retrieved_at is None:
        retrieved_at = datetime.utcnow()

    # Map raw fields to canonical fields
    # Handle different field names that sources might use
    title = (
        raw_item.get("title") or
        raw_item.get("name") or  # Support "name" for business listings
        ""
    )
    if not title:
        raise ValueError("Article must have a title or name")

    # Get URL (use 'url' or fallback to empty string)
    raw_url = raw_item.get("url", "")
    if not raw_url:
        # For multi-site crawls, URL might not be extracted
        raw_url = raw_item.get("raw_url", "")

    # Create normalized Article
    article = Article(
        # Required metadata
        source_name=source_name,
        source_type=source_type,
        retrieved_at=retrieved_at,
        raw_url=raw_url,

        # Core content
        title=title,
        author=raw_item.get("author"),
        published_at=_parse_date(raw_item.get("date_published") or raw_item.get("date_posted")),
        summary=raw_item.get("summary") or raw_item.get("description"),
        content=raw_item.get("content"),

        # Categorization
        language=raw_item.get("language"),
        tags=_parse_tags(raw_item.get("tags")),

        # Additional metadata
        image_url=raw_item.get("image_url") or raw_item.get("image") or raw_item.get("cover"),
        category=raw_item.get("category"),
    )

    return article


def _parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """
    Parse date string to datetime object.

    Args:
        date_str: Date string in various formats

    Returns:
        datetime object or None if parsing fails
    """
    if not date_str:
        return None

    # Try common date formats
    from dateutil import parser

    try:
        return parser.parse(date_str)
    except (ValueError, TypeError, parser.ParserError):
        return None


def _parse_tags(tags: Optional[str]) -> Optional[List[str]]:
    """
    Parse tags from string or list to list of strings.

    Args:
        tags: Tags as string (comma-separated) or list

    Returns:
        List of tag strings or None
    """
    if not tags:
        return None

    if isinstance(tags, list):
        return [str(tag) for tag in tags]

    if isinstance(tags, str):
        # Split by comma, semicolon, or pipe
        for separator in [",", ";", "|"]:
            if separator in tags:
                return [tag.strip() for tag in tags.split(separator) if tag.strip()]

        return [tags]

    return None


def normalize_articles(
    raw_items: List[Dict[str, Any]],
    source_name: str,
    source_type: str = "news",
) -> List[Article]:
    """
    Normalize multiple raw articles to canonical schema.

    Args:
        raw_items: List of raw extracted articles
        source_name: Name of the source configuration
        source_type: Type of source

    Returns:
        List of normalized Article objects
    """
    normalized = []
    errors = []

    for i, raw_item in enumerate(raw_items):
        try:
            article = normalize_article(raw_item, source_name, source_type)
            normalized.append(article)
        except ValueError as e:
            errors.append((i, str(e)))

    if errors:
        from utils.logger import logger
        logger.warning(f"Failed to normalize {len(errors)} articles:")
        for i, error in errors[:5]:  # Show first 5 errors
            logger.warning(f"  Item {i}: {error}")
        if len(errors) > 5:
            logger.warning(f"  ... and {len(errors) - 5} more")

    return normalized
