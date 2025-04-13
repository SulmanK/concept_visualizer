"""
JWT utilities for Supabase storage authentication.

This module provides functions for generating Supabase-compatible JWTs for secure
access to Supabase storage buckets.
"""

import time
import logging
import json
import base64
from typing import Dict, Any, Optional

from jose import jwt
from jose.exceptions import JWTError

from app.core.config import settings

# Set up logging
logger = logging.getLogger(__name__)


def create_supabase_jwt(user_id: str, expiry_seconds: int = 259200) -> str:
    """
    Create a Supabase-compatible JWT with user ID in claims.
    
    Args:
        user_id: User's ID
        expiry_seconds: Token expiry in seconds (default 3 days)
        
    Returns:
        JWT token string
        
    Raises:
        ValueError: If JWT creation fails
    """
    try:
        # Create payload with Supabase-specific claims
        current_time = int(time.time())
        expiry_time = current_time + expiry_seconds
        
        payload = {
            # Standard JWT claims
            "iat": current_time,  # Issued at
            "exp": expiry_time,   # Expiry
            "sub": user_id,       # Subject (user identifier)
            
            # Supabase-specific claims
            "role": "authenticated",
            "aud": "authenticated",
            
            # Custom claim for user ID in the format Supabase expects
            "user_metadata": {
                "user_id": user_id,  # Custom claim for our app
            },
            
            # Additional claims to help with debugging
            "user_id": user_id
        }
        
        # Create JWT using the configured secret key
        token = jwt.encode(
            payload,
            settings.SUPABASE_JWT_SECRET,
            algorithm="HS256"
        )
        
        return token
    except Exception as e:
        error_message = f"Failed to create JWT: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def verify_jwt(token: str) -> Dict[str, Any]:
    """
    Verify a JWT token and return the claims.
    
    Args:
        token: JWT token to verify
        
    Returns:
        Dict of claims from the token
        
    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        claims = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=["HS256"]
        )
        return claims
    except jwt.ExpiredSignatureError:
        error_message = "JWT token has expired"
        logger.warning(error_message)
        raise ValueError(error_message)
    except JWTError as e:
        error_message = f"Invalid JWT token: {str(e)}"
        logger.warning(error_message)
        raise ValueError(error_message)
    except Exception as e:
        error_message = f"Error verifying JWT: {str(e)}"
        logger.error(error_message)
        raise ValueError(error_message)


def extract_user_id_from_token(token: str, validate: bool = True) -> Optional[str]:
    """
    Extract the user ID from a JWT token.
    
    Args:
        token: JWT token
        validate: Whether to fully validate the token (set to False for rate limiting purposes)
        
    Returns:
        User ID or None if not found or token is invalid
    """
    try:
        if validate:
            # Full validation for authentication purposes
            claims = verify_jwt(token)
        else:
            # Simple decode without full validation - just for rate limiting
            claims = decode_token(token)
            if not claims:
                logger.warning("Failed to decode token")
                return None
        
        # Try to get user ID from different possible locations
        if "user_id" in claims:
            return claims["user_id"]
        elif "sub" in claims:
            return claims["sub"]
        elif "user_metadata" in claims and "user_id" in claims["user_metadata"]:
            return claims["user_metadata"]["user_id"]
            
        logger.warning("No user_id found in JWT token")
        return None
    except Exception as e:
        logger.warning(f"Failed to extract user_id from token: {str(e)}")
        return None


def create_supabase_jwt_for_storage(path: str, expiry_timestamp: int) -> str:
    """
    Create a Supabase-compatible JWT specifically for storage signed URLs.
    
    This function creates a token in the same format that Supabase uses for
    signed URLs, which is different from the authentication JWT format.
    
    Args:
        path: The storage path for which to create the signed URL
        expiry_timestamp: Expiration timestamp (unix time)
        
    Returns:
        JWT token string suitable for signed URLs
    """
    # Create payload matching Supabase's signed URL token format
    payload = {
        "url": path,  # Storage path
        "iat": int(time.time()),  # Issued at
        "exp": expiry_timestamp  # Expiration timestamp
    }
    
    # Generate and sign the token
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return token


def decode_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Simple decode of JWT token without verification.
    
    Args:
        token: JWT token to decode
        
    Returns:
        Decoded payload or None if decoding failed
    """
    try:
        # Get payload part (second segment)
        parts = token.split('.')
        if len(parts) != 3:
            return None
            
        # Decode the payload
        padded = parts[1] + '=' * (4 - len(parts[1]) % 4)
        decoded = base64.b64decode(padded)
        payload = json.loads(decoded)
        return payload
    except Exception as e:
        logger.warning(f"Error decoding token: {str(e)}")
        return None 