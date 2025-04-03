# Rate Limiting in Concept Visualizer API

This document describes the rate limiting implementation in the Concept Visualizer API.

## Overview

The API uses SlowAPI (a FastAPI-compatible rate limiting library) with Redis to implement rate limiting for various endpoints. Rate limiting helps:

- Prevent abuse and DoS attacks
- Ensure fair usage of resources
- Protect backend services from overload
- Manage costs for external APIs (like JigsawStack)

## Implementation Details

### Technology Stack

- **SlowAPI**: A rate limiting library compatible with FastAPI
- **Redis**: Used as the storage backend for rate limiting data
- **Upstash**: Managed Redis service used in production

### Configuration

The rate limiter is configured in `backend/app/core/rate_limiter.py` and integrated into the application in `backend/app/main.py`.

### Rate Limits by Endpoint

The following rate limits are applied to different endpoints:

| Endpoint Group | Rate Limit | Notes |
|----------------|------------|-------|
| `/api/concepts/generate*` | 10/month | Resource-intensive image generation |
| `/api/storage/store` | 10/month | Storage creation operations |
| `/api/concepts/refine` | 10/hour | Resource-intensive image refinement |
| `/api/storage/*` (GET) | 30/minute | Read operations |
| `/api/sessions/*` | 60/hour | Session management |
| `/api/svg/convert-to-svg` | 20/hour | Resource-intensive SVG conversion |

### Fallback Behavior

If Redis is unavailable, the system falls back to in-memory storage for rate limiting. Note that this doesn't persist across application restarts and doesn't work in multi-instance deployments.

## Customizing Rate Limits

To modify rate limits, update the respective endpoint handlers in:

- `backend/app/api/routes/concept.py`
- `backend/app/api/routes/concept_storage.py`
- `backend/app/api/routes/session.py`
- `backend/app/api/routes/svg_conversion.py`

## Default Limits

Default rate limits for all other endpoints are configured in `backend/app/core/rate_limiter.py`:

```python
default_limits=["200/day", "50/hour", "10/minute"]
```

## Environment Variables

The following environment variables are used for Redis configuration:

- `CONCEPT_UPSTASH_REDIS_URL`: URL of the Upstash Redis instance
- `CONCEPT_UPSTASH_REDIS_PASSWORD`: Password for Redis authentication
- `CONCEPT_UPSTASH_REDIS_PORT`: Redis port (default: 6379)

## Rate Limit Response

When a client exceeds the rate limit, they receive a `429 Too Many Requests` response with a JSON body:

```json
{
  "detail": "Rate limit exceeded: 10 per 1month"
}
```

The response also includes the following headers:
- `Retry-After`: Time in seconds until the limit resets
- `X-RateLimit-Limit`: The rate limit ceiling
- `X-RateLimit-Remaining`: The number of requests left for the time window
- `X-RateLimit-Reset`: The time at which the rate limit resets

## Recommendations for Clients

Clients should:

1. Handle 429 responses gracefully with appropriate backoff
2. Check the `X-RateLimit-Remaining` header to monitor quota usage
3. Use the `Retry-After` header to determine when to retry
4. Implement client-side throttling when approaching limits 