# Rate Limit Headers Middleware

This documentation covers the rate limit headers middleware used in the Concept Visualizer API.

## Overview

The `rate_limit_headers.py` module provides middleware that adds standard rate limit headers to API responses. This middleware:

- Extracts rate limit information from the request state
- Adds standardized rate limit headers to HTTP responses
- Works in conjunction with the rate limit application middleware

## Components

### RateLimitHeadersMiddleware

```python
class RateLimitHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware that adds rate limit headers to all API responses."""
```

This middleware class is responsible for adding rate limit headers to API responses.

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
    """Process the request and add rate limit headers to the response."""
```

The dispatch method:

1. Processes the request by calling the next middleware or route handler
2. Checks if rate limit information is available in `request.state.limiter_info`
3. Extracts limit, remaining, and reset values
4. Adds appropriate headers to the response

## Rate Limit Headers

The middleware adds the following headers to responses:

| Header                  | Description                                                             |
| ----------------------- | ----------------------------------------------------------------------- |
| `X-RateLimit-Limit`     | The maximum number of requests allowed in the current time window       |
| `X-RateLimit-Remaining` | The number of requests remaining in the current time window             |
| `X-RateLimit-Reset`     | The time at which the current rate limit window resets (Unix timestamp) |

## Usage Example

```python
from fastapi import FastAPI
from app.api.middleware.rate_limit_headers import RateLimitHeadersMiddleware

app = FastAPI()

# Add rate limit headers middleware
app.add_middleware(RateLimitHeadersMiddleware)
```

## Integration with Rate Limit Apply Middleware

This middleware works in conjunction with the `RateLimitApplyMiddleware` from `rate_limit_apply.py`, which:

1. Checks if the request exceeds rate limits
2. Stores rate limit information in `request.state.limiter_info`
3. Passes control to the next middleware

The `RateLimitHeadersMiddleware` then uses this information to add appropriate headers to the response.

## Client Behavior

Clients can use these headers to:

- Display rate limit information to users
- Implement backoff strategies when approaching limits
- Schedule retries based on the reset time
- Self-throttle requests to avoid hitting limits

## Example Response Headers

```
HTTP/1.1 200 OK
Content-Type: application/json
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1672531200
```

In this example, the client is allowed 10 requests per time period, has 8 requests remaining, and the current time window resets at Unix timestamp 1672531200.
