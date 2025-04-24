# Application Factory Module

The `factory.py` module provides the central application factory function that creates and configures the FastAPI application for the Concept Visualizer API.

## Overview

The application factory pattern is used to:

1. Initialize the FastAPI application with proper configuration
2. Set up middleware for CORS, authentication, and rate limiting
3. Configure API routes and error handlers
4. Set up logging and other application-wide services

This approach improves testability and allows for different configurations in different environments.

## Main Factory Function

```python
def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    # Set up logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_dir="logs"
    )

    # Create FastAPI app with OpenAPI configuration
    app = FastAPI(
        title="Concept Visualizer API",
        description="API for generating and managing visual concepts",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure middleware, routes, etc.
    # ...

    return app
```

## Configuration Steps

### CORS Configuration

The factory configures Cross-Origin Resource Sharing (CORS) based on environment settings:

```python
cors_origins = settings.CORS_ORIGINS
if not cors_origins:
    # Fallback for development
    cors_origins = [
        "http://localhost",
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Process-Time", "X-Rate-Limit-Limit", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"],
    max_age=86400  # 24 hours cache for preflight requests
)
```

### Middleware Configuration

Middleware is added in a specific order (executed in reverse):

```python
# Add authentication middleware
app.add_middleware(AuthMiddleware, public_paths=PUBLIC_PATHS)

# Add rate limit apply middleware
app.add_middleware(RateLimitApplyMiddleware)

# Add rate limit headers middleware
app.add_middleware(RateLimitHeadersMiddleware)
```

Note: FastAPI/Starlette executes middleware in **reverse** order of registration:

1. First RateLimitHeadersMiddleware (adds headers to responses)
2. Then RateLimitApplyMiddleware (checks and applies limits)
3. Then AuthMiddleware (authenticates the user)

### Route Configuration

API routes are configured through a dedicated function:

```python
# Configure API routes (this also sets up error handlers)
configure_api_routes(app)
```

### Rate Limiting Setup

Rate limiting is configured for the application:

```python
# Configure rate limiting
setup_limiter_for_app(app)
```

## Usage

The factory is used in the main application module:

```python
# In main.py
from app.core.factory import create_app

app = create_app()
```

## Testing

For testing, you can create a test version of the application with modified settings:

```python
# In a test file
from app.core.factory import create_app
from unittest.mock import patch

def test_app():
    with patch('app.core.config.settings') as mock_settings:
        # Configure mock settings
        mock_settings.CORS_ORIGINS = ["http://testserver"]
        mock_settings.LOG_LEVEL = "ERROR"
        # ...

        # Create test app
        app = create_app()
        # Use app for testing
```

## Related Documentation

- [Config](config.md): Application configuration used by the factory
- [API Router](../api/router.md): API route configuration function
- [Auth Middleware](../api/middleware/auth_middleware.md): Authentication middleware
- [Rate Limiting](api/middleware/rate_limit_apply.md): Rate limiting middleware
- [Logging Setup](../utils/logging/setup.md): Logging configuration
