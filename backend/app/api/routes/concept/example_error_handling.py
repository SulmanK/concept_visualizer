"""Example route with proper error handling.

This module demonstrates the recommended approach for error handling in API routes.
"""

import logging
from typing import Any, Dict

from fastapi import APIRouter, Depends, Request

from app.api.dependencies import CommonDependencies

# Import API errors directly only if you need to raise them explicitly
# For most cases, you should let the exception handler convert ApplicationError types
from app.api.errors import InternalServerError

# Import domain/application error types for catching
from app.core.exceptions import ApplicationError, AuthenticationError, ConceptNotFoundError, DatabaseError, JigsawStackError, ResourceNotFoundError
from app.core.exceptions import ValidationError as AppValidationError
from app.models.concept.request import PromptRequest

# Configure logging
logger = logging.getLogger("example_error_handling")

router = APIRouter()


@router.get("/concept/{concept_id}", response_model=Dict[str, Any])
async def get_concept_example(
    concept_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
) -> Dict[str, Any]:
    """Example route showing proper error handling with the application's error system.

    Args:
        concept_id: ID of the concept to retrieve
        request: FastAPI request object
        commons: Common dependencies including services

    Returns:
        Dict[str, Any]: The concept data

    Raises:
        Various exceptions that will be properly mapped to API errors by the error handler
    """
    # Process the request to extract user information
    commons.process_request(request)

    try:
        # Get user ID from commons
        user_id = commons.user_id
        if not user_id:
            # This will be mapped to 401 Unauthorized by the error handler
            raise AuthenticationError(message="Authentication required")

        # Validate concept_id format
        if not concept_id or len(concept_id) < 5:
            # This will be mapped to 422 Unprocessable Entity by the error handler
            raise AppValidationError(
                message="Invalid concept ID format",
                field_errors={"concept_id": ["Concept ID must be at least 5 characters"]},
            )

        # Try to fetch the concept using the persistence service
        try:
            # Use get_concept_detail with the required user_id parameter
            concept = await commons.concept_persistence_service.get_concept_detail(concept_id=concept_id, user_id=user_id)

            # Check if the concept belongs to the current user
            if concept.get("user_id") != user_id:
                # This will be mapped to 403 Forbidden by the error handler
                # Use AuthenticationError for lack of permissions
                raise AuthenticationError(
                    message="You don't have permission to access this concept",
                    details={"concept_id": concept_id, "user_id": user_id},
                )

            # Return the concept data
            return concept

        except ConceptNotFoundError:
            # This will be mapped to 404 Not Found by the error handler
            # Just re-raise it - the global exception handler will convert it
            raise

        except DatabaseError as e:
            # This will be mapped to 500 Internal Server Error by the error handler
            logger.error(f"Database error: {e.message}", exc_info=True)
            raise

    except ApplicationError as e:
        # For all ApplicationError subclasses, we just re-raise
        # The global exception handler will map them to the appropriate API errors
        # You can add custom logging here if needed
        if isinstance(e, ResourceNotFoundError):
            logger.warning(f"Resource not found: {e.message}")
        else:
            logger.error(f"Application error: {e.message}", exc_info=True)
        raise

    except Exception as e:
        # For unexpected errors, wrap them in an InternalServerError
        # This ensures a consistent API response format
        error_msg = f"Unexpected error retrieving concept: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise InternalServerError(detail=error_msg)


@router.post("/concept-analyze", response_model=Dict[str, Any])
async def analyze_concept_example(
    request: PromptRequest,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> Dict[str, Any]:
    """Example route showing how to handle different types of application errors.

    Args:
        request: The prompt request
        req: FastAPI request object
        commons: Common dependencies

    Returns:
        Dict[str, Any]: Analysis results
    """
    try:
        # Process user info
        commons.process_request(req)

        # Validation example
        if not request.logo_description:
            raise AppValidationError(
                message="Logo description is required",
                field_errors={"logo_description": ["This field is required"]},
            )

        # Simulate a service call that might fail
        try:
            # This is just an example - in a real route you'd call actual services
            analysis_results = {
                "complexity": "medium",
                "estimated_generation_time": "2 seconds",
                "prompt_quality": "high",
            }

            # Example of conditional error raising
            if "error" in request.logo_description.lower():
                # Simulate a service error
                raise JigsawStackError(
                    message="Unable to analyze concept with the AI service",
                    endpoint="concept-analysis",
                    details={"reason": "Service temporarily unavailable"},
                )

            return analysis_results

        except JigsawStackError as e:
            # You can add specific logging or transformations here
            # before re-raising for the global handler
            logger.error(f"JigsawStack API error: {e.message}", exc_info=True)
            raise

    except ApplicationError as e:
        # Log at appropriate level based on error type
        if isinstance(e, AppValidationError):
            logger.warning(f"Validation error: {e.message}")
        elif isinstance(e, AuthenticationError):
            logger.warning(f"Authentication error: {e.message}")
        else:
            logger.error(f"Application error: {e.message}", exc_info=True)
        # Just re-raise - global exception handler will map it
        raise

    except Exception as e:
        # For unexpected errors
        error_msg = f"Unexpected error analyzing concept: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise InternalServerError(detail=error_msg)
