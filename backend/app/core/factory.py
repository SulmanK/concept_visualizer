"""
Application factory for the Concept Visualizer API.

This module provides functions to create and configure the FastAPI application.
"""

import logging
from typing import Optional

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import configure_api_routes
from app.core.config import settings
from app.core.middleware import PrioritizationMiddleware
from app.core.limiter import setup_rate_limiter
from app.core.exceptions import ConfigurationError
from app.utils.logging import setup_logging


def create_app() -> FastAPI:
    """
    Create and configure a FastAPI application instance.
    
    This function initializes a FastAPI application with appropriate settings,
    middleware, rate limiting, and routes.
    
    Returns:
        FastAPI: A configured FastAPI application instance
        
    Raises:
        ConfigurationError: If application configuration fails
    """
    logger = logging.getLogger(__name__)
    
    try:
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
        
        try:
            # Setup rate limiting
            limiter = setup_rate_limiter(app)
            logger.info("Rate limiting configured successfully")
        except Exception as e:
            logger.error(f"Failed to configure rate limiting: {str(e)}")
            # Continue without rate limiting rather than failing application startup
            logger.warning("Application will run without rate limiting")
        
        # Configure CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        logger.info(f"CORS configured with origins: {settings.CORS_ORIGINS}")
        
        # Add prioritization middleware
        app.add_middleware(PrioritizationMiddleware)
        logger.info("Prioritization middleware configured")
        
        # Configure API routes and error handlers
        configure_api_routes(app)
        logger.info("API routes and error handlers configured")
        
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
        
        logger.info("Application initialization complete")
        return app
        
    except Exception as e:
        error_message = f"Failed to initialize application: {str(e)}"
        logger.critical(error_message)
        raise ConfigurationError(
            message=error_message,
            details={"environment": settings.ENVIRONMENT}
        ) 