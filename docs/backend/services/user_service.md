# User Service

The `UserService` is responsible for managing user accounts, authentication, authorization, and user-related operations within the application.

## Overview

The User Service provides a high-level API for:

1. User registration and account management
2. Authentication and session management
3. Authorization and permission checking
4. User profile management and preferences
5. User activity tracking and analytics

## Key Components

### UserService Class

```python
class UserService:
    """Service for managing users and authentication."""
    
    def __init__(
        self, 
        user_persistence: UserPersistenceService,
        auth_provider: AuthProvider,
        config: UserServiceConfig
    ):
        """Initialize the UserService with required dependencies."""
```

**Dependencies:**
- `user_persistence`: Service for persisting user data in the database
- `auth_provider`: Provider for authentication mechanisms
- `config`: Configuration parameters for the user service

### User Authentication

```python
async def authenticate_user(
    self,
    email: str,
    password: str
) -> AuthToken:
    """Authenticate a user with email and password."""
```

Authenticates a user with the provided credentials.

**Parameters:**
- `email`: User's email address
- `password`: User's password

**Returns:**
- `AuthToken`: Authentication token for the user session

```python
async def verify_token(
    self,
    token: str
) -> User:
    """Verify an authentication token and return the associated user."""
```

Verifies an authentication token and returns the associated user.

**Parameters:**
- `token`: Authentication token to verify

**Returns:**
- `User`: The authenticated user

### User Registration and Management

```python
async def register_user(
    self,
    email: str,
    password: str,
    name: str,
    profile_data: Dict[str, Any] = {}
) -> User:
    """Register a new user."""
```

Registers a new user with the provided information.

**Parameters:**
- `email`: User's email address
- `password`: User's password
- `name`: User's full name
- `profile_data`: Additional profile information

**Returns:**
- `User`: The newly created user

```python
async def update_user_profile(
    self,
    user_id: str,
    profile_updates: Dict[str, Any]
) -> User:
    """Update a user's profile information."""
```

Updates a user's profile information.

**Parameters:**
- `user_id`: ID of the user to update
- `profile_updates`: Dictionary containing profile fields to update

**Returns:**
- `User`: The updated user

```python
async def delete_user(
    self,
    user_id: str
) -> None:
    """Delete a user account."""
```

Deletes a user account.

**Parameters:**
- `user_id`: ID of the user to delete

### Password Management

```python
async def change_password(
    self,
    user_id: str,
    current_password: str,
    new_password: str
) -> bool:
    """Change a user's password."""
```

Changes a user's password.

**Parameters:**
- `user_id`: ID of the user
- `current_password`: User's current password
- `new_password`: User's new password

**Returns:**
- `bool`: True if password was successfully changed

```python
async def request_password_reset(
    self,
    email: str
) -> bool:
    """Request a password reset for a user."""
```

Initiates a password reset process for a user.

**Parameters:**
- `email`: Email address of the user

**Returns:**
- `bool`: True if password reset request was successfully initiated

```python
async def reset_password(
    self,
    reset_token: str,
    new_password: str
) -> bool:
    """Reset a user's password using a reset token."""
```

Resets a user's password using a reset token.

**Parameters:**
- `reset_token`: Password reset token
- `new_password`: User's new password

**Returns:**
- `bool`: True if password was successfully reset

### Authorization and Permissions

```python
async def check_permission(
    self,
    user_id: str,
    permission: str,
    resource_id: Optional[str] = None
) -> bool:
    """Check if a user has a specific permission."""
```

Checks if a user has a specific permission.

**Parameters:**
- `user_id`: ID of the user
- `permission`: Permission to check
- `resource_id`: Optional ID of the resource to check permission against

**Returns:**
- `bool`: True if user has the specified permission

```python
async def assign_role(
    self,
    user_id: str,
    role: str
) -> User:
    """Assign a role to a user."""
```

Assigns a role to a user.

**Parameters:**
- `user_id`: ID of the user
- `role`: Role to assign

**Returns:**
- `User`: The updated user with the new role

### User Preferences

```python
async def get_user_preferences(
    self,
    user_id: str
) -> Dict[str, Any]:
    """Get a user's preferences."""
```

Retrieves a user's preferences.

**Parameters:**
- `user_id`: ID of the user

**Returns:**
- Dictionary containing the user's preferences

```python
async def update_user_preferences(
    self,
    user_id: str,
    preferences: Dict[str, Any]
) -> Dict[str, Any]:
    """Update a user's preferences."""
```

Updates a user's preferences.

**Parameters:**
- `user_id`: ID of the user
- `preferences`: Dictionary containing preference updates

**Returns:**
- Dictionary containing the updated preferences

### Usage Analytics

```python
async def record_user_activity(
    self,
    user_id: str,
    activity_type: str,
    activity_data: Dict[str, Any] = {}
) -> None:
    """Record a user activity for analytics."""
```

Records a user activity for analytics purposes.

**Parameters:**
- `user_id`: ID of the user
- `activity_type`: Type of activity
- `activity_data`: Additional data about the activity

```python
async def get_user_activity_summary(
    self,
    user_id: str,
    time_period: str = "30d"
) -> Dict[str, Any]:
    """Get a summary of user activity."""
```

Retrieves a summary of a user's activity.

**Parameters:**
- `user_id`: ID of the user
- `time_period`: Time period for the summary (e.g., "7d", "30d", "90d")

