"""
Domain-specific exceptions for the Concept Visualizer application.

This module defines custom exception classes for various error scenarios
in the core application logic. These exceptions are more specific than
the generic API errors and represent application domain failures.
"""

from typing import Optional, Dict, Any, List
import json


class ApplicationError(Exception):
    """Base class for all application-specific exceptions."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize with error message and optional details.
        
        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the exception to a dictionary for API responses.
        
        Returns:
            Dictionary with error message and details
        """
        return {
            "message": self.message,
            "details": self.details
        }
    
    def __str__(self) -> str:
        """Return a string representation of the error."""
        if self.details:
            return f"{self.message} - {json.dumps(self.details)}"
        return self.message


# Authentication Exceptions
class AuthenticationError(ApplicationError):
    """Exception raised for authentication-related errors."""
    
    def __init__(
        self, 
        message: str = "Authentication error", 
        token: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with authentication error details.
        
        Args:
            message: Human-readable error message
            token: Optional token identifier (will be masked for security)
            details: Additional error details
        """
        self.token = token
        
        error_details = details or {}
        if token:
            # Don't include the full token in logs for security
            error_details["token"] = token[:4] + "****" if len(token) > 4 else "****"
            
        super().__init__(message, error_details)


# Supabase/Database Exceptions
class DatabaseError(ApplicationError):
    """Exception raised when a database operation fails."""
    
    def __init__(
        self, 
        message: str = "Database operation failed", 
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with database error details.
        
        Args:
            message: Human-readable error message
            operation: The database operation that failed (e.g., "insert", "select")
            table: The database table involved
            details: Additional error details
        """
        self.operation = operation
        self.table = table
        
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        if table:
            error_details["table"] = table
            
        super().__init__(message, error_details)


class StorageError(ApplicationError):
    """Exception raised when a storage operation fails."""
    
    def __init__(
        self, 
        message: str = "Storage operation failed", 
        operation: Optional[str] = None,
        bucket: Optional[str] = None,
        path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with storage error details.
        
        Args:
            message: Human-readable error message
            operation: The storage operation that failed (e.g., "upload", "download")
            bucket: The storage bucket involved
            path: The storage path involved
            details: Additional error details
        """
        self.operation = operation
        self.bucket = bucket
        self.path = path
        
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
        if bucket:
            error_details["bucket"] = bucket
        if path:
            error_details["path"] = path
            
        super().__init__(message, error_details)


# External API Integration Exceptions
class JigsawStackError(ApplicationError):
    """Base exception for JigsawStack API errors."""
    
    def __init__(
        self, 
        message: str = "JigsawStack API error", 
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with JigsawStack error details.
        
        Args:
            message: Human-readable error message
            status_code: HTTP status code from the API
            endpoint: The API endpoint that failed
            details: Additional error details
        """
        self.status_code = status_code
        self.endpoint = endpoint
        
        error_details = details or {}
        if status_code:
            error_details["status_code"] = status_code
        if endpoint:
            error_details["endpoint"] = endpoint
            
        super().__init__(message, error_details)


class JigsawStackConnectionError(JigsawStackError):
    """Exception raised when connection to JigsawStack API fails."""
    
    def __init__(
        self, 
        message: str = "Failed to connect to JigsawStack API", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with connection error details."""
        super().__init__(message, details=details)


class JigsawStackAuthenticationError(JigsawStackError):
    """Exception raised when authentication with JigsawStack API fails."""
    
    def __init__(
        self, 
        message: str = "JigsawStack API authentication failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with authentication error details."""
        super().__init__(message, status_code=401, details=details)


class JigsawStackGenerationError(JigsawStackError):
    """Exception raised when content generation with JigsawStack API fails."""
    
    def __init__(
        self, 
        message: str = "JigsawStack content generation failed", 
        content_type: Optional[str] = None,
        prompt: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with generation error details.
        
        Args:
            message: Human-readable error message
            content_type: Type of content being generated (e.g., "image", "palette")
            prompt: Prompt used for generation
            details: Additional error details
        """
        self.content_type = content_type
        self.prompt = prompt
        
        error_details = details or {}
        if content_type:
            error_details["content_type"] = content_type
        # Don't include the full prompt in error details as it might be sensitive
        if prompt:
            # Just include the first 50 characters
            error_details["prompt_preview"] = prompt[:50] + ("..." if len(prompt) > 50 else "")
            
        super().__init__(message, details=error_details)


# Rate Limiting Exceptions
class RateLimitError(ApplicationError):
    """Exception raised when internal rate limiting is exceeded."""
    
    def __init__(
        self, 
        message: str = "Rate limit exceeded", 
        endpoint: Optional[str] = None,
        limit: Optional[str] = None,
        reset_after: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with rate limit details.
        
        Args:
            message: Human-readable error message
            endpoint: The endpoint being rate limited
            limit: Description of the rate limit (e.g., "10/minute")
            reset_after: When the rate limit will reset
            details: Additional error details
        """
        self.endpoint = endpoint
        self.limit = limit
        self.reset_after = reset_after
        
        error_details = details or {}
        if endpoint:
            error_details["endpoint"] = endpoint
        if limit:
            error_details["limit"] = limit
        if reset_after:
            error_details["reset_after"] = reset_after
            
        super().__init__(message, error_details)


# Session Exceptions
class SessionError(ApplicationError):
    """Exception raised for session management errors."""
    
    def __init__(
        self, 
        message: str = "Session error", 
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with session error details.
        
        Args:
            message: Human-readable error message
            session_id: ID of the session involved
            details: Additional error details
        """
        self.session_id = session_id
        
        error_details = details or {}
        if session_id:
            # Don't include the full session ID in logs for privacy
            error_details["session_id"] = session_id[:4] + "****" if len(session_id) > 4 else "****"
            
        super().__init__(message, error_details)


class SessionNotFoundError(SessionError):
    """Exception raised when a session is not found."""
    
    def __init__(
        self, 
        message: str = "Session not found", 
        session_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with session not found details."""
        super().__init__(message, session_id=session_id, details=details)


class SessionCreationError(SessionError):
    """Exception raised when session creation fails."""
    
    def __init__(
        self, 
        message: str = "Failed to create session", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with session creation error details."""
        super().__init__(message, details=details)


# Concept Exceptions
class ConceptError(ApplicationError):
    """Base exception for concept-related errors."""
    
    def __init__(
        self, 
        message: str = "Concept error", 
        concept_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with concept error details.
        
        Args:
            message: Human-readable error message
            concept_id: ID of the concept involved
            details: Additional error details
        """
        self.concept_id = concept_id
        
        error_details = details or {}
        if concept_id:
            error_details["concept_id"] = concept_id
            
        super().__init__(message, error_details)


class ConceptNotFoundError(ConceptError):
    """Exception raised when a concept is not found."""
    
    def __init__(
        self, 
        message: str = "Concept not found", 
        concept_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with concept not found details."""
        super().__init__(message, concept_id=concept_id, details=details)


class ConceptCreationError(ConceptError):
    """Exception raised when concept creation fails."""
    
    def __init__(
        self, 
        message: str = "Failed to create concept", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with concept creation error details."""
        super().__init__(message, details=details)


class ConceptStorageError(ConceptError):
    """Exception raised when storing a concept fails."""
    
    def __init__(
        self, 
        message: str = "Failed to store concept", 
        concept_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with concept storage error details."""
        super().__init__(message, concept_id=concept_id, details=details)


class ConceptRefinementError(ConceptError):
    """Exception raised when refining a concept fails."""
    
    def __init__(
        self, 
        message: str = "Failed to refine concept", 
        concept_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with concept refinement error details."""
        super().__init__(message, concept_id=concept_id, details=details)


# Image Processing Exceptions
class ImageProcessingError(ApplicationError):
    """Exception raised for image processing errors."""
    
    def __init__(
        self, 
        message: str = "Image processing failed", 
        operation: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with image processing error details.
        
        Args:
            message: Human-readable error message
            operation: The processing operation that failed
            details: Additional error details
        """
        self.operation = operation
        
        error_details = details or {}
        if operation:
            error_details["operation"] = operation
            
        super().__init__(message, error_details)


class ExportError(ImageProcessingError):
    """Exception raised when image export or conversion fails."""
    
    def __init__(
        self, 
        message: str = "Image export failed", 
        format: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with export error details.
        
        Args:
            message: Human-readable error message
            format: The target format that failed (e.g., "png", "svg", "jpg")
            details: Additional error details
        """
        error_details = details or {}
        if format:
            error_details["format"] = format
            
        super().__init__(message, operation="image_export", details=error_details)


class ColorPaletteApplicationError(ImageProcessingError):
    """Exception raised when applying a color palette to an image fails."""
    
    def __init__(
        self, 
        message: str = "Failed to apply color palette", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with color palette application error details."""
        super().__init__(message, operation="apply_palette", details=details)


# Configuration Exceptions
class ConfigurationError(ApplicationError):
    """Exception raised for configuration-related errors."""
    
    def __init__(
        self, 
        message: str = "Configuration error", 
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with configuration error details.
        
        Args:
            message: Human-readable error message
            config_key: The configuration key involved
            details: Additional error details
        """
        self.config_key = config_key
        
        error_details = details or {}
        if config_key:
            error_details["config_key"] = config_key
            
        super().__init__(message, error_details)


class EnvironmentVariableError(ConfigurationError):
    """Exception raised when a required environment variable is missing."""
    
    def __init__(
        self, 
        message: str = "Required environment variable is missing", 
        variable_name: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with environment variable error details.
        
        Args:
            message: Human-readable error message
            variable_name: Name of the missing environment variable
            details: Additional error details
        """
        self.variable_name = variable_name
        
        error_details = details or {}
        if variable_name:
            error_details["variable_name"] = variable_name
            
        super().__init__(message, error_details)


# Image Storage Exceptions
class ImageStorageError(StorageError):
    """Exception raised when an image storage operation fails."""
    
    def __init__(
        self, 
        message: str = "Image storage operation failed", 
        operation: Optional[str] = None,
        bucket: Optional[str] = None,
        path: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with image storage error details.
        
        Args:
            message: Human-readable error message
            operation: The storage operation that failed (e.g., "upload", "download")
            bucket: The storage bucket involved
            path: The storage path involved
            details: Additional error details
        """
        super().__init__(message, operation, bucket, path, details)


class ImageNotFoundError(ImageStorageError):
    """Exception raised when an image is not found in storage."""
    
    def __init__(
        self, 
        message: str = "Image not found", 
        path: Optional[str] = None,
        bucket: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with image not found details.
        
        Args:
            message: Human-readable error message
            path: The storage path that was requested
            bucket: The storage bucket that was queried
            details: Additional error details
        """
        super().__init__(message, operation="download", bucket=bucket, path=path, details=details)


# API Error Exceptions
class ResourceNotFoundError(ApplicationError):
    """Exception raised when a requested resource is not found."""
    
    def __init__(
        self, 
        message: str = "Resource not found", 
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with resource not found details.
        
        Args:
            message: Human-readable error message
            resource_type: Type of resource that was not found
            resource_id: ID of the resource that was not found
            details: Additional error details
        """
        self.resource_type = resource_type
        self.resource_id = resource_id
        
        error_details = details or {}
        if resource_type:
            error_details["resource_type"] = resource_type
        if resource_id:
            error_details["resource_id"] = resource_id
            
        super().__init__(message, error_details)


class ValidationError(ApplicationError):
    """Exception raised when input validation fails."""
    
    def __init__(
        self, 
        message: str = "Validation error", 
        field_errors: Optional[Dict[str, List[str]]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with validation error details.
        
        Args:
            message: Human-readable error message
            field_errors: Dictionary mapping field names to lists of error messages
            details: Additional error details
        """
        self.field_errors = field_errors or {}
        
        error_details = details or {}
        if field_errors:
            error_details["field_errors"] = field_errors
            
        super().__init__(message, error_details)


class ServiceUnavailableError(ApplicationError):
    """Exception raised when a service is unavailable."""
    
    def __init__(
        self, 
        message: str = "Service unavailable", 
        service_name: Optional[str] = None,
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with service unavailable details.
        
        Args:
            message: Human-readable error message
            service_name: Name of the unavailable service
            retry_after: Seconds after which to retry the request
            details: Additional error details
        """
        self.service_name = service_name
        self.retry_after = retry_after
        
        error_details = details or {}
        if service_name:
            error_details["service_name"] = service_name
        if retry_after:
            error_details["retry_after"] = retry_after
            
        super().__init__(message, error_details)


class TaskError(ApplicationError):
    """Base exception for task-related errors."""
    
    def __init__(
        self, 
        message: str = "Task error", 
        task_id: Optional[str] = None,
        task_type: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize with task error details.
        
        Args:
            message: Human-readable error message
            task_id: ID of the task involved
            task_type: Type of the task involved
            details: Additional error details
        """
        self.task_id = task_id
        self.task_type = task_type
        
        error_details = details or {}
        if task_id:
            error_details["task_id"] = task_id
        if task_type:
            error_details["task_type"] = task_type
            
        super().__init__(message, error_details)


class TaskNotFoundError(TaskError):
    """Exception raised when a task is not found."""
    
    def __init__(
        self, 
        message: str = "Task not found", 
        task_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with task not found details."""
        super().__init__(message, task_id=task_id, details=details)


class ConceptGenerationError(ApplicationError):
    """Error during the concept generation process."""
    
    def __init__(
        self, 
        message: str = "Concept generation failed", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with concept generation error details."""
        super().__init__(message, details)


class DatabaseTransactionError(DatabaseError):
    """Error during a multi-step database operation."""
    
    def __init__(
        self, 
        message: str = "Database transaction failed", 
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with database transaction error details."""
        super().__init__(message, operation=operation, table=table, details=details)


class RateLimitRuleError(ApplicationError):
    """Error related to rate limit configuration or application."""
    
    def __init__(
        self, 
        message: str = "Rate limit rule error", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with rate limit rule error details."""
        super().__init__(message, details)


class ExternalServiceError(ApplicationError):
    """Error communicating with an external service."""
    
    def __init__(
        self, 
        service_name: str, 
        message: str = "External service error", 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with external service error details."""
        error_details = details or {}
        error_details["service_name"] = service_name
        super().__init__(message, error_details)


class StorageOperationError(StorageError):
    """Specific error during a storage operation."""
    
    def __init__(
        self, 
        message: str = "Storage operation failed", 
        operation: Optional[str] = None, 
        bucket: Optional[str] = None, 
        path: Optional[str] = None, 
        details: Optional[Dict[str, Any]] = None
    ):
        """Initialize with storage operation error details."""
        super().__init__(message, operation=operation, bucket=bucket, path=path, details=details) 