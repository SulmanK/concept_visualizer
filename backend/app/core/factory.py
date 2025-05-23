"""Application factory.

This module provides the main application factory function for creating and
configuring the FastAPI application.
"""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.middleware.auth_middleware import AuthMiddleware
from app.api.middleware.rate_limit_apply import PUBLIC_PATHS, RateLimitApplyMiddleware
from app.api.middleware.rate_limit_headers import RateLimitHeadersMiddleware
from app.api.router import configure_api_routes
from app.core.config import settings
from app.core.limiter.config import setup_limiter_for_app
from app.utils.logging.setup import setup_logging

logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    """Create and configure the FastAPI application.

    Returns:
        FastAPI: Configured FastAPI application
    """
    # Set up logging
    setup_logging(log_level=settings.LOG_LEVEL, log_dir="logs")  # Create a logs directory in the project root

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

    logger.debug(f"CORS configured with allowed origins: {cors_origins}")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=[
            "X-Process-Time",
            "X-Rate-Limit-Limit",
            "X-Rate-Limit-Remaining",
            "X-Rate-Limit-Reset",
        ],
        max_age=86400,  # 24 hours cache for preflight requests
    )

    # Configure middleware
    # Note: The order of middleware registration is important.
    # FastAPI/Starlette executes middleware in REVERSE order of registration.
    # So we need to register in the opposite order of execution:

    # Add rate limit headers middleware (runs last)
    app.add_middleware(RateLimitHeadersMiddleware)
    logger.debug("Added rate limit headers middleware")

    # Add rate limit apply middleware (runs second)
    app.add_middleware(RateLimitApplyMiddleware)
    logger.debug("Added rate limit apply middleware")

    # Configure authentication middleware (runs first)
    app.add_middleware(AuthMiddleware, public_paths=PUBLIC_PATHS)
    logger.debug("Added authentication middleware")

    # Configure API routes (this also sets up error handlers via configure_error_handlers)
    configure_api_routes(app)
    logger.debug("Configured API routes and error handlers")

    # Configure rate limiting
    setup_limiter_for_app(app)

    return app
