"""
Health API routes package.

This module exposes the health API routes for checking system status and rate limits.
"""

from fastapi import APIRouter

from app.api.routes.health.check import router as check_router
from app.api.routes.health.limits import router as limits_router

# Create a combined router
router = APIRouter()

# Include the check and limits routers
router.include_router(check_router)
router.include_router(limits_router) 