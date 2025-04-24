"""Concept storage API routes package.

This module initializes the concept storage API routes package and exposes the router.
"""

from fastapi import APIRouter

from app.api.routes.concept_storage.storage_routes import router as storage_router

# Re-export the router
router = storage_router
