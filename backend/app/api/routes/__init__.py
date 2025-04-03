"""
API routes package initialization.

This module initializes the API routes package and exposes router objects.
"""

from fastapi import APIRouter

from backend.app.api.routes import concept, health, concept_storage, session, svg_conversion

# Create main API router
api_router = APIRouter()

# Include sub-routers with appropriate prefixes
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(
    concept.router, prefix="/concepts", tags=["concepts"]
)
api_router.include_router(
    concept_storage.router, prefix="/storage", tags=["storage"]
)
api_router.include_router(
    session.router, prefix="/sessions", tags=["sessions"]
)
api_router.include_router(
    svg_conversion.router, prefix="/svg", tags=["svg"]
) 