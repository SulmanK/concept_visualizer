"""
SVG conversion API routes package.

This module exposes the SVG conversion API routes for transforming raster images to SVG format.
"""

from fastapi import APIRouter

from app.api.routes.svg.converter import router as converter_router

# Create a combined router
router = APIRouter()

# Include the converter router
router.include_router(converter_router) 