"""
Concept generation and refinement endpoints.

This module provides endpoints for generating and refining visual concepts.
"""

import logging
import traceback
import uuid
from typing import Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request
from pydantic import ValidationError
from slowapi.util import get_remote_address

from backend.app.models.request import PromptRequest, RefinementRequest
from backend.app.models.response import GenerationResponse, PaletteVariation
from backend.app.services.concept_service import ConceptService, get_concept_service
from backend.app.services.session_service import SessionService, get_session_service
from backend.app.services.image_service import ImageService, get_image_service
from backend.app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service

# Configure logging
logger = logging.getLogger("concept_api")

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Generate a new visual concept based on the provided prompt and store it.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        concept_service: The concept generation service
        session_service: Service for managing sessions
        image_service: Service for image operations
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The generated concept data
    
    Raises:
        HTTPException: If there was an error generating the concept
    """
    # Apply rate limit
    limiter = req.app.state.limiter
    try:
        # Use the rate limit function properly with a specific key
        key_func = get_remote_address
        rate_limit = "10/month"
        user_id = key_func(req)
        
        # Log the rate limiting attempt
        logger.info(f"Applying rate limit '{rate_limit}' to user {user_id}")
        
        # Try-except block for the rate limit to handle connection issues
        try:
            limiter.limit(rate_limit)(key_func)(req)
            logger.info("SlowAPI rate limit applied successfully")
        except Exception as e:
            logger.error(f"SlowAPI rate limiting error: {str(e)}")
        
        # Use our custom direct Redis tracking as a more reliable method
        if hasattr(limiter, 'increment_rate_limit'):
            success = limiter.increment_rate_limit(
                user_id=user_id,
                endpoint="/api/concept/generate",
                period="month"
            )
            if success:
                logger.info("Rate limit counter incremented successfully in Redis")
            else:
                logger.warning("Failed to increment rate limit counter in Redis")
        
        logger.info("Rate limit tracking completed")
    except Exception as e:
        logger.error(f"Error applying rate limit: {str(e)}")
        # Continue even if rate limiting fails
    
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # Generate base image and store it in Supabase Storage
        base_image_path, base_image_url = await image_service.generate_and_store_image(
            request.logo_description,
            session_id
        )
        
        if not base_image_path or not base_image_url:
            raise HTTPException(status_code=500, detail="Failed to generate or store image")
        
        # Generate color palettes
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
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            created_at=stored_concept.get("created_at", ""),
            image_url=base_image_url,
            variations=[
                PaletteVariation(
                    name=p["name"],
                    colors=p["colors"],
                    description=p.get("description", ""),
                    image_url=p["image_url"]
                ) 
                for p in palette_variations
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-with-palettes", response_model=GenerationResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Generate a new visual concept with multiple color palette variations,
    using a single base image and OpenCV color transformation.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        num_palettes: Number of distinct palette variations to generate (default: 7)
        concept_service: The concept generation service
        session_service: Service for managing sessions
        image_service: Service for image handling
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The generated concept with multiple variations
    
    Raises:
        HTTPException: If there was an error during generation
    """
    # Apply rate limit
    limiter = req.app.state.limiter
    try:
        # Use the rate limit function properly with a specific key
        key_func = get_remote_address
        rate_limit = "10/month"
        user_id = key_func(req)
        
        # Log the rate limiting attempt
        logger.info(f"Applying rate limit '{rate_limit}' to user {user_id}")
        
        # Try-except block for the rate limit to handle connection issues
        try:
            limiter.limit(rate_limit)(key_func)(req)
            logger.info("SlowAPI rate limit applied successfully")
        except Exception as e:
            logger.error(f"SlowAPI rate limiting error: {str(e)}")
        
        # Use our custom direct Redis tracking as a more reliable method
        if hasattr(limiter, 'increment_rate_limit'):
            success = limiter.increment_rate_limit(
                user_id=user_id,
                endpoint="/api/concept/generate-with-palettes",
                period="month"
            )
            if success:
                logger.info("Rate limit counter incremented successfully in Redis")
            else:
                logger.warning("Failed to increment rate limit counter in Redis")
        
        logger.info("Rate limit tracking completed")
    except Exception as e:
        logger.error(f"Error applying rate limit: {str(e)}")
        # Continue even if rate limiting fails
    
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # First, generate color palettes based on the theme description
        palettes = await concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description,
            num_palettes=num_palettes
        )
        
        if not palettes:
            raise HTTPException(status_code=500, detail="Failed to generate color palettes")
        
        # Generate a single high-quality base image
        logger.info(f"Generating base image for concept with prompt: {request.logo_description}")
        base_image_path, base_image_url = await image_service.generate_and_store_image(
            request.logo_description,
            session_id
        )
        
        if not base_image_path or not base_image_url:
            raise HTTPException(status_code=500, detail="Failed to generate or store base image")
        
        # Apply different color palettes using OpenCV transformation
        logger.info(f"Creating {len(palettes)} color variations using OpenCV")
        palette_variations = []
        
        for palette in palettes:
            # Apply each palette to the base image using the new OpenCV method
            from backend.app.core.supabase import get_supabase_client
            supabase_client = get_supabase_client()
            
            # Transform the image with the current palette
            palette_image_path = await supabase_client.apply_color_palette(
                base_image_path,
                palette["colors"],
                session_id
            )
            
            if palette_image_path:
                # Get public URL
                palette_image_url = supabase_client.get_image_url(
                    palette_image_path, 
                    "palette-images"
                )
                
                # Create variation with URL for response
                variation = {
                    "name": palette["name"],
                    "colors": palette["colors"],
                    "description": palette.get("description", ""),
                    "image_path": palette_image_path,
                    "image_url": palette_image_url
                }
                palette_variations.append(variation)
                logger.info(f"Created palette variation: {palette['name']}")
            else:
                logger.error(f"Failed to create variation for palette: {palette['name']}")
        
        if not palette_variations:
            raise HTTPException(status_code=500, detail="Failed to create any color variations")
        
        # Store concept in Supabase
        stored_concept = await storage_service.store_concept(
            session_id=session_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            base_image_path=base_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise HTTPException(status_code=500, detail="Failed to store concept")
        
        # Return generation response with all variations
        return GenerationResponse(
            prompt_id=stored_concept["id"],
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            created_at=stored_concept.get("created_at", ""),
            # Default image is the base image
            image_url=base_image_url,
            # Include all variations
            variations=[
                PaletteVariation(
                    name=v["name"],
                    colors=v["colors"],
                    description=v.get("description", ""),
                    image_url=v["image_url"]
                )
                for v in palette_variations
            ]
        )
    except Exception as e:
        logger.error(f"Error in generate_concept_with_palettes: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


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
    limiter = req.app.state.limiter
    try:
        # Use the rate limit function properly with a specific key
        key_func = get_remote_address
        rate_limit = "10/hour"
        user_id = key_func(req)
        
        # Log the rate limiting attempt
        logger.info(f"Applying rate limit '{rate_limit}' to user {user_id}")
        
        # Try-except block for the rate limit to handle connection issues
        try:
            limiter.limit(rate_limit)(key_func)(req)
            logger.info("SlowAPI rate limit applied successfully")
        except Exception as e:
            logger.error(f"SlowAPI rate limiting error: {str(e)}")
        
        # Use our custom direct Redis tracking as a more reliable method
        if hasattr(limiter, 'increment_rate_limit'):
            success = limiter.increment_rate_limit(
                user_id=user_id,
                endpoint="/api/concept/refine",
                period="hour"
            )
            if success:
                logger.info("Rate limit counter incremented successfully in Redis")
            else:
                logger.warning("Failed to increment rate limit counter in Redis")
        
        logger.info("Rate limit tracking completed")
    except Exception as e:
        logger.error(f"Error applying rate limit: {str(e)}")
        # Continue even if rate limiting fails
    
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # Refine image and store it in Supabase Storage
        logo_desc = request.logo_description or "the existing logo"
        theme_desc = request.theme_description or "the existing theme"
        
        # Refine and store the image
        refined_image_path, refined_image_url = await image_service.refine_and_store_image(
            prompt=f"Refine this logo design: {logo_desc}. Theme/style: {theme_desc}. "
                  f"Refinement instructions: {request.refinement_prompt}.",
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