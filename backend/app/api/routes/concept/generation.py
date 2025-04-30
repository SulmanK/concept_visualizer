"""Concept generation endpoints.

This module provides endpoints for generating visual concepts.
"""

import json
import logging
import traceback
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from google.cloud import pubsub_v1

from app.api.dependencies import CommonDependencies

# Import specific API errors
from app.api.errors import InternalServerError, ResourceNotFoundError, ServiceUnavailableError, TaskNotFoundError
from app.core.config import settings
from app.core.constants import TASK_STATUS_FAILED, TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, TASK_TYPE_GENERATION

# Import domain/application error types for catching
from app.core.exceptions import ApplicationError, AuthenticationError, ConceptCreationError, ImageProcessingError, JigsawStackError, RateLimitError
from app.core.exceptions import ValidationError as AppValidationError
from app.models.concept.request import PromptRequest
from app.models.concept.response import GenerationResponse
from app.models.task.response import TaskResponse
from app.services.task.service import TaskError
from app.utils.api_limits import apply_multiple_rate_limits
from app.utils.security.mask import mask_id, mask_path

# Configure logging
logger = logging.getLogger("concept_generation_api")

router = APIRouter()


@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> GenerationResponse:
    """Generate a new visual concept based on the provided prompt and store it.

    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        commons: Common dependencies including services

    Returns:
        GenerationResponse: The generated concept data

    Raises:
        ValidationError: If the request validation fails
        UnauthorizedError: If user is not authenticated
        ServiceUnavailableError: If there was an error generating the concept
        BadRequestError: If the request parameters are invalid
        InternalServerError: If there was an unexpected error
    """
    # Process the request to extract user information
    commons.process_request(req)

    try:
        # Apply both generation and storage rate limits
        await apply_multiple_rate_limits(
            req,
            [
                {"endpoint": "/concepts/generate", "rate_limit": "10/month"},
                {"endpoint": "/concepts/store", "rate_limit": "10/month"},
            ],
        )

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
                    check_only=True,
                )

                storage_status = check_rate_limit(
                    user_id=full_user_id,
                    endpoint="/concepts/store",
                    limit="10/month",
                    check_only=True,
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
                    "reset": limit_status.get("reset_at", 0),
                }

                logger.debug(f"Stored rate limit info for {endpoint} after increment: " f"remaining={limit_status.get('remaining', 0)}")
        except Exception as e:
            logger.error(f"Error storing post-increment rate limit info: {str(e)}")

        # Validate inputs
        if not request.logo_description or not request.theme_description:
            raise AppValidationError(
                message="Logo and theme descriptions are required",
                field_errors={
                    "logo_description": ["Field is required"] if not request.logo_description else [],
                    "theme_description": ["Field is required"] if not request.theme_description else [],
                },
            )

        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise AuthenticationError(message="Authentication required")

        # Generate base image and store it in Supabase Storage
        # Use ConceptService to generate the concept instead of ImageService
        concept_response = await commons.concept_service.generate_concept(
            logo_description=request.logo_description,
            theme_description=request.theme_description,
            user_id=user_id,
            skip_persistence=True,  # Skip persistence in the service, we'll handle it here
        )

        # Extract the image URL and image data
        image_url = concept_response["image_url"]
        image_data = concept_response.get("image_data")

        if not image_url:
            raise JigsawStackError(message="Failed to generate base concept")

        logger.debug(f"Generated base concept with image URL: {mask_id(image_url)}")

        # Check if we have image_data directly from the concept service
        if not image_data:
            # If not, we need to download it - this is a fallback for backward compatibility
            logger.debug("Image data not provided in concept response, downloading from URL")
            try:
                # Check if the image_url is a file path
                if image_url.startswith("file://"):
                    import os

                    # Extract the file path from the URL
                    file_path = image_url[7:]  # Remove the "file://" prefix

                    # Check if the file exists
                    if not os.path.exists(file_path):
                        logger.error(f"Local file not found: {mask_id(file_path)}")
                        raise JigsawStackError(message="Image file not found")

                    # Read the file
                    with open(file_path, "rb") as f:
                        image_data = f.read()

                    logger.debug(f"Read image data from local file: {mask_id(file_path)}")
                else:
                    # For remote URLs, use httpx to download
                    import httpx

                    async with httpx.AsyncClient() as client:
                        httpx_response = await client.get(image_url)
                        httpx_response.raise_for_status()
                        image_data = httpx_response.content

                    logger.debug(f"Downloaded image data from remote URL: {mask_id(image_url)}")

                if not image_data:
                    logger.error(f"No image data obtained from: {mask_id(image_url)}")
                    raise JigsawStackError(message="Failed to get image data for palette variations")
            except Exception as e:
                error_msg = f"Error getting image data: {str(e)}"
                logger.error(error_msg)
                logger.debug(traceback.format_exc())
                raise JigsawStackError(message=error_msg)

        # Store the base image - we've separated this from concept generation
        try:
            # Generate a unique ID for the concept
            concept_id = str(uuid.uuid4())

            # Store the image
            image_path = f"concepts/{user_id}/{concept_id}.png"

            # Use ImagePersistenceService to store the image
            image_url = await commons.image_persistence_service.store_image(
                image_data=image_data,
                content_type="image/png",
                user_id=user_id,
                file_name=f"{concept_id}.png",
            )

            logger.info(f"Stored base concept image at: {mask_path(image_path)}")

            # Extract colors from the image using ImageService
            colors = await commons.image_service.extract_color_palette(image_data=image_data, num_colors=8)

            logger.debug(f"Extracted {len(colors)} colors from base concept image")

            # Generate palette from colors
            from app.services.concept.helpers.palette_generator import get_palette_from_colors

            palette = get_palette_from_colors(colors)

            # Store concept metadata
            concept_data = {
                "id": concept_id,
                "user_id": user_id,
                "prompt": {
                    "logo_description": request.logo_description,
                    "theme_description": request.theme_description,
                },
                "base_image_path": image_path,
                "colors": colors,
                "palette": palette,
                "created_at": datetime.now().isoformat(),
            }

            # Use ConceptPersistenceService to store the concept
            await commons.concept_persistence_service.store_concept(concept_data)

            logger.info(f"Stored concept metadata with ID: {mask_id(concept_id)}")

            # Construct and return the response
            return GenerationResponse(
                prompt_id=concept_id,
                logo_description=request.logo_description,
                theme_description=request.theme_description,
                created_at=datetime.now().isoformat(),
                image_url=image_url,
                color_palette=None,
                original_image_url=None,
                refinement_prompt=None,
                variations=[],
            )

        except Exception as e:
            error_msg = f"Error storing concept: {str(e)}"
            logger.error(error_msg)
            logger.debug(traceback.format_exc())
            raise ConceptCreationError(message=error_msg)

    except RateLimitError as e:
        # Rate limit errors will be translated to appropriate API errors
        # by the application_error_handler
        logger.warning(f"Rate limit exceeded: {e.message}")
        raise

    except AppValidationError as e:
        # Validation errors will be translated
        logger.warning(f"Validation error: {e.message}")
        raise

    except AuthenticationError as e:
        # Auth errors will be translated
        logger.warning(f"Authentication error: {e.message}")
        raise

    except (JigsawStackError, ConceptCreationError, ImageProcessingError) as e:
        # Domain-specific errors will be translated
        logger.error(f"Service error: {e.message}", exc_info=True)
        raise

    except ApplicationError as e:
        # Catch all other application errors to ensure proper translation
        logger.error(f"Application error: {e.message}", exc_info=True)
        raise

    except Exception as e:
        # Catch unexpected errors
        error_msg = f"Unexpected error generating concept: {str(e)}"
        logger.error(error_msg, exc_info=True)
        raise InternalServerError(detail=error_msg)


