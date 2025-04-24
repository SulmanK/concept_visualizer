# Authentication Routes

This documentation covers the authentication endpoints in the Concept Visualizer API.

## Overview

The `auth_routes.py` module provides endpoints for authentication with Supabase, including anonymous sign-in, token refresh, and sign-out functionality.

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

### Anonymous Sign-In

```python
@router.post("/signin-anonymous", response_model=AuthResponse)
async def signin_anonymous(req: Request, commons: CommonDependencies = Depends()):
    """Sign in anonymously using Supabase."""
```

This endpoint creates an anonymous user in Supabase and returns a JWT token for authenticating API requests.

#### Request

```
POST /api/auth/signin-anonymous
```

No request body is required.

#### Response

```json
{
  "user_id": "1234-5678-9012-3456",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": 1672531200
}
```

- `user_id`: Unique identifier for the anonymous user
- `token`: JWT token to use in the Authorization header for future requests
- `expires_at`: Unix timestamp when the token will expire

### Token Refresh

```python
@router.post("/refresh", response_model=AuthResponse)
async def refresh_token(req: Request, commons: CommonDependencies = Depends()):
    """Refresh an existing authentication token."""
```

This endpoint refreshes an existing JWT token, extending its validity period.

#### Request

```
POST /api/auth/refresh
Authorization: Bearer {refresh_token}
```

The endpoint requires the current refresh token in the Authorization header.

#### Response

```json
{
  "user_id": "1234-5678-9012-3456",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_at": 1672617600
}
```

- `user_id`: Unique identifier for the user
- `token`: New JWT token to use for future requests
- `expires_at`: Updated expiration timestamp

### Sign Out

```python
@router.post("/signout", status_code=status.HTTP_204_NO_CONTENT)
async def signout(req: Request, commons: CommonDependencies = Depends()):
    """Sign out a user, invalidating their session."""
```

This endpoint invalidates the user's session, effectively logging them out.

#### Request

```
POST /api/auth/signout
Authorization: Bearer {access_token}
```

The endpoint requires a valid access token in the Authorization header.

#### Response

- Status Code: 204 No Content
- No response body is returned on success

## Error Handling

The authentication endpoints can return the following error responses:

- `401 Unauthorized`: Missing or invalid authentication credentials
- `500 Internal Server Error`: Server-side authentication issues with Supabase
- `503 Service Unavailable`: Authentication service is currently unavailable

## Security Considerations

- User IDs are masked in logs for privacy
- Token expiration is enforced through the `expires_at` field
- Anonymous users have limited access to API functionality

## Usage Examples

### Client-Side Authentication Flow

```javascript
// Authenticate anonymously
async function signInAnonymously() {
  try {
    const response = await fetch("/api/auth/signin-anonymous", {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Authentication failed");
    }

    const auth = await response.json();

    // Store authentication data
    localStorage.setItem(
      "auth",
      JSON.stringify({
        userId: auth.user_id,
        token: auth.token,
        expiresAt: auth.expires_at,
      }),
    );

    return auth;
  } catch (error) {
    console.error("Sign-in failed:", error);
    return null;
  }
}

// Refresh token when needed
async function refreshToken() {
  try {
    const auth = JSON.parse(localStorage.getItem("auth"));

    if (!auth || !auth.token) {
      throw new Error("No authentication data found");
    }

    const response = await fetch("/api/auth/refresh", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });

    if (!response.ok) {
      throw new Error("Token refresh failed");
    }

    const newAuth = await response.json();

    // Update stored authentication data
    localStorage.setItem(
      "auth",
      JSON.stringify({
        userId: newAuth.user_id,
        token: newAuth.token,
        expiresAt: newAuth.expires_at,
      }),
    );

    return newAuth;
  } catch (error) {
    console.error("Token refresh failed:", error);
    return null;
  }
}

// Sign out
async function signOut() {
  try {
    const auth = JSON.parse(localStorage.getItem("auth"));

    if (!auth || !auth.token) {
      return true; // Already signed out
    }

    const response = await fetch("/api/auth/signout", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${auth.token}`,
      },
    });

    // Clear local auth data regardless of response
    localStorage.removeItem("auth");

    return response.ok;
  } catch (error) {
    console.error("Sign-out failed:", error);
    return false;
  }
}
```

## Related Files

- [Auth Middleware](../../middleware/auth_middleware.md): Middleware for authenticating requests
- [Supabase Client](../../../core/supabase/client.md): Client for interacting with Supabase
- [Security](../../../utils/security/mask.md): Utility for masking sensitive information
