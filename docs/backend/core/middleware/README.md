# Core Middleware

The `core/middleware` package provides low-level middleware components that operate at the ASGI level, below the FastAPI application layer.

## Overview

Unlike API middleware which is specific to FastAPI routes, core middleware operates at the ASGI framework level, processing all requests including static files and non-API endpoints. This package includes:

1. Base middleware classes and utilities
2. CORS configuration
3. Request identification
4. Logging and telemetry

## Key Components

### Base Middleware

The base middleware components establish patterns for ASGI middleware implementation:

- Base classes for middleware creation
- Middleware chaining utilities
- Context propagation helpers

### CORS Configuration

The CORS middleware configures Cross-Origin Resource Sharing:

- Allows specified origins
- Controls allowed headers and methods
- Manages preflight requests
- Sets appropriate cache headers

### Request Identification

This middleware adds unique identifiers to requests:

- Generates request IDs for tracing
- Preserves IDs across services
- Includes IDs in response headers
- Supports distributed tracing

### Logging Middleware

Provides request/response logging:

- Captures timing information
- Logs request details
- Records response status
- Supports debug logging

## Usage

Core middleware is typically configured in the application factory:

```python
from app.core.factory import create_app
from app.core.middleware import setup_cors, setup_request_id_middleware

app = create_app()
app = setup_cors(app)
app = setup_request_id_middleware(app)
```

## Related Documentation

- [API Middleware](../../api/middleware/README.md): Higher-level FastAPI middleware
- [Application Factory](../factory.md): Application creation and middleware setup
- [Logging Setup](../../utils/logging/setup.md): Logging configuration
