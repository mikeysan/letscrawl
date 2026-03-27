"""
Filename generation for output files.

This module provides utilities for generating consistent output filenames
with timestamps and proper naming conventions.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional


def generate_filename(
    prefix: str,
    extension: str = "csv",
    timestamp: Optional[datetime] = None,
    *,
    include_source_name: bool = True,
    source_name: Optional[str] = None,
) -> str:
    """
    Generate a filename with timestamp for output files.

    Args:
        prefix: Filename prefix (e.g., 'articles', 'feeds')
        extension: File extension (e.g., 'csv', 'json')
        timestamp: Timestamp to use (defaults to now)
        include_source_name: Whether to include source name in filename
        source_name: Name of the source configuration

    Returns:
        Generated filename
    """
    # Use current time if not provided
    if timestamp is None:
        timestamp = datetime.utcnow()

    # Format timestamp as YYYYMMDD_HHMMSS
    timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")

    # Build filename parts
    parts = [prefix]

    if include_source_name and source_name:
        parts.append(source_name)

    parts.append(timestamp_str)

    # Join with underscores and add extension
    filename = "_".join(parts) + f".{extension}"

    return filename


def get_output_dir(base_dir: str = "output") -> Path:
    """
    Get the output directory, creating it if it doesn't exist.

    Args:
        base_dir: Base directory for outputs

    Returns:
        Path object for output directory
    """
    output_path = Path(base_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path
