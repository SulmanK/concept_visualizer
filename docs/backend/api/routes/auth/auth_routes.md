# Authentication Routes

This documentation covers the authentication endpoints in the Concept Visualizer API.

## Overview

The `auth_routes.py` module provides endpoints for authentication with Supabase, including session checking, login, and logout functionality.

## Models

### AuthResponse

```python
class AuthResponse(BaseModel):
    """Response model for authentication endpoints."""
    user_id: str
    token: str
    expires_at: int
```

This Pydantic model defines the structure of authentication response data:

- `user_id`: The unique identifier for the authenticated user
- `token`: The JWT access token for API requests
- `expires_at`: Timestamp (in seconds) when the token expires

## Available Endpoints

### Check Session

```python
@router.get("/session")
async def get_session(request: Request) -> Dict[str, object]:
    """Check if the user is authenticated."""
```

This endpoint checks if the user has an active authenticated session.

#### Request

```
GET /api/auth/session
```

No request body is required.

#### Response

If authenticated:

```json
{
  "authenticated": true,
  "user": {
    // User object from Supabase
  }
}
```

If not authenticated:

```json
{
  "authenticated": false,
  "message": "No active session"
}
```

### Login

```python
@router.post("/login")
async def login(request: Request, commons: CommonDependencies = Depends()) -> JSONResponse:
    """Log in a user with email and password."""
```

This endpoint authenticates a user with email and password using Supabase.

#### Request

```
POST /api/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

The endpoint requires email and password fields in the request body.

#### Response

If successful:

```json
{
  "authenticated": true,
  "user": {
    // User object from Supabase
  }
}
```

If failed:

```json
{
  "message": "Authentication failed: [error details]"
}
```

### Logout

```python
@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    """Log out the current user by clearing their session."""
```

This endpoint logs out the user by clearing their session data.

#### Request

```
POST /api/auth/logout
```

No request body is required.

#### Response

If successful:

```json
{
  "message": "Logged out successfully"
}
```

If no active session:

```json
{
  "message": "No active session to log out"
}
```

## Error Handling

The authentication endpoints can return the following error responses:

- `400 Bad Request`: Missing required fields in login request
- `401 Unauthorized`: Invalid credentials
- `500 Internal Server Error`: Server-side authentication issues with Supabase

## Security Considerations

- Session-based authentication is used
- User data is stored in the session
- Passwords are never logged or exposed in responses

## Usage Examples

### Client-Side Authentication Flow

```javascript
// Check if user is logged in
async function checkSession() {
  try {
    const response = await fetch("/api/auth/session", {
      method: "GET",
    });

    const data = await response.json();

    return {
      isAuthenticated: data.authenticated,
      user: data.user || null,
    };
  } catch (error) {
    console.error("Session check failed:", error);
    return { isAuthenticated: false, user: null };
  }
}

// Login with email and password
async function login(email, password) {
  try {
    const response = await fetch("/api/auth/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Login failed");
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error("Login failed:", error);
    throw error;
  }
}

// Logout
async function logout() {
  try {
    const response = await fetch("/api/auth/logout", {
      method: "POST",
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.message || "Logout failed");
    }

    return true;
  } catch (error) {
    console.error("Logout failed:", error);
    return false;
  }
}
```

## Related Files

- [Auth Middleware](../../middleware/auth_middleware.md): Middleware for authenticating requests
- [Supabase Client](../../../core/supabase/client.md): Client for interacting with Supabase
