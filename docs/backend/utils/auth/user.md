# User Authentication Utilities

This module provides utilities for extracting and validating user identity in the Concept Visualizer API.

## Overview

The `auth.user` module contains functions for identifying and validating users from various sources, including:

- Request state (populated by middleware)
- Authorization headers
- Session data

This module is essential for endpoints that require user identification and authentication.

## Key Components

### HTTPBearer Authentication Scheme

```python
security = HTTPBearer(auto_error=False)
```

A FastAPI security scheme that extracts Bearer tokens from the Authorization header. The `auto_error=False` setting ensures that unauthenticated requests don't automatically return a 401 error, which allows for optional authentication.

## Core Functions

### `get_current_user_id`

```python
def get_current_user_id(request: Request) -> Optional[str]
```

Extracts and returns the current user ID from the request by checking multiple sources in priority order.

**Parameters:**

- `request`: The FastAPI request object

**Returns:**

- The user ID as a string if available, `None` otherwise

**Behavior:**

1. First checks if a user is in the request state (added by middleware)
2. Then tries to extract user ID from the Authorization header
3. Finally checks the session if available

### `get_current_user_auth`

```python
def get_current_user_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]
```

Extracts user ID from bearer token using the security dependency.

**Parameters:**

- `credentials`: The HTTP Authorization credentials from the security dependency

**Returns:**

- The user ID if available and valid, `None` otherwise

**Behavior:**

1. Validates that credentials exist
2. Decodes the JWT token
3. Extracts the subject (`sub`) claim which contains the user ID

### `get_current_user`

```python
def get_current_user(request: Request) -> dict
```

Gets the current user information as a dictionary, primarily used for endpoints that need user context.

**Parameters:**

- `request`: The FastAPI request object

**Returns:**

- A dictionary containing user information with at least the ID, or an empty dict if no user found

## Usage Examples

### Basic User Identification

```python
from fastapi import APIRouter, Request
from app.utils.auth.user import get_current_user_id

router = APIRouter()

@router.get("/user-info")
async def get_user_info(request: Request):
    user_id = get_current_user_id(request)
    if not user_id:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user_id": user_id
    }
```

### Using Security Dependencies

```python
from fastapi import APIRouter, Depends
from fastapi.security import HTTPAuthorizationCredentials
from app.utils.auth.user import security, get_current_user_auth

router = APIRouter()

@router.get("/protected")
async def protected_route(user_id: str = Depends(get_current_user_auth)):
    if not user_id:
        return {"error": "Unauthorized", "authenticated": False}

    return {
        "authenticated": True,
        "user_id": user_id,
        "message": "This is protected content"
    }
```

### Full User Context

```python
from fastapi import APIRouter, Request
from app.utils.auth.user import get_current_user

router = APIRouter()

@router.get("/user-profile")
async def get_user_profile(request: Request):
    user = get_current_user(request)
    if not user:
        return {"authenticated": False}

    return {
        "authenticated": True,
        "user": user
    }
```

## Integration with JWT

This module uses the `app.utils.jwt_utils` module's `decode_token` function to validate and extract information from JWT tokens. Ensure that the JWT configuration is properly set up for this module to work correctly.
