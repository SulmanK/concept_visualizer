# Application Factory

The `app.core.factory` module provides a factory function to create and configure the FastAPI application instance. This pattern simplifies application initialization and improves testability.

## Key Functions

### `create_app`

```python
def create_app() -> FastAPI
```

Create and configure a FastAPI application instance.

This function initializes a FastAPI application with appropriate settings, middleware, rate limiting, and routes.

**Returns:**

- A configured FastAPI application instance

**Example Usage:**

```python
from app.core.factory import create_app

# Create the application
app = create_app()
```

## Implementation Details

The factory function performs the following setup:

1. **Logging Configuration**:
   - Sets up application logging using `setup_logging`

2. **FastAPI Initialization**:
   - Creates a FastAPI instance with metadata (title, description, version)
   - Configures documentation endpoints (Swagger UI, ReDoc)
   - Sets up contact and license information

3. **Rate Limiting**:
   - Configures rate limiting for API endpoints

4. **Middleware Setup**:
   - Adds CORS middleware with origins from settings
   - Adds PrioritizationMiddleware for request prioritization

5. **API Routes**:
   - Configures all API routes using `configure_api_routes`
   - Sets up error handlers

6. **Root Endpoint**:
   - Defines a root endpoint (`/`) with basic API information

## Factory Pattern Benefits

Using a factory function for application creation provides several benefits:

- **Separation of Concerns**: Clear separation between configuration and usage
- **Testability**: Easier to create test instances with different configurations
- **Readability**: Centralizes application setup logic
- **Extensibility**: Makes it easier to add new configuration options

## Usage in Main Application

The factory is used in the main application entry point:

```python
# main.py
from app.core.factory import create_app

# Create the FastAPI application using the factory function
app = create_app()
``` 