"""
Typed source configuration models for LetsCrawl.

This module defines Pydantic models for source configurations, replacing
the free-form dictionary approach with type-safe, validated configurations.
"""

from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ExtractionMode(str, Enum):
    """
    Extraction strategy modes.

    - CSS: Use CSS selectors for deterministic, fast extraction
    - LLM: Use LLM for complex extraction requiring semantic understanding
    - HYBRID: Use CSS to identify candidates, LLM for detailed extraction
    """

    CSS = "css"
    LLM = "llm"
    HYBRID = "hybrid"


class PaginationConfig(BaseModel):
    """Pagination configuration for multi-page crawls."""

    enabled: bool = Field(True, description="Enable multi-page crawling")
    max_pages: int = Field(1, ge=1, description="Maximum number of pages to crawl")
    delay_between_pages: float = Field(
        2.0, ge=0, description="Delay in seconds between page requests"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "max_pages": 3,
                "delay_between_pages": 5.0,
            }
        }
    }


class CrawlerBehaviorConfig(BaseModel):
    """Browser and crawler behavior settings."""

    headless: bool = Field(True, description="Run browser in headless mode")
    cache_enabled: bool = Field(False, description="Enable response caching")
    verbose_logging: bool = Field(True, description="Enable detailed logging")

    model_config = {
        "json_schema_extra": {
            "example": {
                "headless": True,
                "cache_enabled": False,
                "verbose_logging": True,
            }
        }
    }


class LLMExtractionConfig(BaseModel):
    """LLM extraction strategy configuration."""

    provider: str = Field(
        ...,
        description="LLM provider (e.g., 'groq/llama-3.3-70b-versatile')",
    )
    extraction_type: str = Field("schema", description="Type of extraction (always 'schema')")
    input_format: str = Field("markdown", description="Input format (always 'markdown')")
    instruction: str = Field(..., description="Natural language extraction instructions")

    model_config = {
        "json_schema_extra": {
            "example": {
                "provider": "groq/llama-3.3-70b-versatile",
                "extraction_type": "schema",
                "input_format": "markdown",
                "instruction": "Extract news article information...",
            }
        }
    }


class TranslationConfig(BaseModel):
    """Translation configuration for multi-language support."""

    enabled: bool = Field(False, description="Enable translation")
    target_language: str = Field("en", description="Target language code (e.g., 'en', 'fr')")
    text_fields: List[str] = Field(
        default_factory=lambda: ["title", "description", "content"],
        description="Fields to translate",
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "enabled": True,
                "target_language": "fr",
                "text_fields": ["title", "description", "content"],
            }
        }
    }


class SiteConfig(BaseModel):
    """Configuration for a single website source."""

    name: str = Field(..., description="Human-readable site name")
    base_url: str = Field(..., description="Starting URL for crawling")
    css_selector: str = Field(..., description="CSS selector for content elements")

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "Seneweb (Senegal)",
                "base_url": "https://www.seneweb.com",
                "css_selector": "div.post-sidebar-big",
            }
        }
    }


