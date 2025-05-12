"""Concept refinement routes.

This module provides API endpoints for refining existing visual concepts
based on additional instructions or prompts.
"""

import json
import logging
import traceback

from fastapi import APIRouter, Depends, Request, Response, status
from google.cloud import pubsub_v1
from pydantic import ValidationError

from app.api.dependencies import CommonDependencies

# Import API errors
from app.api.errors import ServiceUnavailableError

# Constants
from app.core.config import settings
from app.core.constants import TASK_STATUS_FAILED, TASK_STATUS_PENDING, TASK_STATUS_PROCESSING, TASK_TYPE_REFINEMENT
from app.core.exceptions import ResourceNotFoundError, TaskError
from app.models.concept.request import RefinementRequest
from app.models.task.response import TaskResponse

# Import for masking sensitive values in logs
from app.utils.security.mask import mask_id

# Configure logger
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter()


@router.post("/refine", response_model=TaskResponse)
async def refine_concept(
    request: RefinementRequest,
    response: Response,
    req: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Refine a concept based on refinement prompt.

    Args:
        request: RefinementRequest containing original image URL and refinement prompt
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

                # --- REFUND LOGIC for 409 Conflict ---
                # Check if there are applied rate limits that need to be refunded
                applied_limits_to_refund = getattr(req.state, "applied_rate_limits_for_refund", [])
                if applied_limits_to_refund:
                    logger.info(f"Attempting to refund rate limits for user {mask_id(user_id)} due to 409 conflict")

                    # Get the Redis store instance from app state limiter
                    redis_store_instance = None
                    if hasattr(req.app.state, "limiter") and hasattr(req.app.state.limiter, "_storage"):
                        redis_store_instance = req.app.state.limiter._storage

                    if redis_store_instance:
                        for limit_to_refund in applied_limits_to_refund:
                            try:
                                # Call the decrement method on the RedisStore
                                logger.info(f"Refunding: endpoint={limit_to_refund['endpoint_rule']}, limit={limit_to_refund['limit_string_rule']}")

                                refund_success = redis_store_instance.decrement_specific_limit(
                                    user_id=limit_to_refund["user_id"],
                                    endpoint_rule=limit_to_refund["endpoint_rule"],
                                    limit_string_rule=limit_to_refund["limit_string_rule"],
                                    amount=limit_to_refund["amount"],
                                )

                                if refund_success:
                                    logger.info(f"Successfully refunded rate limit for {limit_to_refund['endpoint_rule']} for user {mask_id(user_id)}")
                                else:
                                    logger.warning(f"Failed to refund rate limit for {limit_to_refund['endpoint_rule']} for user {mask_id(user_id)}")
                            except Exception as e:
                                logger.error(f"Error refunding rate limit for {limit_to_refund['endpoint_rule']} (user: {mask_id(user_id)}): {e}")
                    else:
                        logger.error(f"Could not obtain RedisStore instance to refund rate limit for 409 conflict for user {mask_id(user_id)}")
                else:
                    logger.debug(f"No applied rate limits found for user {mask_id(user_id)} during 409 conflict. No refund attempted.")
                # --- END REFUND LOGIC ---

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

            # Initialize a Publisher client
            publisher = pubsub_v1.PublisherClient()

            # Get the topic path
            topic_path = publisher.topic_path(settings.PUB_SUB_PROJECT_ID, settings.PUB_SUB_TOPIC_ID)

            logger.debug(f"Publishing to topic: {topic_path}")

            # Create Pub/Sub message payload
            message_data = {
                "task_id": task_id,
                "user_id": user_id,
                "refinement_prompt": request.refinement_prompt,
                "original_image_url": str(request.original_image_url),
                "logo_description": request.logo_description or "",
                "theme_description": request.theme_description or "",
                "task_type": TASK_TYPE_REFINEMENT,
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
                raise ServiceUnavailableError(detail="Failed to queue concept refinement task: pubsub_error")

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
            raise ServiceUnavailableError(detail=f"Error creating task: {str(e)}")

    except (ValidationError, ResourceNotFoundError, ServiceUnavailableError):
        # Re-raise our custom errors directly
        raise
    except Exception as e:
        logger.error(f"Error refining concept: {str(e)}")
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        raise ServiceUnavailableError(detail=f"Error refining concept: {str(e)}")
