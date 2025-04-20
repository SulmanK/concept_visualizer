# Health Check Implementation

This documentation covers the health check implementation in the Concept Visualizer API.

## Overview

The `check.py` module provides health check endpoints to verify that the API is running correctly. These endpoints are designed to be lightweight and responsive even when the system is under heavy load.

## Health Check Caching

The module implements an in-memory caching mechanism to reduce the load on the server during busy periods:

```python
# In-memory cache for health check responses
_health_cache = {
    "status": "ok",
    "timestamp": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(seconds=30)
}
```

The cache has a 30-second expiration time, during which repeated health check requests will return the cached response instead of generating a new one.

## Available Endpoints

### Root Health Check

```python
@router.get("/")
@router.head("/")
async def health_root(request: Request):
    """Root health check endpoint."""
```

This is the simplest health check endpoint, designed to be extremely lightweight. It always returns a 200 OK status with minimal processing.

#### Request

```
GET /api/health/
HEAD /api/health/
```

#### Response

```json
{
  "status": "ok"
}
```

### Detailed Health Check

```python
@router.get("/check")
@router.head("/check")
async def health_check(request: Request):
    """Detailed health check endpoint."""
```

This endpoint provides a more detailed health check that uses the caching mechanism. In a production environment, this could be extended to check database connectivity, external services, etc.

#### Request

```
GET /api/health/check
HEAD /api/health/check
```

#### Response

```json
{
  "status": "ok"
}
```

In case of a non-critical error:

```json
{
  "status": "ok",
  "warning": "Error occurred but service is still responding"
}
```

## Error Handling

The health check endpoints are designed to be resilient:

- Exceptions are caught and logged
- The service returns a successful response even if there are non-critical errors
- Detailed error information is logged for debugging

## Usage in Monitoring

These endpoints are designed to be used with external monitoring tools:

- **Kubernetes Liveness Probe**: Use `/api/health/` for basic liveness checks
- **Kubernetes Readiness Probe**: Use `/api/health/check` for readiness checks
- **Load Balancer Health Checks**: Use either endpoint as appropriate
- **Monitoring Systems**: Tools like Prometheus, Datadog, or New Relic can poll these endpoints

## Example: Kubernetes Manifest

```yaml
livenessProbe:
  httpGet:
    path: /api/health/
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 10
readinessProbe:
  httpGet:
    path: /api/health/check
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 30
```

## Example: External Monitoring Script

```python
import requests
import time
import logging

def check_api_health():
    try:
        response = requests.get("https://api.example.com/api/health/check", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "ok":
                return True
            else:
                logging.warning(f"API returned non-OK status: {data}")
                return False
        else:
            logging.error(f"API health check failed with status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"API health check failed: {str(e)}")
        return False

# Check health every minute
while True:
    if not check_api_health():
        # Alert on failure
        send_alert("API health check failed")
    time.sleep(60)
```

## Related Files

- [Health Endpoints](endpoints.md): Basic health and configuration endpoints
- [Rate Limits](limits.md): Rate limit information endpoints 