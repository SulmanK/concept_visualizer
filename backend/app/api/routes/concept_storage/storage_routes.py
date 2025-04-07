"""
Concept storage endpoints.

This module provides endpoints for storing and retrieving concepts
from the database using user authentication.
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, Response, HTTPException, Request
from slowapi.util import get_remote_address
from fastapi.responses import JSONResponse

from app.models.request import PromptRequest
from app.models.response import GenerationResponse
from app.models.concept import ConceptSummary, ConceptDetail
from app.services.image import get_image_service
from app.services.concept import get_concept_service
from app.services.storage import get_concept_storage_service
from app.services.interfaces import (
    ConceptServiceInterface,
    ImageServiceInterface,
    StorageServiceInterface
)
from app.api.dependencies import CommonDependencies
from app.api.middleware.auth_middleware import get_current_user_id
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError
from app.utils.api_limits import apply_rate_limit
from app.utils.security.mask import mask_id

# Configure logging
logger = logging.getLogger("concept_storage_api")

router = APIRouter()


@router.post("/store", response_model=GenerationResponse)
async def generate_and_store_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
):
    """
    Generate a concept based on user prompt and store it in the database.
    
    Args:
        request: User prompt request with logo and theme descriptions
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including all necessary services
        
    Returns:
        Generated concept with image URL and color palettes
    """
    # Apply rate limit
    await apply_rate_limit(req, "/storage/store", "10/month")
    
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Generate base image and store it in Supabase Storage
        base_image_path, base_image_url = await commons.image_service.generate_and_store_image(
            request.logo_description,
            user_id  # Use user_id instead of session_id
        )
        
        if not base_image_path or not base_image_url:
            raise ServiceUnavailableError(detail="Failed to generate or store image")
        
        # Generate color palettes
        # First get color palettes from JigsawStack
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await commons.image_service.create_palette_variations(
            base_image_path,
            raw_palettes,
            user_id  # Use user_id instead of session_id
        )
        
        # Store concept in Supabase database
        stored_concept = await commons.storage_service.store_concept({
            "user_id": user_id,
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
            "image_path": base_image_path,
            "image_url": base_image_url,
            "color_palettes": palette_variations,
            "is_anonymous": True
        })
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store concept")
        
        # Return generation response
        return GenerationResponse(
            prompt_id=stored_concept["id"],
            image_url=base_image_url,
            color_palettes=[
                {
                    "name": p["name"],
                    "colors": p["colors"],
                    "description": p.get("description"),
                    "image_url": p["image_url"]
                } 
                for p in palette_variations
            ]
        )
    except ServiceUnavailableError:
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating concept: {str(e)}")
        raise ServiceUnavailableError(detail=f"Error generating concept: {str(e)}")


@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
):
    """
    Get recent concepts for the current user.
    
    Args:
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services
        
    Returns:
        List of recent concepts
    """
    # Apply rate limit - higher limits for read operations
    await apply_rate_limit(req, "/storage/recent", "30/minute", "minute")
    
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get recent concepts with signed image URLs using user_id
        return await commons.storage_service.get_recent_concepts(user_id)
    except Exception as e:
        logger.error(f"Error fetching recent concepts: {str(e)}")
        raise ServiceUnavailableError(detail=f"Error fetching recent concepts: {str(e)}")


@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends()
):
    """
    Get detailed information about a specific concept.
    
    Args:
        concept_id: ID of the concept to retrieve
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services
        
    Returns:
        Detailed concept information
    """
    # Apply rate limit - higher limits for read operations
    await apply_rate_limit(req, f"/storage/concept/{concept_id}", "30/minute", "minute")
    
    try:
        # Get user ID from authenticated request
        user_id = get_current_user_id(req)
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get concept detail using storage service with user_id instead of session_id
        concept = await commons.storage_service.get_concept_detail(concept_id, user_id)
        
        if not concept:
            # Use our custom error class instead of generic HTTPException
            raise ResourceNotFoundError(
                resource_type="Concept",
                resource_id=concept_id
            )
        
        return concept
    except ResourceNotFoundError:
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error retrieving concept: {str(e)}")
        # Use our custom error class for service errors
        raise ServiceUnavailableError(detail=f"Error retrieving concept: {str(e)}") 