"""
Concept generation endpoints.

This module provides endpoints for generating visual concepts.
"""

import logging
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, Request

from app.models.request import PromptRequest
from app.models.response import GenerationResponse, PaletteVariation
from app.services.concept_service import ConceptService, get_concept_service
from app.services.session_service import SessionService, get_session_service
from app.services.image_service import ImageService, get_image_service
from app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service
from app.utils.api_limits import apply_rate_limit

# Add new imports for dependencies and errors
from app.api.dependencies import CommonDependencies, get_or_create_session
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError

# Configure logging
logger = logging.getLogger("concept_generation_api")

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Generate a new visual concept based on the provided prompt and store it.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object for setting cookies
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The generated concept data
    
    Raises:
        ServiceUnavailableError: If there was an error generating the concept
        ValidationError: If the request validation fails
    """
    # Apply rate limit
    await apply_rate_limit(req, "/concepts/generate", "10/month")
    
    try:
        # Validate inputs
        if not request.logo_description or not request.theme_description:
            raise ValidationError(
                detail="Logo and theme descriptions are required",
                field_errors={
                    "logo_description": ["Field is required"] if not request.logo_description else [],
                    "theme_description": ["Field is required"] if not request.theme_description else []
                }
            )
        
        # Get or create session using the dependency
        session_id, _ = await get_or_create_session(
            response=response,
            session_service=commons.session_service,
            session_id=session_id
        )
        
        # Generate base image and store it in Supabase Storage
        base_image_path, base_image_url = await commons.image_service.generate_and_store_image(
            request.logo_description,
            session_id
        )
        
        if not base_image_path or not base_image_url:
            raise ServiceUnavailableError(detail="Failed to generate or store image")
        
        # Generate color palettes
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await commons.image_service.create_palette_variations(
            base_image_path,
            raw_palettes,
            session_id
        )
        
        # Store concept in Supabase database
        stored_concept = await commons.storage_service.store_concept(
            session_id=session_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            base_image_path=base_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store concept")
        
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
    except (ValidationError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error generating concept: {str(e)}")


@router.post("/generate-with-palettes", response_model=GenerationResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    commons: CommonDependencies = Depends(),
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
        commons: Common dependencies including all services
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The generated concept with multiple variations
    
    Raises:
        ServiceUnavailableError: If there was an error during generation
        ValidationError: If the request validation fails
    """
    # Apply rate limit
    await apply_rate_limit(req, "/concepts/generate-with-palettes", "10/month")
    
    try:
        # Validate inputs
        if not request.logo_description or not request.theme_description:
            raise ValidationError(
                detail="Logo and theme descriptions are required",
                field_errors={
                    "logo_description": ["Field is required"] if not request.logo_description else [],
                    "theme_description": ["Field is required"] if not request.theme_description else []
                }
            )
            
        # Validate num_palettes
        if num_palettes < 1 or num_palettes > 15:
            raise ValidationError(
                detail="Number of palettes must be between 1 and 15",
                field_errors={"num_palettes": ["Must be between 1 and 15"]}
            )
        
        # Get or create session
        session_id, _ = await get_or_create_session(
            response=response,
            session_service=commons.session_service,
            session_id=session_id
        )
        
        # First, generate color palettes based on the theme description
        palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description,
            num_palettes=num_palettes
        )
        
        if not palettes:
            raise ServiceUnavailableError(detail="Failed to generate color palettes")
        
        # Generate a single high-quality base image
        logger.info(f"Generating base image for concept with prompt: {request.logo_description}")
        base_image_path, base_image_url = await commons.image_service.generate_and_store_image(
            request.logo_description,
            session_id
        )
        
        if not base_image_path or not base_image_url:
            raise ServiceUnavailableError(detail="Failed to generate or store base image")
        
        # Apply different color palettes using OpenCV transformation
        logger.info(f"Creating {len(palettes)} color variations using OpenCV")
        palette_variations = []
        
        for palette in palettes:
            # Apply each palette to the base image using the new OpenCV method
            # Transform the image with the current palette
            palette_image_path = await commons.image_service.apply_color_palette(
                base_image_path,
                palette["colors"],
                session_id
            )
            
            if palette_image_path:
                # Get public URL
                palette_image_url = commons.image_service.get_image_url(
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
        
        if not palette_variations:
            raise ServiceUnavailableError(detail="Failed to create color variations")
        
        # Store the concept with all variations
        stored_concept = await commons.storage_service.store_concept(
            session_id=session_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            base_image_path=base_image_path,
            color_palettes=palette_variations
        )
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store concept")
            
        # Return the combined response
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
    except (ValidationError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error generating concept with palettes: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error generating concept with palettes: {str(e)}") 