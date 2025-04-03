"""
API routes package initialization.

This module initializes the API routes package and exposes router objects.
"""

from fastapi import APIRouter

# Import routers directly
from app.api.routes.concept import router as concept_router
from app.api.routes.concept_storage import router as concept_storage_router
from app.api.routes.health import router as health_router
from app.api.routes.session import router as session_router
from app.api.routes.svg import router as svg_router

# Create main API router
api_router = APIRouter()

# Include sub-routers with appropriate prefixes
api_router.include_router(health_router, prefix="/health", tags=["health"])
api_router.include_router(
    concept_router, prefix="/concepts", tags=["concepts"]
)
api_router.include_router(
    concept_storage_router, prefix="/storage", tags=["storage"]
)
api_router.include_router(
    session_router, prefix="/sessions", tags=["sessions"]
)
api_router.include_router(
    svg_router, prefix="/svg", tags=["svg"]
) 