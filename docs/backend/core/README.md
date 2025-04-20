# Core Module Documentation

The Core module contains foundational infrastructure components for the Concept Visualizer application, including configuration, application factory, exceptions, and integrations with external services.

## Key Components

- [Config](config.md): Application configuration and environment variables
- [Constants](constants.md): Application-wide constants and settings
- [Exceptions](exceptions.md): Custom exception classes
- [Factory](factory.md): Application factory for creating and configuring the FastAPI app

## Subdirectories

- [Limiter](limiter/README.md): Rate limiting configuration and implementation
- [Middleware](middleware/README.md): Core middleware components
- [Supabase](supabase/README.md): Supabase client configuration and storage integrations

## Architecture

The Core module provides the foundation upon which the rest of the application is built. It follows these principles:

1. **Configuration Management**: Centralized configuration handling with strong typing and validation
2. **Dependency Isolation**: External service dependencies are isolated and properly configured
3. **Error Standardization**: Custom exceptions for domain-specific error handling
4. **Factory Pattern**: Application initialization through a factory for better testability and configuration

## Example Usage

```python
# Creating the application
from app.core.factory import create_app
app = create_app()

# Accessing configuration
from app.core.config import get_settings
settings = get_settings()
api_key = settings.jigsawstack_api_key

# Using custom exceptions
from app.core.exceptions import RateLimitExceeded
raise RateLimitExceeded("Daily image generation limit exceeded")
``` 