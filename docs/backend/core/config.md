# Configuration Module

The `config.py` module manages application settings for the Concept Visualizer API, loading configuration from environment variables and providing validation.

## Overview

This module is responsible for:
- Loading configuration from environment variables
- Providing default values when appropriate
- Validating required configuration settings
- Handling configuration errors
- Securely logging configuration information with sensitive data masking

## Key Components

### Settings Class

The `Settings` class is a Pydantic model that defines all application settings with their types and default values. It uses `pydantic_settings.BaseSettings` to automatically load values from environment variables.

```python
class Settings(BaseSettings):
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # JigsawStack API settings
    JIGSAWSTACK_API_KEY: str = "dummy_key"
    JIGSAWSTACK_API_URL: str = "https://api.jigsawstack.com"
    
    # Supabase settings, Redis settings, etc.
    # ...
```

### Configuration Validation

The `Settings` class includes a `validate_required_settings` method that checks for missing or invalid configuration values:

```python
def validate_required_settings(self):
    """
    Validate that all required settings are properly configured.
    
    Raises:
        EnvironmentVariableError: If a required setting is missing or has its default value
    """
    # Example validation
    if self.JIGSAWSTACK_API_KEY == "dummy_key":
        raise EnvironmentVariableError(
            message="JigsawStack API key is required",
            variable_name="CONCEPT_JIGSAWSTACK_API_KEY"
        )
    # More validations...
```

### Global Settings Instance

The module provides a global `settings` instance that can be imported and used throughout the application:

```python
# In config.py
settings = Settings()

# In other modules
from app.core.config import settings
api_key = settings.JIGSAWSTACK_API_KEY
```

### Security Features

The module includes secure logging that masks sensitive information:

```python
def get_masked_value(value: str, visible_chars: int = 4) -> str:
    """Return a masked string showing only the first few characters."""
    if not value or len(value) <= visible_chars:
        return "[EMPTY]" if not value else "[TOO_SHORT]"
    return f"{value[:visible_chars]}{'*' * min(8, len(value) - visible_chars)}"
```

## Usage

### Getting Settings

```python
from app.core.config import settings

# Access settings
api_prefix = settings.API_PREFIX
cors_origins = settings.CORS_ORIGINS
api_key = settings.JIGSAWSTACK_API_KEY
```

### Environment-based Configuration

The module handles different configurations based on the environment:

```python
# Only validate settings in production environments
if settings.ENVIRONMENT not in ["development", "test"]:
    try:
        settings.validate_required_settings()
    except EnvironmentVariableError as e:
        raise ConfigurationError(...)
```

## Environment Variables

The module uses environment variables with the prefix `CONCEPT_`. For example:

- `CONCEPT_JIGSAWSTACK_API_KEY`
- `CONCEPT_SUPABASE_URL`
- `CONCEPT_UPSTASH_REDIS_ENDPOINT`

A `.env` file can be used for local development. The path to this file is automatically detected based on the application directory structure.

## Error Handling

Two custom exception types are used for configuration errors:

- `EnvironmentVariableError`: Raised when a specific environment variable is missing or invalid
- `ConfigurationError`: Raised for general configuration issues, often wrapping `EnvironmentVariableError`

## Related Documentation

- [Exceptions](exceptions.md): Custom exception classes used for configuration errors
- [Constants](constants.md): Application constants derived from configuration
- [Factory](factory.md): Application factory that uses these settings 