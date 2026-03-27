"""
Extraction layer for LetsCrawl.

This package isolates Crawl4AI usage and provides a clean interface for
executing extraction jobs with different strategies (CSS, LLM, HYBRID).
"""

from extraction.browser import create_browser_config
from extraction.strategies import (
    create_llm_strategy,
    create_crawler_run_config,
    create_extraction_strategy,
)
from extraction.runner import ExtractionRunner

__all__ = [
    "create_browser_config",
    "create_llm_strategy",
    "create_crawler_run_config",
    "create_extraction_strategy",
    "ExtractionRunner",
]