**Returns:**
- Dictionary containing a summary of the user's activity

## Data Models

### User

```python
class User(BaseModel):
    """Represents a user of the application."""
    
    user_id: str
    email: str
    name: str
    roles: List[str] = []
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None
    profile: Dict[str, Any] = {}
```

Represents a user of the application.

### AuthToken

```python
class AuthToken(BaseModel):
    """Represents an authentication token."""
    
    token: str
    token_type: str = "Bearer"
    expires_at: datetime
    refresh_token: Optional[str] = None
```

Represents an authentication token.

### UserPreferences

```python
class UserPreferences(BaseModel):
    """Represents a user's preferences."""
    
    user_id: str
    theme: str = "light"
    notifications_enabled: bool = True
    email_notifications: bool = True
    language: str = "en"
    custom_settings: Dict[str, Any] = {}
```

Represents a user's preferences.

## Usage Examples

### User Registration and Authentication

```python
from app.services.user_service import UserService
from app.services.persistence.user_persistence import UserPersistenceService
from app.auth.auth_provider import JWTAuthProvider
from app.config.user_service_config import UserServiceConfig

# Initialize dependencies
user_persistence = UserPersistenceService(...)
auth_provider = JWTAuthProvider(...)
config = UserServiceConfig(...)

# Create user service
user_service = UserService(user_persistence, auth_provider, config)

# Register a new user
new_user = await user_service.register_user(
    email="user@example.com",
    password="secure_password123",
    name="John Doe",
    profile_data={
        "bio": "UI/UX Designer with 5 years of experience",
        "location": "San Francisco, CA"
    }
)

# Authenticate the user
auth_token = await user_service.authenticate_user(
    email="user@example.com",
    password="secure_password123"
)

# Use the token to verify the user
user = await user_service.verify_token(auth_token.token)
```

### Managing User Profiles and Preferences

```python
# Update user profile
updated_user = await user_service.update_user_profile(
    user_id="user123",
    profile_updates={
        "bio": "Senior UI/UX Designer with 7 years of experience",
        "website": "https://example.com/johndoe",
        "social_links": {
            "twitter": "@johndoe",
            "linkedin": "linkedin.com/in/johndoe"
        }
    }
)

# Get user preferences
preferences = await user_service.get_user_preferences("user123")

# Update user preferences
updated_preferences = await user_service.update_user_preferences(
    user_id="user123",
    preferences={
        "theme": "dark",
        "notifications_enabled": True,
        "custom_settings": {
            "auto_save": True,
            "font_size": 14
        }
    }
)
```

### Password Management

```python
# Change password
password_changed = await user_service.change_password(
    user_id="user123",
    current_password="secure_password123",
    new_password="even_more_secure_password456"
)

# Request password reset
reset_requested = await user_service.request_password_reset(
    email="user@example.com"
)

# Reset password with token
password_reset = await user_service.reset_password(
    reset_token="reset_token_from_email",
    new_password="new_secure_password789"
)
```

### Authorization and Role Management

```python
# Check if user has permission
has_permission = await user_service.check_permission(
    user_id="user123",
    permission="edit",
    resource_id="concept456"
)

# Assign a role to a user
updated_user = await user_service.assign_role(
    user_id="user123",
    role="premium_user"
)

# Check if user is premium
is_premium = "premium_user" in updated_user.roles
```

## User Authentication Flow

The typical user authentication flow includes:

1. **Registration**: User registers with email, password, and basic profile info
2. **Email Verification**: User verifies their email address (optional)
3. **Login**: User logs in with email and password
4. **Token Issuance**: Service issues authentication and refresh tokens
5. **Protected Resource Access**: User accesses protected resources with the token
6. **Token Refresh**: Service refreshes the token when it's about to expire
7. **Logout**: User logs out, invalidating the current tokens

## Security Considerations

The `UserService` implements several security best practices:

1. **Password Hashing**: Passwords are securely hashed using bcrypt
2. **Rate Limiting**: Authentication attempts are rate-limited to prevent brute force attacks
3. **Token Expiration**: Authentication tokens have a limited lifespan
4. **Refresh Tokens**: Long-lived refresh tokens allow extending sessions securely
5. **Password Policies**: Enforces password complexity requirements
6. **Secure Communications**: All communications are encrypted using TLS

## Error Handling

Common exceptions that may be raised:

- `UserNotFoundError`: When a user with the specified ID doesn't exist
- `AuthenticationError`: When authentication fails due to invalid credentials
- `PasswordMismatchError`: When current password doesn't match during password change
- `InvalidTokenError`: When a token is invalid or expired
- `EmailAlreadyExistsError`: When registering with an email that's already in use

## Integration Points

The `UserService` integrates with several components:

- **Database**: For storing user data
- **Email Service**: For sending verification and password reset emails
- **Auth Provider**: For handling authentication mechanisms
- **Logging Service**: For logging security events
- **Analytics Service**: For tracking user activity

## Related Documentation

- [User Persistence Service](./persistence/user_persistence.md): Service for user data persistence
- [Auth Provider](../auth/auth_provider.md): Authentication provider interface
- [JWT Auth Provider](../auth/jwt_auth_provider.md): JWT-based authentication implementation
- [User API Routes](../api/routes/user_routes.md): API endpoints for user operations
- [Security Best Practices](../security/best_practices.md): Security guidelines 