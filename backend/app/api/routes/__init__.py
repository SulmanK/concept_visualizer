"""
API routes package initialization.

This module initializes the API routes package and exposes router objects.
"""

from fastapi import APIRouter

from backend.app.api.routes import concept, health

# Create main API router
api_router = APIRouter()

# Include sub-routers with appropriate prefixes
api_router.include_router(health.router, tags=["health"])
api_router.include_router(
    concept.router, prefix="/concepts", tags=["concepts"]
) 