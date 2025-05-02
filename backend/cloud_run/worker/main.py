"""Cloud Function worker for processing Concept Visualizer tasks.

This module provides the main function for the Cloud Function worker that processes
tasks from Pub/Sub and updates the database accordingly.
"""

import asyncio
import base64
import json
import logging
import os
import traceback
from typing import Any, Dict

import functions_framework
import httpx
from functions_framework import CloudEvent

from app.core.config import settings
from app.core.constants import TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, TASK_STATUS_PROCESSING, TASK_TYPE_GENERATION, TASK_TYPE_REFINEMENT
from app.core.supabase.client import SupabaseClient
from app.services.concept.service import ConceptService
from app.services.image.processing_service import ImageProcessingService
from app.services.image.service import ImageService
from app.services.jigsawstack.client import JigsawStackClient
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.services.task.service import TaskService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("concept-worker")


def initialize_services() -> Dict[str, Any]:
    """Initialize all required services for task processing.

    Returns:
        Dict: Dictionary containing all initialized services
    """
    # Create Supabase client
    supabase_client = SupabaseClient(
        url=os.environ.get("CONCEPT_SUPABASE_URL", settings.SUPABASE_URL),
        key=os.environ.get("CONCEPT_SUPABASE_SERVICE_ROLE", settings.SUPABASE_SERVICE_ROLE),
    )

    # Initialize persistence services
    image_persistence_service = ImagePersistenceService(client=supabase_client)
    concept_persistence_service = ConceptPersistenceService(client=supabase_client)

    # Initialize image services
    image_processing_service = ImageProcessingService()
    image_service = ImageService(
        persistence_service=image_persistence_service,
        processing_service=image_processing_service,
    )

    # Initialize JigsawStack client
    jigsawstack_client = JigsawStackClient(
        api_key=os.environ.get("CONCEPT_JIGSAWSTACK_API_KEY", settings.JIGSAWSTACK_API_KEY),
        api_url=os.environ.get("CONCEPT_JIGSAWSTACK_API_URL", settings.JIGSAWSTACK_API_URL),
    )

    # Initialize concept service with the correct parameters
    concept_service = ConceptService(
        client=jigsawstack_client,
        image_service=image_service,
        concept_persistence_service=concept_persistence_service,
        image_persistence_service=image_persistence_service,
    )

    # Initialize task service
    task_service = TaskService(
        client=supabase_client,
    )

    return {
        "image_service": image_service,
        "concept_service": concept_service,
        "concept_persistence_service": concept_persistence_service,
        "image_persistence_service": image_persistence_service,
        "task_service": task_service,
    }


