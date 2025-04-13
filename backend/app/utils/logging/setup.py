"""
Logging setup module.

This module configures logging for the application with both console
and file handlers for persistent logs.
"""

import os
import logging
import logging.handlers
from pathlib import Path
from typing import Dict, Any, Optional

def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    log_dir: str = "logs"
) -> None:
    """
    Configure logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Optional custom log format
        log_dir: Directory to store log files (default: 'logs')
    """
    # Convert string log level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Default log format if none provided
    if log_format is None:
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create formatter
    formatter = logging.Formatter(log_format)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    
    # Clear existing handlers to avoid duplicate logs
    if root_logger.handlers:
        root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create log directory if it doesn't exist
    log_directory = Path(log_dir)
    if not log_directory.exists():
        try:
            log_directory.mkdir(parents=True, exist_ok=True)
            print(f"Created log directory: {log_directory.absolute()}")
        except Exception as e:
            print(f"Warning: Could not create log directory {log_directory}: {str(e)}")
            return
    
    # File handler - rotating file handler to prevent huge log files
    try:
        # Main application log
        app_log_file = log_directory / "app.log"
        file_handler = logging.handlers.RotatingFileHandler(
            app_log_file,
            maxBytes=10 * 1024 * 1024,  # 10 MB
            backupCount=5,              # Keep 5 backup files max
            encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Error log - separate file for errors and above
        error_log_file = log_directory / "error.log"
        error_file_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8"
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(formatter)
        root_logger.addHandler(error_file_handler)
        
        print(f"Log files will be written to: {log_directory.absolute()}")
    except Exception as e:
        print(f"Warning: Could not set up file logging: {str(e)}")
        
def get_logger(name: str) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def is_health_check(path: str) -> bool:
    """
    Check if a request path is a health check.
    
    Args:
        path: Request path to check
        
    Returns:
        True if this is a health check path, False otherwise
    """
    health_check_paths = [
        "/health", 
        "/api/health",
        "/ping",
        "/api/ping",
        "/_health"
    ]
    return path in health_check_paths or path.endswith("/health") or path.endswith("/ping") 