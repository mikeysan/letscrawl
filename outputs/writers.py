"""
Output writers for exporting normalized results.

This module provides functions for writing normalized data to CSV, JSON,
and other formats for downstream analysis.
"""

import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Union, Optional
from pydantic import BaseModel

from utils.logger import logger


def write_csv(
    data: Union[List[Dict[str, Any]], List[BaseModel]],
    filename: str,
    *,
    exclude_fields: Optional[List[str]] = None,
    include_fields: Optional[List[str]] = None,
) -> int:
    """
    Write data to CSV file.

    Args:
        data: List of dictionaries or Pydantic models to write
        filename: Output filename
        exclude_fields: Fields to exclude from output
        include_fields: Only include these fields (if specified)

    Returns:
        Number of rows written
    """
    if not data:
        logger.warning(f"No data to write to {filename}")
        return 0

    # Convert Pydantic models to dicts if needed
    if data and isinstance(data[0], BaseModel):
        data = [item.model_dump() for item in data]

    # Get fieldnames
    if include_fields:
        fieldnames = include_fields
    else:
        # Union of all fields across all items
        all_fields = set()
        for item in data:
            all_fields.update(item.keys())
        fieldnames = sorted(all_fields)

        # Exclude fields if specified
        if exclude_fields:
            fieldnames = [f for f in fieldnames if f not in exclude_fields]

    # Write CSV
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

    logger.info(f"Wrote {len(data)} items to {filename}")
    return len(data)


def write_json(
    data: Union[List[Dict[str, Any]], List[BaseModel]],
    filename: str,
    *,
    indent: int = 2,
    exclude_fields: Optional[List[str]] = None,
) -> int:
    """
    Write data to JSON file.

    Args:
        data: List of dictionaries or Pydantic models to write
        filename: Output filename
        indent: JSON indentation level
        exclude_fields: Fields to exclude from output

    Returns:
        Number of items written
    """
    if not data:
        logger.warning(f"No data to write to {filename}")
        return 0

    # Convert Pydantic models to dicts if needed
    if isinstance(data[0], BaseModel):
        data = [item.model_dump(exclude=exclude_fields) for item in data]
    elif exclude_fields:
        # Exclude fields from dicts
        data = [
            {k: v for k, v in item.items() if k not in exclude_fields}
            for item in data
        ]

    # Write JSON
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, default=str)

    logger.info(f"Wrote {len(data)} items to {filename}")
    return len(data)


def write_jsonl(
    data: Union[List[Dict[str, Any]], List[BaseModel]],
    filename: str,
    *,
    exclude_fields: Optional[List[str]] = None,
) -> int:
    """
    Write data to JSON Lines (JSONL) file.

    Each line is a separate JSON object. This format is useful for
    streaming and large datasets.

    Args:
        data: List of dictionaries or Pydantic models to write
        filename: Output filename
        exclude_fields: Fields to exclude from output

    Returns:
        Number of items written
    """
    if not data:
        logger.warning(f"No data to write to {filename}")
        return 0

    # Convert Pydantic models to dicts if needed
    if isinstance(data[0], BaseModel):
        data = [item.model_dump(exclude=exclude_fields) for item in data]
    elif exclude_fields:
        # Exclude fields from dicts
        data = [
            {k: v for k, v in item.items() if k not in exclude_fields}
            for item in data
        ]

    # Write JSONL
    filepath = Path(filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", encoding="utf-8") as f:
        for item in data:
            f.write(json.dumps(item, default=str) + "\n")

    logger.info(f"Wrote {len(data)} items to {filename}")
    return len(data)
