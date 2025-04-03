# Error Handling

This document describes the error handling system used in the Concept Visualizer API.

## Overview

The application implements a standardized error handling system that:
- Provides consistent error responses across all endpoints
- Uses specific error types for different error scenarios
- Includes structured error information for easier client processing
- Enables detailed logging for debugging

## Error Response Format

All API errors follow a standard format:

```json
{
  "detail": "Human-readable error message",
  "status_code": 400,
  "error_code": "validation_error",
  "field_errors": {
    "field_name": ["Error message for this field"]
  }
}
```

Key components:
- `detail`: Human-readable error message
- `status_code`: HTTP status code
- `error_code`: Machine-readable error code for programmatic handling
- `field_errors`: (Optional) Field-specific validation errors

## Custom Error Types

The application defines several custom error types in `app.api.errors`:

### ValidationError (400)

Used for request validation failures:

```python
raise ValidationError(
    detail="Invalid input data",
    field_errors={"name": ["Field is required"]}
)
```

### ResourceNotFoundError (404)

Used when a requested resource doesn't exist:

```python
raise ResourceNotFoundError(
    detail=f"Concept with ID {concept_id} not found"
)
```

### AuthenticationError (401)

Used for authentication failures:

```python
raise AuthenticationError(
    detail="Invalid session ID"
)
```

### ServiceUnavailableError (503)

Used when a service dependency is unavailable:

```python
raise ServiceUnavailableError(
    detail="Image generation service is currently unavailable"
)
```

### RateLimitExceededError (429)

Used when a rate limit is exceeded:

```python
raise RateLimitExceededError(
    detail="Rate limit exceeded. Try again later.",
    retry_after=3600  # Seconds until the rate limit resets
)
```

## Exception Handlers

The application registers custom exception handlers that:
1. Format the error response according to the standard format
2. Log detailed information about the error
3. Include stack traces in development mode

## Best Practices

When implementing API endpoints:

1. **Use Specific Error Types**: Choose the most specific error type for each error scenario
2. **Include Clear Messages**: Error messages should be clear and actionable
3. **Include Field Errors**: For validation errors, include specific field errors
4. **Log Detailed Information**: Log additional context for debugging
5. **Catch Unexpected Errors**: Wrap endpoint logic in try/except blocks to catch unexpected errors

## Example Usage

```python
@router.post("/generate")
async def generate_concept(request: Request, concept_service: ConceptService = Depends()):
    try:
        # Validate input
        if not request.prompt:
            raise ValidationError(
                detail="Prompt is required",
                field_errors={"prompt": ["Field is required"]}
            )
            
        # Call service
        result = await concept_service.generate_concept(request.prompt)
        if not result:
            raise ServiceUnavailableError(
                detail="Failed to generate concept"
            )
            
        return result
    except (ValidationError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        # Log unexpected errors and convert to ServiceUnavailableError
        logger.error(f"Unexpected error: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Unexpected error: {str(e)}") 