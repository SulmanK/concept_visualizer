# Health Check API

This document describes the health check endpoints in the Concept Visualizer API.

## Overview

The health check API provides functionality to:
- Verify API availability and responsiveness
- Check the status of dependent services
- Monitor rate limit usage
- Provide system status information

These endpoints are useful for:
- Client applications to verify API availability
- Monitoring systems to track API health
- Users to check their rate limit status
- Debugging service connection issues

## Endpoints

### Basic Health Check

```
GET /api/health/
```

Performs a basic health check of the API.

#### Response

```json
{
  "status": "healthy",
  "timestamp": "2023-04-01T12:34:56Z",
  "version": "1.0.0",
  "environment": "production"
}
```

### Rate Limit Status

```
GET /api/health/rate-limits
```

Retrieves the current rate limit status for the user.

#### Response

```json
{
  "rate_limits": {
    "concept_generation": {
      "limit": 10,
      "remaining": 5,
      "reset_at": "2023-05-01T00:00:00Z",
      "period": "month"
    },
    "concept_refinement": {
      "limit": 10,
      "remaining": 8,
      "reset_at": "2023-04-02T12:34:56Z",
      "period": "hour"
    },
    "svg_conversion": {
      "limit": 20,
      "remaining": 15,
      "reset_at": "2023-04-02T12:34:56Z",
      "period": "hour"
    },
    "general": {
      "limit": 200,
      "remaining": 180,
      "reset_at": "2023-04-02T00:00:00Z",
      "period": "day"
    }
  },
  "session_id": "user-session-id"
}
```

### Service Health Check

```
GET /api/health/services
```

Checks the health of all dependent services.

#### Response

```json
{
  "services": {
    "jigsawstack": {
      "status": "healthy",
      "latency_ms": 120,
      "last_checked": "2023-04-01T12:34:56Z"
    },
    "supabase": {
      "status": "healthy",
      "latency_ms": 45,
      "last_checked": "2023-04-01T12:34:56Z"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 5,
      "last_checked": "2023-04-01T12:34:56Z"
    }
  },
  "overall_status": "healthy",
  "timestamp": "2023-04-01T12:34:56Z"
}
```

## Implementation Details

### Health Check Process

The health check process:
1. Verifies API server functionality
2. Performs lightweight checks of dependent services
3. Caches service health status with a short TTL to prevent overload
4. Returns appropriate status codes based on the health state

### Rate Limit Checking

Rate limit checking:
1. Retrieves the user's session ID from cookies
2. Queries rate limit counters from the database
3. Calculates remaining quota and reset times
4. Returns detailed rate limit information

### Service Health Checking

Service health checking:
1. Performs minimal operations against each service
2. Measures response time
3. Determines status based on response and latency
4. Aggregates results to determine overall system health

## Error Handling

Common errors:

| Status Code | Error Code | Description |
|-------------|------------|-------------|
| 401 | authentication_error | No session ID provided (for rate limit endpoint) |
| 503 | service_unavailable | One or more dependent services are unhealthy |

## Best Practices

1. **Regular Health Monitoring**: Implement automated health checks in client applications
2. **Proactive Rate Limit Checking**: Check rate limits before making resource-intensive requests
3. **Graceful Degradation**: Handle service unavailability gracefully in client applications
4. **Status Caching**: Cache health status with appropriate TTL to avoid excessive calls 