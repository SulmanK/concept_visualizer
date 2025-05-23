"""Health API routes package.

This module exposes the health API routes for checking system status and rate limits.
"""

from fastapi import APIRouter

from app.api.routes.health.check import router as check_router
from app.api.routes.health.endpoints import router as endpoints_router
from app.api.routes.health.limits import router as limits_router

# Create a combined router
router = APIRouter()

# Include the check and limits routers
router.include_router(check_router)
router.include_router(limits_router)
router.include_router(endpoints_router)

# Define endpoints that should not count against rate limits
NON_COUNTING_ENDPOINTS = [
    "/api/health/rate-limits-status",
    "/api/health/ping",
    "/api/health/status",
    "/api/health/config",
]
