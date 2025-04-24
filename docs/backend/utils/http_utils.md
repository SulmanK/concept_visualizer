# HTTP Utilities

The `http_utils.py` module provides utility functions for HTTP request and response handling throughout the Concept Visualizer API.

## Overview

The HTTP utilities module offers a collection of helper functions for:

1. Creating standardized HTTP responses
2. Handling request data validation
3. Processing HTTP headers
4. Managing HTTP-related errors

These utilities ensure consistent HTTP behavior across the application and reduce code duplication by encapsulating common HTTP operations.

## Key Functions

### Create Standard Response

```python
def create_standard_response(
    data: Any = None,
    message: str = "Success",
    status_code: int = 200,
    headers: Optional[Dict[str, str]] = None
) -> JSONResponse:
    """Create a standardized JSON response with consistent structure."""
```

This function generates a standardized JSON response with a consistent structure.

**Parameters:**

- `data`: The response payload (default: None)
- `message`: Human-readable status message (default: "Success")
- `status_code`: HTTP status code (default: 200)
- `headers`: Additional HTTP headers to include (default: None)

**Returns:**

- A FastAPI JSONResponse object with standardized structure

**Example Response Structure:**

```json
{
  "success": true,
  "message": "Success",
  "data": { ... },
  "timestamp": "2023-11-20T14:30:22Z"
}
```

### Extract Bearer Token

```python
def extract_bearer_token(authorization: Optional[str]) -> Optional[str]:
    """Extract the token value from an Authorization header with Bearer scheme."""
```

This function extracts the token value from an Authorization header with Bearer scheme.

**Parameters:**

- `authorization`: The Authorization header value (e.g., "Bearer xyz123")

**Returns:**

- The extracted token or None if not present/valid

### Parse Query Parameters

```python
def parse_query_parameters(
    params: Dict[str, Any],
    allowed_params: List[str],
    type_mapping: Optional[Dict[str, Type]] = None
) -> Dict[str, Any]:
    """Parse and validate query parameters according to allowed parameters and types."""
```

This function processes query parameters and ensures they match expected types and names.

**Parameters:**

- `params`: Dictionary of query parameters
- `allowed_params`: List of allowed parameter names
- `type_mapping`: Dictionary mapping parameter names to expected types

**Returns:**

- Dictionary of validated and converted parameters

**Raises:**

- `InvalidQueryParameterError`: If a parameter is not allowed or has an invalid type

### Generate URL with Query Parameters

```python
def generate_url_with_params(
    base_url: str,
    params: Dict[str, Any],
    exclude_none: bool = True
) -> str:
    """Generate a URL with properly encoded query parameters."""
```

This function builds a URL with properly encoded query parameters.

**Parameters:**

- `base_url`: Base URL to append parameters to
- `params`: Dictionary of query parameters
- `exclude_none`: Whether to exclude parameters with None values (default: True)

**Returns:**

- Complete URL with encoded query parameters

### Handle Request Exceptions

```python
def handle_request_exceptions(
    func: Callable,
    error_mapping: Optional[Dict[Type[Exception], Tuple[int, str]]] = None
) -> Callable:
    """Decorator for handling common HTTP request exceptions with appropriate responses."""
```

This decorator handles common HTTP request exceptions and converts them to appropriate HTTP responses.

**Parameters:**

- `func`: The function to wrap
- `error_mapping`: Dictionary mapping exception types to (status_code, message) tuples

**Returns:**

- Wrapped function that handles specified exceptions

## Common HTTP Status Utilities

The module provides constants and helper functions for working with HTTP status codes:

```python
# Status code categorization
is_informational = lambda code: 100 <= code < 200
is_success = lambda code: 200 <= code < 300
is_redirect = lambda code: 300 <= code < 400
is_client_error = lambda code: 400 <= code < 500
is_server_error = lambda code: 500 <= code < 600

# Common status code descriptions
STATUS_DESCRIPTIONS = {
    200: "OK",
    201: "Created",
    204: "No Content",
    400: "Bad Request",
    401: "Unauthorized",
    403: "Forbidden",
    404: "Not Found",
    409: "Conflict",
    422: "Unprocessable Entity",
    429: "Too Many Requests",
    500: "Internal Server Error",
    503: "Service Unavailable"
}
```

## Usage Examples

### Creating a Standard Response

```python
from app.utils.http_utils import create_standard_response

# Simple success response
response = create_standard_response(
    data={"user_id": "123", "username": "example_user"},
    message="User retrieved successfully"
)

# Error response with custom headers
error_response = create_standard_response(
    data={"error_code": "INVALID_INPUT", "details": ["Field 'email' is required"]},
    message="Validation error",
    status_code=400,
    headers={"X-Error-Code": "INVALID_INPUT"}
)
```

### Extracting and Validating a Bearer Token

```python
from app.utils.http_utils import extract_bearer_token

def get_current_user(authorization: str = Header(None)):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    # Validate the token and get user information
    # ...

    return user_info
```

### Using the Request Exception Handler

```python
from app.utils.http_utils import handle_request_exceptions
from app.core.exceptions import ValidationError, ResourceNotFoundError

@handle_request_exceptions({
    ValidationError: (400, "Invalid input data"),
    ResourceNotFoundError: (404, "Resource not found"),
    Exception: (500, "An unexpected error occurred")
})
async def create_user(user_data: UserCreate):
    # This function is protected by the exception handler
    # If any of the specified exceptions occur, they will be
    # converted to appropriate HTTP responses

    # Validate input
    if not validate_user_data(user_data):
        raise ValidationError("Invalid user data")

    # Create user
    user = await user_service.create_user(user_data)

    return user
```

## Error Handling

The HTTP utilities module provides helpers for consistent error handling across the API:

```python
def create_error_response(
    message: str,
    status_code: int,
    error_code: str = None,
    details: List[str] = None
) -> JSONResponse:
    """Create a standardized error response."""
```

This function generates a standardized error response with consistent structure.

**Parameters:**

- `message`: Human-readable error message
- `status_code`: HTTP status code (4xx or 5xx)
- `error_code`: Machine-readable error code (e.g., "INVALID_INPUT")
- `details`: Additional error details

**Returns:**

- A FastAPI JSONResponse object with standardized error structure

## Content Type Helpers

The module includes helpers for working with content types:

```python
def is_json_content(content_type: str) -> bool:
    """Check if the content type is JSON."""

def is_multipart_content(content_type: str) -> bool:
    """Check if the content type is multipart form data."""

def is_form_content(content_type: str) -> bool:
    """Check if the content type is form-urlencoded."""
```

These functions validate content type strings for common API content types.

## Related Documentation

- [API Router](../../api/router.md): Main API router that uses these HTTP utilities
- [Error Handling](../../api/errors.md): API error handling that leverages these utilities
- [JWT Utils](jwt_utils.md): JWT utilities that work with HTTP authentication
- [Auth Middleware](../../api/middleware/auth_middleware.md): Authentication middleware using HTTP functions
