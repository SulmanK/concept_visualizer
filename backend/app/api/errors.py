"""
Error handling for API routes.

This module provides custom exception classes and error handlers to ensure
consistent error responses across the API.
"""

import logging
from typing import Dict, Any, Optional, List, Type, Union

from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

# Configure logging
logger = logging.getLogger("api_errors")


class APIError(Exception):
    """Base class for API exceptions with status code and detail message."""
    
    def __init__(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[Dict[str, Any]] = None,
        error_code: Optional[str] = None
    ):
        """
        Initialize API error with status code and detail message.
        
        Args:
            status_code: HTTP status code
            detail: Error message
            headers: Optional HTTP headers to include in response
            error_code: Optional application-specific error code
        """
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        self.error_code = error_code
        super().__init__(detail)


class ResourceNotFoundError(APIError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(
        self, 
        detail: str = "Resource not found",
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None
    ):
        """
        Initialize with 404 status code and detail message.
        
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
            
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=error_msg,
            error_code="RESOURCE_NOT_FOUND"
        )


class ValidationError(APIError):
    """Exception raised for data validation errors."""
    
    def __init__(
        self, 
        detail: str = "Validation error",
        field_errors: Optional[Dict[str, List[str]]] = None
    ):
        """
        Initialize with 422 status code and validation errors.
        
        Args:
            detail: Error message
            field_errors: Optional dictionary mapping field names to error messages
        """
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_code="VALIDATION_ERROR"
        )
        self.field_errors = field_errors


class RateLimitExceededError(APIError):
    """Exception raised when rate limit is exceeded."""
    
    def __init__(
        self, 
        detail: str = "Rate limit exceeded",
        limit: Optional[str] = None,
        reset_at: Optional[str] = None
    ):
        """
        Initialize with 429 status code and rate limit info.
        
        Args:
            detail: Error message
            limit: Optional rate limit description
            reset_at: Optional timestamp when rate limit resets
        """
        headers = {}
        if limit:
            headers["X-RateLimit-Limit"] = limit
        if reset_at:
            headers["X-RateLimit-Reset"] = reset_at
            
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            headers=headers,
            error_code="RATE_LIMIT_EXCEEDED"
        )


class ServiceUnavailableError(APIError):
    """Exception raised when a dependent service is unavailable."""
    
    def __init__(
        self, 
        detail: str = "Service currently unavailable",
        service_name: Optional[str] = None
    ):
        """
        Initialize with 503 status code.
        
        Args:
            detail: Error message
            service_name: Optional name of unavailable service
        """
        error_msg = detail
        if service_name:
            error_msg = f"{service_name} service is currently unavailable"
            
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=error_msg,
            error_code="SERVICE_UNAVAILABLE"
        )


class AuthorizationError(APIError):
    """Exception raised for authorization errors."""
    
    def __init__(self, detail: str = "Not authorized"):
        """Initialize with 403 status code."""
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="AUTHORIZATION_ERROR"
        )


class AuthenticationError(APIError):
    """Exception raised for authentication errors."""
    
    def __init__(self, detail: str = "Authentication required"):
        """Initialize with 401 status code."""
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
            error_code="AUTHENTICATION_ERROR"
        )


async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
    """
    Handle API errors with consistent format.
    
    Args:
        request: The FastAPI request
        exc: The API error exception
        
    Returns:
        JSON response with error details
    """
    # Log the error
    logger.error(
        f"API error: {exc.detail}", 
        extra={
            "status_code": exc.status_code,
            "error_code": getattr(exc, "error_code", None),
            "path": request.url.path,
            "method": request.method,
        }
    )
    
    response = {
        "error": True,
        "detail": exc.detail,
        "status_code": exc.status_code,
    }
    
    # Add error code if available
    if hasattr(exc, "error_code") and exc.error_code:
        response["error_code"] = exc.error_code
        
    # Add field errors for validation errors
    if isinstance(exc, ValidationError) and hasattr(exc, "field_errors") and exc.field_errors:
        response["field_errors"] = exc.field_errors
    
    return JSONResponse(
        status_code=exc.status_code,
        content=response,
        headers=exc.headers or {}
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """
    Convert standard HTTP exceptions to our API error format.
    
    Args:
        request: The FastAPI request
        exc: The HTTP exception
        
    Returns:
        JSON response with error details
    """
    # Log the error
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


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """
    Handle request validation errors with detailed field information.
    
    Args:
        request: The FastAPI request
        exc: The validation exception
        
    Returns:
        JSON response with validation error details
    """
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
    
    # Log the error
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


def configure_error_handlers(app):
    """
    Configure error handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    app.add_exception_handler(APIError, api_error_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler) 