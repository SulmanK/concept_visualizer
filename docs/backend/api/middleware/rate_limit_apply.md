# Rate Limit Apply Middleware

This documentation covers the rate limit application middleware used in the Concept Visualizer API.

## Overview

The `rate_limit_apply.py` module provides middleware that applies rate limits to API requests. This middleware:

- Defines and enforces rate limits for different API endpoints
- Checks incoming requests against configured rate limits
- Rejects requests that exceed limits with appropriate error responses
- Stores rate limit information in the request state for header generation
- Centralizes rate limiting logic that would otherwise be scattered in route handlers

## Rate Limit Configuration

The module defines several configuration constants:

### Rate Limit Rules

```python
RATE_LIMIT_RULES = {
    "/concepts/generate-with-palettes": "10/month",
    "/concepts/refine": "10/month",
    "/concepts/store": "10/month",
    "/storage/store": "10/month",
    "/storage/recent": "30/minute",
    "/storage/concept": "30/minute",
    "/export/process": "50/hour",
}
```

This dictionary maps API endpoints to their rate limit strings. For example, `/concepts/generate-with-palettes` is limited to 10 requests per month.

### Multiple Rate Limits

```python
MULTIPLE_RATE_LIMITS = {
    "/concepts/generate-with-palettes": [
        {"endpoint": "/concepts/generate", "rate_limit": "10/month"},
        {"endpoint": "/concepts/store", "rate_limit": "10/month"}
    ],
}
```

Some endpoints require checking multiple rate limits. This dictionary defines these complex cases.

### Public Paths

```python
PUBLIC_PATHS = [
    "/api/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/auth/session",
    "/api/auth/login",
    "/api/auth/signup",
    "/api/auth/reset-password",
    "/api/auth/magic-link",
]
```

These paths bypass rate limiting entirely.

## Components

### RateLimitApplyMiddleware

```python
class RateLimitApplyMiddleware(BaseHTTPMiddleware):
    """Middleware that applies rate limits to API requests."""
```

This middleware class handles the rate limit application.

#### Constructor

```python
def __init__(self, app: ASGIApp):
    """Initialize the middleware."""
```

Parameters:

- `app`: The ASGI application instance

#### Dispatch Method

```python
async def dispatch(self, request: Request, call_next: Callable) -> Response:
    """Process the request and apply rate limits if applicable."""
```

The dispatch method implements the rate limiting logic:

1. Skips rate limiting if disabled in settings or if limiter is not available
2. Skips for non-API paths, public paths, and OPTIONS requests
3. Gets the user ID for personalized rate limiting
4. Checks if path has multiple rate limits and applies all of them
5. If not, applies the single matching rate limit
6. If any limit is exceeded, raises an HTTP 429 Too Many Requests exception
7. Stores rate limit information in request.state for headers middleware
8. Passes the request to the next middleware or route handler if limits are not exceeded

## Usage Example

```python
from fastapi import FastAPI
from app.api.middleware.rate_limit_apply import RateLimitApplyMiddleware

app = FastAPI()

# Add rate limit apply middleware (should come before the headers middleware)
app.add_middleware(RateLimitApplyMiddleware)
```

## Rate Limit Checking

Rate limits are checked using the `check_rate_limit` function from the core limiter module:

```python
limit_info = check_rate_limit(user_id, endpoint, rate_limit)
is_rate_limited = limit_info.get("exceeded", False)
```

This returns information including:

- Whether the limit is exceeded
- The limit value
- Remaining requests
- Reset time

## Rate Limit Exceeded Response

When a rate limit is exceeded, the middleware returns a 429 Too Many Requests response:

```
HTTP/1.1 429 Too Many Requests
Content-Type: application/json
Retry-After: 1672531200

{
  "detail": "Rate limit exceeded for /concepts/generate (10/month). Try again later."
}
```

The response includes a `Retry-After` header indicating when the client can retry the request.

## Integration with Headers Middleware

The middleware stores rate limit information in `request.state.limiter_info`, which is used by the `RateLimitHeadersMiddleware` to add appropriate headers to responses.

## Best Practices

1. **Rate Limit Configuration**: Keep rate limits reasonable and appropriate for your API's purpose
2. **Public Paths**: Ensure that essential endpoints are included in the PUBLIC_PATHS list
3. **Error Handling**: Provide meaningful error messages that help users understand the limits
4. **Retry-After Headers**: Include these to allow clients to implement proper retry logic
