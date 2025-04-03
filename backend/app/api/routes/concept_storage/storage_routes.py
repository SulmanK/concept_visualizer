"""
Concept storage endpoints.

This module provides endpoints for storing and retrieving concepts
from the database.
"""

import logging
from typing import Optional, List

from fastapi import APIRouter, Depends, Response, Cookie, HTTPException, Request
from slowapi.util import get_remote_address

from app.models.request import PromptRequest
from app.models.response import GenerationResponse
from app.models.concept import ConceptSummary, ConceptDetail
from app.services.session_service import SessionService, get_session_service
from app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service
from app.services.image_service import ImageService, get_image_service
from app.services.concept_service import ConceptService, get_concept_service
from app.utils.rate_limiting import apply_rate_limit

# Configure logging
logger = logging.getLogger("concept_storage_api")

router = APIRouter()


@router.post("/store", response_model=GenerationResponse)
async def generate_and_store_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service)
):
    """
    Generate a concept based on user prompt and store it in the database.
    
    Args:
        request: User prompt request with logo and theme descriptions
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        concept_service: Service for generating concepts
        session_service: Service for managing sessions
        image_service: Service for handling images
        storage_service: Service for storing concepts
        
    Returns:
        Generated concept with image URL and color palettes
    """
    # Apply rate limit
    await apply_rate_limit(req, "/storage/store", "10/month")
    
    try:
        # Get or create session
        session_id, is_new_session = await session_service.get_or_create_session(response)
        
        # Generate base image and store it in Supabase Storage
        base_image_path, base_image_url = await image_service.generate_and_store_image(
            request.logo_description,
            session_id
        )
        
        if not base_image_path or not base_image_url:
            raise HTTPException(status_code=500, detail="Failed to generate or store image")
        
        # Generate color palettes
        # First get color palettes from JigsawStack
        raw_palettes = await concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await image_service.create_palette_variations(
            base_image_path,
            raw_palettes,
            session_id
        )
        
        # Store concept in Supabase database
        stored_concept = await storage_service.store_concept(
            session_id=session_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            base_image_path=base_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise HTTPException(status_code=500, detail="Failed to store concept")
        
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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    req: Request,
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Get recent concepts for the current session.
    
    Args:
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        session_service: Service for managing sessions
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
        
    Returns:
        List of recent concepts
    """
    # Apply rate limit - higher limits for read operations
    await apply_rate_limit(req, "/storage/recent", "30/minute", "minute")
    
    try:
        # Get or create session
        session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
        
        # Return empty list for new sessions
        if is_new_session:
            return []
        
        # Get recent concepts with public image URLs
        return await storage_service.get_recent_concepts(session_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    response: Response,
    req: Request,
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Get detailed information about a specific concept.
    
    Args:
        concept_id: ID of the concept to retrieve
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        session_service: Service for managing sessions
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
        
    Returns:
        Detailed concept information
    """
    # Apply rate limit - higher limits for read operations
    await apply_rate_limit(req, f"/storage/concept/{concept_id}", "30/minute", "minute")
    
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # Get concept detail
        concept = await storage_service.get_concept_detail(concept_id, session_id)
        
        if not concept:
            raise HTTPException(status_code=404, detail="Concept not found")
        
        return concept
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 