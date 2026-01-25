import json
import os
import xml.etree.ElementTree as ET
from typing import Any, Dict

import requests
from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMConfig,
    LLMExtractionStrategy,
)

from models.item import ScrapedItem
from utils.data_utils import is_complete_item, is_duplicate_item
from utils.logger import logger


def validate_rss_feed(url: str) -> bool:
    """
    Validate an RSS feed URL by fetching and parsing it.

    Args:
        url: The RSS feed URL to validate.

    Returns:
        bool: True if the RSS feed is valid, False otherwise.
    """
    try:
        response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
        if response.status_code != 200:
            logger.info(f"RSS feed returned status {response.status_code}: {url}")
            return False

        # Try to parse as XML
        ET.fromstring(response.content)
        logger.info(f"RSS feed validated successfully: {url}")
        return True
    except ET.ParseError as e:
        logger.info(f"RSS feed XML parsing failed: {url} - {e}")
        return False
    except Exception as e:
        logger.info(f"RSS feed validation failed: {url} - {e}")
        return False


def get_browser_config(config: Dict[str, Any]) -> BrowserConfig:
    """
    Returns the browser configuration for the crawler.

    Args:
        config: Dictionary containing crawler configuration settings

    Returns:
        BrowserConfig: The configuration settings for the browser.
    """
    return BrowserConfig(
        browser_type="chromium",
        headless=config.get("HEADLESS", True),
        verbose=config.get("VERBOSE_LOGGING", True),
    )


