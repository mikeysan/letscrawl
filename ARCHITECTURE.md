# Web Crawler Application Architecture

## Overview

This is a Python-based web scraping application designed to extract structured data from websites using LLM-powered extraction. The application supports multiple crawling configurations for different use cases (dental clinics, news sites, RSS feeds, etc.) and includes features like pagination handling, duplicate detection, data validation, and CSV export.

## Core Components

### 1. Main Entry Point (`main.py`)
- Command-line interface using argparse
- Configuration loading and validation
- Orchestrates the crawling process
- Handles RSS mode special cases
- Manages translation functionality

### 2. Configuration System (`config.py`)
- Default configuration template (`DEFAULT_CONFIG`)
- Predefined configurations for different use cases:
  - Dental clinics scraping
  - Minimal configuration (required fields only)
  - Detailed configuration (extended fields)
  - Test configuration (for local HTML files)
  - Books test configuration (Goodreads scraping)
  - News crawler (multi-site African news)
  - RSS feed finder
- Configuration inheritance pattern using dictionary merging
- Translation instruction generation

### 3. Crawling Engine (`crawler.py`)
- Main crawling logic in `crawl_items()` function
- Supports both single-site and multi-site crawling
- Handles pagination with configurable delays
- Manages session state and deduplication
- Saves results to CSV files
- Displays LLM usage statistics

### 4. Scraper Utilities (`utils/scraper_utils.py`)
- Browser configuration creation
- LLM strategy configuration with translation support
- Page fetching and processing
- No-results detection
- RSS feed validation
- Item processing pipeline (deduplication, completeness checking)
- Data validation helpers

### 5. Data Utilities (`utils/data_utils.py`)
- CSV saving functionality
- Item completeness validation
- Duplicate detection
- Data cleaning utilities

### 6. Logging (`utils/logger.py`)
- Centralized logging configuration
- Console and file logging handlers

### 7. Data Models (`models/item.py`)
- Pydantic model defining the scraped item structure
- Schema validation for extracted data

### 8. Testing Suite (`tests/`)
- Unit tests for fetcher, URL utilities, security, and crawler components
- Pytest configuration

## Key Features

### Multi-Mode Crawling
- **Single-site crawling**: Extract data from one website with pagination
- **Multi-site crawling**: Process multiple websites with different selectors
- **RSS feed discovery**: Find and validate RSS/Atom feeds on websites
- **Translation support**: Extract content and translate to target languages

### Configuration Flexibility
- Inheritance-based configuration system
- Per-configuration customization of:
  - CSS selectors
  - Required/optional fields
  - Crawler settings (pagination, delays, headless mode)
  - LLM extraction instructions
  - Translation settings

### Robust Data Processing
- Duplicate detection based on item identifiers
- Completeness validation for required fields
- Error handling and recovery
- RSS feed validation
- Data cleaning and normalization

### Observability
- Detailed logging throughout the crawling process
- LLM usage statistics tracking
- Progress reporting during crawling
- Error reporting with context

## Data Flow

1. **Configuration Loading**: 
   - Command-line arguments parsed to select configuration
   - Base configuration loaded from `config.py`
   - Custom configurations optionally loaded from `my_configs.py`

2. **Initialization**:
   - Browser configuration created from crawler settings
   - LLM strategy configured with extraction instructions
   - Translation applied if requested

3. **Crawling Process**:
   - For each site (single or multiple):
     - Process pages sequentially with pagination
     - Fetch page content using crawl4ai
     - Extract structured data using LLM
     - Validate and deduplicate items
     - Apply translation if enabled
     - Collect valid items

4. **Post-processing**:
   - Save all items to CSV
   - Filter and save complete items (all required fields present)
   - Display LLM usage statistics
   - Clean shutdown

## Dependencies

### Primary Dependencies
- `crawl4ai`: Web crawling and LLM extraction framework
- `pydantic`: Data validation and settings management
- `python-dotenv`: Environment variable management
- `requests`: HTTP requests for RSS validation
- `openai`: LLM API access (via Groq provider)

### Development Dependencies
- `pytest`: Testing framework
- `mypy`: Static type checking
- `ruff`: Linting and code formatting

## Extension Points

1. **New Configurations**: Add new use cases by extending `CONFIGS` in `config.py`
2. **Custom Selectors**: Modify CSS selectors for different site structures
3. **Field Requirements**: Adjust REQUIRED_KEYS and OPTIONAL_KEYS per use case
4. **Translation**: Enable/disable translation and set target languages
5. **Crawler Behavior**: Adjust pagination, delays, caching, and headless mode
6. **LLM Providers**: Change LLM provider/model in configuration
7. **Output Formats**: Modify CSV saving in `data_utils.py` for different formats

## Security Considerations

- API keys loaded from environment variables (not hardcoded)
- Input validation for URLs and configuration values
- Error handling prevents information leakage
- RSS validation includes basic XML parsing safety