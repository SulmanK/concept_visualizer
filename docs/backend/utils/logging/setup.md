# Logging Setup

This module configures logging for the Concept Visualizer application with both console and file handlers for persistent logs.

## Overview

The `logging.setup` module provides a standardized way to configure logging across the application. It sets up:

1. Console logging for immediate feedback during development
2. File logging for persistent records and debugging
3. Separate error logs for easier troubleshooting

## Core Functions

### `setup_logging`

```python
def setup_logging(
    log_level: str = "INFO",
    log_format: Optional[str] = None,
    log_dir: str = "logs"
) -> None
```

Configures logging for the application with both console and file handlers.

**Parameters:**
- `log_level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_format`: Optional custom log format
- `log_dir`: Directory to store log files (default: 'logs')

**Behavior:**
1. Converts the string log level to a logging constant
2. Creates a formatter with the specified format
3. Configures the root logger with the specified level
4. Adds a console handler for immediate output
5. Creates a log directory if it doesn't exist
6. Adds rotating file handlers for both general logs and error logs

### `get_logger`

```python
def get_logger(name: str) -> logging.Logger
```

Gets a logger with the given name.

**Parameters:**
- `name`: Logger name

**Returns:**
- A Logger instance with the specified name

### `is_health_check`

```python
def is_health_check(path: str) -> bool
```

Checks if a request path is a health check endpoint.

**Parameters:**
- `path`: Request path to check

**Returns:**
- `True` if this is a health check path, `False` otherwise

## Usage Examples

### Application Initialization

```python
from app.utils.logging.setup import setup_logging

def init_app():
    # Set up logging at application startup
    setup_logging(
        log_level="DEBUG",  # More verbose during development
        log_dir="app_logs"   # Custom log directory
    )
    
    # Continue with application initialization
```

### Getting a Module-Specific Logger

```python
from app.utils.logging.setup import get_logger

# Get a logger for the current module
logger = get_logger(__name__)

def process_data(data):
    logger.info(f"Processing data: {len(data)} items")
    try:
        # Process data
        result = [item.process() for item in data]
        logger.debug(f"Processed data successfully")
        return result
    except Exception as e:
        logger.error(f"Error processing data: {str(e)}", exc_info=True)
        raise
```

### Using the Health Check Function

```python
from fastapi import Request
from app.utils.logging.setup import is_health_check

async def log_request_middleware(request: Request, call_next):
    # Skip detailed logging for health checks
    if is_health_check(request.url.path):
        return await call_next(request)
    
    # Full request logging for non-health check endpoints
    # ...
```

## Log Files

When configured with the default settings, the module creates the following files:

- `logs/app.log`: Main application log with all messages at or above the configured level
- `logs/error.log`: Error-only log with messages at ERROR level or above

Both files are configured as rotating file handlers with the following settings:
- Maximum file size: 10 MB
- Maximum backup files: 5

This ensures that logs don't consume too much disk space while still retaining important information.

## Best Practices

1. Call `setup_logging()` early in the application startup process
2. Use module-level loggers with `get_logger(__name__)` for easier message filtering
3. Use appropriate log levels:
   - DEBUG: Detailed information for debugging
   - INFO: Confirmation that things are working as expected
   - WARNING: Indication that something unexpected happened, but the application still works
   - ERROR: Due to a more serious problem, the application couldn't perform a function
   - CRITICAL: A serious error indicating the application may be unable to continue running

4. Include contextual information in log messages to make them more useful for debugging 