async def process_generation_task(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    num_palettes: int,
    services: Dict[str, Any],
) -> None:
    """Process a concept generation task.

    Args:
        task_id: The ID of the task
        user_id: User ID for storage
        logo_description: Description for the logo generation
        theme_description: Description for the theme generation
        num_palettes: Number of palette variations to generate
        services: Dictionary of initialized services
    """
    # Get services from the dictionary
    image_service = services["image_service"]
    concept_service = services["concept_service"]
    concept_persistence_service = services["concept_persistence_service"]
    task_service = services["task_service"]

    logger = logging.getLogger("concept_generation_worker")
    logger.info(f"Starting concept generation task {task_id}")

    try:
        # Update task status to processing
        await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_PROCESSING)

        logger.debug(f"Generating concept for task {task_id}")

        # Generate base concept with an image
        concept_response = await concept_service.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=user_id,
            skip_persistence=True,  # Skip persistence in the service, we'll handle it here
        )

        # Log the response keys for debugging
        if concept_response:
            logger.debug(f"Concept response keys: {list(concept_response.keys())}")
        else:
            raise Exception("Failed to generate base concept: empty response")

        # Extract the image URL and image data
        image_url = concept_response.get("image_url")
        image_data = concept_response.get("image_data")

        # Check for valid image_url
        if not image_url:
            logger.error(f"Failed to get image_url from concept_response: {concept_response}")
            raise Exception("Failed to generate base concept: missing image_url in response")

        logger.debug(f"Generated base concept with image URL: {image_url}")

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
                        logger.error(f"Local file not found: {file_path}")
                        raise Exception("Image file not found")

                    # Read the file
                    with open(file_path, "rb") as f:
                        image_data = f.read()

                    logger.debug(f"Read image data from local file: {file_path}")
                else:
                    # For remote URLs, use httpx to download
                    async with httpx.AsyncClient() as client:
                        httpx_response = await client.get(image_url)
                        httpx_response.raise_for_status()
                        image_data = httpx_response.content

                    logger.debug(f"Downloaded image data from remote URL: {image_url}")

                if not image_data:
                    logger.error(f"No image data obtained from: {image_url}")
                    raise Exception("Failed to get image data for palette variations")
            except Exception as e:
                error_msg = f"Error getting image data: {str(e)}"
                logger.error(error_msg)
                raise Exception(error_msg)
        else:
            logger.info(f"Using image data from concept service response, size: {len(image_data)} bytes")

        # Store the image in Supabase
        image_persistence_service = services["image_persistence_service"]
        result = await image_persistence_service.store_image(
            image_data=image_data,
            user_id=user_id,
            metadata={
                "logo_description": logo_description,
                "theme_description": theme_description,
            },
        )

        image_path = result[0]
        stored_image_url = result[1]

        logger.info(f"Stored image at path: {image_path}")

        # Generate color palettes
        try:
            raw_palettes = await concept_service.generate_color_palettes(
                theme_description=theme_description,
                logo_description=logo_description,
                num_palettes=num_palettes,
            )

            if not raw_palettes:
                logger.error("No palettes generated from generate_color_palettes")
                raise Exception("Failed to generate color palettes")

            logger.info(f"Generated {len(raw_palettes)} color palettes")
        except Exception as palette_error:
            logger.error(f"Error generating color palettes: {str(palette_error)}")
            raise Exception(f"Failed to generate color palettes: {str(palette_error)}")

        # Create palette variations
        try:
            palette_variations = await image_service.create_palette_variations(
                base_image_data=image_data,
                palettes=raw_palettes,
                user_id=user_id,
                blend_strength=0.75,
            )

            if not palette_variations:
                logger.error("No palette variations created")
                raise Exception("Failed to create palette variations")

            logger.info(f"Created {len(palette_variations)} palette variations")
        except Exception as variation_error:
            logger.error(f"Error creating palette variations: {str(variation_error)}")
            raise Exception(f"Failed to create palette variations: {str(variation_error)}")

        # Store concept in database with the correct image_path
        stored_concept = await concept_persistence_service.store_concept(
            {
                "user_id": user_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "image_path": image_path,  # Use the path from the stored image
                "image_url": stored_image_url,
                "color_palettes": palette_variations,
                "is_anonymous": True,
            }
        )

        if not stored_concept:
            raise Exception("Failed to store concept")

        concept_id = stored_concept
        if isinstance(stored_concept, dict):
            concept_id = stored_concept.get("id", stored_concept)

        logger.info(f"Stored concept with ID: {concept_id}")

        # Update task status to completed
        await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_COMPLETED, result_id=concept_id)

        logger.info(f"Completed task {task_id} successfully")

    except Exception as e:
        error_msg = f"Error in generation task: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Exception traceback: {traceback.format_exc()}")

        # Update task status to failed
        try:
            await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=error_msg)
        except Exception as update_err:
            logger.error(f"Error updating task status: {str(update_err)}")


async def process_refinement_task(
    task_id: str,
    user_id: str,
    refinement_prompt: str,
    original_image_url: str,
    logo_description: str,
    theme_description: str,
    services: Dict[str, Any],
) -> None:
    """Process a concept refinement task.

    Args:
        task_id: The ID of the task
        user_id: User ID for storage
        refinement_prompt: Instructions for refinement
        original_image_url: URL of the image to refine
        logo_description: Description of the logo
        theme_description: Description of the theme
        services: Dictionary of initialized services
    """
    # Get services from the dictionary
    image_service = services["image_service"]
    concept_service = services["concept_service"]
    concept_persistence_service = services["concept_persistence_service"]
    image_persistence_service = services["image_persistence_service"]
    task_service = services["task_service"]

    logger = logging.getLogger("concept_refinement_worker")
    logger.info(f"Starting concept refinement task {task_id}")

    try:
        # Update task status to processing and update the timestamp
        await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_PROCESSING)

        logger.info(f"Starting refinement task {task_id} for user {user_id}")

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
                logger.error(f"Task {task_id}: Failed to refine image")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message="Failed to refine image: No image data returned from service",
                )
                return

            refined_image_data = refinement_result["image_data"]
            result = await image_persistence_service.store_image(
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
                logger.error(f"Task {task_id}: Failed to store refined image")
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
                logger.error(f"Task {task_id}: {error_message}")
                await task_service.update_task_status(
                    task_id=task_id,
                    status=TASK_STATUS_FAILED,
                    error_message=error_message,
                )
                return

            # Apply color palettes to create variations
            try:
                # Use our created service to process the variations
                palette_variations = await image_service.create_palette_variations(
                    base_image_data=refined_image_data,
                    palettes=raw_palettes,
                    user_id=user_id,
                )  # Use the already downloaded image data
            except Exception as e:
                error_message = f"Failed to create palette variations: {str(e)}"
                logger.error(f"Task {task_id}: {error_message}")
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

                logger.info(f"Task {task_id}: Successfully stored refined concept {concept_id}")

                # Update task status to completed
                await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_COMPLETED, result_id=concept_id)

                logger.info(f"Task {task_id}: Completed successfully with result {concept_id}")

            except Exception as e:
                error_message = f"Failed to store refined concept: {str(e)}"
                logger.error(f"Task {task_id}: {error_message}")
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
            logger.error(f"Error in refinement process: {str(e)}")
            return

    except Exception as e:
        # Top-level exception handling
        logger.error(f"Error in refinement task: {str(e)}")
        await task_service.update_task_status(
            task_id=task_id,
            status=TASK_STATUS_FAILED,
            error_message=f"Error in refinement task: {str(e)}",
        )


