"""
Logging utility for the Concept Visualizer API.

This module configures the application's logging system.
"""

import logging
import sys

from app.core.config import settings


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
    
    # Configure specific loggers with custom levels
    # Set httpx to WARNING to reduce API request logs
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # Set uvicorn access logs to WARNING
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    
    # Set session service to a higher level to reduce noise
    logging.getLogger("session_service").setLevel(logging.INFO)
    
    # Keep detailed logs for concept-related services
    logging.getLogger("concept_service").setLevel(log_level)
    logging.getLogger("concept_api").setLevel(log_level)
    
    # Log that the logger has been configured
    logging.info(f"Logging configured with level: {settings.LOG_LEVEL}")


def get_logger(name: str, level: int = None) -> logging.Logger:
    """
    Get a logger for a specific module.
    
    Args:
        name: The name for the logger, typically __name__
        level: Optional custom log level to set
        
    Returns:
        logging.Logger: A configured logger instance
    """
    logger = logging.getLogger(name)
    if level is not None:
        logger.setLevel(level)
    return logger


def is_health_check(path: str) -> bool:
    """
    Check if a request path is a health check.
    
    Args:
        path: Request path
        
    Returns:
        bool: True if this is a health check path
    """
    return path.endswith("/health") or "/health/" in path 