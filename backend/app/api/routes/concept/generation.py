"""
Concept generation endpoints.

This module provides endpoints for generating visual concepts.
"""

import logging
import traceback
import uuid
from typing import Optional, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, Request, BackgroundTasks, status
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.models.request import PromptRequest
from app.models.response import GenerationResponse, PaletteVariation, TaskResponse
from app.utils.api_limits import apply_rate_limit, apply_multiple_rate_limits
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
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError, TaskNotFoundError
from app.core.config import settings
from app.utils.api_limits.decorators import store_rate_limit_info
from app.utils.api_limits.endpoints import apply_rate_limit, apply_multiple_rate_limits
from app.utils.security.mask import mask_id
from app.services.task.service import TaskError

# Configure logging
logger = logging.getLogger("concept_generation_api")

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """
    Generate a new visual concept based on the provided prompt and store it.
    
    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services
    
    Returns:
        GenerationResponse: The generated concept data
    
    Raises:
        ServiceUnavailableError: If there was an error generating the concept
        ValidationError: If the request validation fails
        HTTPException: If rate limit is exceeded (429) or user is not authenticated (401)
    """
    # Apply both generation and storage rate limits - this will raise an HTTPException if limit is exceeded
    await apply_multiple_rate_limits(req, [
        {"endpoint": "/concepts/generate", "rate_limit": "10/month"},
        {"endpoint": "/concepts/store", "rate_limit": "10/month"}
    ])
    
    # Store rate limit info after the actual rate limiting
    try:
        user_id = None
        if hasattr(req, "state") and hasattr(req.state, "user") and req.state.user:
            user_id = req.state.user.get("id")
        
        if user_id:
            from app.core.limiter import check_rate_limit
            
            # Get full user_id format
            full_user_id = f"user:{user_id}"
            
            # Use the lower of the two limits for the headers
            generation_status = check_rate_limit(
                user_id=full_user_id, 
                endpoint="/concepts/generate",
                limit="10/month",
                check_only=True
            )
            
            storage_status = check_rate_limit(
                user_id=full_user_id, 
                endpoint="/concepts/store",
                limit="10/month",
                check_only=True
            )
            
            # Use the status with fewer remaining calls
            if generation_status.get("remaining", 0) <= storage_status.get("remaining", 0):
                limit_status = generation_status
                endpoint = "/concepts/generate"
            else:
                limit_status = storage_status
                endpoint = "/concepts/store"
            
            # Store in request.state for the middleware to use
            req.state.limiter_info = {
                "limit": limit_status.get("limit", 0),
                "remaining": limit_status.get("remaining", 0),
                "reset": limit_status.get("reset_at", 0)
            }
            
            logger.debug(
                f"Stored rate limit info for {endpoint} after increment: "
                f"remaining={limit_status.get('remaining', 0)}"
            )
    except Exception as e:
        logger.error(f"Error storing post-increment rate limit info: {str(e)}")
    
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
        
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Generate base image and store it in Supabase Storage
        # The new API returns (image_path, image_url)
        image_path, image_url = await commons.image_service.generate_and_store_image(
            request.logo_description,
            user_id  # Use user_id instead of session_id
        )
        
        if not image_path or not image_url:
            raise ServiceUnavailableError(detail="Failed to generate or store image")
        
        # Generate color palettes
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        palette_variations = await commons.image_service.create_palette_variations(
            image_path,
            raw_palettes,
            user_id  # Use user_id instead of session_id
        )
        
        # Store concept in Supabase database
        stored_concept = await commons.storage_service.store_concept({
            "user_id": user_id,
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
            "image_path": image_path,
            "image_url": image_url,
            "color_palettes": palette_variations,
            "is_anonymous": True
        })
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store concept")
        
        # Handle case where storage service returns just the ID string
        concept_id = stored_concept
        created_at = datetime.now().isoformat()
        if isinstance(stored_concept, dict):
            concept_id = stored_concept.get("id", stored_concept)
            created_at = stored_concept.get("created_at", created_at)
            
        # Return the combined response
        # The response model now has validators that handle URL conversion
        return GenerationResponse(
            prompt_id=concept_id,
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            created_at=created_at,
            image_url=image_url,
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


@router.post("/generate-with-palettes", response_model=TaskResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    commons: CommonDependencies = Depends(),
):
    """
    Generate concept with color palettes (background task).
    
    This endpoint creates a background task to generate a concept with color palettes.
    It returns a task ID that can be used to check the status of the task.
    
    Args:
        request: Prompt request containing logo and theme descriptions
        background_tasks: FastAPI background tasks
        response: FastAPI response object
        req: FastAPI request object
        num_palettes: Number of color palettes to generate
        commons: Common dependencies
        
    Returns:
        TaskResponse: Task details for the created background task
        
    Raises:
        ValidationError: If the request is invalid
        ServiceUnavailableError: If task creation fails
    """
    try:
        # Get dependencies from commons
        user_id = commons.user_id
        
        # Check rate limits for concept generation
        await apply_rate_limit(req, "/concepts/generate-with-palettes", "10/month")
        
        # Check rate limits for concept storage
        await apply_rate_limit(req, "/concepts/store", "10/month")
        
        # Create metadata for the task
        task_metadata = {
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
            "num_palettes": num_palettes
        }
        
        # Check for existing active tasks for this user
        try:
            # Look for any pending or processing tasks of type concept_generation
            active_tasks = await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status="pending"
            )
            active_tasks.extend(await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status="processing"
            ))
            
            # Filter for concept_generation tasks
            active_generation_tasks = [task for task in active_tasks if task.get("type") == "concept_generation"]
            
            if active_generation_tasks:
                # Return the existing task instead of creating a new one
                existing_task = active_generation_tasks[0]
                logger.info(f"Found existing active task {mask_id(existing_task['id'])} for user {mask_id(user_id)}")
                
                # Return HTTP 409 Conflict with details of the existing task
                response.status_code = status.HTTP_409_CONFLICT
                return TaskResponse(
                    task_id=existing_task["id"],
                    status=existing_task["status"],
                    message="A concept generation task is already in progress",
                    type="concept_generation",
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
                task_type="concept_generation",
                metadata=task_metadata
            )
            
            task_id = task["id"]
            logger.info(f"Created task {mask_id(task_id)} for concept generation")
            
            # Add the generation task to background tasks
            background_tasks.add_task(
                generate_concept_background_task,
                task_id=task_id,
                logo_description=request.logo_description,
                theme_description=request.theme_description,
                user_id=user_id,
                num_palettes=num_palettes,
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
                message="Concept generation task created and queued for processing",
                type="concept_generation",
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
        logger.error(f"Error generating concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error generating concept: {str(e)}")


async def generate_concept_background_task(
    task_id: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    num_palettes: int,
    image_service: ImageServiceInterface,
    concept_service: ConceptServiceInterface,
    storage_service: StorageServiceInterface,
    task_service: TaskServiceInterface
):
    """
    Background task function to generate a concept with palettes.
    
    Args:
        task_id: Unique ID for tracking this task
        logo_description: Description of the logo to generate
        theme_description: Description of the theme/style
        user_id: User ID for storage
        num_palettes: Number of color palettes to generate
        image_service: Service for image generation and processing
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
        
        logger.info(f"Starting background generation task {mask_id(task_id)} for user {mask_id(user_id)}")
        
        # Generate base image and store it in Supabase Storage
        try:
            image_path, image_url = await image_service.generate_and_store_image(
                logo_description,
                user_id
            )
            
            if not image_path or not image_url:
                logger.error(f"Task {mask_id(task_id)}: Failed to generate or store image")
                await task_service.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message="Failed to generate or store base image: No image data returned from service"
                )
                return
        except Exception as e:
            error_message = f"Failed to generate or store base image: {str(e)}"
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
                theme_description=theme_description,
                logo_description=logo_description,
                num_palettes=num_palettes
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
                image_path,
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
                "logo_description": logo_description,
                "theme_description": theme_description,
                "image_path": image_path,
                "image_url": image_url,
                "color_palettes": palette_variations,
                "is_anonymous": True
            })
            
            if not stored_concept:
                logger.error(f"Task {mask_id(task_id)}: Failed to store concept")
                await task_service.update_task_status(
                    task_id=task_id,
                    status="failed",
                    error_message="Failed to store concept: No concept ID returned from storage service"
                )
                return
        except Exception as e:
            error_message = f"Failed to store concept in database: {str(e)}"
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
        
        # Now that the task has successfully completed, increment the rate limits
        try:
            # Use check_rate_limit directly, which doesn't require a full request object
            from app.core.limiter import check_rate_limit
            
            # Format user_id for the rate limit checks
            full_user_id = f"user:{user_id}"
            
            # Increment rate limits for both endpoints (use check_only=False to actually increment)
            check_rate_limit(
                user_id=full_user_id, 
                endpoint="/concepts/generate-with-palettes",
                limit="10/month",
                check_only=False
            )
            
            check_rate_limit(
                user_id=full_user_id, 
                endpoint="/concepts/store",
                limit="10/month",
                check_only=False
            )
            
            logger.info(f"Task {mask_id(task_id)}: Incremented rate limits after successful task completion")
        except Exception as rate_limit_error:
            logger.error(f"Task {mask_id(task_id)}: Failed to increment rate limits: {str(rate_limit_error)}")
            # Don't raise here, as the task already completed successfully
        
        logger.info(f"Task {mask_id(task_id)}: Successfully completed concept generation")
        
    except Exception as e:
        error_message = f"Unexpected error in concept generation background task: {str(e)}"
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


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    commons: CommonDependencies = Depends(),
):
    """
    Check the status of a background concept generation or refinement task.
    
    Args:
        task_id: The ID of the task to check
        commons: Common dependencies including services
    
    Returns:
        TaskResponse: The current status of the task
    
    Raises:
        ResourceNotFoundError: If the task does not exist
        ServiceUnavailableError: If there was an error retrieving the task status
    """
    try:
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        # Get task from the task service
        try:
            task = await commons.task_service.get_task(task_id, user_id)
            
            # Convert task data to response model
            return TaskResponse(
                task_id=task["id"],
                status=task["status"],
                message=f"Task is {task['status']}",
                type=task.get("type"),
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at"),
                result_id=task.get("result_id"),
                error=task.get("error_message"),
                metadata=task.get("metadata", {})
            )
        except TaskNotFoundError:
            # If not found in task service, return not found
            raise ResourceNotFoundError(detail=f"Task with ID {mask_id(task_id)} not found")
        
    except ResourceNotFoundError:
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error checking task status: {str(e)}") 