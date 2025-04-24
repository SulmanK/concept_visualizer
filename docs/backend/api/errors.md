# API Error Handling

This documentation covers the error handling system in the Concept Visualizer API.

## Overview

The `errors.py` module defines a comprehensive error handling system for the API layer. It includes:

- A hierarchy of API-specific error classes
- Mapping from application domain errors to HTTP errors
- Custom exception handlers for FastAPI
- Standardized error response format

## Error Hierarchy

All API errors inherit from the base `APIError` class, which extends FastAPI's `HTTPException`. The inheritance structure is as follows:

```
APIError
├── BadRequestError (400)
├── UnauthorizedError (401)
│   └── AuthenticationError
├── ForbiddenError (403)
│   └── AuthorizationError
├── NotFoundError (404)
│   └── ResourceNotFoundError
├── MethodNotAllowedError (405)
├── NotAcceptableError (406)
├── ConflictError (409)
├── GoneError (410)
├── UnprocessableEntityError (422)
│   └── ValidationError
├── TooManyRequestsError (429)
│   └── RateLimitExceededError
├── InternalServerError (500)
├── BadGatewayError (502)
├── ServiceUnavailableError (503)
└── GatewayTimeoutError (504)
```

## Standard Error Fields

All API errors include the following standard fields in their JSON response:

- `status_code`: The HTTP status code
- `detail`: A human-readable error message
- `type`: The error type (class name)
- `request_id`: A unique identifier for the request (for tracking)
- `timestamp`: When the error occurred

Some errors add additional fields:

- `ValidationError`: Includes `field_errors` with specific validation issues
- `ResourceNotFoundError`: Includes `resource_type` and `resource_id`
- `RateLimitExceededError`: Includes `limit` and `reset_at` information

## Usage Examples

### Raising API Errors

```python
# Basic error
raise BadRequestError("Invalid request parameters")

# Resource not found with context
raise ResourceNotFoundError(
    detail="Concept not found",
    resource_type="concept",
    resource_id="12345"
)

# Validation error with field details
raise ValidationError(
    detail="Invalid input data",
    field_errors={"name": ["Field is required", "Must be at least 3 characters"]}
)
```

### Mapping Domain Errors

The module provides a function to map application domain errors to API errors:

```python
from app.core.exceptions import ResourceNotFoundException
from app.api.errors import map_application_error_to_api_error

try:
    # Some operation that might raise domain errors
    service.get_concept(concept_id)
except ResourceNotFoundException as e:
    # Map to appropriate API error
    api_error = map_application_error_to_api_error(e)
    raise api_error
```

## Error Handler Configuration

The module provides a `configure_error_handlers` function that registers exception handlers with the FastAPI application. This ensures consistent error responses across the API.

```python
from fastapi import FastAPI
from app.api.errors import configure_error_handlers

app = FastAPI()
configure_error_handlers(app)
```

## Best Practices

1. **Use Specific Error Classes**: Always use the most specific error class for the situation.
2. **Provide Meaningful Messages**: Error messages should be clear and actionable.
3. **Include Context**: When possible, include context about the error (e.g., resource IDs, field names).
4. **Log Appropriately**: Errors are automatically logged with appropriate severity levels.
5. **Map Domain Errors**: Use `map_application_error_to_api_error` to convert domain errors to API errors.
