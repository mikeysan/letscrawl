"""
Logging configuration for letscrawl.

Provides a centralized logger instance with configurable log levels.
"""

import logging
import os
import sys


def setup_logger(name: str = "letscrawl") -> logging.Logger:
    """
    Set up and configure a logger instance.

    Args:
        name: The name of the logger (default: "letscrawl")

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)

    # Only configure if not already configured
    if not logger.handlers:
        # Get log level from environment variable (default: INFO)
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Validate log level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if log_level not in valid_levels:
            log_level = "INFO"

        logger.setLevel(getattr(logging, log_level))

        # Create console handler with formatting
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    return logger


# Create and export the default logger instance
logger = setup_logger()
