"""
Concept refinement endpoints.

This module provides endpoints for refining existing visual concepts.
"""

import logging
import traceback
import uuid
from typing import Optional, Dict, Any

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
    StorageServiceInterface,
    TaskServiceInterface
)
from app.api.dependencies import CommonDependencies
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError
from app.utils.security.mask import mask_id
from app.services.task.service import TaskError

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
    # Check rate limit without incrementing
    try:
        user_id = None
        if hasattr(req, "state") and hasattr(req.state, "user") and req.state.user:
            user_id = req.state.user.get("id")
        
        if user_id:
            from app.core.limiter import check_rate_limit
            
            # Get full user_id format
            full_user_id = f"user:{user_id}"
            
            # Only check the limit without incrementing
            rate_status = check_rate_limit(
                user_id=full_user_id, 
                endpoint="/concepts/refine",
                limit="10/hour",
                check_only=True
            )
            
            # Check if over the limit
            if rate_status.get("remaining", 0) <= 0:
                logger.info(f"Rate limit exceeded for /concepts/refine: {rate_status}")
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Maximum {rate_status.get('limit')} requests per hour"
                )
            
            # Store in request.state for the middleware to use
            req.state.limiter_info = {
                "limit": rate_status.get("limit", 0),
                "remaining": rate_status.get("remaining", 0),
                "reset": rate_status.get("reset_at", 0)
            }
            
            logger.debug(
                f"Stored rate limit info for /concepts/refine: "
                f"remaining={rate_status.get('remaining', 0)}"
            )
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error checking rate limit: {str(e)}")
    
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
            
        # Check if user already has pending or processing tasks
        user_tasks = await commons.task_service.get_tasks_by_user(
            user_id=user_id,
            status="pending",
            limit=1
        )
        
        if user_tasks and len(user_tasks) > 0:
            logger.info(f"User {mask_id(user_id)} already has a pending task: {mask_id(user_tasks[0]['id'])}")
            return TaskResponse(
                task_id=user_tasks[0]["id"],
                status=user_tasks[0]["status"],
                message="You already have a task in progress. Please wait for it to complete.",
                type=user_tasks[0].get("type"),
                created_at=user_tasks[0].get("created_at"),
                metadata=user_tasks[0].get("metadata", {})
            )
            
        user_tasks = await commons.task_service.get_tasks_by_user(
            user_id=user_id,
            status="processing",
            limit=1
        )
        
        if user_tasks and len(user_tasks) > 0:
            logger.info(f"User {mask_id(user_id)} already has a processing task: {mask_id(user_tasks[0]['id'])}")
            return TaskResponse(
                task_id=user_tasks[0]["id"],
                status=user_tasks[0]["status"],
                message="You already have a task in progress. Please wait for it to complete.",
                type=user_tasks[0].get("type"),
                created_at=user_tasks[0].get("created_at"),
                metadata=user_tasks[0].get("metadata", {})
            )
        
        # Create a task record
        task_metadata = {
            "refinement_prompt": request.refinement_prompt,
            "original_image_url": request.original_image_url,
            "logo_description": request.logo_description,
            "theme_description": request.theme_description
        }
        
        try:
            task = await commons.task_service.create_task(
                user_id=user_id,
                task_type="concept_refinement",
                metadata=task_metadata
            )
            
            task_id = task["id"]
            logger.info(f"Created task {mask_id(task_id)} for concept refinement")
            
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
                storage_service=commons.storage_service,
                task_service=commons.task_service
            )
            
            # Set response status to 202 Accepted
            response.status_code = status.HTTP_202_ACCEPTED
            
            # Return the task information
            return TaskResponse(
                task_id=task_id,
                status="pending",
                message="Concept refinement task created and queued for processing",
                type="concept_refinement",
                created_at=task.get("created_at"),
                metadata=task_metadata
            )
        
        except TaskError as e:
            logger.error(f"Error creating task: {str(e)}")
            raise ServiceUnavailableError(detail=f"Error creating task: {str(e)}")
            
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
    storage_service: StorageServiceInterface,
    task_service: TaskServiceInterface
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
        task_service: Service for updating task status
    """
    try:
        # Update task status to processing
        await task_service.update_task_status(
            task_id=task_id,
            status="processing"
        )
        
        logger.info(f"Starting background refinement task {mask_id(task_id)} for user {mask_id(user_id)}")
        
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
            logger.error(f"Task {mask_id(task_id)}: Failed to refine or store image")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message="Failed to refine or store image"
            )
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
            "is_anonymous": True
        })
        
        if not stored_concept:
            logger.error(f"Task {mask_id(task_id)}: Failed to store refined concept")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message="Failed to store refined concept"
            )
            return
        
        # Update task status to completed with result ID
        concept_id = stored_concept
        if isinstance(stored_concept, dict):
            concept_id = stored_concept.get("id", stored_concept)
            
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            result_id=concept_id
        )
        
        # Now that the task has successfully completed, increment the rate limit
        try:
            from app.core.limiter import apply_rate_limit
            
            # Increment rate limit
            await apply_rate_limit(user_id, "/concepts/refine", "10/hour")
            
            logger.info(f"Task {mask_id(task_id)}: Incremented rate limit after successful task completion")
        except Exception as rate_limit_error:
            logger.error(f"Task {mask_id(task_id)}: Failed to increment rate limit: {str(rate_limit_error)}")
            # Don't raise here, as the task already completed successfully
        
        logger.info(f"Task {mask_id(task_id)}: Successfully completed concept refinement")
        
    except Exception as e:
        logger.error(f"Task {mask_id(task_id)}: Error in background task: {str(e)}")
        logger.debug(f"Task {mask_id(task_id)}: Exception traceback: {traceback.format_exc()}")
        
        # Update task status to failed
        try:
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=str(e)
            )
        except Exception as update_error:
            logger.error(f"Failed to update task status: {str(update_error)}") 