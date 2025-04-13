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

from app.models.concept.request import PromptRequest
from app.models.concept.response import GenerationResponse, PaletteVariation
from app.models.task.response import TaskResponse
from app.utils.api_limits import apply_rate_limit, apply_multiple_rate_limits
from app.services.concept.interface import ConceptServiceInterface
from app.services.image.interface import ImageServiceInterface
from app.services.persistence.interface import ConceptPersistenceServiceInterface, StorageServiceInterface
from app.services.task.interface import TaskServiceInterface
from app.api.dependencies import CommonDependencies
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError, ValidationError, TaskNotFoundError
from app.core.config import settings
from app.core.constants import (
    TASK_STATUS_PENDING, 
    TASK_STATUS_PROCESSING, 
    TASK_STATUS_COMPLETED, 
    TASK_STATUS_FAILED, 
    TASK_TYPE_GENERATION
)
from app.utils.api_limits.decorators import store_rate_limit_info
from app.utils.api_limits.endpoints import apply_rate_limit, apply_multiple_rate_limits
from app.utils.security.mask import mask_id, mask_path
from app.services.task.service import TaskError
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.core.supabase.client import SupabaseClient

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
    # Process the request to extract user information
    commons.process_request(req)
    
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
        # Use ConceptService to generate the concept instead of ImageService
        concept_response = await commons.concept_service.generate_concept(
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            user_id=user_id,
            skip_persistence=True  # Skip persistence in the service, we'll handle it here
        )
        
        # Extract the image URL
        image_url = concept_response["image_url"]
        
        if not image_url:
            raise ServiceUnavailableError(detail="Failed to generate base concept")
        
        logger.info(f"Generated base concept with image URL: {mask_id(image_url)}")
        
        # Generate color palettes
        raw_palettes = await commons.concept_service.generate_color_palettes(
            theme_description=request.theme_description,
            logo_description=request.logo_description
        )
        
        # Apply color palettes to create variations and store in Supabase Storage
        # First get the image data if image_path is available
        base_image_data = None
        if "image_path" in concept_response:
            try:
                # Get image data from persistence service
                base_image_data = await commons.image_persistence_service.get_image_async(
                    concept_response["image_path"]
                )
            except Exception as e:
                logger.error(f"Error fetching image data: {str(e)}")
                # Continue with palette variations even if we can't fetch the image data
                # as create_palette_variations might handle this case
                
        # Apply color palettes to create variations
        palette_variations = await commons.image_service.create_palette_variations(
            base_image_data=base_image_data,
            palettes=raw_palettes,
            user_id=user_id
        )
        
        # Store concept in Supabase database
        stored_concept = await commons.concept_persistence_service.store_concept({
            "user_id": user_id,
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
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
    # Process the request to extract user information
    commons.process_request(req)
    
    try:
        # Get dependencies from commons
        user_id = commons.user_id
        
        # Check for existing active tasks for this user
        try:
            # Look for any pending or processing tasks of type concept_generation
            active_tasks = await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status=TASK_STATUS_PENDING
            )
            processing_tasks = await commons.task_service.get_tasks_by_user(
                user_id=user_id,
                status=TASK_STATUS_PROCESSING
            )
            
            # Combine the task lists
            all_active_tasks = active_tasks + processing_tasks
            
            # Filter for concept_generation tasks
            active_generation_tasks = [task for task in all_active_tasks if task.get("type") == TASK_TYPE_GENERATION]
            
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
                    type=TASK_TYPE_GENERATION,
                    created_at=existing_task.get("created_at"),
                    updated_at=existing_task.get("updated_at"),
                    metadata=existing_task.get("metadata", {})
                )
        except Exception as e:
            # Log the error but continue with creating a new task
            logger.warning(f"Error checking for existing tasks: {str(e)}")
        
        # Create metadata for the task
        task_metadata = {
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
            "num_palettes": num_palettes
        }
        
        try:
            task = await commons.task_service.create_task(
                user_id=user_id,
                task_type=TASK_TYPE_GENERATION,
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
                concept_persistence_service=commons.concept_persistence_service,
                task_service=commons.task_service
            )
            
            # Set response status to 202 Accepted
            response.status_code = status.HTTP_202_ACCEPTED
            
            # Return the task information
            return TaskResponse(
                task_id=task_id,
                status=TASK_STATUS_PENDING,
                message="Concept generation task created and queued for processing",
                type=TASK_TYPE_GENERATION,
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
    concept_persistence_service: StorageServiceInterface,
    task_service: TaskServiceInterface
):
    """
    Background task function to generate a concept.
    
    Args:
        task_id: Unique ID for tracking this task
        logo_description: Description of the logo to generate
        theme_description: Description of the theme/style
        user_id: User ID for storage
        num_palettes: Number of color palettes to generate
        image_service: Service for image generation and processing
        concept_service: Service for concept generation
        concept_persistence_service: Service for storing concepts
        task_service: Service for updating task status
    """
    import traceback  # for detailed error reporting
    
    logger = logging.getLogger("concept_generation_bg")
    logger.info(f"Starting background concept generation task {mask_id(task_id)}")
    
    try:
        # Update task status to processing
        await task_service.update_task_status(
            task_id=task_id,
            status="processing"
        )
        
        logger.info(f"Generating concept for task {mask_id(task_id)}")
        
        # Generate base concept with an image
        concept_response = await concept_service.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=user_id,
            skip_persistence=True  # Skip persistence in the service, we'll handle it here
        )
        
        # Extract the image URL
        image_url = concept_response["image_url"]
        
        if not image_url:
            raise ServiceUnavailableError(detail="Failed to generate base concept")
        
        logger.info(f"Generated base concept with image URL: {mask_id(image_url)}")
        
        # Get the image data - handle both remote URLs and local file paths
        try:
            # Check if the image_url is a file path
            if image_url.startswith("file://"):
                import os
                # Extract the file path from the URL
                file_path = image_url[7:]  # Remove the "file://" prefix
                
                # Check if the file exists
                if not os.path.exists(file_path):
                    logger.error(f"Local file not found: {mask_id(file_path)}")
                    raise ServiceUnavailableError(detail="Image file not found")
                
                # Read the file
                with open(file_path, "rb") as f:
                    image_data = f.read()
                    
                logger.info(f"Read image data from local file: {mask_id(file_path)}")
            else:
                # For remote URLs, use httpx to download
                import httpx
                async with httpx.AsyncClient() as client:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image_data = response.content
                    
                logger.info(f"Downloaded image data from remote URL: {mask_id(image_url)}")
                
            if not image_data:
                logger.error(f"No image data obtained from: {mask_id(image_url)}")
                raise ServiceUnavailableError(detail="Failed to get image data for palette variations")
        except Exception as e:
            error_msg = f"Error getting image data: {str(e)}"
            logger.error(error_msg)
            raise ServiceUnavailableError(detail=error_msg)
        
        # First, store the image in Supabase
        # Create a direct instance of the image persistence service
        supabase_client = SupabaseClient(url=settings.SUPABASE_URL, key=settings.SUPABASE_KEY)
        image_persistence_service = ImagePersistenceService(client=supabase_client)
        
        image_path, stored_image_url = image_persistence_service.store_image(
            image_data=image_data,
            user_id=user_id,
            metadata={
                "logo_description": logo_description,
                "theme_description": theme_description
            }
        )
        
        logger.info(f"Stored image at path: {mask_path(image_path)}")
        
        # Generate color palettes
        raw_palettes = await concept_service.generate_color_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes
        )
        
        if not raw_palettes:
            raise ServiceUnavailableError(detail="Failed to generate color palettes")
            
        logger.info(f"Generated {len(raw_palettes)} color palettes")
        
        # Create palette variations using direct service instances
        from app.services.image.service import ImageService
        from app.services.image.processing_service import ImageProcessingService
        
        # Create all needed services directly
        image_processing_service = ImageProcessingService()
        
        # Create the image service with our services
        image_svc = ImageService(
            persistence_service=image_persistence_service,
            processing_service=image_processing_service
        )
        
        # Create palette variations
        palette_variations = await image_svc.create_palette_variations(
            base_image_data=image_data,
            palettes=raw_palettes,
            user_id=user_id,
            blend_strength=0.75
        )
        
        if not palette_variations:
            raise ServiceUnavailableError(detail="Failed to create palette variations")
            
        logger.info(f"Created {len(palette_variations)} palette variations")
        
        # Store concept in database with the correct image_path
        stored_concept = await concept_persistence_service.store_concept({
            "user_id": user_id,
            "logo_description": logo_description,
            "theme_description": theme_description,
            "image_path": image_path,  # Use the path from the stored image
            "image_url": stored_image_url,
            "color_palettes": palette_variations,
            "is_anonymous": True
        })
        
        if not stored_concept:
            raise ServiceUnavailableError(detail="Failed to store concept")
            
        concept_id = stored_concept
        if isinstance(stored_concept, dict):
            concept_id = stored_concept.get("id", stored_concept)
            
        logger.info(f"Stored concept with ID: {mask_id(concept_id)}")
            
        # Update task status to completed
        await task_service.update_task_status(
            task_id=task_id,
            status="completed",
            result_id=concept_id
        )
        
        logger.info(f"Completed background task {mask_id(task_id)} successfully")
    
    except Exception as e:
        error_msg = f"Error in background task: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        
        # Update task status to failed
        try:
            await task_service.update_task_status(
                task_id=task_id,
                status="failed",
                error_message=error_msg
            )
        except Exception as update_err:
            logger.error(f"Error updating task status: {str(update_err)}")


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    req: Request,
    commons: CommonDependencies = Depends(),
):
    """
    Get the status of a background task.
    
    Args:
        task_id: The ID of the task to check
        req: The FastAPI request object
        commons: Common dependencies
    
    Returns:
        TaskResponse: The task details
    
    Raises:
        HTTPException: If the task is not found
    """
    # Process the request to extract user information
    commons.process_request(req)
    
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