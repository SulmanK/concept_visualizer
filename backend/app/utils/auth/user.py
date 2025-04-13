"""
User authentication utilities.

This module provides helper functions for extracting and validating user identity.
"""

import logging
from typing import Optional
from fastapi import Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.utils.jwt_utils import decode_token

# Set up logging
logger = logging.getLogger(__name__)

# Authentication scheme
security = HTTPBearer(auto_error=False)


def get_current_user_id(request: Request) -> Optional[str]:
    """
    Extract and return the current user ID from the request.
    
    This function first checks for a user in the request state (added by middleware),
    then tries to extract it from the Authorization header, and finally checks 
    the session if available.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        The user ID if available, None otherwise
    """
    # Check if a user is in the request state (added by middleware)
    if hasattr(request, "state") and hasattr(request.state, "user"):
        user = request.state.user
        if user and isinstance(user, dict) and "id" in user:
            return user.get("id")
    
    # Extract from Authorization header as second priority
    try:
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            token = auth.replace("Bearer ", "")
            payload = decode_token(token)
            if payload and "sub" in payload:
                return payload["sub"]
    except Exception as e:
        logger.debug(f"Failed to extract user ID from token: {str(e)}")
    
    # Try to get from session if available (lowest priority)
    try:
        if "session" in request.scope and request.session.get("user"):
            user = request.session["user"]
            if isinstance(user, dict) and "id" in user:
                return user.get("id")
    except (AttributeError, AssertionError) as e:
        # SessionMiddleware not installed or session not available
        logger.debug(f"Session access failed: {str(e)}")
    
    return None


def get_current_user_auth(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Optional[str]:
    """
    Extract user ID from bearer token using the security dependency.
    
    Args:
        credentials: The HTTP Authorization credentials
        
    Returns:
        The user ID if available and valid, None otherwise
    """
    if not credentials:
        return None
        
    try:
        payload = decode_token(credentials.credentials)
        if payload and "sub" in payload:
            return payload["sub"]
    except Exception as e:
        logger.error(f"Error extracting user ID from token: {str(e)}")
        
    return None


def get_current_user(request: Request) -> dict:
    """
    Get the current user information as a dictionary.
    
    This function returns user information including the user ID.
    It's primarily used for endpoints that need user context.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        A dictionary containing user information with at least the ID
    """
    user_id = get_current_user_id(request)
    if not user_id:
        return {}
        
    # Return a dict with the user ID and any other user info that might be needed
    return {"id": user_id} 