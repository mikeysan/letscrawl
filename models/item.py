from typing import Optional

from pydantic import BaseModel


class ScrapedItem(BaseModel):
    """
    Base model for scraped items with common fields.
    All fields are optional since different scraping configurations
    may require different subsets of fields.
    """

    # Core identifiers
    title: Optional[str] = None
    name: Optional[str] = None  # Alias for title (used in product/business listings)
    url: Optional[str] = None

    # Content
    description: Optional[str] = None
    content: Optional[str] = None  # Main article text

    # Business/Specialty fields
    phone: Optional[str] = None
    website: Optional[str] = None
    hours: Optional[str] = None
    specialties: Optional[str] = None
    reviews: Optional[str] = None

    # E-commerce fields
    price: Optional[str] = None
    image_url: Optional[str] = None
    image: Optional[str] = None  # Alias for image_url
    cover: Optional[str] = None  # Alias for image_url (used in book listings)
    category: Optional[str] = None
    rating: Optional[str] = None
    reviews_count: Optional[int] = None

    # Location/Contact
    location: Optional[str] = None
    contact: Optional[str] = None

    # Publication metadata
    date_posted: Optional[str] = None
    date_published: Optional[str] = None  # Publication date for news
    author: Optional[str] = None

    # Categorization
    tags: Optional[str] = None
    additional_info: Optional[str] = None

    # RSS-specific
    feed_valid: Optional[bool] = None  # True if RSS feed URL is valid
