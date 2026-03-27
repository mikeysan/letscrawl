"""
Article model for news and blog content scraping.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field

from .canonical import ScrapedItem


class Article(ScrapedItem):
    """
    Canonical model for article-like content (news, blog posts, etc.).

    This model normalizes article fields across different sources to provide
    consistent data for research workflows.
    """

    # Core content (required)
    title: str = Field(..., description="Article title or headline")

    # Authorship (optional but recommended for articles)
    author: Optional[str] = Field(None, description="Author name or byline")

    # Publication metadata
    published_at: Optional[datetime] = Field(
        None,
        description="Publication date and time"
    )

    # Content (optional - can be summary or full text)
    summary: Optional[str] = Field(None, description="Brief summary or excerpt")
    content: Optional[str] = Field(None, description="Full article text or main content")

    # Categorization
    language: Optional[str] = Field(None, description="ISO 639-1 language code (e.g., 'en', 'fr')")
    tags: Optional[List[str]] = Field(None, description="Tags, categories, or keywords")

    # Additional metadata
    image_url: Optional[str] = Field(None, description="URL of primary image or thumbnail")
    category: Optional[str] = Field(None, description="Primary category or section")

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat() if v else None
        },
        "json_schema_extra": {
            "example": {
                "source_name": "Seneweb (Senegal)",
                "source_type": "news",
                "retrieved_at": "2026-03-27T10:30:00Z",
                "raw_url": "https://www.seneweb.com/article-123",
                "title": "Example News Article",
                "author": "Jane Doe",
                "published_at": "2026-03-27T08:00:00Z",
                "summary": "A brief summary of the article...",
                "content": "Full article text here...",
                "language": "fr",
                "tags": ["politics", "senegal"],
            }
        }
    }
