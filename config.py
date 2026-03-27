# config.py

import os
from typing import Any

# Default configuration for dental clinics example
DEFAULT_CONFIG = {
    "BASE_URL": "https://www.opencare.com/dentists/new-york-ny/",
    # Updated selector for OpenCare dental listings
    "CSS_SELECTOR": "div[data-test='search-result-card']",
    "REQUIRED_KEYS": [
        "name",
        "location",
        "description",
        "rating",
    ],
    # Optional fields that can be enabled/disabled
    "OPTIONAL_KEYS": [
        "phone",
        "website",
        "hours",
        "specialties",
        "reviews",
        "price",
    ],
    # Crawler settings
    "CRAWLER_CONFIG": {
        "MULTI_PAGE": True,  # Set to False for single page scraping
        # Maximum number of pages to scrape (ignored if MULTI_PAGE is False)
        "MAX_PAGES": 5,
        # Delay in seconds between page requests
        "DELAY_BETWEEN_PAGES": 2,
        "HEADLESS": False,  # Run browser in visible mode for debugging
        "CACHE_ENABLED": False,  # Enable/disable caching
        "VERBOSE_LOGGING": True,  # Enable detailed logging
    },
    # LLM Configuration
    "LLM_CONFIG": {
        "PROVIDER": "groq/llama-3.3-70b-versatile",
        "EXTRACTION_TYPE": "schema",
        "INPUT_FORMAT": "markdown",
        "INSTRUCTION": """
        Extract dental clinic information from the content. For each
        clinic, find:

        Required information:
        - Name: The full name of the dental clinic or dentist's practice
        - Location: The complete address of the clinic
        - Description: A brief description of the clinic, their services,
          or the dentist's expertise
        - Rating: The numerical rating (out of 5 stars) if available

        Additional information if present:
        - Phone number
        - Website URL
        - Operating hours
        - List of dental specialties or services offered
        - Number of reviews
        - Price range or insurance information

        Extract this information for each dental clinic card or listing
        found in the content.
        """,
    },
    # Translation Configuration
    "TRANSLATION_CONFIG": {
        "ENABLED": False,
        "TARGET_LANGUAGE": "en",
        "TEXT_FIELDS": ["title", "description", "content"],
    },
}

# RSS feed CSS selector (long, reused across multiple site configs)
_RSS_SELECTOR = (
    "link[type='application/rss+xml'], link[type='application/atom+xml'], "
    "a[href*='/rss'], a[href*='/feed'], a[href*='.rss'], a[href*='.xml']"
)

