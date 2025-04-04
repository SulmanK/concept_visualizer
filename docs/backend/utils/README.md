# Utilities Documentation

The `app/utils` directory contains various utility functions and helpers used throughout the application. These utilities are organized into focused subdirectories based on their functionality.

## Directory Structure

```
app/utils/
├── __init__.py           # Re-exports all utilities
├── api_limits/           # API rate limiting utilities
│   ├── __init__.py       # Exports rate limiting functions
│   └── endpoints.py      # Rate limiting implementation
├── data/                 # Data transformation utilities
│   └── __init__.py       # (Placeholder)
├── logging/              # Logging configuration
│   ├── __init__.py       # Exports logging functions
│   └── setup.py          # Logging setup implementation
├── security/             # Security-related utilities
│   ├── __init__.py       # Exports security functions
│   └── mask.py           # Data masking implementation
└── validation/           # Validation utilities
    └── __init__.py       # (Placeholder)
```

## Module Documentation

- [API Limits](./api_limits.md) - Rate limiting utilities for API endpoints
- [Logging](./logging.md) - Logging configuration and utilities
- [Security](./security.md) - Security utilities including data masking

## Usage

All utility functions can be imported directly from the `app.utils` package:

```python
from app.utils import setup_logging, get_logger, apply_rate_limit, mask_id

# Use the utility functions
setup_logging()
logger = get_logger(__name__)
await apply_rate_limit(request, "/endpoint", "10/month")
masked_session_id = mask_id(session_id)
``` 