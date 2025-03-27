"""
Main application entry point for the Concept Visualizer API.

This module initializes the FastAPI application and includes all routes.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import api_router
from app.core.config import settings
from app.utils.logging import setup_logging

# Configure application logging
setup_logging()

# Initialize FastAPI app
app = FastAPI(
    title="Concept Visualizer API",
    description=(
        "API for generating and refining visual concepts using JigsawStack"
    ),
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[str(origin) for origin in settings.CORS_ORIGINS],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router with prefix
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns information about the API and links to documentation.
    """
    return {
        "message": "Welcome to the Concept Visualizer API",
        "documentation": "/docs",
    } 