"""
Application factory.

This module provides the main application factory function for creating and
configuring the FastAPI application.
"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import configure_api_routes
from app.core.config import settings
from app.core.limiter.config import setup_limiter_for_app
from app.utils.logging.setup import setup_logging
from app.api.middleware.auth_middleware import AuthMiddleware
from app.api.middleware.rate_limit_headers import RateLimitHeadersMiddleware


logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """
    Create and configure the FastAPI application.
    
    Returns:
        FastAPI: Configured FastAPI application
    """
    # Set up logging
    setup_logging(
        log_level=settings.LOG_LEVEL,
        log_dir="logs"  # Create a logs directory in the project root
    )
    
    # Create FastAPI app with OpenAPI configuration
    app = FastAPI(
        title="Concept Visualizer API",
        description="API for generating and managing visual concepts",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )
    
    # Configure CORS
    # Use more specific origins in production; for development allow localhost
    cors_origins = settings.CORS_ORIGINS
    if not cors_origins:
        # Fallback for development
        cors_origins = [
            "http://localhost",
            "http://localhost:3000",  # React default
            "http://localhost:5173",  # Vite default
            "http://127.0.0.1:3000",
            "http://127.0.0.1:5173",
        ]
        
    logger.info(f"CORS configured with allowed origins: {cors_origins}")
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Process-Time", "X-Rate-Limit-Limit", "X-Rate-Limit-Remaining", "X-Rate-Limit-Reset"],
        max_age=86400  # 24 hours cache for preflight requests
    )
    
    # Configure authentication middleware
    public_paths = [
        "/api/health",        # Health root endpoint
        "/api/health/check",  # Health check endpoint
        "/api/health/rate-limits", # Rate limits endpoint
        "/api/health/rate-limits-status", # Non-counting rate limits endpoint
        "/api/auth/signin-anonymous",  # Anonymous auth endpoint
        "/docs",              # Swagger UI
        "/redoc",             # ReDoc UI
        "/openapi.json",      # OpenAPI schema
    ]
    app.add_middleware(AuthMiddleware, public_paths=public_paths)
    
    # Add rate limit headers middleware
    app.add_middleware(RateLimitHeadersMiddleware)
    logger.info("Added rate limit headers middleware")
    
    # Configure API routes
    configure_api_routes(app)
    
    # Configure rate limiting
    setup_limiter_for_app(app)
    
    return app 