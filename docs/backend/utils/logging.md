# Logging Utilities

The `app.utils.logging` module provides functions to configure and use the application's logging system. It ensures consistent log formatting and level configuration throughout the application.

## Key Functions

### `setup_logging`

```python
def setup_logging() -> None
```

Configure the application's logging system.

This function sets up logging with appropriate handlers, formatters, and log levels based on application settings.

**Example Usage:**

```python
from app.utils.logging import setup_logging

# Call at application startup
setup_logging()
```

### `get_logger`

```python
def get_logger(name: str, level: int = None) -> logging.Logger
```

Get a logger for a specific module.

**Parameters:**

- `name`: The name for the logger, typically `__name__`
- `level`: Optional custom log level to set

**Returns:**

- A configured `logging.Logger` instance

**Example Usage:**

```python
from app.utils.logging import get_logger

# Get a logger for the current module
logger = get_logger(__name__)

# Log messages at different levels
logger.debug("Debug message")
logger.info("Info message")
logger.warning("Warning message")
logger.error("Error message")
```

### `is_health_check`

```python
def is_health_check(path: str) -> bool
```

Check if a request path is a health check.

**Parameters:**

- `path`: Request path

**Returns:**

- `True` if this is a health check path, `False` otherwise

**Example Usage:**

```python
from app.utils.logging import is_health_check

# In a middleware or request handler
if is_health_check(request.url.path):
    # Use different logging or processing for health checks
    pass
```

## Implementation Details

The logging configuration includes:

- Console output to stdout
- Formatted logs with timestamps and log levels
- Customized log levels for different modules:
  - httpx: WARNING (to reduce API request logs)
  - uvicorn.access: WARNING (to reduce access logs)
  - session_service: INFO
  - concept_service: Based on settings
  - concept_api: Based on settings

Log levels are configured from application settings, with INFO as the default if not specified. 