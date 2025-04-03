"""
Session API routes package.

This module initializes the session API routes package and exposes the router.
"""

from fastapi import APIRouter

from app.api.routes.session.session_routes import router as session_router

# Re-export the router
router = session_router 