# Exceptions Module

The `exceptions.py` module defines a comprehensive hierarchy of custom exceptions for the Concept Visualizer application. These domain-specific exceptions provide detailed error information for various scenarios.

## Overview

The exception system follows a hierarchical structure:

- `ApplicationError` - The base class for all application exceptions
- Domain-specific errors (e.g., `ConceptError`, `JigsawStackError`)
- Specific error cases (e.g., `ConceptNotFoundError`, `JigsawStackGenerationError`)

All exceptions include:

- Descriptive error messages
- Additional context in a `details` dictionary
- Consistent serialization to JSON/dictionary for API responses

## Exception Hierarchy

```
ApplicationError
├── AuthenticationError
├── DatabaseError
│   └── DatabaseTransactionError
├── StorageError
│   ├── ImageStorageError
│   │   └── ImageNotFoundError
│   └── StorageOperationError
├── JigsawStackError
│   ├── JigsawStackConnectionError
│   ├── JigsawStackAuthenticationError
│   └── JigsawStackGenerationError
├── RateLimitError
│   └── RateLimitRuleError
├── SessionError
│   ├── SessionNotFoundError
│   └── SessionCreationError
├── ConceptError
│   ├── ConceptNotFoundError
│   ├── ConceptCreationError
│   ├── ConceptStorageError
│   └── ConceptRefinementError
├── ImageProcessingError
│   ├── ExportError
│   └── ColorPaletteApplicationError
├── ConfigurationError
│   └── EnvironmentVariableError
├── ResourceNotFoundError
├── ValidationError
├── ServiceUnavailableError
├── TaskError
│   └── TaskNotFoundError
├── ConceptGenerationError
└── ExternalServiceError
```

## Base Exception Class

```python
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
        """Convert the exception to a dictionary for API responses."""
        return {
            "message": self.message,
            "details": self.details
        }
```

## Key Exception Categories

### Authentication Errors

```python
class AuthenticationError(ApplicationError):
    """Exception raised for authentication-related errors."""

    def __init__(
        self,
        message: str = "Authentication error",
        token: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        # Implementation with token masking for security
```

### Database Errors

```python
class DatabaseError(ApplicationError):
    """Exception raised when a database operation fails."""

    def __init__(
        self,
        message: str = "Database operation failed",
        operation: Optional[str] = None,
        table: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        # Implementation
```

### External API Errors

```python
class JigsawStackError(ApplicationError):
    """Base exception for JigsawStack API errors."""

    def __init__(
        self,
        message: str = "JigsawStack API error",
        status_code: Optional[int] = None,
        endpoint: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        # Implementation
```

### Rate Limiting Errors

```python
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
        # Implementation
```

### Configuration Errors

```python
class ConfigurationError(ApplicationError):
    """Exception raised for configuration issues."""

    def __init__(
        self,
        message: str = "Configuration error",
        config_key: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        # Implementation
```

## Usage Examples

### Raising Exceptions

```python
# Raising a simple exception
raise ConceptNotFoundError(concept_id="abc123")

# Raising an exception with custom message and details
raise JigsawStackGenerationError(
    message="Failed to generate logo due to invalid prompt",
    content_type="logo",
    prompt="A minimalist logo for coffee shop",
    details={"error_code": "INVALID_PROMPT"}
)
```

### Handling Exceptions

```python
try:
    result = await concept_service.generate_concept(prompt)
    return result
except ConceptGenerationError as e:
    # Log the error
    logger.error(f"Concept generation failed: {str(e)}")
    # Convert to HTTP exception
    raise HTTPException(status_code=500, detail=e.to_dict())
except JigsawStackAuthenticationError as e:
    # Handle authentication failures
    logger.error(f"JigsawStack authentication failed: {str(e)}")
    raise HTTPException(status_code=503, detail=e.to_dict())
```

### Error Response Format

When exceptions are converted to API responses, they follow this structure:

```json
{
  "message": "Concept generation failed due to invalid prompt",
  "details": {
    "content_type": "logo",
    "prompt_preview": "A minimalist logo for coffee shop",
    "error_code": "INVALID_PROMPT"
  }
}
```

## Security Considerations

The exceptions module implements security practices:

1. **Sensitive Data Masking**: Tokens, passwords, and other sensitive information are masked in error details
2. **Limited Information Disclosure**: Full prompts and other potentially sensitive input are truncated
3. **Production Error Handling**: Different behavior in production to avoid revealing implementation details

## Related Documentation

- [Config](config.md): Configuration system that uses these exceptions
- [API Errors](../api/errors.md): How exceptions are translated to API responses