# Example configurations for different use cases
CONFIGS: dict[str, dict[str, Any]] = {
    "dental": DEFAULT_CONFIG,
    "minimal": {
        **DEFAULT_CONFIG,
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],  # type: ignore[dict-item]
            "MULTI_PAGE": False,
            "VERBOSE_LOGGING": False,
            "HEADLESS": True,
        },
        "OPTIONAL_KEYS": [],  # Only collect required fields
    },
    "detailed": {
        **DEFAULT_CONFIG,
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],  # type: ignore[dict-item]
            "MAX_PAGES": 10,
            "DELAY_BETWEEN_PAGES": 3,
        },
        "REQUIRED_KEYS": list(DEFAULT_CONFIG["REQUIRED_KEYS"]) + ["phone", "website"],
    },
    "test": {
        **DEFAULT_CONFIG,
        "BASE_URL": "file:///" + os.path.abspath("test.html").replace("\\", "/"),
        "CSS_SELECTOR": "div.item-card",
        "REQUIRED_KEYS": ["title", "description", "location", "rating"],
        "OPTIONAL_KEYS": [],
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],  # type: ignore[dict-item]
            "MULTI_PAGE": False,
            "HEADLESS": False,
            "VERBOSE_LOGGING": True,
        },
        "LLM_CONFIG": {
            **DEFAULT_CONFIG["LLM_CONFIG"],  # type: ignore[dict-item]
            "INSTRUCTION": """
            Extract information from each item card. For each item, find:

            Required information:
            - Title: The title of the item (h2 text)
            - Description: The description text
            - Location: The location text
            - Rating: The numerical rating

            Additional information if present:
            - Phone number
            - Website URL

            Extract this information for each item card found in the content.
            """,
        },
    },
    # Added by configuration generator
    "books_test": {
        **DEFAULT_CONFIG,
        "BASE_URL": "https://www.goodreads.com/review/list/57629976",
        "CSS_SELECTOR": "#books.table .cover .value",
        "REQUIRED_KEYS": ["title", "image", "cover", "description"],
        "OPTIONAL_KEYS": ["url"],
        "CRAWLER_CONFIG": {
            "MULTI_PAGE": True,
            "MAX_PAGES": 3,
            "DELAY_BETWEEN_PAGES": 5,
            "HEADLESS": True,
            "CACHE_ENABLED": False,
            "VERBOSE_LOGGING": True,
        },
        "LLM_CONFIG": {
            "PROVIDER": "groq/llama-3.3-70b-versatile",
            "EXTRACTION_TYPE": "schema",
            "INPUT_FORMAT": "markdown",
            "INSTRUCTION": "Locate and download book cover images",
        },
    },
    # News crawler for multiple African news sites
    "news": {
        **DEFAULT_CONFIG,
        # Use SITES list for multiple websites with different selectors
        "SITES": [
            {
                "name": "Seneweb (Senegal)",
                "BASE_URL": "https://www.seneweb.com",
                "CSS_SELECTOR": "div.post-sidebar-big",
            },
            {
                "name": "The Namibian (Namibia)",
                "BASE_URL": "https://www.namibian.com.na",
                "CSS_SELECTOR": "article, .news-article, .post-item",
            },
            {
                "name": "New Times (Rwanda)",
                "BASE_URL": "https://www.newtimes.co.rw",
                "CSS_SELECTOR": ".article",
            },
        ],
        # Minimal fields for news articles
        "REQUIRED_KEYS": ["title", "date_published"],
        "OPTIONAL_KEYS": ["content"],
        # Crawler settings
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],  # type: ignore[dict-item]
            "MULTI_PAGE": True,
            "MAX_PAGES": 3,
            "DELAY_BETWEEN_PAGES": 5,
            "HEADLESS": True,
            "CACHE_ENABLED": False,
            "VERBOSE_LOGGING": True,
        },
        "LLM_CONFIG": {
            **DEFAULT_CONFIG["LLM_CONFIG"],  # type: ignore[dict-item]
            "INSTRUCTION": """
            Extract news article information from each article element:
            - Title: The headline/title of the news article
            - Content: The main article text or summary description
            - Date Published: The publication date (in any recognizable format)

            Focus on extracting clean, readable text content for each field.
            """,
        },
    },
    # RSS Feed URL Finder - finds all RSS feed URLs on websites
    "rss": {
        **DEFAULT_CONFIG,
        # Sites to scan for RSS feeds
        "SITES": [
            {
                "name": "CNN",
                "BASE_URL": "https://cnn.com",
                "CSS_SELECTOR": _RSS_SELECTOR,
            },
            {
                "name": "BBC",
                "BASE_URL": "https://bbc.com",
                "CSS_SELECTOR": _RSS_SELECTOR,
            },
            {
                "name": "NYTimes",
                "BASE_URL": "https://nytimes.com",
                "CSS_SELECTOR": _RSS_SELECTOR,
            },
        ],
        # Only need URL field for RSS feeds
        "REQUIRED_KEYS": ["url"],
        "OPTIONAL_KEYS": [],
        # Crawler settings
        "CRAWLER_CONFIG": {
            **DEFAULT_CONFIG["CRAWLER_CONFIG"],  # type: ignore[dict-item]
            "MULTI_PAGE": False,  # Single page scanning
            "HEADLESS": True,
            "CACHE_ENABLED": False,
            "VERBOSE_LOGGING": True,
        },
        "LLM_CONFIG": {
            **DEFAULT_CONFIG["LLM_CONFIG"],  # type: ignore[dict-item]
            "INSTRUCTION": """
            Find all RSS feed URLs on this page.

            Extract the full URL for each RSS feed found. Look for:
            1. <link> tags with type="application/rss+xml" or
               type="application/atom+xml"
            2. Anchor tags (<a>) linking to /rss, /feed, .rss, or .xml files
            3. Common RSS indicators in link text ("RSS", "Subscribe", "Feed")
            4. Both absolute and relative URLs (include relative URLs as-is)

            Extract ALL RSS feed URLs found on the page. Return only the URLs.
            """,
        },
    },
}


