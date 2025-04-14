"""
Concept API routes package.

This module exposes the concept API routes for generating and refining visual concepts.
"""

from fastapi import APIRouter

from app.api.routes.concept.generation import router as generation_router
from app.api.routes.concept.refinement import router as refinement_router
from app.api.routes.concept.example_error_handling import router as example_router

# Create a combined router
router = APIRouter()

# Include the generation and refinement routers
router.include_router(generation_router)
router.include_router(refinement_router)
router.include_router(example_router, prefix="/examples") 