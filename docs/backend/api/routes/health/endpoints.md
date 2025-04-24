# Health Endpoints

This documentation covers the health and configuration endpoints in the Concept Visualizer API.

## Overview

The `endpoints.py` module provides basic health check endpoints that report the current status of the application and expose non-sensitive configuration data to the frontend.

## Available Endpoints

### Health Check

```python
@router.get("/ping")
async def ping():
    """Simple endpoint for checking if the server is alive."""
```

This endpoint returns a simple status message to confirm that the API is running.

#### Request

```
GET /api/health/ping
```

#### Response

```json
{
  "status": "ok",
  "timestamp": "2023-01-01T12:00:00.123456"
}
```

- `status`: Always "ok" if the server is running
- `timestamp`: ISO-formatted datetime of when the request was processed

### Frontend Configuration

```python
@router.get("/config", response_model=Dict[str, StorageBucketsConfig])
async def get_frontend_config():
    """Get configuration values for the frontend."""
```

This endpoint returns non-sensitive configuration values needed by the frontend.

#### Request

```
GET /api/health/config
```

#### Response

```json
{
  "storage": {
    "concept": "concepts",
    "palette": "palettes"
  }
}
```

- `storage`: Information about storage bucket names
  - `concept`: The bucket name for storing concept images
  - `palette`: The bucket name for storing palette images

## Configuration Model

The endpoint uses a Pydantic model for response validation:

```python
class StorageBucketsConfig(BaseModel):
    """Storage bucket names for frontend use."""
    concept: str
    palette: str
```

## Security Considerations

- These endpoints only expose non-sensitive configuration values
- No authentication is required to access these endpoints
- Rate limiting is still applied to prevent abuse

## Usage Examples

### Checking API Health

```javascript
// Frontend example (JavaScript)
const checkHealth = async () => {
  try {
    const response = await fetch("/api/health/ping");
    const data = await response.json();

    if (data.status === "ok") {
      console.log("API is healthy");
      return true;
    } else {
      console.error("API health check failed");
      return false;
    }
  } catch (error) {
    console.error("API is unreachable", error);
    return false;
  }
};
```

### Fetching Configuration

```javascript
// Frontend example (JavaScript)
const getConfig = async () => {
  try {
    const response = await fetch("/api/health/config");
    const config = await response.json();

    // Use the storage bucket names
    console.log("Concept bucket:", config.storage.concept);
    console.log("Palette bucket:", config.storage.palette);

    return config;
  } catch (error) {
    console.error("Failed to load configuration", error);
    return null;
  }
};
```

## Related Files

- [Health Check Implementation](check.md): More detailed health checks
- [Rate Limits](limits.md): Rate limit information endpoints
- [Utility Functions](utils.md): Helper functions for health endpoints