def get_translation_instruction(
    base_instruction: str,
    target_language: str,
    text_fields: list[str] | None = None
) -> str:
    """Augment extraction instruction with translation requirements."""
    if text_fields is None:
        text_fields = ["title", "description", "content"]

    language_names = {
        "en": "English",
        "fr": "French",
        "es": "Spanish",
        "de": "German",
        "it": "Italian",
        "pt": "Portuguese",
        "ar": "Arabic",
        "zh": "Chinese",
        "ja": "Japanese",
    }
    language_name = language_names.get(target_language, target_language)

    translation_augmentation = f"""

TRANSLATION REQUIREMENT:
After extracting the information, translate the following text fields to
{language_name} ({target_language}):
- {", ".join(text_fields)}

Translation Guidelines:
1. Only translate the specified text fields ({", ".join(text_fields)})
2. Do NOT translate: URLs, dates, ratings, numerical values, or structured data
3. Maintain the original format and structure of the data
4. If text is already in {language_name}, return it as-is (no translation needed)
5. Ensure the translation captures the original meaning and context
6. For proper nouns (names, places, brands), transliterate appropriately
"""

    return base_instruction + translation_augmentation


def validate_config_fields(config_name: str, config: dict[str, Any]) -> bool:
    """
    Validate that configuration fields match the ScrapedItem model schema.

    Args:
        config_name: Name of the configuration being validated
        config: Configuration dictionary to validate

    Returns:
        bool: True if valid

    Raises:
        ValueError: If configuration fields don't match ScrapedItem schema
    """
    from models.item import ScrapedItem

    # Get valid field names from ScrapedItem model
    valid_fields = set(ScrapedItem.model_fields.keys())

    # Validate REQUIRED_KEYS
    required_keys = config.get("REQUIRED_KEYS", [])
    invalid_required = [key for key in required_keys if key not in valid_fields]

    if invalid_required:
        raise ValueError(
            f"Configuration '{config_name}' has invalid REQUIRED_KEYS: "
            f"{invalid_required}\n"
            f"Valid fields are: {sorted(valid_fields)}"
        )

    # Validate OPTIONAL_KEYS
    optional_keys = config.get("OPTIONAL_KEYS", [])
    invalid_optional = [key for key in optional_keys if key not in valid_fields]

    if invalid_optional:
        raise ValueError(
            f"Configuration '{config_name}' has invalid OPTIONAL_KEYS: "
            f"{invalid_optional}\n"
            f"Valid fields are: {sorted(valid_fields)}"
        )

    # Validate required config sections exist
    required_sections = ["CRAWLER_CONFIG", "LLM_CONFIG"]
    missing_sections = [section for section in required_sections if section not in config]

    if missing_sections:
        raise ValueError(
            f"Configuration '{config_name}' is missing required sections: "
            f"{missing_sections}"
        )

    # Validate CRAWLER_CONFIG has required fields
    required_crawler_fields = ["MULTI_PAGE"]
    crawler_config = config.get("CRAWLER_CONFIG", {})
    missing_crawler_fields = [
        field for field in required_crawler_fields if field not in crawler_config
    ]

    if missing_crawler_fields:
        raise ValueError(
            f"Configuration '{config_name}' CRAWLER_CONFIG is missing "
            f"required fields: {missing_crawler_fields}"
        )

    # Validate LLM_CONFIG has required fields
    required_llm_fields = ["PROVIDER", "INSTRUCTION"]
    llm_config = config.get("LLM_CONFIG", {})
    missing_llm_fields = [
        field for field in required_llm_fields if field not in llm_config
    ]

    if missing_llm_fields:
        raise ValueError(
            f"Configuration '{config_name}' LLM_CONFIG is missing "
            f"required fields: {missing_llm_fields}"
        )

    # Validate that either BASE_URL or SITES is present
    has_base_url = "BASE_URL" in config
    has_sites = "SITES" in config

    if not has_base_url and not has_sites:
        raise ValueError(
            f"Configuration '{config_name}' must have either BASE_URL or SITES"
        )

    if has_sites:
        # Validate SITES structure
        sites = config["SITES"]
        if not isinstance(sites, list) or len(sites) == 0:
            raise ValueError(
                f"Configuration '{config_name}' SITES must be a non-empty list"
            )

        for i, site in enumerate(sites):
            if not isinstance(site, dict):
                raise ValueError(
                    f"Configuration '{config_name}' SITES[{i}] must be a dictionary"
                )

            required_site_fields = ["name", "BASE_URL", "CSS_SELECTOR"]
            missing_site_fields = [
                field for field in required_site_fields if field not in site
            ]

            if missing_site_fields:
                raise ValueError(
                    f"Configuration '{config_name}' SITES[{i}] is missing "
                    f"required fields: {missing_site_fields}"
                )

    return True
