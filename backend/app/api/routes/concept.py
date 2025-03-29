"""
Concept generation and refinement endpoints.

This module provides endpoints for generating and refining visual concepts.
"""

from fastapi import APIRouter, Depends, HTTPException, Response, Cookie
from typing import Optional, List

from backend.app.models.request import PromptRequest, RefinementRequest
from backend.app.models.response import GenerationResponse, PaletteVariation
from backend.app.services.concept_service import ConceptService, get_concept_service
from backend.app.services.session_service import SessionService, get_session_service
from backend.app.services.image_service import ImageService, get_image_service
from backend.app.services.concept_storage_service import ConceptStorageService, get_concept_storage_service

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
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
        raw_palettes = await concept_service.generate_color_palettes(request.theme_description)
        
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
    num_palettes: int = 3,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Generate a new visual concept with multiple color palette variations,
    each with its own distinct image.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object for setting cookies
        num_palettes: Number of distinct palette variations to generate (default: 3)
        concept_service: The concept generation service
        session_service: Service for managing sessions
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The generated concept with multiple variations
    
    Raises:
        HTTPException: If there was an error during generation
    """
    try:
        # Get or create session
        session_id, _ = await session_service.get_or_create_session(response, session_id)
        
        # Generate concept with multiple palette variations
        palettes, variation_images = await concept_service.generate_concept_with_palettes(
            request.logo_description,
            request.theme_description,
            num_palettes
        )
        
        if not variation_images:
            raise HTTPException(status_code=500, detail="Failed to generate images for any palette")
        
        # Convert URLs to storage paths (for database storage)
        palette_for_storage = []
        for variation in variation_images:
            # In a real implementation, you'd need to download the image and upload to Supabase
            # For this example, we'll assume the image_url is already a valid path
            image_url = variation["image_url"]
            image_path = f"{session_id}/{image_url.split('/')[-1]}" 
            
            palette_for_storage.append({
                "name": variation["name"],
                "colors": variation["colors"],
                "description": variation.get("description", ""),
                "image_path": image_path,
                "image_url": image_url
            })
        
        # Store the first image as the "base" concept
        base_variation = variation_images[0]
        base_image_path = f"{session_id}/{base_variation['image_url'].split('/')[-1]}"
        
        # Store concept in Supabase
        stored_concept = await storage_service.store_concept(
            session_id=session_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            base_image_path=base_image_path,
            color_palettes=palette_for_storage
        )
        
        if not stored_concept:
            raise HTTPException(status_code=500, detail="Failed to store concept")
        
        # Return generation response with all variations
        return GenerationResponse(
            prompt_id=stored_concept["id"],
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            created_at=stored_concept.get("created_at", ""),
            # Default image is the first variation
            image_url=variation_images[0]["image_url"],
            # Include all variations
            variations=[
                PaletteVariation(
                    name=v["name"],
                    colors=v["colors"],
                    description=v.get("description", ""),
                    image_url=v["image_url"]
                )
                for v in variation_images
            ]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine", response_model=GenerationResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """
    Refine an existing concept based on the provided request and store it.
    
    Args:
        request: The refinement request with original image and new instructions
        response: FastAPI response object for setting cookies
        concept_service: The concept generation service
        session_service: Service for managing sessions
        image_service: Service for image operations
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
    
    Returns:
        GenerationResponse: The refined concept data
    
    Raises:
        HTTPException: If there was an error refining the concept
    """
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
            f"{theme_desc} {request.refinement_prompt}"
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