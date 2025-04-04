"""
Session management endpoints.

This module provides endpoints for managing user sessions.
"""

import logging
import traceback
from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, Request
from pydantic import BaseModel
from typing import Optional
from slowapi.util import get_remote_address

from app.services.session_service import SessionService, get_session_service

# Add imports for new dependencies and errors
from app.api.dependencies import get_or_create_session
from app.api.errors import ServiceUnavailableError, ValidationError, AuthenticationError

# Configure logging
logger = logging.getLogger("session_api")

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
    # Rate limiting removed for session operations to reduce connection errors
    
    try:
        session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
        return SessionResponse(
            session_id=session_id,
            is_new_session=is_new_session,
            message="Session created successfully" if is_new_session else "Using existing session"
        )
    except Exception as e:
        logger.error(f"Failed to create session: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Failed to create session: {str(e)}")


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
    # Rate limiting removed for session operations to reduce connection errors
    
    try:
        # Validate request
        if not request.client_session_id:
            raise ValidationError(
                detail="Client session ID is required",
                field_errors={"client_session_id": ["Field is required"]}
            )
            
        client_session_id = request.client_session_id
        cookie_session_id = session_id
        
        # Fast path: if the session IDs match exactly and are valid, return immediately
        if client_session_id and cookie_session_id and client_session_id == cookie_session_id:
            # Just log a brief message at debug level
            session_service.logger.debug(f"Quick session sync - IDs match")
            
            # Only check if it's a valid session in the database
            if session_service.session_storage.get_session(client_session_id):
                # Silently update activity in the background
                try:
                    session_service.session_storage.update_session_activity(client_session_id)
                except Exception:
                    # Ignore errors in activity update
                    pass
                
                return SessionResponse(
                    session_id=client_session_id,
                    is_new_session=False,
                    message="Session valid, no sync needed"
                )
        
        # Only log minimal info to reduce noise
        session_service.logger.debug("Processing full session sync")
        
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
        
        return SessionResponse(
            session_id=final_session_id,
            is_new_session=is_new_session,
            message=message
        )
    except ValidationError:
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        session_service.logger.error(f"Error syncing session: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Failed to sync session: {str(e)}") 