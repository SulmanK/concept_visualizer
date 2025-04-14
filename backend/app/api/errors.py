"""
API-specific errors for the Concept Visualizer API.

This module defines API-specific error classes that map domain/application errors
to appropriate HTTP responses.
"""

from typing import Optional, Dict, Any, List, Type, Union
from fastapi import HTTPException, status, Request
from fastapi.responses import JSONResponse
from fastapi.exception_handlers import http_exception_handler as fastapi_http_exception_handler
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

import logging
from app.core.exceptions import ApplicationError

# Configure logging
logger = logging.getLogger("api.errors")


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


class MethodNotAllowedError(APIError):
    """Exception for 405 Method Not Allowed errors."""
    
    def __init__(
        self, 
        detail: str = "Method not allowed",
        allowed_methods: Optional[List[str]] = None,
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize method not allowed error."""
        headers = headers or {}
        if allowed_methods:
            headers["Allow"] = ", ".join(allowed_methods)
        super().__init__(status_code=status.HTTP_405_METHOD_NOT_ALLOWED, detail=detail, headers=headers)


class NotAcceptableError(APIError):
    """Exception for 406 Not Acceptable errors."""
    
    def __init__(
        self, 
        detail: str = "Cannot satisfy the request Accept header",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize not acceptable error."""
        super().__init__(status_code=status.HTTP_406_NOT_ACCEPTABLE, detail=detail, headers=headers)


class ConflictError(APIError):
    """Exception for 409 Conflict errors."""
    
    def __init__(
        self, 
        detail: str = "Resource conflict",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize conflict error."""
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail, headers=headers)


class GoneError(APIError):
    """Exception for 410 Gone errors."""
    
    def __init__(
        self, 
        detail: str = "Resource no longer available",
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize gone error."""
        super().__init__(status_code=status.HTTP_410_GONE, detail=detail, headers=headers)


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


class BadGatewayError(APIError):
    """Exception for 502 Bad Gateway errors."""
    
    def __init__(
        self, 
        detail: str = "Invalid response from upstream server", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize bad gateway error."""
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
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


class GatewayTimeoutError(APIError):
    """Exception for 504 Gateway Timeout errors."""
    
    def __init__(
        self, 
        detail: str = "Gateway timeout", 
        headers: Optional[Dict[str, str]] = None
    ):
        """Initialize gateway timeout error."""
        super().__init__(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
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
        # Authentication and authorization errors
        AuthenticationError,
        
        # Resource errors
        ResourceNotFoundError, ConceptNotFoundError, ImageNotFoundError, 
        SessionNotFoundError, TaskNotFoundError,
        
        # Validation errors
        ValidationError,
        
        # Rate limiting
        RateLimitError, RateLimitRuleError,
        
        # Service availability
        ServiceUnavailableError as AppServiceUnavailableError,
        
        # Database errors
        DatabaseError, StorageError, DatabaseTransactionError, StorageOperationError,
        
        # Integration errors
        JigsawStackError, JigsawStackConnectionError, JigsawStackAuthenticationError,
        ExternalServiceError,
        
        # Processing errors
        ImageProcessingError, ExportError, ColorPaletteApplicationError,
        
        # Concept errors
        ConceptError, ConceptCreationError, ConceptStorageError, ConceptRefinementError,
        ConceptGenerationError,
        
        # Configuration errors
        ConfigurationError, EnvironmentVariableError
    )
    
    # Convert the error message
    detail = error.message
    
    # Map specific error types to API errors
    # Authentication and authorization
    if isinstance(error, AuthenticationError):
        return UnauthorizedError(detail=detail)
    
    # Not found errors
    if isinstance(error, (ResourceNotFoundError, ConceptNotFoundError, 
                          ImageNotFoundError, SessionNotFoundError,
                          TaskNotFoundError)):
        return NotFoundError(detail=detail)
    
    # Validation errors
    if isinstance(error, ValidationError):
        field_errors = error.details.get("field_errors")
        if field_errors:
            return UnprocessableEntityError(detail={"detail": detail, "field_errors": field_errors})
        return UnprocessableEntityError(detail=detail)
    
    # Rate limit errors
    if isinstance(error, RateLimitError):
        retry_after = error.details.get("reset_after")
        return TooManyRequestsError(detail=detail, retry_after=retry_after)
    
    # Rate limit rule configuration errors
    if isinstance(error, RateLimitRuleError):
        logger.error(f"Rate limit rule error: {detail}")
        return InternalServerError(detail="Server configuration error")
    
    # Service unavailable errors
    if isinstance(error, AppServiceUnavailableError):
        retry_after = error.details.get("retry_after")
        return ServiceUnavailableError(detail=detail, retry_after=retry_after)
    
    # External service errors
    if isinstance(error, ExternalServiceError):
        service_name = error.details.get("service_name", "unknown")
        return ServiceUnavailableError(
            detail=f"{service_name} service is currently unavailable: {detail}"
        )
    
    # Database transaction errors (generally 500)
    if isinstance(error, DatabaseTransactionError):
        return InternalServerError(detail="Database operation failed")
    
    # Storage operation errors (generally 503)
    if isinstance(error, StorageOperationError):
        return ServiceUnavailableError(detail="Storage service unavailable")
    
    # Database errors (generally 500 unless more specific)
    if isinstance(error, (DatabaseError, StorageError)):
        return InternalServerError(detail=detail)
    
    # JigsawStack integration errors
    if isinstance(error, JigsawStackConnectionError):
        return ServiceUnavailableError(detail=detail)
    
    if isinstance(error, JigsawStackAuthenticationError):
        # This is an internal auth error, not a user auth error
        return InternalServerError(detail="Error authenticating with external service")
    
    if isinstance(error, JigsawStackError):
        status_code = error.details.get("status_code")
        if status_code:
            if status_code == 400:
                return BadRequestError(detail=detail)
            elif status_code == 429:
                return TooManyRequestsError(detail=detail)
            elif status_code == 503:
                return ServiceUnavailableError(detail=detail)
            else:
                return BadGatewayError(detail=detail)
        return ServiceUnavailableError(detail=detail)
    
    # Concept generation errors
    if isinstance(error, ConceptGenerationError):
        return ServiceUnavailableError(detail="Failed to generate concept. Please try again later.")
    
    # Processing errors
    if isinstance(error, (ImageProcessingError, ExportError, ColorPaletteApplicationError)):
        return UnprocessableEntityError(detail=detail)
    
    # Concept errors
    if isinstance(error, (ConceptCreationError, ConceptStorageError, ConceptRefinementError)):
        return UnprocessableEntityError(detail=detail)
    
    # Configuration errors (generally 500)
    if isinstance(error, (ConfigurationError, EnvironmentVariableError)):
        # Log these as they're typically serious server issues
        logger.error(f"Configuration error: {detail}")
        return InternalServerError(detail="Server configuration error")
    
    # Default to internal server error
    logger.warning(f"Unmapped application error type: {type(error).__name__}")
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
        Initialize with 422 status code and validation details.
        
        Args:
            detail: Error message
            field_errors: Map of field names to error messages
        """
        if field_errors:
            detail_dict = {"detail": detail, "field_errors": field_errors}
            super().__init__(detail=detail_dict)
        else:
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
        Initialize with 429 status code and rate limit details.
        
        Args:
            detail: Error message
            limit: The rate limit that was exceeded (e.g., "100/hour")
            reset_at: When the rate limit will reset
        """
        headers = {}
        
        # Convert reset_at to Retry-After if possible
        if reset_at:
            try:
                # Attempt to convert to integer seconds
                import datetime
                from dateutil import parser
                
                reset_dt = parser.parse(reset_at)
                now = datetime.datetime.now(tz=reset_dt.tzinfo)
                seconds_until_reset = int((reset_dt - now).total_seconds())
                
                # Only set if positive
                if seconds_until_reset > 0:
                    headers["Retry-After"] = str(seconds_until_reset)
            except Exception:
                # If parsing fails, don't set the header
                pass
        
        # Include rate limit info in the detail if provided
        if limit or reset_at:
            detail_msg = detail
            if limit:
                detail_msg += f" (limit: {limit})"
            if reset_at:
                detail_msg += f" (resets at: {reset_at})"
            detail = detail_msg
            
        super().__init__(detail=detail, headers=headers)


class AuthorizationError(ForbiddenError):
    """Legacy exception for authorization errors."""
    
    def __init__(self, detail: str = "Not authorized"):
        """Initialize with 403 status code and authorization error message."""
        super().__init__(detail=detail)


class AuthenticationError(UnauthorizedError):
    """Legacy exception for authentication errors."""
    
    def __init__(self, detail: str = "Authentication required"):
        """Initialize with 401 status code and authentication error message."""
        super().__init__(detail=detail)


def configure_error_handlers(app):
    """
    Configure exception handlers for consistent error responses.
    
    Args:
        app: The FastAPI application instance
    """
    @app.exception_handler(APIError)
    async def api_error_handler(request: Request, exc: APIError) -> JSONResponse:
        """
        Handle all API-specific errors with a consistent response format.
        
        Args:
            request: The FastAPI request
            exc: The exception that was raised
            
        Returns:
            JSONResponse with appropriate status code and content
        """
        # Log server errors (500+)
        if exc.status_code >= 500:
            logger.error(
                f"API error: {exc.detail}",
                exc_info=True
            )
        # Log client errors with warning level
        elif exc.status_code >= 400:
            logger.warning(
                f"Client error: {exc.status_code} - {exc.detail}"
            )
            
        # Construct the response
        content = {"detail": exc.detail}
        return JSONResponse(
            status_code=exc.status_code,
            content=content,
            headers=exc.headers
        )
        
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
        """
        Handle regular HTTP exceptions using the same format as APIError.
        
        Args:
            request: The FastAPI request
            exc: The exception that was raised
            
        Returns:
            JSONResponse with appropriate status code and content
        """
        # Log server errors (500+)
        if exc.status_code >= 500:
            logger.error(
                f"HTTP error: {exc.detail}",
                exc_info=True
            )
        # Log client errors with warning level
        elif exc.status_code >= 400:
            logger.warning(
                f"Client HTTP error: {exc.status_code} - {exc.detail}"
            )
            
        # For regular Starlette HTTP exceptions, we use the basic format
        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail},
            headers=exc.headers
        )
        
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
        """
        Handle request validation errors (422 Unprocessable Entity).
        
        Args:
            request: The FastAPI request
            exc: The validation exception that was raised
            
        Returns:
            JSONResponse with field-specific error details
        """
        # Log the validation error
        logger.warning(
            f"Request validation error: {exc.errors()}"
        )
        
        # Convert validation errors to a more user-friendly format
        field_errors = {}
        error_messages = []
        
        for error in exc.errors():
            # Get the field location (typically 'body', 'query', 'path', etc.)
            loc = error.get('loc', [])
            
            # Skip the first item which is typically 'body', 'query', etc.
            if len(loc) > 1:
                field_path = '.'.join(str(x) for x in loc[1:])
                
                # Add to field-specific errors
                if field_path not in field_errors:
                    field_errors[field_path] = []
                field_errors[field_path].append(error.get('msg', 'Invalid value'))
                
                # Add a readable message
                error_messages.append(f"{field_path}: {error.get('msg', 'Invalid value')}")
            else:
                # Handle errors without a specific field
                error_messages.append(error.get('msg', 'Validation error'))
                
        # Construct the response
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": "Request validation error",
                "field_errors": field_errors,
                "errors": error_messages
            }
        )
        
    @app.exception_handler(ApplicationError)
    async def application_error_handler(request: Request, exc: ApplicationError) -> JSONResponse:
        """
        Handle application domain exceptions by mapping them to API errors.
        
        Args:
            request: The FastAPI request
            exc: The domain exception that was raised
            
        Returns:
            JSONResponse with mapped API error details
        """
        # Convert the application error to an API error
        api_error = map_application_error_to_api_error(exc)
        
        # Log based on error severity
        if api_error.status_code >= 500:
            logger.error(
                f"Application error mapped to {api_error.status_code}: {exc.message}",
                exc_info=True
            )
        else:
            logger.warning(
                f"Application error mapped to {api_error.status_code}: {exc.message}"
            )
            
        # Include error details if available
        content = {"detail": api_error.detail}
        if hasattr(exc, "details") and exc.details:
            # Filter out sensitive information
            safe_details = {k: v for k, v in exc.details.items() 
                           if k not in ["token", "api_key", "password", "secret"]}
            if safe_details:
                content["details"] = safe_details
                
        return JSONResponse(
            status_code=api_error.status_code,
            content=content,
            headers=api_error.headers or {}
        )

    # Legacy handler for TaskNotFoundError (can be removed once all routes are updated)
    @app.exception_handler(TaskNotFoundError)
    async def task_not_found_handler(request: Request, exc: TaskNotFoundError) -> JSONResponse:
        """Legacy handler for task not found errors."""
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)}
        ) 