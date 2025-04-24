"""Authentication routes for the Concept Visualizer API.

This module provides API endpoints for user authentication.
"""

import logging
import traceback
from typing import Dict

from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse

from app.api.dependencies import CommonDependencies

router = APIRouter()

logger = logging.getLogger(__name__)


@router.get("/session")
async def get_session(request: Request) -> Dict[str, object]:
    """Check if the user is authenticated.

    Args:
        request: The FastAPI request object

    Returns:
        JSON response with user session information if authenticated,
        or an error message if not
    """
    # Check if session exists and has user data
    if not hasattr(request, "session") or "user" not in request.session:
        return {"authenticated": False, "message": "No active session"}

    # Return session info
    return {
        "authenticated": True,
        "user": request.session["user"],
    }


@router.post("/login")
async def login(request: Request, commons: CommonDependencies = Depends()) -> JSONResponse:
    """Log in a user with email and password.

    Args:
        request: The FastAPI request object
        commons: Common dependencies including services

    Returns:
        JSON response with authentication status and user information if successful
    """
    try:
        # Get request body
        data = await request.json()

        # Validate required fields
        if "email" not in data or "password" not in data:
            return JSONResponse(
                status_code=400,
                content={"message": "Email and password are required"},
            )

        # Extract credentials
        email = data["email"]
        password = data["password"]

        # Authenticate with Supabase
        # Use the client's auth object instead of a non-existent method
        auth_response = commons.supabase_client.client.auth.sign_in_with_password(
            {
                "email": email,
                "password": password,
            }
        )

        # Store user in session
        if not hasattr(request, "session"):
            # Return error if session middleware isn't configured
            return JSONResponse(
                status_code=500,
                content={"message": "Session middleware not configured"},
            )

        # Get user from response
        user = auth_response.user

        # Store in session
        request.session["user"] = user

        # Return success with user data
        return JSONResponse(
            status_code=200,
            content={
                "authenticated": True,
                "user": user,
            },
        )

    except Exception as e:
        logger.error(f"Error during login: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            status_code=401,
            content={"message": f"Authentication failed: {str(e)}"},
        )


@router.post("/logout")
async def logout(request: Request) -> JSONResponse:
    """Log out the current user by clearing their session.

    Args:
        request: The FastAPI request object

    Returns:
        JSON response confirming successful logout
    """
    try:
        # Clear user from session
        if hasattr(request, "session") and "user" in request.session:
            del request.session["user"]
            return JSONResponse(
                status_code=200,
                content={"message": "Logged out successfully"},
            )
        else:
            return JSONResponse(
                status_code=200,
                content={"message": "No active session to log out"},
            )

    except Exception as e:
        logger.error(f"Error during logout: {str(e)}")
        logger.debug(traceback.format_exc())
        return JSONResponse(
            status_code=500,
            content={"message": f"Logout failed: {str(e)}"},
        )