async def process_pubsub_message(message: Dict[str, Any], services: Dict[str, Any]) -> None:
    """Process a message from Pub/Sub based on its task type.

    Args:
        message: The message payload from Pub/Sub
        services: Dictionary of initialized services

    Raises:
        ValueError: If the task type is unknown
    """
    task_type = message.get("task_type")
    task_id = message.get("task_id")

    if not task_id:
        logger.error("Message missing required task_id field")
        return

    if task_type == TASK_TYPE_GENERATION:
        user_id = message.get("user_id")
        logo_description = message.get("logo_description")
        theme_description = message.get("theme_description")

        # Ensure we have required fields
        if not user_id or not logo_description or not theme_description:
            logger.error(f"Missing required fields for generation task: user_id={user_id}, logo_description={bool(logo_description)}, theme_description={bool(theme_description)}")
            await services["task_service"].update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message="Missing required fields for generation task",
            )
            return

        await process_generation_task(
            task_id=task_id,
            user_id=str(user_id),
            logo_description=str(logo_description),
            theme_description=str(theme_description),
            num_palettes=int(message.get("num_palettes", 7)),
            services=services,
        )
    elif task_type == TASK_TYPE_REFINEMENT:
        user_id = message.get("user_id")
        refinement_prompt = message.get("refinement_prompt")
        original_image_url = message.get("original_image_url")

        # Ensure we have required fields
        if not user_id or not refinement_prompt or not original_image_url:
            logger.error(f"Missing required fields for refinement task: user_id={user_id}, refinement_prompt={bool(refinement_prompt)}, original_image_url={bool(original_image_url)}")
            await services["task_service"].update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message="Missing required fields for refinement task",
            )
            return

        await process_refinement_task(
            task_id=task_id,
            user_id=str(user_id),
            refinement_prompt=str(refinement_prompt),
            original_image_url=str(original_image_url),
            logo_description=str(message.get("logo_description", "")),
            theme_description=str(message.get("theme_description", "")),
            services=services,
        )
    else:
        logger.error(f"Unknown task type: {task_type}")
        raise ValueError(f"Unknown task type: {task_type}")


@functions_framework.cloud_event
def handle_pubsub(cloud_event: CloudEvent) -> None:
    """Cloud Function entry point triggered by Pub/Sub CloudEvents.

    Args:
        cloud_event: The CloudEvent object containing the Pub/Sub message
    """
    logger = logging.getLogger("concept-worker-function")
    try:
        # Extract and decode the Pub/Sub message data
        if "message" not in cloud_event.data or "data" not in cloud_event.data["message"]:
            logger.error("Invalid CloudEvent format: Missing message data.")
            # Acknowledge implicitly by returning, or raise to potentially trigger retry
            return

        message_data_base64 = cloud_event.data["message"]["data"]
        message_data_bytes = base64.b64decode(message_data_base64)
        message = json.loads(message_data_bytes.decode("utf-8"))
        task_id = message.get("task_id", "UNKNOWN")
        logger.info(f"Processing Pub/Sub message for task ID: {task_id}")

        # Initialize services *per invocation*
        services = initialize_services()

        # Run the async processing logic
        # Using asyncio.run is suitable for Cloud Functions entry points
        asyncio.run(process_pubsub_message(message, services))

        logger.info(f"Successfully processed task ID: {task_id}")
        # Function completes, execution environment terminates

    except Exception as e:
        task_id = message.get("task_id", "UNKNOWN") if "message" in locals() else "UNKNOWN"
        logger.error(f"FATAL error processing task {task_id}: {e}", exc_info=True)
        # Re-raising signals failure to the platform for potential retries
        raise
