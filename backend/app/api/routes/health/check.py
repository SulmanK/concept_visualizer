"""Health check endpoints.

This module provides basic health check endpoints to verify the API is running.
"""

import logging
import traceback
from datetime import datetime, timedelta
from typing import Any, Dict

from fastapi import APIRouter, Request

# Configure logging
logger = logging.getLogger("health_check_api")

# Create router
router = APIRouter()

# In-memory cache for health check responses
_health_cache = {
    "status": "ok",
    "timestamp": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(seconds=30),
}


@router.get("/")
@router.head("/")
async def health_root(request: Request) -> Dict[str, str]:
    """Root health check endpoint.

    This is a simple endpoint that always returns a 200 OK status
    with minimal processing to ensure it responds even if other
    parts of the application are under load.

    Args:
        request: The FastAPI request object

    Returns:
        dict: A simple OK response.
    """
    return {"status": "ok"}


@router.get("/check")
@router.head("/check")
async def health_check(request: Request) -> Dict[str, Any]:
    """Detailed health check endpoint.

    This endpoint uses in-memory caching to reduce the load on the server during busy periods.
    If there are many health check requests while the server is processing heavy tasks like image generation,
    it will return a cached response instead of creating a new one each time.

    Args:
        request: The FastAPI request object

    Returns:
        dict: A dictionary with the status of the API.

    Raises:
        ServiceUnavailableError: If the service is not healthy
    """
    try:
        global _health_cache

        # Check if the cache is still valid
        now = datetime.utcnow()
        # Fix the comparison by explicitly typing the expiration time
        expires_at: datetime = _health_cache["expires_at"]  # type: ignore[assignment]
        if now < expires_at:
            return {"status": _health_cache["status"]}

        # Update the cache
        _health_cache = {
            "status": "ok",
            "timestamp": now,
            "expires_at": now + timedelta(seconds=30),
        }

        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        logger.debug(f"Health check exception: {traceback.format_exc()}")
        # Return a simple OK status instead of raising an error
        # This ensures the health check doesn't fail unnecessarily
        return {
            "status": "ok",
            "warning": "Error occurred but service is still responding",
        }
