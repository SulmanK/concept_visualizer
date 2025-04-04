# Core Middleware

The `app.core.middleware` module provides middleware components used by the application to handle cross-cutting concerns like request prioritization.

## Available Middleware

### PrioritizationMiddleware

```python
from app.core.middleware import PrioritizationMiddleware

app.add_middleware(PrioritizationMiddleware)
```

This middleware prioritizes important API endpoints (like concept generation) over less critical endpoints (like health checks) when the server is busy.

#### Key Features

- **Request Prioritization**: Ensures concept generation endpoints get priority
- **Load Management**: Limits concurrent concept generation requests
- **Resource Allocation**: Serves cached responses for health checks during high load
- **Performance Tracking**: Adds response timing headers

#### Implementation Details

The middleware uses a semaphore to limit concurrent generation processes and tracks the number of active generation requests. When the server is busy with many generation requests, it can:

1. Prioritize concept generation endpoints
2. Serve cached responses for health check endpoints
3. Track request processing time
4. Add performance metrics to response headers

#### Example Configuration

```python
from fastapi import FastAPI
from app.core.middleware import PrioritizationMiddleware

app = FastAPI()
app.add_middleware(PrioritizationMiddleware)
```

#### Internal Implementation

The middleware identifies request types based on URL paths and HTTP methods:

- **High Priority**: Concept generation/refinement endpoints (`POST /api/concept/generate`, etc.)
- **Low Priority**: Health check endpoints (`GET /api/health`)
- **Special Handling**: Session endpoints that bypass rate limiting 