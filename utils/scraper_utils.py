import json
import os
from typing import Dict, List, Set, Tuple, Any

from crawl4ai import (
    AsyncWebCrawler,
    BrowserConfig,
    CacheMode,
    CrawlerRunConfig,
    LLMExtractionStrategy,
)

from models.item import ScrapedItem
from utils.data_utils import is_complete_item, is_duplicate_item


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
        verbose=config.get("VERBOSE_LOGGING", True)
    )


def get_llm_strategy(config: Dict[str, Any]) -> LLMExtractionStrategy:
    """
    Returns the configuration for the language model extraction strategy.

    Args:
        config: Dictionary containing LLM configuration settings

    Returns:
        LLMExtractionStrategy: The settings for how to extract data using LLM.
    """
    return LLMExtractionStrategy(
        provider=config.get("PROVIDER", "groq/deepseek-r1-distill-llama-70b"),
        api_token=os.getenv("GROQ_API_KEY"),
        schema=ScrapedItem.model_json_schema(),
        extraction_type=config.get("EXTRACTION_TYPE", "schema"),
        instruction=config.get("INSTRUCTION", (
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
        )),
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
            wait_until="networkidle",  # Wait for network to be idle
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
        return any(phrase.lower() in result.cleaned_html.lower() 
                  for phrase in no_results_phrases)
    else:
        print(f"Error checking for no results: {result.error_message}")

    return False


async def fetch_and_process_page(
    crawler: AsyncWebCrawler,
    page_number: int,
    base_url: str,
    css_selector: str,
    llm_strategy: LLMExtractionStrategy,
    session_id: str,
    required_keys: List[str],
    seen_titles: Set[str],
) -> Tuple[List[dict], bool]:
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
    
    print(f"\nProcessing page {page_number}: {url}")

    # Check for no results
    no_results = await check_no_results(crawler, url, session_id)
    if no_results:
        print("No results found on this page.")
        return [], True

    # Fetch page content with additional wait time
    result = await crawler.arun(
        url=url,
        config=CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=llm_strategy,
            css_selector=css_selector,
            session_id=session_id,
            wait_until="networkidle"  # Wait for network to be idle
        ),
    )

    if not result.success:
        print(f"Error fetching page {page_number}: {result.error_message}")
        return [], False

    if not result.extracted_content:
        print(f"No content extracted from page {page_number}.")
        return [], False

    # Parse extracted content
    try:
        extracted_data = json.loads(result.extracted_content)
        if not extracted_data:
            print(f"No data found on page {page_number}.")
            return [], False
            
        if True:  # Always show extracted data for debugging
            print(f"Raw extracted data from page {page_number}:")
            print(json.dumps(extracted_data, indent=2))
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from page {page_number}: {str(e)}")
        return [], False

    # Process items
    complete_items = []
    for item in extracted_data:
        # Remove error key if it's False
        if item.get("error") is False:
            item.pop("error", None)

        # Get the title (main identifier) of the item
        title = item.get("title")
        if not title:
            print("Item found without a title, skipping...")
            continue

        # Validate item data
        if not is_complete_item(item, required_keys):
            missing_keys = [key for key in required_keys if key not in item or not item[key]]
            print(f"Incomplete data for '{title}'")
            print(f"Missing required fields: {', '.join(missing_keys)}")
            continue

        if is_duplicate_item(title, seen_titles):
            print(f"Duplicate found: {title}")
            continue

        # Add item to results
        seen_titles.add(title)
        complete_items.append(item)

    print(f"\nFound {len(complete_items)} valid items on page {page_number}.")
    return complete_items, False
