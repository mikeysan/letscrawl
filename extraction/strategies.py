"""
Extraction strategy management for Crawl4AI.

This module handles the creation and configuration of extraction strategies
(CSS, LLM, HYBRID) for Crawl4AI.
"""

import os
from typing import Optional, Union
from crawl4ai import (
    CrawlerRunConfig,
    CacheMode,
    LLMConfig,
    LLMExtractionStrategy,
)
from models.source import (
    SourceConfig,
    ExtractionMode,
    LLMExtractionConfig,
    TranslationConfig,
)


def create_llm_strategy(
    config: LLMExtractionConfig,
    translation: Optional[TranslationConfig] = None,
) -> LLMExtractionStrategy:
    """
    Create an LLM extraction strategy for Crawl4AI.

    Args:
        config: LLM extraction configuration
        translation: Optional translation configuration

    Returns:
        LLMExtractionStrategy: Configured LLM extraction strategy
    """
    # Get API key
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it in your .env file or export it before running.\n"
            "Example: export GROQ_API_KEY='your-api-key-here'"
        )

    # Build instruction
    instruction = config.instruction

    # Apply translation if enabled
    if translation and translation.enabled:
        instruction = _apply_translation(
            instruction,
            translation.target_language,
            translation.text_fields,
        )

    return LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider=config.provider,
            api_token=api_key,
        ),
        extraction_type=config.extraction_type,
        instruction=instruction,
        input_format=config.input_format,
        verbose=True,
    )


def _apply_translation(
    base_instruction: str,
    target_language: str,
    text_fields: list[str],
) -> str:
    """
    Augment extraction instruction with translation requirements.

    Args:
        base_instruction: Original extraction instruction
        target_language: Target language code (e.g., 'en', 'fr')
        text_fields: Fields to translate

    Returns:
        str: Instruction augmented with translation requirements
    """
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


def create_crawler_run_config(
    css_selector: str,
    extraction_strategy: Optional[Union[LLMExtractionStrategy, object]] = None,
    session_id: Optional[str] = None,
    cache_mode: CacheMode = CacheMode.BYPASS,
    wait_until: str = "domcontentloaded",
) -> CrawlerRunConfig:
    """
    Create a CrawlerRunConfig for Crawl4AI.

    Args:
        css_selector: CSS selector for content elements
        extraction_strategy: Extraction strategy (LLM, CSS, etc.)
        session_id: Session identifier for browser context
        cache_mode: Cache mode for responses
        wait_until: Wait condition for page load

    Returns:
        CrawlerRunConfig: Configured crawler run settings
    """
    config = CrawlerRunConfig(
        css_selector=css_selector,
        cache_mode=cache_mode,
        session_id=session_id,
        wait_until=wait_until,
    )

    # Add extraction strategy if provided
    if extraction_strategy is not None:
        config.extraction_strategy = extraction_strategy

    return config


def create_extraction_strategy(
    source_config: SourceConfig,
    translation: Optional[TranslationConfig] = None,
) -> Optional[Union[LLMExtractionStrategy, object]]:
    """
    Create the appropriate extraction strategy based on source configuration.

    This is the main strategy factory that chooses between CSS, LLM, and HYBRID
    extraction modes.

    Args:
        source_config: Typed source configuration
        translation: Optional translation configuration

    Returns:
        Extraction strategy object or None (for CSS-only mode)

    Raises:
        ValueError: If extraction mode is not supported
    """
    mode = source_config.extraction_mode

    if mode == ExtractionMode.CSS:
        # CSS-only extraction (not yet implemented - return None)
        # TODO: Implement CssExtractionStrategy when Crawl4AI supports it
        return None

    elif mode == ExtractionMode.LLM:
        # LLM extraction
        if source_config.llm_config is None:
            raise ValueError("LLM config is required for LLM extraction mode")
        return create_llm_strategy(source_config.llm_config, translation)

    elif mode == ExtractionMode.HYBRID:
        # HYBRID extraction (CSS + LLM)
        # For now, fall back to LLM-only
        # TODO: Implement true HYBRID mode with CSS pre-filtering
        if source_config.llm_config is None:
            raise ValueError("LLM config is required for HYBRID extraction mode")
        return create_llm_strategy(source_config.llm_config, translation)

    else:
        raise ValueError(f"Unsupported extraction mode: {mode}")
