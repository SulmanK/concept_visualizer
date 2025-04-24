"""Concept refinement routes.

This module provides API endpoints for refining existing visual concepts
based on additional instructions or prompts.
"""

import logging
import traceback

import httpx
from fastapi import APIRouter, BackgroundTasks, Depends, Request, Response, status
from pydantic import ValidationError

from app.api.dependencies import CommonDependencies

# Constants
from app.core.constants import TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, TASK_TYPE_REFINEMENT
from app.core.exceptions import ResourceNotFoundError, ServiceUnavailableError, TaskError
from app.models.concept.request import RefinementRequest
from app.models.task.response import TaskResponse
from app.services.concept.interface import ConceptServiceInterface
from app.services.image.interface import ImageServiceInterface
from app.services.persistence.interface import ConceptPersistenceServiceInterface, ImagePersistenceServiceInterface
from app.services.task.interface import TaskServiceInterface

# Import for masking sensitive values in logs
from app.utils.security.mask import mask_id

# Configure logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    background_tasks: BackgroundTasks,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Refine a concept based on refinement prompt.

    Args:
        request: RefinementRequest containing original image URL and refinement prompt
        background_tasks: FastAPI background tasks
        response: FastAPI response object
        req: FastAPI request object for rate limiting
        commons: Common dependencies

    Returns:
        TaskResponse: Task details for the created background task

    Raises:
        ValidationError: If the request is invalid
        ResourceNotFoundError: If the specified concept does not exist
        ServiceUnavailableError: If task creation fails
    """
    try:
        # Get dependencies from commons
        user_id = commons.user_id

        # Ensure user_id is a string (it should be, but mypy needs assurance)
        if user_id is None:
            user_id = "anonymous"  # Fallback user ID if none is available

        # Create metadata for the task
        task_metadata = {
            "original_image_url": str(request.original_image_url),
            "refinement_prompt": request.refinement_prompt,
            "logo_description": request.logo_description or "",
            "theme_description": request.theme_description or "",
        }

        # Check for existing active tasks for this user
        try:
            # Look for any pending or processing tasks of type concept_refinement
            active_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status=TASK_STATUS_PENDING)
            processing_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status=TASK_STATUS_PROCESSING)

            # Combine the task lists
            all_active_tasks = active_tasks + processing_tasks

            # Filter for concept_refinement tasks
            active_refinement_tasks = [task for task in all_active_tasks if task.get("type") == TASK_TYPE_REFINEMENT]

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
                    type=TASK_TYPE_REFINEMENT,
                    created_at=existing_task.get("created_at"),
                    updated_at=existing_task.get("updated_at", None),
                    completed_at=existing_task.get("completed_at", None),
                    metadata=existing_task.get("metadata", task_metadata),
                    result_id=existing_task.get("result_id", None),
                    image_url=existing_task.get("image_url", None),
                    error_message=existing_task.get("error_message", None),
                )
        except Exception as e:
            # Log the error but continue with creating a new task
            logger.warning(f"Error checking for existing tasks: {str(e)}")

        try:
            task = await commons.task_service.create_task(user_id=user_id, task_type=TASK_TYPE_REFINEMENT, metadata=task_metadata)

            task_id = task["id"]
            logger.info(f"Created task {mask_id(task_id)} for concept refinement")

            # Add the refinement task to background tasks
            background_tasks.add_task(
                refine_concept_background_task,
                task_id=task_id,
                refinement_prompt=request.refinement_prompt,
                original_image_url=str(request.original_image_url),
                logo_description=request.logo_description or "",
                theme_description=request.theme_description or "",
                user_id=user_id,
                image_service=commons.image_service,
                concept_service=commons.concept_service,
                concept_persistence_service=commons.concept_persistence_service,
                image_persistence_service=commons.image_persistence_service,
                task_service=commons.task_service,
            )

            # Set response status to 202 Accepted
            response.status_code = status.HTTP_202_ACCEPTED

            # Return the task information
            return TaskResponse(
                task_id=task_id,
                status=TASK_STATUS_PENDING,
                message="Concept refinement task created and queued for processing",
                type=TASK_TYPE_REFINEMENT,
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at", None),
                completed_at=None,
                metadata=task_metadata,
                result_id=None,
                image_url=None,
                error_message=None,
            )

        except TaskError as e:
            logger.error(f"Error creating task: {str(e)}")
            raise ServiceUnavailableError(
                message=f"Error creating task: {str(e)}",
                details={"error_type": "task_creation_error"},
            )

    except (ValidationError, ResourceNotFoundError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error refining concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(
            message=f"Error refining concept: {str(e)}",
            details={"error_type": "refinement_error"},
        )


async def refine_concept_background_task(
    task_id: str,
    refinement_prompt: str,
    original_image_url: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    image_service: ImageServiceInterface,
    concept_service: ConceptServiceInterface,
    concept_persistence_service: ConceptPersistenceServiceInterface,
    image_persistence_service: ImagePersistenceServiceInterface,
    task_service: TaskServiceInterface,
) -> None:
    """Background task function to refine a concept.

    Args:
        task_id: Unique ID for tracking this task
        refinement_prompt: Instructions for refinement
        original_image_url: URL of the image to refine
        logo_description: Description of the logo
        theme_description: Description of the theme/style
        user_id: User ID for storage
        image_service: Service for image refinement and processing
        concept_service: Service for concept generation
        concept_persistence_service: Service for storing concepts
        image_persistence_service: Service for storing images
        task_service: Service for updating task status
    """
    try:
        # Update task status to processing and update the timestamp
        await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_PROCESSING)

        logger.info(f"Starting background refinement task {mask_id(task_id)} for user {mask_id(user_id)}")

        # Refine and store the image
        try:
            # First, download the original image
            async with httpx.AsyncClient() as client:
                response = await client.get(original_image_url)
                response.raise_for_status()
                # No need to store image_data here as it's not used

            # Use concept service to refine the image
            refinement_result = await concept_service.refine_concept(
                original_image_url=original_image_url,
                refinement_prompt=refinement_prompt,
                logo_description=logo_description,
                theme_description=theme_description,
                strength=0.7,  # Control how much to preserve original image
            )

            if not refinement_result or "image_data" not in refinement_result:
                logger.error(f"Task {mask_id(task_id)}: Failed to refine image")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message="Failed to refine image: No image data returned from service",
                )
                return

            # Store the refined image using image persistence service
            # Create a new instance directly instead of using the Depends object
            from app.core.config import settings
            from app.core.supabase.client import SupabaseClient
            from app.services.persistence.image_persistence_service import ImagePersistenceService

            # Create the necessary clients
            supabase_client = SupabaseClient(url=settings.SUPABASE_URL, key=settings.SUPABASE_KEY)
            image_storage_service = ImagePersistenceService(client=supabase_client)

            refined_image_data = refinement_result["image_data"]
            result = await image_storage_service.store_image(
                image_data=refined_image_data,
                user_id=user_id,
                metadata={
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                    "refinement_prompt": refinement_prompt,
                },
            )

            refined_image_path = result[0]
            refined_image_url = result[1]

            if not refined_image_path or not refined_image_url:
                logger.error(f"Task {mask_id(task_id)}: Failed to store refined image")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message="Failed to store refined image",
                )
                return

            # Generate color palettes
            try:
                raw_palettes = await concept_service.generate_color_palettes(
                    theme_description=f"{theme_description} {refinement_prompt}",
                    logo_description=logo_description,
                )
            except Exception as e:
                error_message = f"Failed to generate color palettes: {str(e)}"
                logger.error(f"Task {mask_id(task_id)}: {error_message}")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message=error_message,
                )
                return

            # Apply color palettes to create variations
            try:
                # Create a direct ImageService instance
                from app.services.image.processing_service import ImageProcessingService
                from app.services.image.service import ImageService

                # We already have the image_storage_service from above
                image_processor = ImageProcessingService()
                image_svc = ImageService(
                    persistence_service=image_storage_service,
                    processing_service=image_processor,
                )

                # Use our created service to process the variations
                palette_variations = await image_svc.create_palette_variations(
                    base_image_data=refined_image_data,
                    palettes=raw_palettes,
                    user_id=user_id,
                )  # Use the already downloaded image data
            except Exception as e:
                error_message = f"Failed to create palette variations: {str(e)}"
                logger.error(f"Task {mask_id(task_id)}: {error_message}")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message=error_message,
                )
                return

            # Store the refined concept
            try:
                stored_concept = await concept_persistence_service.store_concept(
                    {
                        "user_id": user_id,
                        "logo_description": logo_description,
                        "theme_description": f"{theme_description} {refinement_prompt}",
                        "image_path": refined_image_path,
                        "image_url": refined_image_url,
                        "color_palettes": palette_variations,
                        "is_anonymous": True,
                        "refinement_prompt": refinement_prompt,
                        "original_image_url": original_image_url,
                        "task_id": task_id,
                    }
                )

                # Get concept ID from the result
                concept_id = stored_concept
                if isinstance(stored_concept, dict):
                    concept_id = stored_concept.get("id", stored_concept)

                if not concept_id:
                    raise ValueError("No concept ID returned from storage service")

                logger.info(f"Task {mask_id(task_id)}: Successfully stored refined concept {mask_id(concept_id)}")

                # Update task status to completed
                await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_COMPLETED, result_id=concept_id)

                logger.info(f"Task {mask_id(task_id)}: Completed successfully with result {mask_id(concept_id)}")

            except Exception as e:
                error_message = f"Failed to store refined concept: {str(e)}"
                logger.error(f"Task {mask_id(task_id)}: {error_message}")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message=error_message,
                )
                return

        except Exception as e:
            # Handle any exceptions
            await task_service.update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message=f"Failed to refine image: {str(e)}",
            )
            raise ServiceUnavailableError(
                message=f"Error in refinement process: {str(e)}",
                details={"error_type": "refinement_process_error", "task_id": task_id},
            )
    except Exception as e:
        # Top-level exception handling
        logger.error(f"Error in refinement background task: {str(e)}")
        await task_service.update_task_status(
            task_id=task_id,
            status=TASK_STATUS_FAILED,
            error_message=f"Error in refinement task: {str(e)}",
        )
