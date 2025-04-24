# Rate Limit Endpoints

This documentation covers the rate limit information endpoints in the Concept Visualizer API.

## Overview

The `limits.py` module provides endpoints that allow clients to check their current rate limit status. These endpoints return information about remaining requests allowed for each rate-limited endpoint based on the client's user ID or IP address.

## Key Features

- **Caching**: Uses in-memory caching to reduce load during busy periods
- **Privacy**: Masks sensitive information like user IDs and IPs
- **Flexibility**: Provides both counting and non-counting versions of endpoints
- **Detailed Information**: Returns limit values, remaining requests, and reset times

## Available Endpoints

### Standard Rate Limit Check

```python
@router.get("/rate-limits")
async def rate_limits(request: Request, force_refresh: bool = False):
    """Get current rate limit information for the client."""
```

This endpoint returns the client's current rate limit status but counts against rate limits itself.

#### Request

```
GET /api/health/rate-limits
GET /api/health/rate-limits?force_refresh=true
```

Parameters:

- `force_refresh`: If true, bypasses the cache and gets fresh data (optional, default: false)

#### Response

```json
{
  "user_identifier": "user:1234****",
  "authenticated": true,
  "redis_available": true,
  "limits": {
    "generate_concept": {
      "limit": "10/month",
      "remaining": 8,
      "reset_after": 2419200
    },
    "store_concept": {
      "limit": "10/month",
      "remaining": 9,
      "reset_after": 2419200
    },
    "refine_concept": {
      "limit": "10/hour",
      "remaining": 10,
      "reset_after": 3600
    },
    "export_action": {
      "limit": "50/hour",
      "remaining": 50,
      "reset_after": 3600
    }
  },
  "default_limits": ["200/day", "50/hour", "10/minute"],
  "last_updated": "2023-01-01T12:00:00.123456",
  "cache_expires": "2023-01-01T12:00:05.123456"
}
```

### Non-Counting Rate Limit Check

```python
@router.get("/rate-limits-status")
async def rate_limits_status(request: Request, force_refresh: bool = False):
    """Get current rate limit information without counting against limits."""
```

This endpoint provides the same information as `/rate-limits` but does not count against rate limits.

#### Request

```
GET /api/health/rate-limits-status
GET /api/health/rate-limits-status?force_refresh=true
```

#### Response

Same as `/rate-limits`.

## Implementation Details

### Caching Mechanism

The module implements an in-memory cache for rate limit responses:

```python
# In-memory cache for rate limit responses
_rate_limits_cache: Dict[str, Dict[str, Any]] = {}
```

The cache has a 5-second expiration time, during which repeated requests from the same user will return the cached response.

### User Identification

The endpoint identifies users using the following priority:

1. Authenticated user ID (from request state)
2. User ID from Authorization header (if middleware didn't process it)
3. IP address as fallback

```python
# Cache key format
if auth_user_id:
    cache_key = f"user:{auth_user_id}"
else:
    cache_key = f"ip:{ip_address}"
```

### Limit Checks

The module checks several types of limits:

- `generate_concept`: 10/month limit for concept generation
- `store_concept`: 10/month limit for concept storage
- `refine_concept`: 10/hour limit for concept refinement
- `export_action`: 50/hour limit for export operations

## Usage Examples

### Client-Side Rate Limit Monitoring

```javascript
// Frontend example (JavaScript)
async function checkRateLimits() {
  try {
    const response = await fetch("/api/health/rate-limits-status");
    const limits = await response.json();

    // Example: Show remaining concept generations
    const remaining = limits.limits.generate_concept.remaining;
    const total = limits.limits.generate_concept.limit.split("/")[0];

    // Update UI
    updateProgressBar(remaining, total);

    // Show warning if low on remaining requests
    if (remaining < 3) {
      showWarning(`You have ${remaining} concept generations left this month.`);
    }

    return limits;
  } catch (error) {
    console.error("Failed to check rate limits", error);
    return null;
  }
}
```

### Rate Limit Header Integration

The information from these endpoints can be used together with the rate limit headers:

```javascript
// Check if we're close to a rate limit
async function shouldThrottle(endpoint) {
  const limits = await checkRateLimits();

  if (!limits) return false; // If check fails, don't throttle

  // Get endpoint-specific limit info
  const limitKey = endpointToLimitKey(endpoint); // e.g., /api/concepts/generate → generate_concept
  const limitInfo = limits.limits[limitKey];

  if (!limitInfo) return false;

  // Throttle if less than 10% of limit remaining
  const limit = parseInt(limitInfo.limit.split("/")[0], 10);
  return limitInfo.remaining < limit * 0.1;
}
```

## Security and Privacy

The endpoint includes several security and privacy features:

- User IDs are masked (e.g., `user:1234****`)
- IP addresses are partially obscured (e.g., `ip:192.168.**.**`)
- Redis keys are masked to prevent leaking sensitive information
- The response doesn't include specific keys or implementation details

## Related Files

- [Health Endpoints](endpoints.md): Basic health and configuration endpoints
- [Utility Functions](utils.md): Helper functions for rate limit calculations
- [Rate Limit Apply Middleware](../../middleware/rate_limit_apply.md): Middleware that enforces rate limits
