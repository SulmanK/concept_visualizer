"""
Core Supabase client implementation.

This module provides the base SupabaseClient class for interacting with Supabase.
"""

import logging
import jwt
from typing import Optional, Dict, Any

from supabase import create_client
from postgrest.exceptions import APIError as PostgrestAPIError
from fastapi import Request, HTTPException, status

from ..config import settings, get_masked_value
from ..exceptions import DatabaseError, StorageError, AuthenticationError
from ...utils.security.mask import mask_id


# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Base client for interacting with Supabase."""
    
    def __init__(self, url: str = None, key: str = None, session_id: Optional[str] = None):
        """Initialize Supabase client with configured settings.
        
        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase API key (defaults to settings.SUPABASE_KEY)
            session_id: Optional session ID to store for later use
            
        Raises:
            DatabaseError: If client initialization fails
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.logger = logging.getLogger("supabase_client")
        self.session_id = session_id
        
        try:
            # Initialize Supabase client
            self.client = create_client(self.url, self.key)
            
            # Log initialization with masked session ID if present
            if session_id:
                self.logger.debug(f"Initialized Supabase client with session: {mask_id(session_id)}")
            else:
                self.logger.debug("Initialized Supabase client without session ID")
        except Exception as e:
            error_message = f"Failed to initialize Supabase client: {str(e)}"
            self.logger.error(error_message)
            raise DatabaseError(
                message=error_message,
                details={"url": self.url, "session_id": mask_id(self.session_id) if self.session_id else None}
            )
    
    def get_service_role_client(self):
        """Create a Supabase client with service role permissions.
        
        This client has elevated permissions and can access all resources.
        Use with caution and only for operations that require admin access.
        
        Returns:
            A Supabase client initialized with the service role key
        
        Raises:
            DatabaseError: If client initialization fails
        """
        try:
            # Check if we have the service role key
            service_role_key = settings.SUPABASE_SERVICE_ROLE
            if not service_role_key:
                self.logger.error("Service role key not found in settings")
                raise DatabaseError(
                    message="Service role key not configured",
                    details={"missing_key": "SUPABASE_SERVICE_ROLE"}
                )
            
            self.logger.debug("Creating Supabase client with service role permissions")
            # Create and return a new client with the service role key
            return create_client(self.url, service_role_key)
        except Exception as e:
            error_message = f"Failed to initialize service role client: {str(e)}"
            self.logger.error(error_message)
            raise DatabaseError(
                message=error_message,
                details={"url": self.url}
            )
    
    def _mask_path(self, path: str) -> str:
        """Mask a storage path to protect session ID privacy.
        
        Args:
            path: Storage path potentially containing session ID
            
        Returns:
            Masked path with session ID portion obscured
        """
        if not path or "/" not in path:
            return path
            
        # Split path at first slash to separate session ID from filename
        parts = path.split("/", 1)
        if len(parts) >= 2:
            session_part = parts[0]
            file_part = parts[1]
            return f"{get_masked_value(session_part)}/{file_part}"
        return path
    
    def purge_all_data(self, session_id: Optional[str] = None) -> bool:
        """Purge all data for a session or all data in the system.
        
        WARNING: This is a destructive operation! Use with caution.
        
        Args:
            session_id: Optional session ID to purge only data for this session
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            DatabaseError: If database operation fails
            StorageError: If storage operation fails
        """
        from .session_storage import SessionStorage
        from .concept_storage import ConceptStorage
        from .image_storage import ImageStorage
        
        session_storage = SessionStorage(self)
        concept_storage = ConceptStorage(self)
        image_storage = ImageStorage(self)
        
        try:
            if session_id:
                self.logger.warning(f"Purging all data for session ID {mask_id(session_id)}")
                
                try:
                    # Delete storage objects first (no DB constraints)
                    image_storage.delete_all_storage_objects("concepts", session_id)
                except Exception as e:
                    self.logger.error(f"Error deleting storage objects: {str(e)}")
                    raise StorageError(
                        message=f"Failed to delete storage objects for session: {str(e)}",
                        operation="delete_all",
                        bucket="concepts",
                        path=session_id,
                    )
                
                try:
                    # Delete concepts (and color_variations via cascading delete)
                    concept_storage.delete_all_concepts(session_id)
                except PostgrestAPIError as e:
                    self.logger.error(f"Database error deleting concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                except Exception as e:
                    self.logger.error(f"Error deleting concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Unexpected error deleting concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                
                # Session will remain unless explicitly deleted
                self.logger.info(f"Successfully purged all data for session ID {mask_id(session_id)}")
            else:
                self.logger.warning("PURGING ALL DATA FROM THE SYSTEM!")
                
                try:
                    # Delete all storage objects
                    image_storage.delete_all_storage_objects("concepts")
                except Exception as e:
                    self.logger.error(f"Error deleting all storage objects: {str(e)}")
                    raise StorageError(
                        message=f"Failed to delete all storage objects: {str(e)}",
                        operation="delete_all",
                        bucket="concepts",
                    )
                
                try:
                    # Delete all concepts (and color_variations via cascading delete)
                    self.client.table("concepts").delete().execute()
                except PostgrestAPIError as e:
                    self.logger.error(f"Database error deleting all concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete all concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                except Exception as e:
                    self.logger.error(f"Error deleting all concepts: {str(e)}")
                    raise DatabaseError(
                        message=f"Unexpected error deleting all concepts: {str(e)}",
                        operation="delete",
                        table="concepts",
                    )
                
                try:
                    # Delete all sessions
                    session_storage.delete_all_sessions()
                except Exception as e:
                    self.logger.error(f"Error deleting all sessions: {str(e)}")
                    raise DatabaseError(
                        message=f"Failed to delete all sessions: {str(e)}",
                        operation="delete",
                        table="sessions",
                    )
                
                self.logger.warning("Successfully purged ALL data from the system")
                
            return True
        except (DatabaseError, StorageError):
            # Re-raise these specific exceptions
            raise
        except Exception as e:
            self.logger.error(f"Unexpected error purging data: {str(e)}")
            raise DatabaseError(
                message=f"Unexpected error during data purge: {str(e)}",
                details={"session_id": mask_id(session_id) if session_id else "all_sessions"}
            )


class SupabaseAuthClient:
    """Client for Supabase authentication."""
    
    def __init__(self, url: str = None, key: str = None):
        """Initialize the Supabase authentication client.
        
        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase API key (defaults to settings.SUPABASE_KEY)
            
        Raises:
            AuthenticationError: If client initialization fails
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.jwt_secret = settings.SUPABASE_JWT_SECRET
        self.logger = logging.getLogger("supabase_auth")
        
        try:
            # Initialize Supabase client
            self.client = create_client(self.url, self.key)
            self.logger.debug(f"Initialized Supabase auth client")
        except Exception as e:
            error_message = f"Failed to initialize Supabase auth client: {str(e)}"
            self.logger.error(error_message)
            raise AuthenticationError(
                message=error_message,
                details={"url": self.url}
            )
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return the payload.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Token payload with user information
            
        Raises:
            HTTPException: If token is invalid or verification fails
        """
        try:
            # For testing in development, if no JWT secret is available
            if not self.jwt_secret and settings.ENVIRONMENT == "development":
                self.logger.warning("JWT verification disabled in development mode")
                
                # Simple decode without verification (ONLY FOR DEVELOPMENT)
                payload = jwt.decode(
                    token,
                    options={"verify_signature": False}
                )
                return payload
            
            # Extract project reference from Supabase URL to use as audience
            # This handles cases where the token's audience is the project URL
            project_ref = self.url.strip('/').split('.')[-2].split('/')[-1] if self.url else None
            expected_audience = project_ref or 'authenticated'

            # In development, be more permissive about audience validation
            if settings.ENVIRONMENT == "development":
                self.logger.debug(f"Decoding JWT in development mode with flexible audience validation")
                # Decode with options that skip audience validation in development
                payload = jwt.decode(
                    token,
                    self.jwt_secret,
                    algorithms=["HS256"],
                    options={
                        "verify_signature": True,
                        "verify_aud": False  # Skip audience validation in development
                    }
                )
                
                # Log audience information for debugging
                if 'aud' in payload:
                    self.logger.debug(f"Token audience: {payload['aud']}, Expected: {expected_audience}")
                
                return payload
                
            # In production, do proper validation
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                audience=expected_audience,  # Use the expected audience for validation
                options={"verify_signature": True}
            )
            return payload
        except jwt.ExpiredSignatureError:
            self.logger.warning(f"Token expired: {mask_id(token[:10])}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid token: {str(e)}"
            )
        except Exception as e:
            self.logger.error(f"Unexpected error verifying token: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error verifying authentication token"
            )
    
    def get_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract user information from request authorization header.
        
        Args:
            request: FastAPI request object
            
        Returns:
            User information from token or None if no valid token
        """
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
            
        token = auth_header.replace("Bearer ", "")
        try:
            payload = self.verify_token(token)
            
            # Extract user information from token
            user_info = {
                "id": payload.get("sub"),
                "email": payload.get("email"),
                "app_metadata": payload.get("app_metadata", {}),
                "user_metadata": payload.get("user_metadata", {}),
                "is_anonymous": payload.get("app_metadata", {}).get("is_anonymous", False),
                "role": payload.get("role", "authenticated"),
                "token": token
            }
            
            # Log user identification (masked for privacy)
            self.logger.debug(f"Authenticated user: {mask_id(user_info['id'])}, role: {user_info['role']}")
            return user_info
        except HTTPException:
            # Re-raise HTTP exceptions (already logged in verify_token)
            raise
        except Exception as e:
            self.logger.error(f"Error extracting user from request: {str(e)}")
            return None


def get_supabase_client(session_id: Optional[str] = None) -> SupabaseClient:
    """Create a Supabase client with the specified session ID.
    
    Args:
        session_id: Optional session ID to use
        
    Returns:
        Initialized Supabase client
    """
    return SupabaseClient(session_id=session_id)


def get_supabase_auth_client() -> SupabaseAuthClient:
    """Create a Supabase auth client.
    
    Returns:
        Initialized Supabase auth client
    """
    return SupabaseAuthClient() 