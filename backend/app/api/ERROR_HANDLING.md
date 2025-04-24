# API Error Handling Guide

This document describes the error handling system in the Concept Visualizer API and provides guidance for developers implementing route handlers.

## Overview

The error handling system is designed to:

1. Provide consistent error responses across all API endpoints
2. Map domain-specific application errors to appropriate HTTP status codes
3. Include helpful error details for clients
4. Log errors appropriately based on severity
5. Separate domain/application errors from API-specific errors

## Error Architecture

The error system has two main layers:

1. **Domain/Application Errors** (`app.core.exceptions.ApplicationError`)

   - Define business logic errors independent of API concerns
   - Contain detailed error context in the `details` property
   - Located in `app/core/exceptions.py`

2. **API Errors** (`app.api.errors.APIError`)
   - Extend FastAPI's `HTTPException`
   - Map to specific HTTP status codes
   - Format responses consistently for API clients
   - Located in `app/api/errors.py`

## Recommended Error Handling Pattern

When implementing API route handlers, follow this pattern:

```python
@router.get("/resource/{resource_id}")
async def get_resource(resource_id: str):
    try:
        # Your main logic here
        try:
            # Service calls that might raise domain errors
            resource = await service.get_resource(resource_id)
            return resource
        except ResourceNotFoundError as e:
            # Re-raise domain errors - they will be mapped automatically
            raise

    except ApplicationError as e:
        # Optional: Add custom logging based on error type
        if isinstance(e, ValidationError):
            logger.warning(f"Validation error: {e.message}")
        else:
            logger.error(f"Application error: {e.message}", exc_info=True)
        # Re-raise for automatic mapping by the global handler
        raise

    except Exception as e:
        # For unexpected errors, wrap in InternalServerError
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise InternalServerError(detail=error_msg)
```

This pattern ensures:

- Domain errors are properly mapped to API errors
- Appropriate logging occurs
- Unexpected errors are caught and presented consistently

## Error Classes

### Domain/Application Errors

All domain errors inherit from `ApplicationError` and include:

- `AuthenticationError`: Authentication failures
- `ResourceNotFoundError`: When a requested resource doesn't exist
- `ValidationError`: Domain-level validation failures
- `JigsawStackError`: Errors from the JigsawStack API
- `DatabaseError` / `StorageError`: Data persistence issues
- Many more specific error types

### API Errors

All API errors inherit from `APIError` and include:

- `BadRequestError`: 400 Bad Request
- `UnauthorizedError`: 401 Unauthorized
- `ForbiddenError`: 403 Forbidden
- `NotFoundError`: 404 Not Found
- `UnprocessableEntityError`: 422 Unprocessable Entity
- `TooManyRequestsError`: 429 Too Many Requests
- `InternalServerError`: 500 Internal Server Error
- `ServiceUnavailableError`: 503 Service Unavailable

## Error Mapping

Application errors are automatically mapped to appropriate API errors through the `map_application_error_to_api_error` function and the global exception handler.

For example:

- `AuthenticationError` → 401 Unauthorized
- `ResourceNotFoundError` → 404 Not Found
- `ValidationError` → 422 Unprocessable Entity
- `RateLimitError` → 429 Too Many Requests

## Best Practices

1. **Raise Domain Errors**: In services and other business logic, raise the most specific `ApplicationError` subclass with helpful details

2. **Log Appropriately**: Log errors at the appropriate level based on severity:

   - INFO: Normal operations
   - WARNING: Client errors (400-level)
   - ERROR: Server errors (500-level)

3. **Include Context**: When raising errors, include relevant context in the `details` parameter:

   ```python
   raise ResourceNotFoundError(
       message="User not found",
       resource_type="User",
       resource_id=user_id
   )
   ```

4. **Don't Double-Convert**: In route handlers, simply re-raise application errors - don't manually convert them to API errors

5. **Catch Unexpected Errors**: Always include a final `except Exception` handler to catch unexpected errors and provide a consistent response

## Example

See `app/api/routes/concept/example_error_handling.py` for a complete example of proper error handling in route handlers.

## Error Response Format

All error responses follow this JSON format:

```json
{
  "detail": "Error message",
  "details": {
    "additional": "context",
    "field_errors": {
      "field_name": ["Error message"]
    }
  }
}
```

The `details` field is optional and only included when relevant.
