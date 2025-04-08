"""
Authentication middleware for FastAPI applications.

This module provides middleware for JWT token authentication with Supabase.
"""

import logging
from typing import Optional, Callable, Dict, Any, Union

from fastapi import Request, Response, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint

from app.core.supabase.client import get_supabase_auth_client
from app.core.exceptions import AuthenticationError
from app.utils.security.mask import mask_id


logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle Supabase authentication via JWT tokens."""
    
    def __init__(
        self,
        app,
        public_paths: Optional[list[str]] = None,
    ):
        """
        Initialize the authentication middleware.
        
        Args:
            app: The FastAPI application
            public_paths: List of paths that should be accessible without authentication
        """
        super().__init__(app)
        self.public_paths = public_paths or []
        self.supabase_auth = get_supabase_auth_client()
        self.logger = logging.getLogger("auth_middleware")
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """
        Process the request, verifying authentication when needed.
        
        Args:
            request: The incoming request
            call_next: The next middleware or endpoint in the chain
            
        Returns:
            The HTTP response
        """
        # Always allow OPTIONS requests for CORS
        if request.method == "OPTIONS":
            self.logger.debug(f"Allowing OPTIONS request for CORS: {request.url.path}")
            return await call_next(request)
        
        path = request.url.path
        
        # Handle health/rate-limits endpoints specially - try to authenticate but don't require it
        is_rate_limits_path = path.startswith("/api/health/rate-limits")
        
        # Skip authentication for other public paths
        if self._is_public_path(path) and not is_rate_limits_path:
            self.logger.debug(f"Skipping auth for public path: {path}")
            return await call_next(request)
            
        # Extract Authorization header for debugging
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            self.logger.warning(f"No Authorization header found for path: {path}")
        else:
            # Log a masked version of the header (first 5 chars only)
            masked_auth = auth_header[:5] + "*****" if len(auth_header) > 5 else auth_header
            self.logger.debug(f"Authorization header: {masked_auth}")
        
        # Extract user from authorization header
        try:
            user = self.supabase_auth.get_user_from_request(request)
            
            if user:
                # Attach user info to request state for use in endpoints
                request.state.user = user
                self.logger.debug(f"Authenticated user: {mask_id(user['id'])}")
                return await call_next(request)
            else:
                # No valid user found in token
                
                # For rate limits endpoints, continue without auth
                if is_rate_limits_path:
                    self.logger.debug(f"No auth for rate limits path: {path}, continuing anyway")
                    return await call_next(request)
                
                # For other endpoints, require auth
                self.logger.warning(f"Authentication required for path: {path}")
                # Add CORS headers to auth errors to prevent CORS issues
                return JSONResponse(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    content={"detail": "Authentication required"}
                )
                
        except AuthenticationError as e:
            # Authentication-specific error (already logged in the auth client)
            self.logger.warning(f"Auth error for {path}: {e.message}")
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": e.message}
            )
        except Exception as e:
            # Unexpected error
            self.logger.error(f"Auth middleware error: {str(e)}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Authentication error"}
            )
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if the path should be publicly accessible.
        
        Args:
            path: Request path to check
            
        Returns:
            True if the path is public, False otherwise
        """
        # Always allow docs and openapi endpoints
        if path.startswith("/docs") or path.startswith("/redoc") or path.startswith("/openapi.json"):
            return True
        
        # Check against the list of public paths
        for public_path in self.public_paths:
            if path == public_path or path.startswith(public_path):
                return True
                
        return False


def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """
    Get the current authenticated user from request state.
    
    This is a helper function to be used in FastAPI dependencies.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        User information if authenticated, None otherwise
    """
    return getattr(request.state, "user", None)


def get_current_user_id(request: Request) -> Optional[str]:
    """
    Get the current authenticated user ID from request state.
    
    This is a helper function to be used in FastAPI dependencies.
    
    Args:
        request: The FastAPI request object
        
    Returns:
        User ID if authenticated, None otherwise
    """
    user = get_current_user(request)
    return user["id"] if user else None 