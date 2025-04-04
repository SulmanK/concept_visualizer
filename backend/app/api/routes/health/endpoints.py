"""
Health and configuration endpoints.

This module provides endpoints that report the current status of the application
and provide non-sensitive configuration data to the frontend.
"""

import logging
from typing import Dict, List
from datetime import datetime

from fastapi import APIRouter, Response, Depends
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/ping")
async def ping():
    """Simple endpoint for checking if the server is alive."""
    logger.info("Health check ping received")
    return {"status": "ok", "timestamp": datetime.now().isoformat()}


class StorageBucketsConfig(BaseModel):
    """Storage bucket names for frontend use."""
    concept: str
    palette: str


@router.get("/config", response_model=Dict[str, StorageBucketsConfig])
async def get_frontend_config():
    """
    Get configuration values for the frontend.
    
    Only non-sensitive configuration values are exposed.
    
    Returns:
        Dict containing frontend configuration values
    """
    # Return only the storage bucket names, nothing else sensitive
    return {
        "storage": StorageBucketsConfig(
            concept=settings.STORAGE_BUCKET_CONCEPT,
            palette=settings.STORAGE_BUCKET_PALETTE
        )
    } 