def validate_llm_config(config: Dict[str, Any]) -> None:
    """
    Validate that LLM configuration is complete and API key is set.

    Args:
        config: Dictionary containing LLM configuration settings

    Raises:
        ValueError: If GROQ_API_KEY environment variable is not set
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or export it before running.\n"
            "Example: export GROQ_API_KEY='your-api-key-here'"
        )

    provider = config.get("PROVIDER", "groq/llama-3.3-70b-versatile")
    logger.info(f"LLM provider: {provider}")
    logger.info(f"API key prefix: {api_key[:8]}...")


def get_llm_strategy(
    config: Dict[str, Any], translate: bool = False, target_language: str = "en"
) -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Args:
        config: Dictionary containing LLM configuration settings
        translate: Whether to enable translation (default: False)
        target_language: Target language code for translation (default: "en")

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    validate_llm_config(config)

    base_instruction = config.get(
        "INSTRUCTION",
        (
            "Extract information from the content with these details:\n"
            "- Title/name of the item\n"
            "- Description or main content\n"
            "- Any URLs present\n"
            "- Dates if available\n"
            "- Categories or types\n"
            "- Tags or labels\n"
            "- Ratings if present\n"
            "- Price information\n"
            "- Location/address if applicable\n"
            "- Contact information\n"
            "- Any other relevant metadata\n"
            "\nFormat the output as structured data following the schema."
        ),
    )

    # Apply translation if enabled
    if translate:
        from config import get_translation_instruction

        translation_config = config.get("TRANSLATION_CONFIG", {})
        text_fields = translation_config.get(
            "TEXT_FIELDS", ["title", "description", "content"]
        )

        final_instruction = get_translation_instruction(
            base_instruction, target_language, text_fields
        )
        logger.info(f"Translation enabled: {text_fields} → {target_language}")
    else:
        final_instruction = base_instruction

    return LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider=config.get("PROVIDER", "groq/deepseek-r1-distill-llama-70b"),
            api_token=os.getenv("GROQ_API_KEY"),
        ),
        schema=ScrapedItem.model_json_schema(),
        extraction_type=config.get("EXTRACTION_TYPE", "schema"),
        instruction=final_instruction,
        input_format=config.get("INPUT_FORMAT", "markdown"),
        verbose=True,
    )


async def check_no_results(
    crawler: AsyncWebCrawler,
    url: str,
    session_id: str,
) -> bool:
    """
    Checks if a "No Results Found" message is present on the page.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        url (str): The URL to check.
        session_id (str): The session identifier.

    Returns:
        bool: True if "No Results Found" message is found, False otherwise.
    """
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            session_id=session_id,
            wait_until="domcontentloaded",  # Wait for DOM content to load
        ),
    )

    if result.success:
        # Check for common "no results" indicators
        no_results_phrases = [
            "No Results Found",
            "No matches found",
            "Nothing found",
            "No items found",
            "0 results",
            "No results",
            "Empty",
        ]
        return any(
            phrase.lower() in result.cleaned_html.lower()
            for phrase in no_results_phrases
        )
    else:
        logger.info(f"Error checking for no results: {result.error_message}")

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: list[str],
    seen_titles: set[str],
    rss_validation: bool = False,
) -> tuple[list[dict[str, str]], bool]:
    """
    Fetches and processes a single page of items.

    Args:
        crawler (AsyncWebCrawler): The web crawler instance.
        page_number (int): The page number to fetch.
        base_url (str): The base URL of the website.
        css_selector (str): The CSS selector to target the content.
        llm_strategy (LLMExtractionStrategy): The LLM extraction strategy.
        session_id (str): The session identifier.
        required_keys (List[str]): List of required keys in the item data.
        seen_titles (Set[str]): Set of item titles that have already been seen.
        rss_validation (bool): Whether to validate RSS feed URLs. Default False.

    Returns:
        Tuple[List[dict], bool]:
            - List[dict]: A list of processed items from the page.
            - bool: A flag indicating if the "No Results Found" message was encountered.
    """
    # Construct URL for pagination
    url = base_url
    if page_number > 1:
        # Common pagination patterns
        if "?" in base_url:
            url = f"{base_url}&page={page_number}"
        else:
            url = f"{base_url}?page={page_number}"

    logger.info(f"\nProcessing page {page_number}: {url}")

    # Check for no results
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        logger.info("No results found on this page.")
        return [], True

    # Fetch page content with additional wait time
    logger.debug(f"Starting LLM extraction for page {page_number}...")
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id,
            wait_until="domcontentloaded",  # Wait for DOM content to load
        ),
    )
    logger.debug(f"LLM extraction completed for page {page_number}")

    if not result.success:
        logger.info(f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    if not result.extracted_content:
        logger.warning(
            f"No content extracted from page {page_number}. "
            f"CSS selector '{css_selector}' may have found 0 elements."
        )
        return [], False

    # Parse extracted content
    try:
        extracted_data = json.loads(result.extracted_content)
        if not extracted_data:
            logger.info(f"No data found on page {page_number}.")
            return [], False

        if True:  # Always show extracted data for debugging
            logger.info(f"Raw extracted data from page {page_number}:")
            print(json.dumps(extracted_data, indent=2))

    except json.JSONDecodeError as e:
        logger.info(f"Error parsing JSON from page {page_number}: {str(e)}")
        return [], False

    # Process items
    complete_items = []
    skipped_no_title = 0
    skipped_incomplete = 0
    skipped_duplicate = 0
    skipped_invalid_rss = 0

    for item in extracted_data:
        # Remove error key if it's False
        if item.get("error") is False:
            item.pop("error", None)

        # For RSS validation mode, use URL as identifier; otherwise use title
        if rss_validation:
            url = item.get("url")
            if not url:
                skipped_no_title += 1
                logger.info("RSS feed found without URL, skipping...")
                continue

            # Validate RSS feed URL
            if not validate_rss_feed(url):
                skipped_invalid_rss += 1
                item["feed_valid"] = False
                logger.info(f"Invalid RSS feed: {url}")
                # Optionally still include invalid feeds with feed_valid=False
                # For now, skip them
                continue

            item["feed_valid"] = True
            # Use URL as identifier for RSS feeds
            identifier = url
        else:
            # Get the title (main identifier) of the item
            identifier = item.get("title")
            if not identifier:
                skipped_no_title += 1
                logger.info("Item found without a title, skipping...")
                continue

        # Validate item data
        if not is_complete_item(item, required_keys):
            skipped_incomplete += 1
            missing_keys = [
                key for key in required_keys if key not in item or not item[key]
            ]
            logger.info(f"Incomplete data for '{identifier}'")
            logger.info(f"Missing required fields: {', '.join(missing_keys)}")
            continue

        if is_duplicate_item(identifier, seen_titles):
            skipped_duplicate += 1
            logger.info(f"Duplicate found: {identifier}")
            continue

        # Add item to results
        seen_titles.add(identifier)
        complete_items.append(item)

    # Log summary statistics
    total_items = len(extracted_data)
    if rss_validation:
        logger.info(
            f"\nExtracted {total_items} RSS feed URLs: "
            f"{len(complete_items)} valid, "
            f"{skipped_no_title} no URL, "
            f"{skipped_invalid_rss} invalid RSS feeds, "
            f"{skipped_duplicate} duplicates"
        )
    else:
        logger.info(
            f"\nExtracted {total_items} items: "
            f"{len(complete_items)} valid, "
            f"{skipped_no_title} no title, "
            f"{skipped_incomplete} incomplete, "
            f"{skipped_duplicate} duplicates"
        )
    return complete_items, False
