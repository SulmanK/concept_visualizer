"""
Health check endpoints.

This module provides basic health check endpoints to verify the API is running.
"""

from fastapi import APIRouter, Request
from datetime import datetime, timedelta
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter()

# In-memory cache for health check responses
_health_cache = {
    "status": "ok",
    "timestamp": datetime.utcnow(),
    "expires_at": datetime.utcnow() + timedelta(seconds=30)
}


@router.get("/")
@router.head("/")
async def health_check(request: Request):
    """
    Health check endpoint.
    
    This endpoint uses in-memory caching to reduce the load on the server during busy periods.
    If there are many health check requests while the server is processing heavy tasks like image generation,
    it will return a cached response instead of creating a new one each time.
    
    Returns:
        dict: A dictionary with the status of the API.
    """
    global _health_cache
    
    # Check if the cache is still valid
    now = datetime.utcnow()
    if now < _health_cache["expires_at"]:
        return {"status": _health_cache["status"]}
    
    # Update the cache
    _health_cache = {
        "status": "ok",
        "timestamp": now,
        "expires_at": now + timedelta(seconds=30)
    }
    
    return {"status": "ok"} 