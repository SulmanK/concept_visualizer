"""
API router configuration.

This module configures and exports the main API router with all sub-routers.
"""

from fastapi import APIRouter, FastAPI

from app.api.routes.concept import router as concept_router
from app.api.routes.concept_storage import router as concept_storage_router
from app.api.routes.health import router as health_router
from app.api.routes.svg import router as svg_router
from app.api.routes.auth import router as auth_router
from app.api.errors import configure_error_handlers


def create_api_router() -> APIRouter:
    """
    Create and configure the main API router with all sub-routers.
    
    Returns:
        The configured API router
    """
    # Create main API router
    api_router = APIRouter()
    
    # Include sub-routers with appropriate prefixes
    api_router.include_router(health_router, prefix="/health", tags=["health"])
    api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
    api_router.include_router(
        concept_router, prefix="/concepts", tags=["concepts"]
    )
    api_router.include_router(
        concept_storage_router, prefix="/storage", tags=["storage"]
    )
    api_router.include_router(
        svg_router, prefix="/svg", tags=["svg"]
    )
    
    return api_router


def configure_api_routes(app: FastAPI) -> None:
    """
    Configure API routes and error handlers for the FastAPI application.
    
    Args:
        app: The FastAPI application instance
    """
    # Create and include the API router
    api_router = create_api_router()
    app.include_router(api_router, prefix="/api")
    
    # Configure error handlers
    configure_error_handlers(app) 