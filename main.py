import argparse
import asyncio
import sys
from typing import Any, Dict

from crawl4ai import AsyncWebCrawler
from dotenv import load_dotenv

# Import base configurations
from config import CONFIGS

# Import custom configurations
try:
    from my_configs import *  # noqa: F403
except ImportError:
    from utils.logger import logger

    logger.info("No custom configurations found. Using default templates only.")

from utils.data_utils import save_items_to_csv
from utils.logger import logger
from utils.scraper_utils import (
    fetch_and_process_page,
    get_browser_config,
    get_llm_strategy,
)

load_dotenv()


def parse_args() -> tuple[str, list[str] | None, bool, str]:
    """Parse command line arguments.

    Returns:
        tuple: (config_name, urls, translate, target_language)
    """
    # Get available configurations
    default_configs = ["dental", "minimal", "detailed"]
    custom_configs = [k for k in CONFIGS.keys() if k not in default_configs]

    # Create help text
    help_text = "Configuration to use. Available options:\n"
    help_text += "\nDefault templates:\n"
    for config in default_configs:
        if config in CONFIGS:
            help_text += f"  {config}: For {config} scraping\n"

    if custom_configs:
        help_text += "\nCustom configurations:\n"
        for config in custom_configs:
            help_text += f"  {config}: Custom configuration\n"

    parser = argparse.ArgumentParser(
        description="Deep Seek Web Crawler",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        choices=list(CONFIGS.keys()),
        help=help_text,
    )
    parser.add_argument(
        "--list", action="store_true", help="List available configurations and exit"
    )
    parser.add_argument(
        "--urls", nargs="+", help="URLs to scan for RSS feeds (only for --config rss)"
    )
    parser.add_argument(
        "--translate",
        action="store_true",
        help="Enable translation of extracted content to target language",
    )
    parser.add_argument(
        "--target-language",
        type=str,
        default="en",
        help="Target language for translation (default: en, e.g., 'fr' for French, "
        "'es' for Spanish)",
    )

    args = parser.parse_args()

    if args.list:
        logger.info("\nAvailable configurations:")
        logger.info("\nDefault templates:")
        for config in default_configs:
            if config in CONFIGS:
                logger.info(f"  {config}: For {config} scraping")
        if custom_configs:
            logger.info("\nCustom configurations:")
            for config in custom_configs:
                logger.info(f"  {config}: Custom configuration")
        sys.exit(0)

    # mypy: args.config is guaranteed to be str when --list is not used
    return (
        str(args.config),
        getattr(args, "urls", None),
        args.translate,
        args.target_language,
    )


def get_config(template: str) -> Dict[str, Any]:
    """Get configuration based on template name."""
    if template not in CONFIGS:
        logger.error(f"Error: Unknown configuration '{template}'")
        logger.info("\nTo see available configurations, run:")
        logger.info("python main.py --list")
        sys.exit(1)
    return CONFIGS[template]