@router.post("/generate-with-palettes", response_model=TaskResponse)
async def generate_concept_with_palettes(
    request: PromptRequest,
    response: Response,
    req: Request,
    num_palettes: int = 7,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Generate a new visual concept with multiple color palettes.

    This endpoint creates a background task to generate a concept with multiple
    color palette variations. The task ID is returned immediately, and the
    client can poll for completion status.

    Args:
        request: The prompt request containing logo and theme descriptions
        response: FastAPI response object
        req: The FastAPI request object for rate limiting
        num_palettes: Number of color palette variations to generate (default: 7)
        commons: Common dependencies including services

    Returns:
        TaskResponse: The task information, including ID for polling status

    Raises:
        ValidationError: If the request validation fails
        UnauthorizedError: If user is not authenticated
        ServiceUnavailableError: If there was an error creating the task
    """
    # Process the request to extract user information
    commons.process_request(req)

    try:
        # Use API limits utility to manage rate limiting
        await apply_multiple_rate_limits(
            req,
            [
                {"endpoint": "/concepts/generate", "rate_limit": "10/month"},
                {"endpoint": "/concepts/store", "rate_limit": "10/month"},
            ],
        )

        # Get user ID from commons
        user_id = commons.user_id

        if not user_id:
            raise AuthenticationError(message="Authentication required for generating concept with palettes")

        # Initialize a Publisher client
        publisher = pubsub_v1.PublisherClient()

        # Get the topic path
        topic_path = publisher.topic_path(settings.PUB_SUB_PROJECT_ID, settings.PUB_SUB_TOPIC_ID)

        logger.debug(f"Publishing to topic: {topic_path}")

        # Create task metadata with details needed for processing
        task_metadata = {
            "logo_description": request.logo_description,
            "theme_description": request.theme_description,
            "num_palettes": num_palettes,
        }

        # Check for existing active tasks for this user
        try:
            # Look for any pending or processing tasks of type concept_generation
            active_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status=TASK_STATUS_PENDING)
            processing_tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status=TASK_STATUS_PROCESSING)

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

        # Create a new task in the database
        try:
            task = await commons.task_service.create_task(user_id=user_id, task_type=TASK_TYPE_GENERATION, metadata=task_metadata)

            task_id = task["id"]
            logger.info(f"Created task {mask_id(task_id)} for concept generation with palettes")

            # Create Pub/Sub message payload
            message_data = {
                "task_id": task_id,
                "user_id": user_id,
                "logo_description": request.logo_description,
                "theme_description": request.theme_description,
                "num_palettes": num_palettes,
                "task_type": TASK_TYPE_GENERATION,
            }

            # Convert the message to JSON and then to bytes
            message_json = json.dumps(message_data)
            message_bytes = message_json.encode("utf-8")

            # Publish the message
            try:
                publish_future = publisher.publish(topic_path, data=message_bytes)
                publish_result = publish_future.result()  # Wait for the publish to complete
                logger.info(f"Message published with ID: {publish_result}")
            except Exception as e:
                logger.error(f"Error publishing message to Pub/Sub: {str(e)}")
                # Update task status to failed
                await commons.task_service.update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=f"Failed to queue task: {str(e)}")
                raise ServiceUnavailableError(detail="Failed to queue concept generation task: pubsub_error")

            # Set response status to 202 Accepted
            response.status_code = status.HTTP_202_ACCEPTED

            # Return the task information
            return TaskResponse(
                task_id=task_id,
                status=TASK_STATUS_PENDING,
                message="Concept generation task created and queued for processing",
                type=TASK_TYPE_GENERATION,
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
            raise ServiceUnavailableError(detail=f"Error creating task: {str(e)}")

    except (AuthenticationError, AppValidationError):
        # Let the middleware handle these familiar error types
        raise
    except Exception as e:
        # Log unexpected errors and wrap them in our API error format
        logger.error(f"Error in generate_concept_with_palettes: {str(e)}")
        logger.debug(traceback.format_exc())
        raise ServiceUnavailableError(detail=f"Error queueing concept generation: {str(e)}")


@router.get("/task/{task_id}", response_model=TaskResponse)
async def get_task_status(
    task_id: str,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Get the status of a concept generation task.

    Args:
        task_id: The ID of the task to check
        req: The FastAPI request object
        commons: Common dependencies including services

    Returns:
        TaskResponse: The current task status
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
            task_type = task.get("type")
            # Ensure task_type is a string
            if task_type is None:
                task_type = "unknown"

            return TaskResponse(
                task_id=task["id"],
                status=task["status"],
                message=f"Task is {task['status']}",
                type=task_type,
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at"),
                completed_at=task.get("completed_at"),
                result_id=task.get("result_id"),
                image_url=task.get("image_url"),
                error_message=task.get("error_message"),
                metadata=task.get("metadata", {}),
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
