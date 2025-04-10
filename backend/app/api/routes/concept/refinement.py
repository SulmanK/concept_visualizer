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
    Refine an existing concept (background task).
    
    This endpoint creates a background task to refine an existing concept.
    It returns a task ID that can be used to check the status of the task.
    
    Args:
        request: Refinement request containing original image URL and refinement prompt
        background_tasks: FastAPI background tasks
        response: FastAPI response object
        req: FastAPI request object
        commons: Common dependencies
        
    Returns:
        TaskResponse: Task details for the created background task
        
    Raises:
        ValidationError: If the request is invalid
        ResourceNotFoundError: If the original image does not exist
        ServiceUnavailableError: If task creation fails
    """
    try:
        # Get dependencies from commons
        user_id = commons.user_id
        
        # Check rate limits for concept refinement
        await apply_rate_limit(user_id, "/concepts/refine", "10/month",
                        headers=response.headers, status_only=False, req=req)
        
        # Create metadata for the task
        task_metadata = {
            "original_image_url": request.original_image_url,
            "refinement_prompt": request.refinement_prompt,
            "logo_description": request.logo_description or "",
            "theme_description": request.theme_description or ""
        }
        
        # Check for existing active tasks for this user
        try:
            # Look for any pending or processing tasks of type concept_refinement
            active_tasks = await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status="pending"
            )
            active_tasks.extend(await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status="processing"
            ))
            
            # Filter for concept_refinement tasks
            active_refinement_tasks = [task for task in active_tasks if task.get("type") == "concept_refinement"]
            
            if active_refinement_tasks:
                # Return the existing task instead of creating a new one
                existing_task = active_refinement_tasks[0]
                logger.info(f"Found existing active task {mask_id(existing_task['id'])} for user {mask_id(user_id)}")
                
                # Return HTTP 409 Conflict with details of the existing task
                response.status_code = status.HTTP_409_CONFLICT
                return TaskResponse(
                    task_id=existing_task["id"],
                    status=existing_task["status"],
                    message="A concept refinement task is already in progress",
                    type="concept_refinement",
                    created_at=existing_task.get("created_at"),
                    updated_at=existing_task.get("updated_at"),
                    metadata=existing_task.get("metadata", task_metadata)
                )
        except Exception as e:
            # Log the error but continue with creating a new task
            logger.warning(f"Error checking for existing tasks: {str(e)}")
        
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
                logo_description=request.logo_description or "",
                theme_description=request.theme_description or "",
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
            
    except (ValidationError, ResourceNotFoundError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error refining concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error refining concept: {str(e)}")


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
        # Update task status to processing and update the timestamp
        await task_service.update_task_status(
            task_id=task_id,
            status="processing"
        )
        
        logger.info(f"Starting background refinement task {mask_id(task_id)} for user {mask_id(user_id)}")
        
        # Refine and store the image
        try:
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
                    error_message="Failed to refine or store image: No image data returned from service"
                )
                return
        except Exception as e:
            error_message = f"Failed to refine or store image: {str(e)}"
            logger.error(f"Task {mask_id(task_id)}: {error_message}")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_message
            )
            return
            
        # Generate color palettes
        try:
            raw_palettes = await concept_service.generate_color_palettes(
                theme_description=f"{theme_description} {refinement_prompt}",
                logo_description=logo_description
            )
        except Exception as e:
            error_message = f"Failed to generate color palettes: {str(e)}"
            logger.error(f"Task {mask_id(task_id)}: {error_message}")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_message
            )
            return
        
        # Apply color palettes to create variations and store in Supabase Storage
        try:
            palette_variations = await image_service.create_palette_variations(
                refined_image_path,
                raw_palettes,
                user_id
            )
        except Exception as e:
            error_message = f"Failed to create color variations: {str(e)}"
            logger.error(f"Task {mask_id(task_id)}: {error_message}")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_message
            )
            return
            
        # Store concept in Supabase database
        try:
            stored_concept = await storage_service.store_concept({
                "user_id": user_id,
                "logo_description": f"{logo_description} (Refined: {refinement_prompt})",
                "theme_description": theme_description,
                "image_path": refined_image_path,
                "image_url": refined_image_url,
                "color_palettes": palette_variations,
                "is_anonymous": True,
                "original_image_url": original_image_url,
                "refinement_prompt": refinement_prompt
            })
            
            if not stored_concept:
                logger.error(f"Task {mask_id(task_id)}: Failed to store refined concept")
                await task_service.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message="Failed to store refined concept: No concept ID returned from storage service"
                )
                return
        except Exception as e:
            error_message = f"Failed to store refined concept in database: {str(e)}"
            logger.error(f"Task {mask_id(task_id)}: {error_message}")
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_message
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
            
            # Increment rate limit for refinement endpoint
            await apply_rate_limit(user_id, "/concepts/refine", "10/month")
            
            logger.info(f"Task {mask_id(task_id)}: Incremented rate limit after successful task completion")
        except Exception as rate_limit_error:
            logger.error(f"Task {mask_id(task_id)}: Failed to increment rate limit: {str(rate_limit_error)}")
            # Don't raise here, as the task already completed successfully
        
        logger.info(f"Task {mask_id(task_id)}: Successfully completed concept refinement")
        
    except Exception as e:
        error_message = f"Unexpected error in concept refinement background task: {str(e)}"
        logger.error(f"Task {mask_id(task_id)}: {error_message}")
        logger.debug(f"Task {mask_id(task_id)}: Exception traceback: {traceback.format_exc()}")
        
        # Update task status to failed
        try:
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_message
            )
        except Exception as update_error:
            logger.error(f"Failed to update task status: {str(update_error)}") 