# API Rate Limiting Utilities

The `app.utils.api_limits` module provides functions to apply rate limiting to API endpoints. This helps prevent abuse and ensures fair resource allocation.

## Key Functions

### `apply_rate_limit`

```python
async def apply_rate_limit(
    req: Request,
    endpoint: str,
    rate_limit: str,
    period: str = "month"
) -> None
```

Apply rate limiting to a request.

**Parameters:**

- `req`: The FastAPI request object
- `endpoint`: The endpoint path for tracking (e.g., "/concepts/generate")
- `rate_limit`: The rate limit string (e.g., "10/month")
- `period`: The period for rate limiting (e.g., "month", "hour")

**Returns:**

- `None`

**Example Usage:**

```python
from fastapi import APIRouter, Request
from app.utils.api_limits import apply_rate_limit

router = APIRouter()

@router.post("/generate")
async def generate_concept(request_data: dict, req: Request):
    # Apply rate limit - 10 requests per month
    await apply_rate_limit(req, "/concepts/generate", "10/month")
    
    # Endpoint implementation...
    return {"status": "success"}
```

## Implementation Details

The rate limiting implementation uses two approaches:

1. **SlowAPI Integration**: Leverages the SlowAPI library for decorator-based rate limiting
2. **Direct Redis Tracking**: Uses a custom Redis implementation for more reliable tracking

The implementation handles various edge cases:

- Connection issues with Redis
- Different identification methods (session cookie vs IP address)
- Proper error logging and graceful degradation
```

</rewritten_file>