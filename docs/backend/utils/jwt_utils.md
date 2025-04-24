# JWT Utilities

The `jwt_utils.py` module provides essential utilities for JWT (JSON Web Token) generation, validation, and management in the Concept Visualizer API.

## Overview

This module is responsible for:

1. Creating JWT tokens for authentication and authorization
2. Verifying and validating JWT tokens
3. Generating specialized tokens for Supabase Storage operations
4. Extracting user information from tokens
5. Supporting different token types for various use cases

## Key Functions

### JWT Token Creation

```python
def create_jwt_token(
    subject: str,
    expires_delta: Optional[timedelta] = None,
    claims: Optional[Dict[str, Any]] = None,
    secret_key: Optional[str] = None
) -> str:
    """
    Create a JWT token.

    Args:
        subject: The subject of the token (usually user ID)
        expires_delta: Optional expiration time delta (default: 15 minutes)
        claims: Optional additional claims to include in the token
        secret_key: Optional secret key to sign the token (default: from settings)

    Returns:
        Encoded JWT token as a string

    Raises:
        ValueError: If subject is not provided or secret key is missing
    """
    # Implementation...
```

### Supabase JWT Creation

```python
def create_supabase_jwt(
    user_id: str,
    role: str = "authenticated",
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None
) -> str:
    """
    Create a Supabase-compatible JWT token.

    Args:
        user_id: The user ID to encode in the token
        role: The role to assign (default: "authenticated")
        expires_delta: Optional expiration time delta (default: 24 hours)
        extra_claims: Optional additional claims to include

    Returns:
        Encoded Supabase JWT token as a string

    Raises:
        ValueError: If JWT secret is not configured
    """
    # Implementation...
```

### Storage-Specific JWT

```python
def create_supabase_jwt_for_storage(
    path: str,
    expiry: int = 3600,  # 1 hour
    role: str = "authenticated"
) -> str:
    """
    Create a JWT token specifically for Supabase Storage operations.

    Args:
        path: The storage path being accessed
        expiry: Token expiration time in seconds (default: 1 hour)
        role: The role to assign (default: "authenticated")

    Returns:
        Encoded JWT token for storage operations

    Raises:
        ValueError: If JWT secret is not configured
    """
    # Implementation...
```

### Token Verification

```python
def verify_jwt_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithms: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Verify a JWT token and return its claims.

    Args:
        token: The JWT token to verify
        secret_key: Optional secret key to verify the token (default: from settings)
        algorithms: Optional list of allowed algorithms (default: ["HS256"])

    Returns:
        Dictionary of token claims

    Raises:
        JWTError: If token is invalid or expired
    """
    # Implementation...
```

### User Information Extraction

```python
def get_user_id_from_token(token: str) -> Optional[str]:
    """
    Extract user ID from a JWT token.

    Args:
        token: The JWT token

    Returns:
        User ID from the token or None if extraction fails
    """
    # Implementation...
```

## Token Structure

### Standard Token

The standard JWT token has the following structure:

```json
{
  "sub": "user-123", // Subject (user ID)
  "exp": 1628097060, // Expiration timestamp
  "iat": 1628010660, // Issued at timestamp
  "nbf": 1628010660, // Not valid before timestamp
  "jti": "unique-token-id", // JWT ID (unique identifier)
  "custom_claim": "value" // Any custom claims
}
```

### Supabase Token

Supabase tokens include additional claims required by Supabase:

```json
{
  "aud": "authenticated", // Audience
  "sub": "user-123", // Subject (user ID)
  "email": "user@example.com", // User email (if available)
  "exp": 1628097060, // Expiration timestamp
  "iat": 1628010660, // Issued at timestamp
  "role": "authenticated", // User role
  "session_id": "session-456" // Session ID
}
```

### Storage Token

Storage-specific tokens include claims required for Supabase Storage operations:

```json
{
  "aud": "authenticated", // Audience
  "sub": "user-123", // Subject (user ID)
  "ref": "storage-path", // Storage path reference
  "exp": 1628097060, // Expiration timestamp
  "iat": 1628010660, // Issued at timestamp
  "role": "authenticated" // User role
}
```

## Usage Examples

### Creating a Standard JWT Token

```python
from app.utils.jwt_utils import create_jwt_token
from datetime import timedelta

# Create a token that expires in 30 minutes
token = create_jwt_token(
    subject="user-123",
    expires_delta=timedelta(minutes=30),
    claims={"user_role": "admin", "permissions": ["read", "write"]}
)

print(f"Token: {token}")
```

### Creating a Storage Token

```python
from app.utils.jwt_utils import create_supabase_jwt_for_storage

# Create a token for a specific storage path
storage_token = create_supabase_jwt_for_storage(
    path="user-123/images/profile.png",
    expiry=7200  # 2 hours
)

# Use the token for storage operations
headers = {"Authorization": f"Bearer {storage_token}"}
```

### Verifying a Token

```python
from app.utils.jwt_utils import verify_jwt_token

try:
    # Verify a token and get its claims
    claims = verify_jwt_token(token)

    # Extract user information
    user_id = claims.get("sub")
    user_role = claims.get("user_role")
    permissions = claims.get("permissions", [])

    if "write" in permissions and user_role == "admin":
        # Allow the operation
        pass

except Exception as e:
    # Handle invalid token
    print(f"Token verification failed: {str(e)}")
```

## Security Considerations

The module implements several security best practices:

1. **Token Expiration**: All tokens have an expiration time to limit their validity period
2. **Required Claims**: Tokens include standard claims like `sub`, `exp`, `iat`
3. **Signature Verification**: Tokens are cryptographically signed and verified
4. **Secret Management**: JWT secrets are securely managed through application settings
5. **Minimal Information**: Tokens contain only necessary information

### Secret Key Management

The JWT secret keys are managed through application settings:

```python
# Getting the JWT secret
secret_key = settings.JWT_SECRET_KEY

# Getting the Supabase JWT secret
supabase_secret = settings.CONCEPT_SUPABASE_JWT_SECRET
```

These values should be securely stored in environment variables or a secure vault.

## Error Handling

The module includes comprehensive error handling:

```python
try:
    # Attempt to decode and verify the token
    payload = jwt.decode(
        token,
        key=secret_key,
        algorithms=algorithms or ["HS256"]
    )
    return payload
except jwt.PyJWTError as e:
    # Handle specific JWT errors
    error_msg = f"JWT verification failed: {str(e)}"
    logger.warning(error_msg)
    raise JWTError(error_msg)
```

## Claims Customization

Additional claims can be added to tokens:

```python
# Standard claims automatically added
standard_claims = {
    "sub": subject,
    "exp": expiration_time,
    "iat": issued_at,
    "nbf": not_before,
    "jti": str(uuid.uuid4())
}

# Add custom claims
if claims:
    for key, value in claims.items():
        if key not in standard_claims:
            standard_claims[key] = value
```

## Related Documentation

- [Supabase Client](../../core/supabase/client.md): Uses JWT tokens for authentication
- [Image Storage](../../core/supabase/image_storage.md): Uses storage-specific JWT tokens
- [Auth Middleware](../../api/middleware/auth_middleware.md): Validates JWT tokens for API access
- [Security Utilities](../security/mask.md): Related security utilities
