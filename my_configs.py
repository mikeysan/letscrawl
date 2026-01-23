import os

from config import CONFIGS
from utils.logger import logger

# Get the current directory
current_dir = os.path.dirname(os.path.abspath(__file__))
# Hold this for me.
# #books.table .cover .value img <-- css from goodreads to get the book cover

# Configuration for local test products
test_config = {
    "BASE_URL": "https://www.etsy.com/uk/",
    "CSS_SELECTOR": ".product-card",  # Product card container
    "REQUIRED_KEYS": [
        "title",      # Product name
        "price",      # Product price
        "url"         # Product URL
    ],
    "OPTIONAL_KEYS": [
        "description"
    ],
    "CRAWLER_CONFIG": {
        "MULTI_PAGE": False,  # Single page
        "HEADLESS": True,    # Show browser for demonstration
        "VERBOSE_LOGGING": True,
        "DELAY_BETWEEN_PAGES": 1
    },
    "LLM_CONFIG": {
        "PROVIDER": "groq/deepseek-r1-distill-llama-70b",
        "EXTRACTION_TYPE": "schema",
        "INPUT_FORMAT": "markdown",
        "INSTRUCTION": """
        Extract product information with these details:
        
        Required Information:
        - Product title (from .product-title)
        - Price (from .product-price, convert to numerical value)
        - Product URL (from a[href], make absolute)
        
        Optional Information:
        - Description (from .product-description)
        
        Specific Instructions:
        - Remove '$' from prices and convert to numerical values (e.g., "19.99")
        - For URLs, make them absolute by adding 'http://localhost' to relative paths
        - Clean up any extra whitespace from text
        
        Format the output as structured data following the schema.
        """
    }
}

# Add to CONFIGS dictionary
CONFIGS['etsy'] = test_config

# Show helpful message when this file is run directly
if __name__ == "__main__":
    excluded = ["products", "articles", "businesses", "minimal"]
    custom_configs = [k for k in CONFIGS.keys() if k not in excluded]
    print("Loaded custom configurations:", custom_configs)
    logger.info("\nTo use these configurations, run:")
    logger.info("python main.py --config CONFIG_NAME")
    logger.info("\nAvailable custom configurations:")
    for config in CONFIGS.keys():
        if config not in ["products", "articles", "businesses", "minimal"]:
            logger.info(f"- {config}")
