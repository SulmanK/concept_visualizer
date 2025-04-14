"""
API-specific errors for the Concept Visualizer API.

This module defines API-specific error classes that map domain/application errors
to appropriate HTTP responses.
"""

from typing import Optional, Dict, Any, List, Type, Union
from fastapi import HTTPException, status
from app.core.exceptions import ApplicationError


class APIError(HTTPException):
    """Base class for all API-specific HTTP exceptions."""
    
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize with status code, detail message and optional headers.
        
        Args:
            status_code: HTTP status code
            detail: Human-readable error message
            headers: Optional HTTP headers to include in the response
        """
        super().__init__(status_code=status_code, detail=detail, headers=headers)


class BadRequestError(APIError):
    """Exception for 400 Bad Request errors."""
    
    def __init__(
        self, 
        detail: str = "Bad request", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize bad request error."""
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail, headers=headers)


class UnauthorizedError(APIError):
    """Exception for 401 Unauthorized errors."""
    
    def __init__(
        self, 
        detail: str = "Not authenticated", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize unauthorized error."""
        headers = headers or {}
        headers["WWW-Authenticate"] = "Bearer"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail, headers=headers)


class ForbiddenError(APIError):
    """Exception for 403 Forbidden errors."""
    
    def __init__(
        self, 
        detail: str = "Not authorized to perform this action", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize forbidden error."""
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail, headers=headers)


class NotFoundError(APIError):
    """Exception for 404 Not Found errors."""
    
    def __init__(
        self, 
        detail: str = "Resource not found",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize not found error."""
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail, headers=headers)


class UnprocessableEntityError(APIError):
    """Exception for 422 Unprocessable Entity errors."""
    
    def __init__(
        self, 
        detail: Union[str, Dict[str, Any]] = "Invalid input data", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize unprocessable entity error."""
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            headers=headers
        )


class TooManyRequestsError(APIError):
    """Exception for 429 Too Many Requests errors."""
    
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize rate limit error.
        
        Args:
            detail: Error message
            retry_after: Seconds until the client should retry
            headers: Additional headers
        """
        headers = headers or {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
        super().__init__(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=detail, headers=headers)


class InternalServerError(APIError):
    """Exception for 500 Internal Server Error errors."""
    
    def __init__(
        self, 
        detail: str = "An unexpected error occurred", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize internal server error."""
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=detail,
            headers=headers
        )


class ServiceUnavailableError(APIError):
    """Exception for 503 Service Unavailable errors."""
    
    def __init__(
        self, 
        detail: str = "Service temporarily unavailable", 
        retry_after: Optional[int] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """
        Initialize service unavailable error.
        
        Args:
            detail: Error message
            retry_after: Seconds until the client should retry
            headers: Additional headers
        """
        headers = headers or {}
        if retry_after is not None:
            headers["Retry-After"] = str(retry_after)
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            headers=headers
        )


# Error mapping from application errors to API errors
def map_application_error_to_api_error(error: ApplicationError) -> APIError:
    """
    Map a domain/application error to the appropriate API error.
    
    Args:
        error: The application-level error
        
    Returns:
        An API-level error with appropriate status code and detail
    """
    from app.core.exceptions import (
        AuthenticationError, ResourceNotFoundError, ValidationError,
        RateLimitError, ServiceUnavailableError as AppServiceUnavailableError,
        ConceptNotFoundError, ImageNotFoundError, SessionNotFoundError,
        TaskNotFoundError
    )
    
    # Convert the error message
    detail = error.message
    
    # Map specific error types to API errors
    if isinstance(error, AuthenticationError):
        return UnauthorizedError(detail=detail)
    
    if isinstance(error, (ResourceNotFoundError, ConceptNotFoundError, 
                          ImageNotFoundError, SessionNotFoundError,
                          TaskNotFoundError)):
        return NotFoundError(detail=detail)
    
    if isinstance(error, ValidationError):
        return UnprocessableEntityError(detail=detail)
    
    if isinstance(error, RateLimitError):
        retry_after = error.details.get("reset_after")
        return TooManyRequestsError(detail=detail, retry_after=retry_after)
    
    if isinstance(error, AppServiceUnavailableError):
        retry_after = error.details.get("retry_after")
        return ServiceUnavailableError(detail=detail, retry_after=retry_after)
    
    # Default to internal server error
    return InternalServerError(detail=detail)


# ---------------------------------------------------------------
# Backward Compatibility Classes (for existing route handlers)
# ---------------------------------------------------------------

# Import TaskNotFoundError for backward compatibility
from app.services.task.service import TaskNotFoundError

