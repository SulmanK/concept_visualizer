"""
Session API routes package.

This module initializes the session API routes package and exposes the router.
"""

from fastapi import APIRouter

from app.api.routes.session.session_routes import router as session_router
from app.api.routes.session.token import router as token_router

# Create combined router
router = APIRouter()
router.include_router(session_router)
router.include_router(token_router) 