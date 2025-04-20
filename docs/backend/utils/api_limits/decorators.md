# API Limits Decorators

The `decorators.py` module in the API limits utility package provides function decorators for applying rate limiting and quota restrictions to API endpoints.

## Overview

This module offers a collection of decorators that:

1. Apply rate limiting to API endpoints
2. Track API usage against quotas
3. Enforce access control based on limits
4. Add limit-related headers to responses

These decorators integrate with the application's rate limiting and quota tracking systems to protect API resources from overuse.

## Key Decorators

### Rate Limit

```python
def rate_limit(
    limit: int,
    period: int = 60,
    limit_type: str = "user",
    key_function: Optional[Callable] = None
) -> Callable:
    """Apply rate limiting to an API endpoint."""
```

This decorator applies rate limiting to an API endpoint based on defined parameters.

**Parameters:**
- `limit`: Maximum number of requests allowed within the period
- `period`: Time period in seconds (default: 60 seconds)
- `limit_type`: Type of limit to apply ("user", "ip", "global")
- `key_function`: Optional custom function for generating limit keys

**Returns:**
- Function decorator that applies rate limiting

**Rate Limit Types:**
- `user`: Limit requests per authenticated user
- `ip`: Limit requests per client IP address
- `global`: Limit requests across all clients
- `custom`: Use custom key function to determine limit scope

### Track Usage

```python
def track_usage(
    resource: str,
    amount: int = 1,
    key_function: Optional[Callable] = None
) -> Callable:
    """Track resource usage for quota management."""
```

This decorator tracks API resource usage for quota management.

**Parameters:**
- `resource`: Name of the resource being tracked (e.g., "image_generation")
- `amount`: Amount of resource usage to record (default: 1)
- `key_function`: Optional custom function for determining the user/entity

**Returns:**
- Function decorator that tracks resource usage

### Check Quota

```python
def check_quota(
    resource: str,
    quota_function: Callable,
    key_function: Optional[Callable] = None
) -> Callable:
    """Check if a request is within quota limits before processing."""
```

This decorator validates that a request is within quota limits before processing.

**Parameters:**
- `resource`: Name of the resource being requested
- `quota_function`: Function that returns the quota limit for the user/entity
- `key_function`: Optional custom function for determining the user/entity

**Returns:**
- Function decorator that checks quota before executing the endpoint

**Raises:**
- `QuotaExceededError`: If the request would exceed the quota

### Add Limit Headers

```python
def add_limit_headers() -> Callable:
    """Add rate limit and quota information headers to responses."""
```

This decorator adds informative headers about rate limits and quotas to API responses.

**Returns:**
- Function decorator that adds limit headers to responses

**Added Headers:**
- `X-RateLimit-Limit`: Maximum requests allowed in the current period
- `X-RateLimit-Remaining`: Remaining requests in the current period
- `X-RateLimit-Reset`: Seconds until the limit resets
- `X-Quota-Used`: Current resource usage for the quota period
- `X-Quota-Limit`: Maximum allowed usage for the quota period
- `X-Quota-Reset`: Seconds until the quota period resets

## Custom Key Functions

The module supports custom key functions for flexible limit and quota management:

```python
def create_combined_key(prefix: str, user_id: str) -> str:
    """Create a combined key for rate limiting or quota tracking."""
    return f"{prefix}:{user_id}"
    
def get_organization_key(request: Request) -> str:
    """Get an organization-based key for limiting requests per organization."""
    # Extract organization ID from request
    # ...
    return f"org:{org_id}"
```

These functions can be passed to decorators to customize how limits are applied.

## Usage Examples

### Basic Rate Limiting

```python
from fastapi import APIRouter, Depends
from app.utils.api_limits.decorators import rate_limit, add_limit_headers
from app.api.dependencies import get_current_user

router = APIRouter()

@router.get("/items/")
@rate_limit(limit=100, period=3600)  # 100 requests per hour per user
@add_limit_headers()
async def list_items(current_user = Depends(get_current_user)):
    """List items with rate limiting applied."""
    # Implementation...
    return {"items": []}
```

### Tiered Rate Limiting

```python
from app.utils.api_limits.decorators import rate_limit

def get_user_tier_limit(request: Request) -> int:
    """Get rate limit based on user tier."""
    user = request.state.user
    if user.tier == "premium":
        return 1000
    elif user.tier == "standard":
        return 100
    else:
        return 10

@router.post("/generate-image/")
@rate_limit(
    limit=get_user_tier_limit,  # Dynamic limit based on user tier
    period=3600,
    limit_type="user"
)
async def generate_image(request: Request, data: ImageRequest):
    """Generate an image with tier-based rate limiting."""
    # Implementation...
    return {"image_url": "..."}
```

### Quota Checking and Usage Tracking

```python
from app.utils.api_limits.decorators import check_quota, track_usage

def get_generation_quota(user_id: str) -> int:
    """Get the user's image generation quota."""
    user = get_user_by_id(user_id)
    return user.monthly_generation_quota

@router.post("/generate-concept/")
@check_quota(
    resource="concept_generation",
    quota_function=get_generation_quota
)
@track_usage(
    resource="concept_generation",
    amount=1
)
async def generate_concept(request: Request, data: ConceptRequest):
    """Generate a concept with quota checking and usage tracking."""
    # Implementation...
    return {"concept_id": "..."}
```

## Integration with Limiter System

The decorators integrate with the application's core limiter system:

```python
from app.core.limiter import get_limiter

# The decorators use the configured limiter
limiter = get_limiter()

def rate_limit(...):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Use the limiter to check and update limits
            is_allowed = await limiter.check_rate_limit(key, limit, period)
            if not is_allowed:
                raise RateLimitExceededError(...)
            
            # Execute the original function
            return await func(*args, **kwargs)
        return wrapper
    return decorator
```

## Error Handling

The decorators raise specific exceptions when limits are exceeded:

- `RateLimitExceededError`: When rate limits are exceeded
- `QuotaExceededError`: When quotas are exceeded

These exceptions are caught by the API's error handling middleware and converted to appropriate HTTP responses.

## Related Documentation

- [API Limits Endpoints](endpoints.md): API endpoints for checking limits
- [Rate Limit Headers](../../api/middleware/rate_limit_headers.md): Middleware for rate limit headers
- [Rate Limit Apply](../../api/middleware/rate_limit_apply.md): Middleware for applying rate limits
- [Limiter Config](../../core/limiter/config.md): Configuration for the rate limiter
- [Redis Store](../../core/limiter/redis_store.md): Redis backend for limit tracking 