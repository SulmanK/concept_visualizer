"""
Logging utility for the Concept Visualizer API.

This module configures the application's logging system.
"""

import logging
import sys

from backend.app.core.config import settings


def setup_logging() -> None:
    """
    Configure the application's logging system.
    
    This function sets up logging with appropriate handlers, formatters,
    and log levels based on application settings.
    """
    # Get the root logger
    root_logger = logging.getLogger()
    
    # Set the log level based on settings
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(log_level)
    
    # Create a console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Set formatter - including timestamp, level and message
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    # Remove existing handlers to avoid duplicates
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Add the handler to the logger
    root_logger.addHandler(console_handler)
    
    # Log that the logger has been configured
    logging.info(f"Logging configured with level: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: The name for the logger, typically __name__
        
    Returns:
        logging.Logger: A configured logger instance
    """
    return logging.getLogger(name) 