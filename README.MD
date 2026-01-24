# LetsCrawl - Intelligent Web Crawler 🤖

A powerful and flexible web crawler that uses Groq's LLM API to intelligently extract structured data from any website. Perfect for data scientists, researchers, and developers who need to gather and analyze web data.

## ✨ Features

🧠 **Intelligent Extraction**
- Uses Groq's LLM API for smart data parsing
- Understands context and extracts meaningful data
- Handles various data formats and structures

🎯 **Flexible Targeting**
- CSS selector-based element targeting
- Multi-page crawling support
- Multi-site crawling with different selectors
- Configurable delay between requests
- Cache support for faster development

🌍 **Translation Support**
- Optional translation of extracted content during extraction
- Single-pass: extract + translate together in one API call
- Support for multiple target languages
- Preserves non-translatable fields (URLs, dates, ratings)

🛠️ **Easy Configuration**
- Ready-to-use templates for common use cases
- Customizable extraction rules
- Configurable browser settings
- Headless mode support

📊 **Data Management**
- Automatic CSV file generation
- Duplicate detection
- Required field validation
- Structured data output

🔒 **Safe & Respectful**
- Configurable delays between requests
- Cache mechanism to reduce server load

## Getting Started

### 1. Environment Setup

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your Groq API key:
   ```
   GROQ_API_KEY=your_api_key_here
   ```
   Get your API key from [Groq Console](https://console.groq.com)

### 2. Available Configuration Templates 🔧

List all available configurations:
```bash
python main.py --list
```

Built-in configurations:

- **`dental`**: Dental clinic listings (default template)
- **`minimal`**: Single-page scraping with minimal output
- **`detailed`**: Extended multi-page crawling with more fields
- **`news`**: Multi-site news article scraping (Seneweb, The Namibian, New Times)
- **`rss`**: RSS feed URL finder for websites

### 3. Running the Crawler

Basic usage:
```bash
# List available configurations
python main.py --list

# Run with a specific configuration
python main.py --config news
python main.py --config dental
python main.py --config rss
```

#### Translation Feature

Translate extracted content to English (default):
```bash
python main.py --config news --translate
```

Translate to a specific language:
```bash
# Translate to French
python main.py --config news --translate --target-language fr

# Translate to Spanish
python main.py --config news --translate --target-language es

# Supported languages: en, fr, es, de, it, pt, ar, zh, ja
```

#### Custom URLs (RSS Config)

Override default sites with custom URLs:
```bash
python main.py --config rss --urls https://cnn.com https://bbc.com
python main.py --config news --urls https://www.seneweb.com
```

### 4. Output

The crawler generates two CSV files:
- `items.csv`: Contains all scraped items
- `complete_items.csv`: Contains only items with all required fields

### 5. Creating Custom Configurations

To create a new configuration, open `config.py` and add to the `CONFIGS` dictionary:

```python
"my_config": {
    **DEFAULT_CONFIG,  # Inherit from default
    "BASE_URL": "https://example.com",
    "CSS_SELECTOR": "div.item",
    "REQUIRED_KEYS": ["name", "price"],
    "OPTIONAL_KEYS": ["description", "rating"],
    "CRAWLER_CONFIG": {
        **DEFAULT_CONFIG["CRAWLER_CONFIG"],
        "MULTI_PAGE": False,
        "MAX_PAGES": 5,
        "DELAY_BETWEEN_PAGES": 2,
    },
    "LLM_CONFIG": {
        **DEFAULT_CONFIG["LLM_CONFIG"],
        "INSTRUCTION": """
        Extract product information from each item:
        - Name: Product title
        - Price: Current price
        - Description: Product description
        - Rating: Numerical rating if available
        """
    }
}
```

Or create a separate `my_configs.py` file:
```python
from config import DEFAULT_CONFIG, CONFIGS

CONFIGS["my_custom_config"] = {
    **DEFAULT_CONFIG,
    "BASE_URL": "https://example.com",
    # ... rest of configuration
}
```

#### Configuration Options

- **`BASE_URL`**: Starting URL for crawling
- **`CSS_SELECTOR`**: CSS selector to identify items on the page
- **`REQUIRED_KEYS`**: Fields that must be present (filtering)
- **`OPTIONAL_KEYS`**: Additional fields to extract if available
- **`SITES`**: For multi-site crawling, list of sites with different selectors
- **`CRAWLER_CONFIG`**: Browser and pagination settings
  - `MULTI_PAGE`: Enable multi-page crawling
  - `MAX_PAGES`: Maximum number of pages to crawl
  - `DELAY_BETWEEN_PAGES`: Delay in seconds between requests
  - `HEADLESS`: Run browser in headless mode
  - `CACHE_ENABLED`: Enable caching for faster development
  - `VERBOSE_LOGGING`: Enable detailed logging
- **`LLM_CONFIG`**: LLM extraction settings
  - `PROVIDER`: LLM provider (default: groq/llama-3.3-70b-versatile)
  - `EXTRACTION_TYPE`: Type of extraction (schema)
  - `INPUT_FORMAT`: Input format (markdown)
  - `INSTRUCTION`: Custom extraction instructions
- **`TRANSLATION_CONFIG`**: Translation settings
  - `ENABLED`: Enable translation by default for this config
  - `TARGET_LANGUAGE`: Default target language code
  - `TEXT_FIELDS`: List of fields to translate

### 6. Troubleshooting

If you encounter issues:
1. Check your `GROQ_API_KEY` in .env file
2. Ensure all dependencies are installed: `pip install -r requirements.txt`
3. Check that CSS selectors match the target website structure
4. Use browser DevTools to inspect the page and find correct selectors
5. Try with `HEADLESS: False` in crawler config to see the browser
6. Check terminal output for detailed error messages

## License

See LICENSE file for details.