class SourceConfig(BaseModel):
    """
    Complete source configuration for a scraping job.

    This model replaces the free-form dictionary configuration with a
    type-safe, validated structure.
    """

    # Core configuration
    name: str = Field(..., description="Configuration name")
    extraction_mode: ExtractionMode = Field(
        ExtractionMode.LLM, description="Extraction strategy mode"
    )

    # Data requirements
    required_keys: List[str] = Field(..., description="Required field names")
    optional_keys: List[str] = Field(
        default_factory=list, description="Optional field names"
    )

    # Source configuration (either single site or multi-site)
    base_url: Optional[str] = Field(None, description="Single-site URL (mutually exclusive with sites)")
    css_selector: Optional[str] = Field(None, description="Single-site selector (mutually exclusive with sites)")
    sites: Optional[List[SiteConfig]] = Field(None, description="Multi-site configuration")

    # Behavior settings
    pagination: PaginationConfig = Field(
        default_factory=PaginationConfig, description="Pagination settings"
    )
    crawler_behavior: CrawlerBehaviorConfig = Field(
        default_factory=CrawlerBehaviorConfig, description="Crawler behavior settings"
    )

    # Extraction configuration
    llm_config: Optional[LLMExtractionConfig] = Field(None, description="LLM extraction settings")

    # Translation (optional)
    translation: Optional[TranslationConfig] = Field(None, description="Translation settings")

    @field_validator("sites")
    @classmethod
    def validate_sites(cls, v, info):
        """Ensure either single-site or multi-site configuration is used."""
        if v is not None:
            # Multi-site mode
            if len(v) == 0:
                raise ValueError("sites list cannot be empty")
            return v

        # If no sites, must have base_url and css_selector
        if info.data.get("base_url") is None or info.data.get("css_selector") is None:
            raise ValueError(
                "Must provide either sites (multi-site) or both base_url and css_selector (single-site)"
            )
        return v

    @field_validator("llm_config")
    @classmethod
    def validate_llm_config(cls, v, info):
        """Ensure LLM config is provided for LLM/HYBRID modes."""
        extraction_mode = info.data.get("extraction_mode")
        if extraction_mode in [ExtractionMode.LLM, ExtractionMode.HYBRID] and v is None:
            raise ValueError(f"llm_config is required for {extraction_mode} mode")
        return v

    @field_validator("required_keys", "optional_keys")
    @classmethod
    def validate_keys(cls, v, info):
        """Validate field names against ScrapedItem schema."""
        from models.item import ScrapedItem

        valid_fields = set(ScrapedItem.model_fields.keys())
        invalid_fields = [key for key in v if key not in valid_fields]

        if invalid_fields:
            field_name = info.field_name
            raise ValueError(
                f"Invalid {field_name}: {invalid_fields}. "
                f"Valid fields: {sorted(valid_fields)}"
            )
        return v

    def is_multi_site(self) -> bool:
        """Check if this is a multi-site configuration."""
        return self.sites is not None

    def get_crawler_config_dict(self) -> dict:
        """Convert to legacy dictionary format for backward compatibility."""
        config = {
            "MULTI_PAGE": self.pagination.enabled,
            "MAX_PAGES": self.pagination.max_pages,
            "DELAY_BETWEEN_PAGES": self.pagination.delay_between_pages,
            "HEADLESS": self.crawler_behavior.headless,
            "CACHE_ENABLED": self.crawler_behavior.cache_enabled,
            "VERBOSE_LOGGING": self.crawler_behavior.verbose_logging,
        }
        return config

    def get_llm_config_dict(self) -> dict:
        """Convert LLM config to legacy dictionary format."""
        if self.llm_config is None:
            return {}
        return {
            "PROVIDER": self.llm_config.provider,
            "EXTRACTION_TYPE": self.llm_config.extraction_type,
            "INPUT_FORMAT": self.llm_config.input_format,
            "INSTRUCTION": self.llm_config.instruction,
        }

    model_config = {
        "json_schema_extra": {
            "example": {
                "name": "news",
                "extraction_mode": "llm",
                "required_keys": ["title", "date_published"],
                "optional_keys": ["content"],
                "sites": [
                    {
                        "name": "Seneweb (Senegal)",
                        "base_url": "https://www.seneweb.com",
                        "css_selector": "div.post-sidebar-big",
                    }
                ],
                "pagination": {"enabled": True, "max_pages": 3, "delay_between_pages": 5.0},
                "crawler_behavior": {"headless": True, "cache_enabled": False, "verbose_logging": True},
                "llm_config": {
                    "provider": "groq/llama-3.3-70b-versatile",
                    "extraction_type": "schema",
                    "input_format": "markdown",
                    "instruction": "Extract news article information...",
                },
            }
        }
    }
