"""
JWT utilities for Supabase storage authentication.

This module provides functions for generating Supabase-compatible JWTs for secure
access to Supabase storage buckets.
"""

import time
from typing import Dict, Any

from jose import jwt

from app.core.config import settings


def create_supabase_jwt(session_id: str, expiry_seconds: int = 259200) -> str:
    """
    Create a Supabase-compatible JWT with session ID in claims.
    
    Args:
        session_id: User's session ID
        expiry_seconds: Token validity period in seconds (default: 3 days / 259200 seconds)
        
    Returns:
        JWT token string
    """
    now = int(time.time())
    
    # Get Supabase project reference from URL
    # Example: "https://pstdcfittpjhxzynbdbu.supabase.co" -> "pstdcfittpjhxzynbdbu"
    supabase_project_ref = settings.SUPABASE_URL.replace("https://", "").split(".")[0] if settings.SUPABASE_URL else ""
    
    # Create payload with standard and custom claims
    # This structure follows Supabase's expected JWT format
    payload = {
        # Standard claims
        "iss": settings.SUPABASE_URL,  # Issuer
        "iat": now,  # Issued at
        "exp": now + expiry_seconds,  # Expiration
        "aud": settings.SUPABASE_URL,  # Audience - must match your Supabase URL
        "role": "anon",  # Role (anonymous)
        
        # Custom claim for session ID in the format Supabase expects
        "sub": "",  # No authenticated user
        "session_id": session_id,  # Custom claim for our app
        
        # App metadata is where Supabase looks for custom claims
        "app_metadata": {
            "session_id": session_id
        }
    }
    
    # Generate and sign the token
    token = jwt.encode(payload, settings.SUPABASE_JWT_SECRET, algorithm="HS256")
    return token

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