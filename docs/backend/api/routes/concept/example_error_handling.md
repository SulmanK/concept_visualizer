# Example Error Handling for Concept Routes

This documentation covers the example error handling implementation in the Concept Visualizer API.

## Overview

The `example_error_handling.py` module demonstrates the recommended approaches for error handling in API routes. It serves as a reference implementation for other endpoints to follow, showing how to properly use the application's error system.

## Available Endpoints

### Get Concept Example

```python
@router.get("/concept/{concept_id}", response_model=Dict[str, Any])
async def get_concept_example(
    concept_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
):
    """Example route showing proper error handling with the application's error system."""
```

This endpoint demonstrates retrieving a concept and handling various potential errors.

#### Request

```
GET /api/concepts/examples/concept/{concept_id}
```

Path parameters:

- `concept_id`: ID of the concept to retrieve

#### Response

```json
{
  "id": "1234-5678-9012-3456",
  "user_id": "user-1234",
  "image_url": "https://storage.example.com/concepts/1234-5678-9012-3456.png",
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling",
  "created_at": "2023-01-01T12:00:00.123456"
}
```

#### Error Responses

- `401 Unauthorized`: Missing authentication
- `403 Forbidden`: User doesn't own the requested concept
- `404 Not Found`: Concept doesn't exist
- `422 Unprocessable Entity`: Invalid concept ID format
- `500 Internal Server Error`: Database or other server errors

### Analyze Concept Example

```python
@router.post("/concept-analyze", response_model=Dict[str, Any])
async def analyze_concept_example(
    request: PromptRequest,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """Example route showing how to handle different types of application errors."""
```

This endpoint demonstrates analyzing a concept description and handling different error scenarios.

#### Request

```
POST /api/concepts/examples/concept-analyze
Content-Type: application/json

{
  "logo_description": "A modern coffee shop logo with coffee beans",
  "theme_description": "Warm brown tones, natural feeling"
}
```

#### Response

```json
{
  "complexity": "medium",
  "estimated_generation_time": "2 seconds",
  "prompt_quality": "high"
}
```

#### Error Responses

- `401 Unauthorized`: Missing authentication
- `422 Unprocessable Entity`: Missing required fields
- `503 Service Unavailable`: External AI service unavailable

## Error Handling Patterns

The module demonstrates several key error handling patterns:

1. **Domain Error Mapping**: Application-specific errors (like `AppValidationError`, `ResourceNotFoundError`) are caught and re-raised to be handled by the global exception handler.

2. **Error Logging**: Different error types are logged at appropriate levels (warning for validation, error for server issues).

3. **Specific Error Types**: Custom error types provide detailed information about what went wrong.

4. **Consistent API Responses**: All errors are converted to standardized API responses.

### Example Pattern

```python
try:
    # Business logic that might raise errors
except ApplicationError as e:
    # For all ApplicationError subclasses, we just re-raise
    # The global exception handler will map them to the appropriate API errors
    # You can add custom logging here if needed
    if isinstance(e, ResourceNotFoundError):
        logger.warning(f"Resource not found: {e.message}")
    else:
        logger.error(f"Application error: {e.message}", exc_info=True)
    raise
except Exception as e:
    # For unexpected errors, wrap them in an InternalServerError
    # This ensures a consistent API response format
    error_msg = f"Unexpected error: {str(e)}"
    logger.error(error_msg, exc_info=True)
    raise InternalServerError(detail=error_msg)
```

## Related Files

- [API Errors](../../errors.md): Global API error definitions
- [Core Exceptions](../../../core/exceptions.md): Application-specific exception types
- [Generation](generation.md): Concept generation endpoints
- [Refinement](refinement.md): Concept refinement endpoints