async def crawl_items(
    config: dict[str, Any],
    rss_mode: bool = False,
    translate: bool = False,
    target_language: str = "en",
) -> None:
    """
    Main function to crawl and extract data from websites.

    Args:
        config: Dictionary containing crawler configuration
        rss_mode: Whether to enable RSS feed validation mode
        translate: Whether to enable translation of extracted content
        target_language: Target language code for translation
    """
    # Initialize configurations
    browser_config = get_browser_config(config["CRAWLER_CONFIG"])
    llm_strategy = get_llm_strategy(
        config["LLM_CONFIG"], translate=translate, target_language=target_language
    )
    session_id = "crawl_session"

    # Initialize state variables
    all_items: list[dict[str, Any]] = []
    seen_titles: set[str] = set()

    required_keys = config["REQUIRED_KEYS"]
    multi_page = config["CRAWLER_CONFIG"]["MULTI_PAGE"]
    max_pages = config["CRAWLER_CONFIG"].get("MAX_PAGES", 1)
    delay = config["CRAWLER_CONFIG"].get("DELAY_BETWEEN_PAGES", 2)

    # Check if config uses SITES list (multi-site crawling) or single BASE_URL
    if "SITES" in config:
        sites = config["SITES"]
        logger.info(f"\nStarting multi-site crawler with {len(sites)} sites")
        logger.info("Required fields: %s", ", ".join(required_keys))
        logger.info("Optional fields: %s", ", ".join(config.get("OPTIONAL_KEYS", [])))
        logger.info("\nInitializing crawler...\n")

        async with AsyncWebCrawler(config=browser_config) as crawler:
            for site in sites:
                site_name = site.get("name", "Unknown site")
                base_url = site["BASE_URL"]
                css_selector = site["CSS_SELECTOR"]

                logger.info(f"\n{'=' * 60}")
                logger.info(f"Crawling: {site_name}")
                logger.info(f"URL: {base_url}")
                logger.info(f"Mode: {'Multi-page' if multi_page else 'Single-page'}")
                if multi_page:
                    logger.info(f"Max pages: {max_pages}")
                logger.info(f"{'=' * 60}\n")

                page_number = 1
                while True:
                    # Fetch and process data from the current page
                    items, no_results_found = await fetch_and_process_page(
                        crawler,
                        page_number,
                        base_url,
                        css_selector,
                        llm_strategy,
                        session_id,
                        required_keys,
                        seen_titles,
                        rss_validation=rss_mode,
                    )

                    if no_results_found:
                        logger.info(
                            "\nNo more items found. Ending crawl for this site."
                        )
                        break

                    if not items:
                        logger.warning(f"\nNo items extracted from page {page_number}.")
                        break

                    # Add site source to each item
                    for item in items:
                        item["source_site"] = site_name

                    # Add the items from this page to the total list
                    all_items.extend(items)

                    # Check if we should continue to next page
                    if not multi_page or page_number >= max_pages:
                        mode = "page limit" if multi_page else "single page mode"
                        logger.info(f"\nReached {mode}. Ending crawl for this site.")
                        break

                    page_number += 1
                    logger.info(f"\nMoving to page {page_number}...")
                    await asyncio.sleep(delay)

                logger.info(
                    f"\nCompleted crawling {site_name}. "
                    f"Total items so far: {len(all_items)}"
                )
                await asyncio.sleep(delay)  # Delay between sites
    else:
        # Single site crawling (original behavior)
        page_number = 1
        base_url = config["BASE_URL"]
        css_selector = config["CSS_SELECTOR"]

        logger.info(f"\nStarting crawler with {base_url}")
        logger.info(f"Mode: {'Multi-page' if multi_page else 'Single-page'}")
        if multi_page:
            logger.info(f"Max pages: {max_pages}")
        logger.info("Required fields: %s", ", ".join(required_keys))
        logger.info("Optional fields: %s", ", ".join(config.get("OPTIONAL_KEYS", [])))
        logger.info("\nInitializing crawler...\n")

        # Start the web crawler context
        async with AsyncWebCrawler(config=browser_config) as crawler:
            while True:
                # Fetch and process data from the current page
                items, no_results_found = await fetch_and_process_page(
                    crawler,
                    page_number,
                    base_url,
                    css_selector,
                    llm_strategy,
                    session_id,
                    required_keys,
                    seen_titles,
                    rss_validation=rss_mode,
                )

                if no_results_found:
                    logger.info("\nNo more items found. Ending crawl.")
                    break

                if not items:
                    logger.warning(f"\nNo items extracted from page {page_number}.")
                    break

                # Add the items from this page to the total list
                all_items.extend(items)

                # Check if we should continue to next page
                if not multi_page or page_number >= max_pages:
                    mode = "page limit" if multi_page else "single page mode"
                    logger.info(f"\nReached {mode}. Ending crawl.")
                    break

                page_number += 1
                logger.info(f"\nMoving to page {page_number}...")
                await asyncio.sleep(delay)

    # Save the collected items to CSV files
    if all_items:
        # Save all items
        save_items_to_csv(all_items, "items.csv")
        logger.info(f"\nSaved {len(all_items)} items to 'items.csv'")

        # Save complete items (those with all required fields)
        complete_items = [
            item
            for item in all_items
            if all(key in item and item[key] for key in required_keys)
        ]
        save_items_to_csv(complete_items, "complete_items.csv")
        logger.info(
            "Saved %d complete items to 'complete_items.csv'", len(complete_items)
        )
    else:
        logger.warning("\nNo items were found during the crawl.")

    # Display usage statistics for the LLM strategy
    logger.info("\nLLM Usage Statistics:")
    llm_strategy.show_usage()


async def main() -> None:
    """Entry point of the script."""
    # Get configuration template from command line
    template, urls, translate, target_language = parse_args()
    config = get_config(template)

    # If --urls provided with rss config, override SITES list
    if template == "rss" and urls:
        # Get the CSS selector from the first site in the default config
        css_selector = CONFIGS["rss"]["SITES"][0]["CSS_SELECTOR"]
        # Create dynamic site entries for each URL
        CONFIGS["rss"]["SITES"] = [
            {"name": url, "BASE_URL": url, "CSS_SELECTOR": css_selector} for url in urls
        ]
        # Update config reference
        config = CONFIGS["rss"]
        logger.info(f"Using custom URLs: {', '.join(urls)}")

    # Detect if we're in RSS mode
    rss_mode = template == "rss" or config.get("REQUIRED_KEYS") == ["url"]

    # Validate LLM configuration before starting crawl
    try:
        from utils.scraper_utils import validate_llm_config

        validate_llm_config(config["LLM_CONFIG"])
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)

    try:
        await crawl_items(
            config,
            rss_mode=rss_mode,
            translate=translate,
            target_language=target_language,
        )
    except KeyboardInterrupt:
        logger.warning("\nCrawling interrupted by user.")
    except Exception as e:
        logger.error(f"\nAn error occurred: {str(e)}")
    finally:
        logger.info("\nCrawling completed.")


if __name__ == "__main__":
    asyncio.run(main())
