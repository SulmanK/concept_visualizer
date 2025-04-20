# Rate Limiter Documentation

The `limiter` module provides a comprehensive rate limiting system for the Concept Visualizer API, protecting resources from abuse and ensuring fair usage.

## Overview

The rate limiter is built on Redis and provides:

1. **Flexible Rate Limit Rules**: Define limits by user, endpoint, or resource type
2. **Header-Based Feedback**: Clients receive headers indicating their limits and usage
3. **Decorators for Routes**: Easy application of rate limits to FastAPI endpoints
4. **Custom Key Generation**: Sophisticated key generation to track usage across dimensions

## Components

- [Config](config.md): Configuration for the rate limiter, including rule definitions
- [Redis Store](redis_store.md): Redis-based storage backend for tracking rate limits
- [Keys](keys.md): Key generation utilities for identifying rate-limited resources
- [Decorators](decorators.md): FastAPI decorators for applying rate limits to routes

## Architecture

The rate limiting system follows these principles:

1. **Separation of Concerns**:
   - Configuration (limit definitions)
   - Storage (tracking limit state)
   - Key generation (identifying resources)
   - Application (enforcing limits)

2. **Middleware + Decorator Pattern**:
   - Middleware applies global rate limits and adds headers
   - Decorators apply endpoint-specific limits

3. **Sliding Window Algorithm**:
   - Tracks requests in a time window for accurate limiting

## Example Usage

### Applying Rate Limits to Routes

```python
from fastapi import APIRouter, Depends
from app.core.limiter.decorators import rate_limit

router = APIRouter()

# Apply a rate limit to an endpoint
@router.post("/generate")
@rate_limit(limit="5/minute", key_func="user_endpoint")
async def generate_concept(request: ConceptRequest):
    # This endpoint is limited to 5 calls per minute per user
    return await service.generate_concept(request.prompt)

# Apply multiple rate limits
@router.post("/refine")
@rate_limit(limit="10/minute", key_func="user_endpoint")  # Per-user limit
@rate_limit(limit="100/minute", key_func="endpoint")  # Global endpoint limit
async def refine_concept(request: RefinementRequest):
    # This endpoint has both per-user and global limits
    return await service.refine_concept(request.concept_id, request.feedback)
```

### Key Formats

The system uses key formats to track different types of limits:

```
# Global endpoint limit
rl:endpoint:{endpoint_name}

# Per-user endpoint limit
rl:user:{user_id}:endpoint:{endpoint_name}

# Per-user resource limit
rl:user:{user_id}:resource:{resource_type}
```

## Implementing New Rate Limits

To add a new rate limit:

1. Define the limit in `config.py`
2. If needed, create a new key function in `keys.py`
3. Apply the limit using decorators or middleware

## Related Documentation

- [Rate Limit Apply Middleware](../../api/middleware/rate_limit_apply.md): Middleware that enforces limits
- [Rate Limit Headers Middleware](../../api/middleware/rate_limit_headers.md): Middleware that adds limit headers
- [Health Endpoints](../../api/routes/health/limits.md): Endpoints for checking rate limit status 