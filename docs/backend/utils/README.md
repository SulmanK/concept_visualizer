# Utils Documentation

The Utils module contains utility functions and helpers used throughout the Concept Visualizer application.

## Structure

- [API Limits](api_limits/README.md): Utilities for API rate limiting
- [Auth](auth/README.md): Authentication and authorization utilities
- [Data](data/README.md): Data manipulation utilities
- [Logging](logging/README.md): Logging configuration and utilities
- [Security](security/README.md): Security-related utilities
- [Validation](validation/README.md): Data validation utilities

## Key Files

- [HTTP Utils](http_utils.md): Utilities for HTTP requests and responses
- [JWT Utils](jwt_utils.md): JSON Web Token handling utilities

## Purpose

The Utils module provides reusable functions and utilities that:

1. Simplify common operations
2. Ensure consistent implementation of cross-cutting concerns
3. Reduce code duplication
4. Abstract implementation details for better maintainability

## Guidelines for Utils

When adding utilities, follow these guidelines:

1. **Pure Functions**: Utilities should be pure functions when possible
2. **Single Responsibility**: Each utility should have a single, well-defined responsibility
3. **Documentation**: All utilities should be well-documented with docstrings
4. **Type Hints**: Include type hints for improved developer experience
5. **Testability**: Utilities should be easily testable

## Example Usage

```python
from app.utils.http_utils import create_success_response, create_error_response
from app.utils.security.mask import mask_sensitive_data

# Creating standardized responses
def get_user_data(user_id: str):
    try:
        user = get_user_by_id(user_id)
        masked_user = mask_sensitive_data(user, fields=["password", "ssn"])
        return create_success_response(data=masked_user)
    except Exception as e:
        return create_error_response(message=str(e))

# Using logging utilities
from app.utils.logging.setup import get_logger
logger = get_logger(__name__)

def process_data(data: dict):
    logger.info("Processing data", extra={"data_size": len(data)})
    # Processing logic
    logger.debug("Data processed successfully") 