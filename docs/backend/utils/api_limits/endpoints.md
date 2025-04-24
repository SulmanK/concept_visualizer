# API Rate Limiting Endpoints

This module provides functions for applying rate limits to API endpoints in the Concept Visualizer application.

## Overview

The `api_limits.endpoints` module contains utility functions that implement rate limiting for API endpoints. It works with the rate limiting middleware to enforce usage quotas and prevent abuse of the API.

## Key Functions

### `apply_rate_limit`

```python
async def apply_rate_limit(
    req: Request,
    endpoint: str,
    rate_limit: str,
    period: Optional[str] = None
) -> Dict[str, Any]
```

Applies rate limiting to a single endpoint.

**Parameters:**

- `req`: FastAPI request object
- `endpoint`: Name of the endpoint for rate limiting (used in the rate limit key)
- `rate_limit`: Rate limit string (e.g., "10/minute")
- `period`: Optional time period override

**Returns:**

- Dictionary containing rate limit information

**Raises:**

- `HTTPException`: If rate limit is exceeded (status code 429)

**Behavior:**

1. Skips rate limiting if it's disabled in settings
2. Identifies the user from authentication token or falls back to IP address
3. Checks if the rate limit has been exceeded
4. Adds rate limit headers to the response
5. Raises an exception if the rate limit is exceeded

### `apply_multiple_rate_limits`

```python
async def apply_multiple_rate_limits(
    req: Request,
    rate_limits: List[Dict[str, str]]
) -> Dict[str, Any]
```

Applies multiple rate limits for a single endpoint. This is useful when an endpoint needs to track usage against multiple different resource quotas.

**Parameters:**

- `req`: FastAPI request object
- `rate_limits`: List of dictionaries with keys:
  - `endpoint`: Name of the endpoint for rate limiting
  - `rate_limit`: Rate limit string (e.g., "10/minute")
  - `period`: Optional time period override

**Returns:**

- Dictionary containing combined rate limit information

**Raises:**

- `HTTPException`: If any rate limit is exceeded (status code 429)

**Behavior:**

1. Checks each rate limit in sequence
2. Returns detailed information about all rate limits that were checked
3. Raises an exception immediately if any rate limit is exceeded

## Usage Examples

### Single Rate Limit

```python
from fastapi import APIRouter, Request, Depends
from app.utils.api_limits.endpoints import apply_rate_limit

router = APIRouter()

@router.post("/generate")
async def generate_concept(request: Request):
    # Apply rate limit of 10 requests per minute for concept generation
    await apply_rate_limit(request, "generate_concept", "10/minute")

    # Continue with the endpoint logic if rate limit is not exceeded
    return {"success": True}
```

### Multiple Rate Limits

```python
from fastapi import APIRouter, Request
from app.utils.api_limits.endpoints import apply_multiple_rate_limits

router = APIRouter()

@router.post("/generate-and-store")
async def generate_and_store(request: Request):
    # Apply multiple rate limits
    await apply_multiple_rate_limits(request, [
        {
            "endpoint": "generate_concept",
            "rate_limit": "10/minute"
        },
        {
            "endpoint": "store_concept",
            "rate_limit": "100/day"
        }
    ])

    # Continue with the endpoint logic if no rate limits are exceeded
    return {"success": True}
```

## Rate Limit Headers

When rate limiting is applied, the following headers are added to the response:

- `X-RateLimit-Limit`: Maximum number of requests allowed within the period
- `X-RateLimit-Remaining`: Number of requests remaining in the current period
- `X-RateLimit-Reset`: Time in seconds until the rate limit resets

These headers follow standard conventions used by APIs like GitHub and Twitter.

## Integration with FastAPI

This module is designed to work with FastAPI's dependency injection system, but can also be called directly within route handlers. It integrates with the core rate limiting system defined in `app.core.limiter`.
