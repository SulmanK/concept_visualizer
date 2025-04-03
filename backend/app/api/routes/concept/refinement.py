"""
Concept refinement endpoints.

This module provides endpoints for refining existing visual concepts.
"""

import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request

from app.models.request import RefinementRequest
from app.models.response import GenerationResponse, PaletteVariation
from app.services.concept_service import ConceptService, get_concept_service
from app.services.session_service import SessionService, get_session_service
from app.services.image_service import ImageService, get_image_service
from app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service
from app.utils.rate_limiting import apply_rate_limit

# Configure logging
logger = logging.getLogger("concept_refinement_api")

router = APIRouter()


@router.post("/refine", response_model=GenerationResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    req: Request,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Refine an existing concept based on user feedback.
    
    Args:
        request: The refinement request containing feedback and concept ID
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        concept_service: The concept service
        session_service: Service for managing sessions
        image_service: Service for image operations
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The refined concept data
    
    Raises:
        HTTPException: If there was an error refining the concept
    """
    # Apply rate limit
    await apply_rate_limit(req, "/concepts/refine", "10/hour", "hour")
    
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # Refine image and store it in Supabase Storage
        logo_desc = request.logo_description or "the existing logo"
        theme_desc = request.theme_description or "the existing theme"
        
        # Refine and store the image
        refined_image_path, refined_image_url = await image_service.refine_and_store_image(
            prompt=(
                f"Refine this logo design: {logo_desc}. Theme/style: {theme_desc}. "
                f"Refinement instructions: {request.refinement_prompt}."
            ),
            original_image_url=request.original_image_url,
            session_id=session_id,
            strength=0.7  # Control how much to preserve original image
        )
        
        if not refined_image_path or not refined_image_url:
            raise HTTPException(status_code=500, detail="Failed to refine or store image")
        
        # Generate color palettes
        raw_palettes = await concept_service.generate_color_palettes(
            theme_description=f"{theme_desc} {request.refinement_prompt}",
            logo_description=logo_desc
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await image_service.create_palette_variations(
            refined_image_path,
            raw_palettes,
            session_id
        )
        
        # Store concept in Supabase database
        logo_description = request.logo_description or "Refined logo"
        theme_description = request.theme_description or "Refined theme"
        
        stored_concept = await storage_service.store_concept(
            session_id=session_id,
            logo_description=f"{logo_description} - {request.refinement_prompt}",
            theme_description=theme_description,
            base_image_path=refined_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise HTTPException(status_code=500, detail="Failed to store refined concept")
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 