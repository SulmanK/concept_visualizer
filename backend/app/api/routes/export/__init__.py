"""Export routes for the API.

This module provides routes for exporting images in different formats.
"""

from fastapi import APIRouter

from .export_routes import router as export_router

# Create the main export router
router = APIRouter()

# Include the export routes
router.include_router(export_router)

__all__ = ["router"]
