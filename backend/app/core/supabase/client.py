"""Core Supabase client implementation.

This module provides the base SupabaseClient class for interacting with Supabase.
"""

import logging
from typing import Any, Dict, Optional, cast

import jwt
from fastapi import Request

from supabase import create_client

from ...utils.security.mask import mask_id
from ..config import settings
from ..exceptions import AuthenticationError, DatabaseError

# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Base client for interacting with Supabase."""

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
        session_id: Optional[str] = None,
    ):
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
                details={
                    "url": self.url,
                    "session_id": mask_id(self.session_id) if self.session_id else None,
                },
            )

    def get_service_role_client(self) -> Any:
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
                    details={"missing_key": "SUPABASE_SERVICE_ROLE"},
                )

            self.logger.debug("Creating Supabase client with service role permissions")
            # Create and return a new client with the service role key
            return create_client(self.url, service_role_key)
        except Exception as e:
            error_message = f"Failed to initialize service role client: {str(e)}"
            self.logger.error(error_message)
            raise DatabaseError(message=error_message, details={"url": self.url})


class SupabaseAuthClient:
    """Client for Supabase authentication."""

    def __init__(self, url: Optional[str] = None, key: Optional[str] = None):
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
            self.logger.debug("Initialized Supabase auth client")
        except Exception as e:
            error_message = f"Failed to initialize Supabase auth client: {str(e)}"
            self.logger.error(error_message)
            raise AuthenticationError(message=error_message, details={"url": self.url})

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and extract user data.

        Args:
            token: JWT token to verify

        Returns:
            User data from the token payload

        Raises:
            AuthenticationError: If token verification fails
        """
        if not token:
            self.logger.warning("Empty token provided for verification")
            raise AuthenticationError(message="No token provided", details={"code": "no_token"})

        try:
            # Define JWT decoding options based on our needs
            options = {
                "verify_signature": True,  # Verify using the secret
                "verify_aud": False,  # Don't check audience claim
                "verify_exp": True,  # Check expiration
                "require": ["exp", "sub"],  # Require these claims
            }

            # Decode and verify the token
            payload = jwt.decode(token, self.jwt_secret, algorithms=["HS256"], options=options)

            # Log successful verification with masked subject
            if "sub" in payload:
                masked_sub = mask_id(payload["sub"])
                self.logger.debug(f"Successfully verified token for subject: {masked_sub}")
            else:
                self.logger.debug("Successfully verified token (no subject claim)")

            # Explicitly cast to Dict[str, Any] to satisfy mypy
            return cast(Dict[str, Any], payload)

        except jwt.ExpiredSignatureError:
            self.logger.warning("Token expired")
            raise AuthenticationError(message="Token expired", details={"code": "token_expired"})
        except jwt.InvalidTokenError as e:
            self.logger.warning(f"Invalid token: {str(e)}")
            raise AuthenticationError(message=f"Invalid token: {str(e)}", details={"code": "invalid_token"})
        except Exception as e:
            self.logger.error(f"Unexpected error verifying token: {str(e)}")
            raise AuthenticationError(
                message=f"Token verification failed: {str(e)}",
                details={"code": "verification_error"},
            )

    def get_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract and verify user information from a FastAPI request.

        This checks for:
        1. Authorization header with Bearer token
        2. Session cookie

        Args:
            request: FastAPI Request object

        Returns:
            User data if found and verified, None otherwise

        Raises:
            AuthenticationError: If authentication fails
        """
        # Try Authorization header first
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                # Get the token payload
                payload = self.verify_token(token)

                # Extract user information from token
                user_info = {
                    "id": payload.get("sub"),  # The subject claim contains the user ID
                    "email": payload.get("email"),
                    "app_metadata": payload.get("app_metadata", {}),
                    "user_metadata": payload.get("user_metadata", {}),
                    "is_anonymous": payload.get("app_metadata", {}).get("is_anonymous", False),
                    "role": payload.get("role", "authenticated"),
                    "token": token,  # Include the original token
                }

                # Log user identification (masked for privacy)
                if user_info["id"]:
                    self.logger.debug(f"Authenticated user: {mask_id(user_info['id'])}, role: {user_info['role']}")

                return user_info
            except AuthenticationError as e:
                # Rethrow with the specific auth error
                raise e
            except Exception as e:
                self.logger.error(f"Error verifying bearer token: {str(e)}")
                raise AuthenticationError(
                    message=f"Bearer token verification failed: {str(e)}",
                    details={"code": "bearer_verification_error"},
                )

        # TODO: Add support for session cookies if needed

        # No valid authentication found
        return None


def get_supabase_client(session_id: Optional[str] = None) -> SupabaseClient:
    """Get a configured Supabase client instance.

    Args:
        session_id: Optional session ID to associate with the client

    Returns:
        Configured SupabaseClient
    """
    return SupabaseClient(session_id=session_id)


def get_supabase_auth_client() -> SupabaseAuthClient:
    """Get a configured Supabase authentication client instance.

    Returns:
        Configured SupabaseAuthClient
    """
    return SupabaseAuthClient()