# These classes maintain the old API for routes that haven't been updated yet
class ResourceNotFoundError(NotFoundError):
    """Legacy exception for resource not found errors."""
    
    def __init__(
        self, 
        detail: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        """
        Initialize with 404 status code and resource details.
        
        Args:
            detail: Error message
            resource_type: Optional type of resource not found
            resource_id: Optional ID of resource not found
        """
        error_msg = detail
        if resource_type and resource_id:
            error_msg = f"{resource_type} with ID '{resource_id}' not found"
        elif resource_type:
            error_msg = f"{resource_type} not found"
            
        super().__init__(detail=error_msg)


class ValidationError(UnprocessableEntityError):
    """Legacy exception for validation errors."""
    
    def __init__(
        self, 
        detail: str = "Validation error",
        field_errors: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize with validation error details.
        
        Args:
            detail: Error message
            field_errors: Optional field-specific errors
        """
        # Store field errors for backward compatibility
        self.field_errors = field_errors
        super().__init__(detail=detail)


class RateLimitExceededError(TooManyRequestsError):
    """Legacy exception for rate limit errors."""
    
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        limit: Optional[str] = None,
        reset_at: Optional[str] = None
    ):
        """
        Initialize with rate limit details.
        
        Args:
            detail: Error message
            limit: Optional rate limit descriptor
            reset_at: Optional reset timestamp
        """
        headers = {}
        if limit:
            headers["X-RateLimit-Limit"] = limit
        if reset_at:
            headers["X-RateLimit-Reset"] = reset_at
            
        super().__init__(detail=detail, headers=headers)


class AuthorizationError(ForbiddenError):
    """Legacy exception for authorization errors."""
    
    def __init__(self, detail: str = "Not authorized"):
        """Initialize with 403 status code."""
        super().__init__(detail=detail)


class AuthenticationError(UnauthorizedError):
    """Legacy exception for authentication errors."""
    
    def __init__(self, detail: str = "Authentication required"):
        """Initialize with 401 status code."""
        super().__init__(detail=detail)


# Function to configure error handlers in FastAPI app
def configure_error_handlers(app):
    """
    Configure exception handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Import FastAPI types inside the function to avoid circular imports
    from fastapi import Request
    from fastapi.responses import JSONResponse
    from fastapi.exceptions import RequestValidationError
    from starlette.exceptions import HTTPException as StarletteHTTPException
    import logging
    
    logger = logging.getLogger("api_errors")
    
    # Handler for APIError
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """Handle APIError exceptions."""
        logger.error(
            f"API error: {exc.detail}", 
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        response = {
            "error": True,
            "detail": exc.detail,
            "status_code": exc.status_code,
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response,
            headers=exc.headers or {}
        )
    
    # Handler for standard HTTPException
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """Handle standard HTTP exceptions."""
        logger.error(
            f"HTTP exception: {exc.detail}", 
            extra={
                "status_code": exc.status_code,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        response = {
            "error": True,
            "detail": exc.detail,
            "status_code": exc.status_code,
        }
        
        return JSONResponse(
            status_code=exc.status_code,
            content=response,
            headers=exc.headers or {}
        )
    
    # Handler for validation errors
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """Handle validation errors with field details."""
        # Convert validation errors to a more usable format
        field_errors = {}
        for error in exc.errors():
            # Extract field location and name
            location = error.get("loc", [])
            if len(location) > 1:  # First item is usually 'body', 'query', etc.
                field_name = ".".join(str(loc) for loc in location[1:])
                # Add error to the field errors dict
                if field_name not in field_errors:
                    field_errors[field_name] = []
                field_errors[field_name].append(error.get("msg", "Invalid value"))
        
        logger.error(
            "Validation error", 
            extra={
                "path": request.url.path,
                "method": request.method,
                "errors": field_errors
            }
        )
        
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": True,
                "detail": "Validation error",
                "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
                "error_code": "VALIDATION_ERROR",
                "field_errors": field_errors
            }
        )
    
    # Handler for domain-specific application errors
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        """Map application errors to API errors."""
        logger.error(
            f"Application error: {exc.message}", 
            extra={
                "error_type": exc.__class__.__name__,
                "details": exc.details,
                "path": request.url.path,
                "method": request.method,
            }
        )
        
        # Use our mapping function to convert ApplicationError to APIError
        api_error = map_application_error_to_api_error(exc)
        
        response = {
            "error": True,
            "detail": api_error.detail,
            "status_code": api_error.status_code,
        }
        
        return JSONResponse(
            status_code=api_error.status_code,
            content=response,
            headers=api_error.headers or {}
        )
    
    # Handler specifically for TaskNotFoundError
    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        """Handle TaskNotFoundError specifically."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "error": True,
                "detail": str(exc),
                "code": "task_not_found"
            }
        ) 