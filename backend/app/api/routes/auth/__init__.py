"""Authentication routes package.

This package provides authentication-related API endpoints.
"""

from fastapi import APIRouter

from .auth_routes import router as auth_router

# Create the auth router
router = APIRouter()

# Include auth routes
router.include_router(auth_router, prefix="", tags=["auth"])
