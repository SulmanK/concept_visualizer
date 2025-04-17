# Rate Limit Optimization Design Document

## Problem Statement

The current rate limit implementation has the following issues:

1. The frontend's rate limit check endpoint (`/api/health/rate-limits`) itself decrements the user's rate limit counter.
2. When users refresh the page (F5), each reload triggers a new set of API calls that count against rate limits.
3. The counter increments for all API requests made during page load, which may include non-essential calls like checking rate limits.
4. On navigation between SPA pages, the rate limit counters don't update, creating an inconsistent experience.

## Solution Design

We'll implement a professional approach to rate limit handling that follows industry best practices used by major APIs like GitHub, Stripe, and Twitter.

### 1. Non-Counting Rate Limit Endpoint

Create a dedicated endpoint for checking rate limits that doesn't count against the user's quota.

#### Backend Implementation

```python
@router.get("/rate-limits-status", include_in_schema=True)
async def rate_limits_status(request: Request):
    """Get current rate limit information without counting against limits.
    
    This endpoint is explicitly exempted from rate limiting.
    """
    # Same implementation as /rate-limits but marked as non-counting
    # in the rate limiter
```

### 2. Rate Limit Headers in Every Response

Add standard rate limit headers to all API responses so clients can track limits without making dedicated calls.

#### Backend Implementation

1. Create a middleware that adds rate limit headers to all API responses:

```python
# In app/api/middleware/rate_limit_headers.py
class RateLimitHeadersMiddleware:
    """Add rate limit headers to all API responses."""
    
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add headers if rate limit info is available from request state
        if hasattr(request.state, "limiter_info"):
            info = request.state.limiter_info
            response.headers["X-RateLimit-Limit"] = str(info.get("limit", ""))
            response.headers["X-RateLimit-Remaining"] = str(info.get("remaining", ""))
            response.headers["X-RateLimit-Reset"] = str(info.get("reset", ""))
            
        return response
```

2. Register this middleware in the app factory.

### 3. Client-Side Rate Limit Cache

Implement a sophisticated client-side cache for rate limits with automatic expiration.

#### Frontend Implementation

```typescript
// In rateLimitService.ts
interface RateLimitCache {
  limits: RateLimitsResponse;
  timestamp: number;
  expiresAt: number;
}

// Cache rate limits in memory with expiration
const rateLimitCache: Record<string, RateLimitCache> = {};

// Extract rate limit info from response headers
export const extractRateLimitHeaders = (
  response: Response,
  endpoint: string
): void => {
  // Get header values
  const limit = response.headers.get("X-RateLimit-Limit");
  const remaining = response.headers.get("X-RateLimit-Remaining");
  const reset = response.headers.get("X-RateLimit-Reset");
  
  if (limit && remaining && reset) {
    // Update cache for this specific endpoint
    updateRateLimitCache(endpoint, {
      limit: parseInt(limit, 10),
      remaining: parseInt(remaining, 10),
      reset: parseInt(reset, 10)
    });
  }
};
```

### 4. Optimistic UI Updates

Update the UI optimistically when actions are performed to reflect rate limit changes without waiting for refreshes.

```typescript
// In useRateLimits.ts
const useRateLimits = () => {
  // ... existing implementation

  // Add a function to optimistically update limits when an action is performed
  const decrementRateLimit = useCallback((endpoint: string) => {
    setRateLimits((current) => {
      if (!current) return current;
      
      // Create a deep copy of the rate limits
      const updated = { ...current };
      
      // Find the appropriate limit category based on endpoint
      const category = mapEndpointToCategory(endpoint);
      
      if (category && updated.limits[category]) {
        // Decrement the remaining count
        updated.limits[category].remaining = Math.max(
          0, 
          updated.limits[category].remaining - 1
        );
      }
      
      return updated;
    });
  }, []);
  
  return {
    rateLimits,
    isLoading,
    error,
    refetch: fetchData,
    decrementRateLimit
  };
};
```

### 5. Endpoint Exemption Pattern

Explicitly exempt status and health endpoints from counting against rate limits.

#### Backend Implementation

```python
# In app/api/routes/health/__init__.py
NON_COUNTING_ENDPOINTS = [
    "/health/rate-limits-status",
    "/health/ping",
    "/health/status"
]

# In app/core/limiter/config.py
# Add configuration for non-counting endpoints
NON_COUNTING_ENDPOINTS = [
    *health.NON_COUNTING_ENDPOINTS,
    # Add other endpoints that shouldn't count against limits
]
```

## Implementation Plan

### Backend Changes

1. Create a new non-counting endpoint `GET /api/health/rate-limits-status`
2. Implement rate limit header middleware
3. Update rate limit check logic to exempt specified endpoints
4. Add response headers to all API endpoints

### Frontend Changes

1. Enhance `rateLimitService.ts` with caching and header extraction
2. Update `useRateLimits.ts` hook to use cache and support optimistic updates
3. Modify API client to extract rate limit headers from all responses
4. Update UI components to react to rate limit changes

## Best Practices Implemented

1. **Non-Counting Status Endpoints**: Following GitHub and Stripe APIs' approach of excluding status endpoints from rate limits.
2. **X-RateLimit Headers**: Using standard HTTP header conventions (GitHub, Twitter APIs).
3. **Client-Side Caching**: Implementing sophisticated caching similar to SDKs for Twilio and Stripe.
4. **Optimistic UI Updates**: Using the same pattern as professional API dashboards.
5. **Consistent Experience**: Ensuring consistent rate limit display across page navigations.

## Expected Results

1. Page refreshes will no longer significantly impact rate limit counters
2. Rate limit status will be consistent across page navigations
3. Users will have accurate information about their remaining API quota
4. The application will feel more professional with optimistic UI updates
5. Backend load will be reduced by leveraging client-side caching

## Monitoring and Validation

After implementation, we should:

1. Monitor Redis usage patterns to verify reduced load
2. Track client-side cache hit rates
3. Validate the user experience across different devices and browsers
4. Measure performance impact of the changes 