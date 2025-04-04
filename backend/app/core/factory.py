"""
Application factory for the Concept Visualizer API.

This module provides functions to create and configure the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import configure_api_routes
from app.core.config import settings
from app.core.middleware import PrioritizationMiddleware
from app.core.rate_limiter import setup_rate_limiter
from app.utils.logging import setup_logging


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.
    
    This function initializes a FastAPI application with appropriate settings,
    middleware, rate limiting, and routes.
    
    Returns:
        FastAPI: A configured FastAPI application instance
    """
    # Configure application logging
    setup_logging()
    
    # Initialize FastAPI app
    app = FastAPI(
        title="Concept Visualizer API",
        description=(
            "API for generating and refining visual concepts using JigsawStack. "
            "This API provides endpoints for creating logo designs with matching "
            "color palettes and refining existing designs based on user feedback."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        terms_of_service="https://example.com/terms/",
        contact={
            "name": "Concept Visualizer Team",
            "url": "https://example.com/contact/",
            "email": "support@example.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
    )
    
    # Setup rate limiting
    limiter = setup_rate_limiter(app)
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add prioritization middleware
    app.add_middleware(PrioritizationMiddleware)
    
    # Configure API routes and error handlers
    configure_api_routes(app)
    
    # Register root endpoint
    @app.get("/")
    async def root():
        """
        Root endpoint.
        
        Returns information about the API and links to documentation.
        """
        return {
            "message": "Welcome to the Concept Visualizer API",
            "documentation": "/docs",
            "redoc": "/redoc",
            "api_prefix": settings.API_PREFIX,
            "version": "0.1.0",
        }
    
    return app 