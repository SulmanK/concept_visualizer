"""
Concept refinement endpoints.

This module provides endpoints for refining existing visual concepts.
"""

import logging
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.request import RefinementRequest
from app.models.response import GenerationResponse, PaletteVariation
from app.utils.api_limits import apply_rate_limit
from app.services.concept import get_concept_service
from app.services.session import get_session_service
from app.services.image import get_image_service
from app.services.storage import get_concept_storage_service
from app.services.interfaces import (
    ConceptServiceInterface,
    SessionServiceInterface, 
    ImageServiceInterface,
    StorageServiceInterface
)
from app.api.dependencies import CommonDependencies, get_or_create_session
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError

# Configure logging
logger = logging.getLogger("concept_refinement_api")

router = APIRouter()


@router.post("/refine", response_model=GenerationResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Refine an existing concept based on user feedback.
    
    Args:
        request: The refinement request containing feedback and concept ID
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including all services
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The refined concept data
    
    Raises:
        ServiceUnavailableError: If there was an error refining the concept
        ValidationError: If the request validation fails
    """
    # Apply rate limit
    await apply_rate_limit(req, "/concepts/refine", "10/hour", "hour")
    
    try:
        # Validate inputs
        if not request.refinement_prompt:
            raise ValidationError(
                detail="Refinement prompt is required",
                field_errors={
                    "refinement_prompt": ["Field is required"]
                }
            )
        
        if not request.original_image_url:
            raise ValidationError(
                detail="Original image URL is required",
                field_errors={
                    "original_image_url": ["Field is required"]
                }
            )
        
        # Get or create session using dependency
        session_id, _ = await get_or_create_session(
            response=response,
            session_service=commons.session_service,
            session_id=session_id
        )
        
        # Refine image and store it in Supabase Storage
        logo_desc = request.logo_description or "the existing logo"
        theme_desc = request.theme_description or "the existing theme"
        
        # Refine and store the image
        refined_image_path, refined_image_url = await commons.image_service.refine_and_store_image(
            prompt=(
                f"Refine this logo design: {logo_desc}. Theme/style: {theme_desc}. "
                f"Refinement instructions: {request.refinement_prompt}."
            ),
            original_image_url=request.original_image_url,
            session_id=session_id,
            strength=0.7  # Control how much to preserve original image
        )
        
        if not refined_image_path or not refined_image_url:
            raise ServiceUnavailableError(detail="Failed to refine or store image")
        
        # Generate color palettes
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=f"{theme_desc} {request.refinement_prompt}",
            logo_description=logo_desc
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await commons.image_service.create_palette_variations(
            refined_image_path,
            raw_palettes,
            session_id
        )
        
        # Store concept in Supabase database
        logo_description = request.logo_description or "Refined logo"
        theme_description = request.theme_description or "Refined theme"
        
        stored_concept = await commons.storage_service.store_concept(
            session_id=session_id,
            logo_description=f"{logo_description} - {request.refinement_prompt}",
            theme_description=theme_description,
            base_image_path=refined_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store refined concept")
        
        # Return generation response
        return GenerationResponse(
            prompt_id=stored_concept["id"],
            logo_description=f"{logo_description} - {request.refinement_prompt}",
            theme_description=theme_description,
            created_at=stored_concept.get("created_at", ""),
            image_url=refined_image_url,
            variations=[
                PaletteVariation(
                    name=p["name"],
                    colors=p["colors"],
                    description=p.get("description", ""),
                    image_url=p["image_url"]
                ) 
                for p in palette_variations
            ],
            original_image_url=request.original_image_url,
            refinement_prompt=request.refinement_prompt
        )
    except (ValidationError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error refining concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error refining concept: {str(e)}") 