"""
Health check endpoints for the API.

This module provides health check endpoints to monitor the API's status.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns:
        dict: A dictionary with the status of the API.
    """
    return {"status": "ok"} 