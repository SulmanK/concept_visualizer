"""
Token generation and refresh API endpoints.

This module provides endpoints for generating and refreshing JWT tokens
used for authenticated access to Supabase storage buckets.
"""

from fastapi import APIRouter, Depends, Cookie, Response, HTTPException
from typing import Optional, Dict, Any
import time
import logging

from app.services.session.manager import SessionManager
from app.services.session import get_session_service
from app.utils.jwt_utils import create_supabase_jwt
from app.utils.security import mask_id

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/token", tags=["token"])

@router.get("", response_model=Dict[str, Any])
async def get_token(
    response: Response,
    session_service: SessionManager = Depends(get_session_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Get a JWT token for the current session.
    
    This endpoint generates a new JWT token containing the session ID 
    in its claims. If no valid session exists, a new one will be created.
    
    Returns:
        Dict containing the token, expiration time, and session ID
    """
    # Get or create session
    session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
    
    # Generate token
    token = create_supabase_jwt(session_id)
    
    # Calculate expiration time for client reference
    expires_at = int(time.time()) + 3600  # 1 hour from now
    
    # Log token generation (with masked session ID)
    logger.info(f"Generated JWT token for session {mask_id(session_id)}, expires in 1 hour")
    
    return {
        "token": token,
        "expires_at": expires_at,
        "session_id": session_id
    }

@router.post("/refresh", response_model=Dict[str, Any])
async def refresh_token(
    session_service: SessionManager = Depends(get_session_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Refresh the JWT token for the current session.
    
    This endpoint generates a new JWT token for an existing session.
    The session must be valid for a token to be generated.
    
    Returns:
        Dict containing the refreshed token, expiration time, and session ID
        
    Raises:
        HTTPException: If no valid session exists
    """
    if not session_id:
        logger.warning("Token refresh attempt with no session cookie")
        raise HTTPException(status_code=401, detail="No valid session")
    
    # Validate session exists
    session = await session_service.validate_session(session_id)
    if not session:
        logger.warning(f"Token refresh attempt with invalid session {mask_id(session_id)}")
        raise HTTPException(status_code=401, detail="Invalid session")
    
    # Generate new token
    token = create_supabase_jwt(session_id)
    expires_at = int(time.time()) + 3600  # 1 hour from now
    
    # Log token refresh (with masked session ID)
    logger.info(f"Refreshed JWT token for session {mask_id(session_id)}, expires in 1 hour")
    
    return {
        "token": token,
        "expires_at": expires_at,
        "session_id": session_id
    } 