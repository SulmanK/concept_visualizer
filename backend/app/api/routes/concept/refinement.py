"""
Concept refinement endpoints.

This module provides endpoints for refining existing visual concepts.
"""

import logging
import traceback
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Response, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.request import RefinementRequest
from app.models.response import GenerationResponse, PaletteVariation, TaskResponse
from app.utils.api_limits import apply_rate_limit
from app.services.concept import get_concept_service
from app.services.image import get_image_service
from app.services.storage import get_concept_storage_service
from app.services.interfaces import (
    ConceptServiceInterface,
    ImageServiceInterface,
    StorageServiceInterface
)
from app.api.dependencies import CommonDependencies
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError

# Configure logging
logger = logging.getLogger("concept_refinement_api")

router = APIRouter()


@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """
    Refine an existing concept based on user feedback.
    
    This endpoint starts the refinement process in the background and immediately
    returns a task ID. The client can check the status of the task using the task ID.
    
    Args:
        request: The refinement request containing feedback and concept ID
        background_tasks: FastAPI background tasks to run after response
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including all services
    
    Returns:
        TaskResponse: The task ID to check the status of the refinement
    
    Raises:
        ServiceUnavailableError: If there was an error refining the concept
        ValidationError: If the request validation fails
        HTTPException: If user is not authenticated (401)
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
        
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Generate a unique task ID
        task_id = str(uuid.uuid4())
        
        # Add the refinement task to background tasks
        background_tasks.add_task(
            refine_concept_background_task,
            task_id=task_id,
            refinement_prompt=request.refinement_prompt,
            original_image_url=request.original_image_url,
            logo_description=request.logo_description or "the existing logo",
            theme_description=request.theme_description or "the existing theme",
            user_id=user_id,
            image_service=commons.image_service,
            concept_service=commons.concept_service,
            storage_service=commons.storage_service
        )
        
        # Set response status to 202 Accepted
        response.status_code = status.HTTP_202_ACCEPTED
        
        # Return the task ID for the client to check status
        return TaskResponse(
            task_id=task_id,
            status="processing",
            message="Concept refinement started"
        )
        
    except (ValidationError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error starting concept refinement: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error starting concept refinement: {str(e)}")


async def refine_concept_background_task(
    task_id: str,
    refinement_prompt: str,
    original_image_url: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    image_service: ImageServiceInterface,
    concept_service: ConceptServiceInterface,
    storage_service: StorageServiceInterface
):
    """
    Background task function to refine a concept.
    
    Args:
        task_id: Unique ID for tracking this task
        refinement_prompt: Instructions for refinement
        original_image_url: URL of the image to refine
        logo_description: Description of the logo
        theme_description: Description of the theme/style
        user_id: User ID for storage
        image_service: Service for image refinement and processing
        concept_service: Service for concept generation
        storage_service: Service for storing concepts
    """
    try:
        logger.info(f"Starting background refinement task {task_id} for user {user_id}")
        
        # Refine and store the image
        refined_image_path, refined_image_url = await image_service.refine_and_store_image(
            prompt=(
                f"Refine this logo design: {logo_description}. Theme/style: {theme_description}. "
                f"Refinement instructions: {refinement_prompt}."
            ),
            original_image_url=original_image_url,
            user_id=user_id,
            strength=0.7  # Control how much to preserve original image
        )
        
        if not refined_image_path or not refined_image_url:
            logger.error(f"Task {task_id}: Failed to refine or store image")
            # TODO: Store task error status
            return
        
        # Generate color palettes
        raw_palettes = await concept_service.generate_color_palettes(
            theme_description=f"{theme_description} {refinement_prompt}",
            logo_description=logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await image_service.create_palette_variations(
            refined_image_path,
            raw_palettes,
            user_id
        )
        
        # Store concept in Supabase database
        stored_concept = await storage_service.store_concept({
            "user_id": user_id,
            "logo_description": f"{logo_description} - {refinement_prompt}",
            "theme_description": theme_description,
            "image_path": refined_image_path,
            "image_url": refined_image_url,
            "color_palettes": palette_variations,
            "is_anonymous": True,
            "task_id": task_id,
            "status": "completed"
        })
        
        if not stored_concept:
            logger.error(f"Task {task_id}: Failed to store refined concept")
            # TODO: Store task error status
            return
        
        logger.info(f"Task {task_id}: Successfully completed concept refinement")
        
        # TODO: Could implement a notification mechanism here to inform the frontend
        # e.g., WebSockets, polling endpoint, etc.
        
    except Exception as e:
        logger.error(f"Task {task_id}: Error in background task: {str(e)}")
        logger.debug(f"Task {task_id}: Exception traceback: {traceback.format_exc()}")
        # TODO: Store task error status 