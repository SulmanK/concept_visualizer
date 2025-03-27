"""
Concept generation and refinement endpoints.

This module provides endpoints for generating and refining visual concepts.
"""

from fastapi import APIRouter, Depends, HTTPException

from app.models.request import PromptRequest, RefinementRequest
from app.models.response import GenerationResponse
from app.services.concept_service import ConceptService, get_concept_service

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    service: ConceptService = Depends(get_concept_service),
):
    """
    Generate a new visual concept based on the provided prompt.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        service: The concept generation service
    
    Returns:
        GenerationResponse: The generated concept data
    
    Raises:
        HTTPException: If there was an error generating the concept
    """
    try:
        result = await service.generate_concept(
            request.logo_description, request.theme_description
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/refine", response_model=GenerationResponse)
async def refine_concept(
    request: RefinementRequest,
    service: ConceptService = Depends(get_concept_service),
):
    """
    Refine an existing concept based on the provided request.
    
    Args:
        request: The refinement request with original image and new instructions
        service: The concept generation service
    
    Returns:
        GenerationResponse: The refined concept data
    
    Raises:
        HTTPException: If there was an error refining the concept
    """
    try:
        result = await service.refine_concept(
            request.original_image_url,
            request.logo_description,
            request.theme_description,
            request.refinement_prompt,
            request.preserve_aspects,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 