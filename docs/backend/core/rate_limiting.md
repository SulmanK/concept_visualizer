# Rate Limiting

This document describes the rate limiting system used in the Concept Visualizer application.

## Overview

Rate limiting is essential for:
- Protecting the API from abuse
- Ensuring fair resource allocation
- Preventing service degradation during high traffic
- Managing costs for external API calls (JigsawStack)

## Implementation

The application uses a multi-layered rate limiting approach:

1. **Global Rate Limiting**: Limits all requests to the API
2. **Endpoint-Specific Rate Limiting**: More restrictive limits for resource-intensive endpoints
3. **Custom Rate Limiting**: Special handling for specific operations like SVG conversion

## Rate Limit Definitions

| Endpoint | Rate Limit | Reason |
|----------|------------|--------|
| `/api/concept/generate` | 10/month | Resource-intensive, external API costs |
| `/api/concept/refine` | 10/hour | Resource-intensive, external API costs |
| `/api/svg/convert-to-svg` | 20/hour | CPU-intensive operation |
| Most other endpoints | 200/day, 50/hour, 10/minute | General protection |

## Technical Implementation

### Components

1. **SlowAPI Integration**:
   - Uses the SlowAPI library to integrate rate limiting with FastAPI
   - Configures rate limits in the main application setup

2. **Redis Backend**:
   - Uses Redis to store rate limit counters
   - Allows distributed rate limiting across multiple instances
   - Configured in `core/rate_limiter.py`

3. **Utility Functions**:
   - `apply_rate_limit`: Function to apply rate limits to specific endpoints
   - Implemented in `utils/rate_limiting.py`

4. **Fallback Mechanism**:
   - In-memory fallback when Redis is unavailable
   - Ensures rate limiting still works in degraded mode

### Example Usage

```python
from app.utils.rate_limiting import apply_rate_limit

@router.post("/generate")
async def generate_concept(request: Request):
    # Apply rate limit for this endpoint
    await apply_rate_limit(request, "/api/concept/generate", "10/month", "month")
    
    # Rest of the endpoint logic
    # ...
```

## Rate Limit Monitoring

The application provides an endpoint to check the current rate limit status:

- `GET /api/health/rate-limits`: Returns the current rate limit status for the user

This endpoint can be used by frontend applications to show users their remaining quota.

## Rate Limit Response

When a rate limit is exceeded, the API returns a standard error response:

```json
{
  "detail": "Rate limit exceeded. Try again in [time period].",
  "status_code": 429,
  "error_code": "rate_limit_exceeded"
}
```

## Configuration

Rate limiting can be configured through environment variables:

- `CONCEPT_RATE_LIMIT_ENABLED`: Enable/disable rate limiting
- `CONCEPT_REDIS_URL`: Redis connection URL for rate limiting storage

## Handling Rate Limit Errors

Clients should handle 429 responses gracefully by:
1. Displaying a friendly message to users
2. Including the retry-after period if provided
3. Potentially implementing exponential backoff for automated retries 

## API Rate Limiting Usage

The API uses rate limiting in two ways:

1. SlowAPI declarative rate limiting
2. Direct Redis rate limiting tracking

- Implemented in `utils/api_limits/endpoints.py`
- Applied to all key endpoints to prevent abuse

```python
from app.utils.api_limits import apply_rate_limit

# Example usage in an API endpoint
@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(request: PromptRequest, req: Request):
    # Apply rate limit (10 requests per month)
    await apply_rate_limit(req, "/concepts/generate", "10/month")
    
    # Endpoint implementation
    # ...
``` 