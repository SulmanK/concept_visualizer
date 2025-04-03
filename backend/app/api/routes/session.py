"""
Session management endpoints.

This module provides endpoints for managing user sessions.
"""

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from slowapi.util import get_remote_address

from backend.app.services.session_service import SessionService, get_session_service


router = APIRouter()


class SessionSyncRequest(BaseModel):
    """Request body for session sync endpoint."""
    
    client_session_id: str


class SessionResponse(BaseModel):
    """Response model for session endpoints."""
    
    session_id: str
    is_new_session: bool = False
    message: Optional[str] = None


@router.post("/", response_model=SessionResponse)
async def create_session(
    response: Response,
    req: Request,
    session_service: SessionService = Depends(get_session_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """Create a new session or return the existing one.
    
    Args:
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        session_service: Service for managing sessions
        session_id: Optional session ID from cookies
    
    Returns:
        SessionResponse containing the session ID
    """
    # Apply rate limit - higher limits for session operations
    limiter = req.app.state.limiter
    limiter.limit("60/hour")(get_remote_address)(req)
    
    try:
        session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
        return SessionResponse(
            session_id=session_id,
            is_new_session=is_new_session,
            message="Session created successfully" if is_new_session else "Using existing session"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")


@router.post("/sync", response_model=SessionResponse)
async def sync_session(
    request: SessionSyncRequest,
    response: Response,
    req: Request,
    session_service: SessionService = Depends(get_session_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """Synchronize the client session with the server.
    
    This endpoint helps resolve mismatches between frontend and backend session IDs.
    
    Args:
        request: Session sync request containing client session ID
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        session_service: Service for managing sessions
        session_id: Optional session ID from cookies
    
    Returns:
        SessionResponse containing the synchronized session ID
    """
    # Apply rate limit - higher limits for session operations
    limiter = req.app.state.limiter
    limiter.limit("60/hour")(get_remote_address)(req)
    
    try:
        client_session_id = request.client_session_id
        cookie_session_id = session_id
        
        # Log all session IDs for debugging
        session_service.logger.info("Session sync request received")
        session_service.logger.info(f"- Client session ID: {client_session_id}")
        session_service.logger.info(f"- Cookie session ID: {cookie_session_id}")
        
        # Use get_or_create_session with the client_session_id parameter
        # This will prioritize the client-provided session ID
        final_session_id, is_new_session = await session_service.get_or_create_session(
            response, 
            session_id=cookie_session_id, 
            client_session_id=client_session_id
        )
        
        message = (
            "New session created during synchronization" 
            if is_new_session 
            else "Session synchronized successfully"
        )
        
        session_service.logger.info(f"Synced session ID: {final_session_id}, is_new: {is_new_session}")
        
        return SessionResponse(
            session_id=final_session_id,
            is_new_session=is_new_session,
            message=message
        )
    except Exception as e:
        session_service.logger.error(f"Error syncing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to sync session: {str(e)}") 