"""
Source registry for managing typed source configurations.

This module provides a centralized registry for source configurations,
allowing for type-safe, validated source definitions.
"""

from typing import Dict
from models.source import SourceConfig


class SourceRegistry:
    """
    Registry for managing source configurations.

    Provides methods to register, retrieve, and list source configurations.
    """

    def __init__(self):
        self._sources: Dict[str, SourceConfig] = {}

    def register(self, source: SourceConfig) -> None:
        """
        Register a source configuration.

        Args:
            source: SourceConfig to register

        Raises:
            ValueError: If a source with the same name already exists
        """
        if source.name in self._sources:
            raise ValueError(f"Source '{source.name}' already registered")
        self._sources[source.name] = source

    def get(self, name: str) -> SourceConfig:
        """
        Retrieve a source configuration by name.

        Args:
            name: Name of the source to retrieve

        Returns:
            SourceConfig: The requested source configuration

        Raises:
            KeyError: If source not found
        """
        if name not in self._sources:
            available = ", ".join(self.list_sources())
            raise KeyError(
                f"Source '{name}' not found. Available sources: {available}"
            )
        return self._sources[name]

    def list_sources(self) -> list[str]:
        """
        List all registered source names.

        Returns:
            List of source names
        """
        return list(self._sources.keys())

    def has_source(self, name: str) -> bool:
        """
        Check if a source is registered.

        Args:
            name: Name of the source to check

        Returns:
            bool: True if source exists
        """
        return name in self._sources

    def to_legacy_dict(self) -> dict:
        """
        Convert all sources to legacy dictionary format for backward compatibility.

        Returns:
            Dict mapping source names to legacy config dictionaries
        """
        legacy_configs = {}
        for name, source in self._sources.items():
            legacy_config = {
                "NAME": source.name,
                "EXTRACTION_MODE": source.extraction_mode.value,
                "REQUIRED_KEYS": source.required_keys,
                "OPTIONAL_KEYS": source.optional_keys,
                "CRAWLER_CONFIG": source.get_crawler_config_dict(),
            }

            # Add LLM config if present
            if source.llm_config:
                legacy_config["LLM_CONFIG"] = source.get_llm_config_dict()

            # Add translation config if present
            if source.translation:
                legacy_config["TRANSLATION_CONFIG"] = {
                    "ENABLED": source.translation.enabled,
                    "TARGET_LANGUAGE": source.translation.target_language,
                    "TEXT_FIELDS": source.translation.text_fields,
                }

            # Add single-site or multi-site configuration
            if source.is_multi_site():
                legacy_config["SITES"] = [
                    {
                        "name": site.name,
                        "BASE_URL": site.base_url,
                        "CSS_SELECTOR": site.css_selector,
                    }
                    for site in source.sites
                ]
            else:
                legacy_config["BASE_URL"] = source.base_url
                legacy_config["CSS_SELECTOR"] = source.css_selector

            legacy_configs[name] = legacy_config

        return legacy_configs


# Global registry instance
_registry = SourceRegistry()


def register_source(source: SourceConfig) -> None:
    """Register a source in the global registry."""
    _registry.register(source)


def get_source(name: str) -> SourceConfig:
    """Get a source from the global registry."""
    return _registry.get(name)


def list_sources() -> list[str]:
    """List all registered source names."""
    return _registry.list_sources()


def has_source(name: str) -> bool:
    """Check if a source exists in the global registry."""
    return _registry.has_source(name)


def get_registry() -> SourceRegistry:
    """Get the global registry instance."""
    return _registry
