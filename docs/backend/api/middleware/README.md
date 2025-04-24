# API Middleware

This documentation provides an overview of the middleware components used in the Concept Visualizer API.

## Overview

Middleware in the Concept Visualizer API sits between the client and the route handlers, processing requests and responses to implement cross-cutting concerns such as:

- Authentication
- Rate limiting
- Response headers
- Logging
- Error handling

These middleware components use the FastAPI/Starlette middleware system, which follows the ASGI specification.

## Available Middleware

The API includes the following middleware components:

| Middleware                                      | File                    | Purpose                                  |
| ----------------------------------------------- | ----------------------- | ---------------------------------------- |
| [Authentication Middleware](auth_middleware.md) | `auth_middleware.py`    | JWT token validation and user extraction |
| [Rate Limit Application](rate_limit_apply.md)   | `rate_limit_apply.py`   | Enforces API rate limits                 |
| [Rate Limit Headers](rate_limit_headers.md)     | `rate_limit_headers.md` | Adds rate limit headers to responses     |

## Middleware Order

The order in which middleware is applied is important:

1. **Rate Limit Headers Middleware** - Added first, executed last (on response)
2. **Rate Limit Application Middleware** - Applied after headers middleware
3. **Authentication Middleware** - Applied last, executed first (on request)

This ensures that:

- Authentication happens before rate limiting (so we can identify the user)
- Rate limits are applied before handling the request
- Headers are added to the response after processing

## Configuring Middleware

Middleware is configured in the application factory function:

```python
from fastapi import FastAPI
from app.api.middleware.auth_middleware import AuthMiddleware
from app.api.middleware.rate_limit_apply import RateLimitApplyMiddleware
from app.api.middleware.rate_limit_headers import RateLimitHeadersMiddleware

def create_app() -> FastAPI:
    app = FastAPI()

    # Add middleware in reverse order (last added = first executed)
    app.add_middleware(
        AuthMiddleware,
        public_paths=["/api/health", "/api/auth/login"]
    )
    app.add_middleware(RateLimitApplyMiddleware)
    app.add_middleware(RateLimitHeadersMiddleware)

    return app
```

## Authentication Flow

The authentication middleware:

1. Extracts the JWT token from the Authorization header
2. Validates the token with the Supabase client
3. Attaches user information to the request state
4. Allows or rejects the request based on authentication status

## Rate Limiting Flow

The rate limiting system:

1. Checks if the request path matches any rate limit rules
2. Determines the user identity (from authentication)
3. Checks if the user has exceeded their rate limits
4. Rejects the request if limits are exceeded
5. Adds rate limit information to the request state
6. Adds rate limit headers to the response

## Bypassing Middleware

Certain paths bypass some or all middleware:

- Documentation paths (`/docs`, `/redoc`, `/openapi.json`) bypass authentication and rate limiting
- Health check endpoints (`/api/health/*`) bypass authentication but include rate limit headers
- Authentication endpoints (`/api/auth/*`) bypass authentication and rate limiting

## Extended Functionality

The middleware can be extended with additional functionality:

- Logging middleware to log request details
- Tracing middleware for performance monitoring
- CORS middleware for cross-origin requests
- Compression middleware for response compression

## Best Practices

1. **Keep Middleware Focused**: Each middleware should handle a single concern
2. **Order Matters**: Be careful about the order in which middleware is applied
3. **Error Handling**: Middleware should handle errors gracefully
4. **Performance**: Middleware runs on every request, so keep it efficient
5. **Testing**: Test middleware in isolation and integration
