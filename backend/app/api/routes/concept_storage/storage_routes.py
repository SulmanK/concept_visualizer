"""Concept storage routes.

This module provides API endpoints for storing and retrieving
visual concepts from the database.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from pydantic import HttpUrl

from app.api.dependencies import CommonDependencies
from app.core.exceptions import ResourceNotFoundError, ServiceUnavailableError
from app.models.concept.request import PromptRequest
from app.models.concept.response import ConceptDetail, ConceptSummary, GenerationResponse

# Utility function to get current user ID from request
from app.utils.auth.user import get_current_user_id

# Configure logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.post("/store", response_model=GenerationResponse)
async def generate_and_store_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> GenerationResponse:
    """Generate and store a new concept based on prompt.

    This endpoint handles both generation and storage in a single call:
    1. Generates a base image based on the logo description
    2. Generates color palettes based on the theme
    3. Creates color variations of the base image
    4. Stores everything in the database

    Args:
        request: Prompt request with logo and theme descriptions
        response: FastAPI response object
        req: FastAPI request object
        commons: Common dependencies including services

    Returns:
        Generated concept with image URL and color palettes
    """
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Generate base concept using ConceptService (returns image data and URL)
        concept_response = await commons.concept_service.generate_concept(
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            user_id=user_id,
            skip_persistence=True,  # Skip persistence in the service, we'll handle it here
        )

        if not concept_response or not isinstance(concept_response, dict):
            raise ServiceUnavailableError("Failed to generate base concept")

        # Explicitly cast to Dict for mypy
        concept_response_dict: Dict[str, Any] = concept_response

        # Extract image URL and path
        image_url = concept_response_dict.get("image_url")
        image_path = concept_response_dict.get("image_path")

        if not image_url or not image_path:
            raise ServiceUnavailableError("Failed to generate or store image")

        # Generate color palettes
        # First get color palettes from JigsawStack
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description,
        )

        # Apply color palettes to create variations and store in Supabase Storage
        # Use image_service to process palettes but get image data through image_persistence_service
        image_data = await commons.image_persistence_service.get_image(image_path)
        palette_variations = await commons.image_service.create_palette_variations(base_image_data=image_data, palettes=raw_palettes, user_id=user_id)

        # Store concept in Supabase database
        stored_concept = await commons.concept_persistence_service.store_concept(
            {
                "user_id": user_id,
                "logo_description": request.logo_description,
                "theme_description": request.theme_description,
                "image_path": image_path,
                "image_url": image_url,
                "color_palettes": palette_variations,
                "is_anonymous": True,
            }
        )

        if not stored_concept:
            raise ServiceUnavailableError("Failed to store concept")

        # Handle prompt_id based on the type of stored_concept
        # It could be either a string (just the ID) or a dictionary with an id field
        prompt_id: str = ""
        if isinstance(stored_concept, dict) and "id" in stored_concept:
            prompt_id = stored_concept["id"]
        elif isinstance(stored_concept, str):
            prompt_id = stored_concept
        else:
            raise ServiceUnavailableError("Invalid concept storage response format")

        # Transform the string URL to HttpUrl object if needed
        image_url_obj = image_url
        if isinstance(image_url, str):
            image_url_obj = HttpUrl(image_url)

        # Return generation response with all required fields
        return GenerationResponse(
            prompt_id=prompt_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            created_at=datetime.utcnow().isoformat(),
            image_url=image_url_obj,
            color_palette=None,  # No single palette (using variations instead)
            original_image_url=None,  # Not a refinement
            refinement_prompt=None,  # Not a refinement
        )
    except ServiceUnavailableError:
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating concept: {str(e)}")
        raise ServiceUnavailableError(f"Error generating concept: {str(e)}")


@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    req: Request,
    limit: int = Query(10, ge=1, le=50),
    commons: CommonDependencies = Depends(),
) -> List[Dict[str, Any]]:
    """Get recent concepts for the current user.

    Args:
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        limit: Maximum number of concepts to return (default: 10, max: 50)
        commons: Common dependencies including services

    Returns:
        List of recent concepts
    """
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Get recent concepts with paths from persistence service
        concepts = await commons.concept_persistence_service.get_recent_concepts(user_id, limit)

        # Log to verify color_variations are present
        for i, concept in enumerate(concepts):
            variations_count = len(concept.get("color_variations", []))
            logger.info(f"Concept {i+1}/{len(concepts)} (ID: {concept['id']}): {variations_count} color variations")

        # Process each concept to add signed URLs only if needed
        for concept in concepts:
            # Only generate a new URL if one doesn't already exist
            if concept.get("image_path") and not concept.get("image_url"):
                concept["image_url"] = commons.image_persistence_service.get_image_url(concept["image_path"])

            # Process color variations if they exist
            if "color_variations" in concept and concept["color_variations"]:
                for variation in concept["color_variations"]:
                    # Only generate a new URL if one doesn't already exist
                    if variation.get("image_path") and not variation.get("image_url"):
                        variation["image_url"] = commons.image_persistence_service.get_image_url(variation["image_path"])

                # Log after processing all variations
                logger.info(f"Processed {len(concept['color_variations'])} variations for concept {concept['id']}")

        return concepts
    except Exception as e:
        logger.error(f"Error fetching recent concepts: {str(e)}")
        raise ServiceUnavailableError(f"Error fetching recent concepts: {str(e)}")


@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> Dict[str, Any]:
    """Get detailed information about a specific concept.

    Args:
        concept_id: ID of the concept to retrieve
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services

    Returns:
        Detailed concept information
    """
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Get concept detail using storage service with user_id instead of session_id
        concept = await commons.concept_persistence_service.get_concept_detail(concept_id, user_id)

        if not concept:
            # Use our custom error class instead of generic HTTPException
            raise ResourceNotFoundError(resource_type="Concept", resource_id=concept_id)

        # Only generate a new URL if one doesn't already exist
        if concept.get("image_path") and not concept.get("image_url"):
            concept["image_url"] = commons.image_persistence_service.get_image_url(concept["image_path"])

        # Process color variations if they exist
        if "color_variations" in concept and concept["color_variations"]:
            for variation in concept["color_variations"]:
                # Only generate a new URL if one doesn't already exist
                if variation.get("image_path") and not variation.get("image_url"):
                    variation["image_url"] = commons.image_persistence_service.get_image_url(variation["image_path"])

        return concept
    except ResourceNotFoundError:
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error retrieving concept: {str(e)}")
        # Use our custom error class for service errors
        raise ServiceUnavailableError(f"Error retrieving concept: {str(e)}")
