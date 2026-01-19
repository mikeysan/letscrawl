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


def parse_args() -> str:
    """Parse command line arguments."""
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
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--config",
        type=str,
        required=True,
        choices=list(CONFIGS.keys()),
        help=help_text,
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available configurations and exit"
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
    return str(args.config)


def get_config(template: str) -> Dict[str, Any]:
    """Get configuration based on template name."""
    if template not in CONFIGS:
        logger.error(f"Error: Unknown configuration '{template}'")
        logger.info("\nTo see available configurations, run:")
        logger.info("python main.py --list")
        sys.exit(1)
    return CONFIGS[template]


async def crawl_items(config: dict[str, Any]) -> None:
    """
    Main function to crawl and extract data from websites.

    Args:
        config: Dictionary containing crawler configuration
    """
    # Initialize configurations
    browser_config = get_browser_config(config["CRAWLER_CONFIG"])
    llm_strategy = get_llm_strategy(config["LLM_CONFIG"])
    session_id = "crawl_session"

    # Initialize state variables
    page_number = 1
    all_items: list[dict[str, Any]] = []
    seen_titles: set[str] = set()
    
    required_keys = config["REQUIRED_KEYS"]
    multi_page = config["CRAWLER_CONFIG"]["MULTI_PAGE"]
    max_pages = config["CRAWLER_CONFIG"].get("MAX_PAGES", 1)
    delay = config["CRAWLER_CONFIG"].get("DELAY_BETWEEN_PAGES", 2)

    logger.info(f"\nStarting crawler with {config['BASE_URL']}")
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
                config["BASE_URL"],
                config["CSS_SELECTOR"],
                llm_strategy,
                session_id,
                required_keys,
                seen_titles,
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
                logger.info(
                    f"\nReached {'page limit' if multi_page else 'single page mode'}."
                    " Ending crawl."
                )
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
            item for item in all_items
            if all(key in item and item[key] for key in required_keys)
        ]
        save_items_to_csv(complete_items, "complete_items.csv")
        logger.info(
            "Saved %d complete items to 'complete_items.csv'",
            len(complete_items)
        )
    else:
        logger.warning("\nNo items were found during the crawl.")

    # Display usage statistics for the LLM strategy
    logger.info("\nLLM Usage Statistics:")
    llm_strategy.show_usage()


async def main() -> None:
    """Entry point of the script."""
    # Get configuration template from command line
    template = parse_args()
    config = get_config(template)

    try:
        await crawl_items(config)
    except KeyboardInterrupt:
        logger.warning("\nCrawling interrupted by user.")
    except Exception as e:
        logger.error(f"\nAn error occurred: {str(e)}")
    finally:
        logger.info("\nCrawling completed.")


if __name__ == "__main__":
    asyncio.run(main())
