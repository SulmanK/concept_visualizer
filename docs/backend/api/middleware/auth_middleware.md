# Authentication Middleware

This documentation covers the authentication middleware used in the Concept Visualizer API.

## Overview

The `auth_middleware.py` module provides middleware for JWT token authentication with Supabase. It:

- Verifies JWT tokens in request headers
- Extracts and validates user information
- Attaches user data to request state for use in endpoints
- Handles authentication errors with appropriate responses
- Provides utility functions for extracting user information

## Components

### AuthMiddleware

```python
class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Supabase authentication via JWT tokens."""
```

This middleware class handles the authentication process:

#### Constructor

```python
def __init__(
    self,
    app,
    public_paths: Optional[list[str]] = None,
):
    """Initialize the authentication middleware."""
```

Parameters:
- `app`: The FastAPI application instance
- `public_paths`: List of paths that should be accessible without authentication

#### Dispatch Method

```python
async def dispatch(
    self, request: Request, call_next: RequestResponseEndpoint
) -> Response:
    """Process the request, verifying authentication when needed."""
```

The dispatch method:
1. Allows OPTIONS requests for CORS
2. Skips authentication for public paths
3. Extracts and validates JWT tokens from the Authorization header
4. Attaches user data to request state if authenticated
5. Returns appropriate error responses for authentication failures

### Utility Functions

The module provides two utility functions for extracting user information:

```python
def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get the current authenticated user from request state."""
```

```python
def get_current_user_id(request: Request) -> Optional[str]:
    """Get the current authenticated user ID from request state."""
```

These functions can be used in FastAPI dependencies to access the authenticated user.

## Usage Examples

### Configuring the Middleware

```python
from fastapi import FastAPI
from app.api.middleware.auth_middleware import AuthMiddleware

app = FastAPI()

# Configure auth middleware with public paths
app.add_middleware(
    AuthMiddleware,
    public_paths=[
        "/api/health",
        "/api/auth/login",
        "/api/auth/register",
    ]
)
```

### Using Authenticated User in Endpoints

```python
from fastapi import APIRouter, Request, Depends
from app.api.middleware.auth_middleware import get_current_user, get_current_user_id

router = APIRouter()

@router.get("/profile")
async def get_profile(
    user_id: str = Depends(get_current_user_id)
):
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    # Use user_id to fetch and return user profile
    return {"user_id": user_id, "profile": "..."}
```

## Authentication Flow

1. Client includes a JWT token in the Authorization header: `Authorization: Bearer [token]`
2. AuthMiddleware extracts and validates the token using Supabase auth client
3. If valid, user information is attached to request.state.user
4. If invalid or missing, a 401 Unauthorized response is returned
5. For public paths (including docs), authentication is skipped

## Special Cases

- **OPTIONS Requests**: Always allowed for CORS preflight requests
- **Documentation Endpoints**: `/docs`, `/redoc`, and `/openapi.json` are automatically public
- **Rate Limit Endpoints**: For `/api/health/rate-limits/*`, authentication is attempted but not required

## Security Considerations

- Tokens are validated cryptographically by the Supabase auth client
- User IDs are masked in logs for security
- Authentication errors include minimal information to prevent information leakage 