# API Router

This documentation covers the API router configuration in the Concept Visualizer application.

## Overview

The `router.py` module configures and exports the main API router with all sub-routers. It provides functions to:

- Create the main API router with all routes
- Configure the API router in a FastAPI application
- Set up proper route prefixes and tags

## Functions

### create_api_router

```python
def create_api_router() -> APIRouter:
    """Create and configure the main API router with all sub-routers."""
```

This function creates the main API router and includes all sub-routers with appropriate prefixes and tags.

#### Included Sub-Routers

| Sub-Router             | Prefix      | Tags           |
| ---------------------- | ----------- | -------------- |
| health_router          | `/health`   | `["health"]`   |
| auth_router            | `/auth`     | `["auth"]`     |
| concept_router         | `/concepts` | `["concepts"]` |
| concept_storage_router | `/storage`  | `["storage"]`  |
| export_router          | `/export`   | `["export"]`   |
| task_router            | `/tasks`    | `["tasks"]`    |

### configure_api_routes

```python
def configure_api_routes(app: FastAPI) -> None:
    """Configure API routes and error handlers for the FastAPI application."""
```

This function sets up the API router in a FastAPI application. It:

1. Creates the main API router using `create_api_router()`
2. Includes the API router with the `/api` prefix
3. Configures error handlers for the application

## Usage Example

```python
from fastapi import FastAPI
from app.api.router import configure_api_routes

# Create FastAPI application
app = FastAPI(title="Concept Visualizer API")

# Configure API routes
configure_api_routes(app)

# The application now has the following routes:
# - /api/health/...
# - /api/auth/...
# - /api/concepts/...
# - /api/storage/...
# - /api/export/...
# - /api/tasks/...
```

## API Structure

The API follows a structured organization:

1. **Health Endpoints**: `/api/health/*` - System health and status
2. **Auth Endpoints**: `/api/auth/*` - Authentication operations
3. **Concept Endpoints**: `/api/concepts/*` - Concept generation and refinement
4. **Storage Endpoints**: `/api/storage/*` - Concept storage operations
5. **Export Endpoints**: `/api/export/*` - Concept export functionality
6. **Task Endpoints**: `/api/tasks/*` - Background task management

## Error Handling

The router configuration also sets up error handlers using the `configure_error_handlers` function from the `app.api.errors` module. This ensures consistent error responses across all API endpoints.
