"""Cloud Function worker for processing Concept Visualizer tasks.

This module provides the main function for the Cloud Function worker that processes
tasks from Pub/Sub and updates the database accordingly.
"""

import asyncio
import base64
import json
import logging
import os
import time
import traceback
from typing import Any, Dict, Optional, cast

import functions_framework
import httpx
from cloudevents.http import CloudEvent

from app.core.config import settings
from app.core.constants import TASK_STATUS_COMPLETED, TASK_STATUS_FAILED, TASK_TYPE_GENERATION, TASK_TYPE_REFINEMENT
from app.core.exceptions import JigsawStackError
from app.core.supabase.client import SupabaseClient
from app.services.concept.service import ConceptService
from app.services.image.processing_service import ImageProcessingService
from app.services.image.service import ImageService
from app.services.jigsawstack.client import JigsawStackClient
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.services.task.service import TaskService

# Configure dynamic logging level
log_level_str = os.environ.get("CONCEPT_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("concept-worker-main")

# Type for our services dictionary
ServicesDict = Dict[str, Any]

# Global service instances
SERVICES_GLOBAL: Optional[Dict[str, Any]] = None

# Initialize on module import - global service initialization
logger.info("Initializing services globally for worker instance...")
try:
    # Create Supabase client (use service role directly for worker)
    _supabase_client_global = SupabaseClient(
        url=os.environ.get("CONCEPT_SUPABASE_URL", settings.SUPABASE_URL),
        key=os.environ.get("CONCEPT_SUPABASE_SERVICE_ROLE", settings.SUPABASE_SERVICE_ROLE),  # Crucial for worker
    )

    # Initialize persistence services
    _image_persistence_service_global = ImagePersistenceService(client=_supabase_client_global)
    _concept_persistence_service_global = ConceptPersistenceService(client=_supabase_client_global)

    # Initialize image services
    _image_processing_service_global = ImageProcessingService()
    _image_service_global = ImageService(
        persistence_service=_image_persistence_service_global,
        processing_service=_image_processing_service_global,
    )

    # Initialize JigsawStack client
    _jigsawstack_client_global = JigsawStackClient(
        api_key=os.environ.get("CONCEPT_JIGSAWSTACK_API_KEY", settings.JIGSAWSTACK_API_KEY),
        api_url=os.environ.get("CONCEPT_JIGSAWSTACK_API_URL", settings.JIGSAWSTACK_API_URL),
    )

    # Initialize concept service
    _concept_service_global = ConceptService(
        client=_jigsawstack_client_global,
        image_service=_image_service_global,
        concept_persistence_service=_concept_persistence_service_global,
        image_persistence_service=_image_persistence_service_global,
    )

    # Initialize task service
    _task_service_global = TaskService(client=_supabase_client_global)

    SERVICES_GLOBAL = {
        "image_service": _image_service_global,
        "concept_service": _concept_service_global,
        "concept_persistence_service": _concept_persistence_service_global,
        "image_persistence_service": _image_persistence_service_global,
        "task_service": _task_service_global,
        # Add JigsawStack client if needed directly by tasks
        "jigsawstack_client": _jigsawstack_client_global,
    }
    logger.info("Global services initialized successfully.")
except Exception as e:
    logger.critical(f"FATAL: Failed to initialize global services: {e}", exc_info=True)
    SERVICES_GLOBAL = None  # Indicate failure


# Add HTTP handler for health checks
@functions_framework.http
def http_endpoint(request: Any) -> Dict[str, str]:
    """HTTP handler for health checks.

    Cloud Run will use this endpoint to verify that the instance is healthy.

    Args:
        request: HTTP request object

    Returns:
        An HTTP response with status information
    """
    logger.info("Received health check request")
    return {"status": "healthy", "message": "Concept worker is ready to process tasks"}


async def generate_base_concept(
    task_id: str,
    logo_description: str,
    theme_description: str,
    user_id: str,
    concept_service: Any,
) -> Dict[str, Any]:
    """Generate the base concept with image.

    Args:
        task_id: The ID of the task
        logo_description: Description for logo generation
        theme_description: Description for theme generation
        user_id: User ID
        concept_service: ConceptService instance

    Returns:
        Dict with concept response data

    Raises:
        Exception: If generation fails
    """
    logger = logging.getLogger("concept_generator")

    gen_start = time.time()
    try:
        concept_response = await concept_service.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=user_id,
            skip_persistence=True,  # Skip persistence in the service, we'll handle it here
        )
    except JigsawStackError as jse:
        logger.error(f"Task {task_id}: JigsawStack API error: {jse}")
        raise Exception(f"Base concept generation failed: JigsawStack API error: {jse}")
    except httpx.TimeoutException as te:
        logger.error(f"Task {task_id}: Request timeout error: {te}")
        raise Exception(f"Base concept generation failed: API request timed out: {te}")
    except httpx.NetworkError as ne:
        logger.error(f"Task {task_id}: Network error: {ne}")
        raise Exception(f"Base concept generation failed: Network error: {ne}")
    except Exception as gen_e:
        raise Exception(f"Base concept generation failed: {gen_e}")

    gen_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Base concept generated at {gen_end:.2f} (Duration: {(gen_end - gen_start):.2f}s)")

    # Log the response keys for debugging
    if concept_response:
        logger.debug(f"Concept response keys: {list(concept_response.keys())}")
    else:
        raise Exception("Failed to generate base concept: empty response")

    # Extract the image URL and image data
    image_url = concept_response.get("image_url")

    # Check for valid image_url
    if not image_url:
        logger.error(f"Failed to get image_url from concept_response: {concept_response}")
        raise Exception("Failed to generate base concept: missing image_url in response")

    logger.debug(f"Generated base concept with image URL: {image_url}")

    # Explicitly cast the response to ensure it matches the return type
    return dict(concept_response)


async def prepare_image_data(task_id: str, concept_response: Dict[str, Any]) -> bytes:
    """Prepare image data from the concept response or download it.

    Args:
        task_id: The ID of the task
        concept_response: The concept generation response

    Returns:
        bytes: The image data

    Raises:
        Exception: If image data cannot be obtained
    """
    logger = logging.getLogger("image_preparer")

    image_url = concept_response.get("image_url")
    image_data = concept_response.get("image_data")

    # Check if we have image_data directly from the concept service
    if not image_data:
        # If not, we need to download it - this is a fallback for backward compatibility
        logger.debug("Image data not provided in concept response, downloading from URL")
        try:
            # Check if the image_url is a file path
            if image_url and image_url.startswith("file://"):
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
                if not image_url:
                    raise Exception("No image URL provided for download")

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

    # Ensure we have bytes to return
    if not isinstance(image_data, bytes):
        raise Exception("Image data is not in bytes format")

    return image_data


async def generate_color_palettes(
    task_id: str,
    theme_description: str,
    logo_description: str,
    num_palettes: int,
    concept_service: Any,
) -> list:
    """Generate color palettes for the concept.

    Args:
        task_id: The ID of the task
        theme_description: Description for theme generation
        logo_description: Description for logo generation
        num_palettes: Number of palettes to generate
        concept_service: ConceptService instance

    Returns:
        list: Generated color palettes

    Raises:
        Exception: If palette generation fails
    """
    logger = logging.getLogger("palette_generator")

    palette_gen_start = time.time()
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
    except JigsawStackError as jse:
        logger.error(f"Task {task_id}: JigsawStack API error during palette generation: {jse}")
        raise Exception(f"Failed to generate color palettes: JigsawStack API error: {jse}")
    except httpx.TimeoutException as te:
        logger.error(f"Task {task_id}: Request timeout during palette generation: {te}")
        raise Exception(f"Failed to generate color palettes: API request timed out: {te}")
    except Exception as palette_error:
        logger.error(f"Error generating color palettes: {str(palette_error)}")
        raise Exception(f"Failed to generate color palettes: {str(palette_error)}")

    palette_gen_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Palettes generated at {palette_gen_end:.2f} (Duration: {(palette_gen_end - palette_gen_start):.2f}s)")

    # Ensure we're returning a list
    return list(raw_palettes)


async def create_palette_variations(
    task_id: str,
    image_data: bytes,
    palettes: list,
    user_id: str,
    image_service: Any,
) -> list:
    """Create palette variations of the base image.

    Args:
        task_id: The ID of the task
        image_data: Base image data
        palettes: Generated color palettes
        user_id: User ID
        image_service: ImageService instance

    Returns:
        list: Palette variations

    Raises:
        Exception: If variation creation fails
    """
    logger = logging.getLogger("variation_creator")

    variation_start = time.time()
    try:
        palette_variations = await image_service.create_palette_variations(
            base_image_data=image_data,
            palettes=palettes,
            user_id=user_id,
            blend_strength=0.75,
        )

        if not palette_variations:
            logger.error("No palette variations created")
            raise Exception("Failed to create palette variations")

        logger.info(f"Created {len(palette_variations)} palette variations")
    except Exception as variation_error:
        logger.error(f"Task {task_id}: Error creating palette variations: {str(variation_error)}")
        # Check for specific error types in the error message
        if "memory" in str(variation_error).lower():
            logger.error(f"Task {task_id}: Memory error during variation creation: {variation_error}")
            raise Exception(f"Failed to create palette variations: Memory error: {str(variation_error)}")
        elif "timeout" in str(variation_error).lower():
            logger.error(f"Task {task_id}: Timeout during variation creation: {variation_error}")
            raise Exception(f"Failed to create palette variations: Operation timed out: {str(variation_error)}")
        raise Exception(f"Failed to create palette variations: {str(variation_error)}")

    variation_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Variations created at {variation_end:.2f} (Duration: {(variation_end - variation_start):.2f}s)")

    # Ensure we're returning a list
    return list(palette_variations)


async def store_concept_and_complete_task(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    image_path: str,
    image_url: str,
    palette_variations: list,
    concept_persistence_service: Any,
    task_service: Any,
    task_start_time: float,
) -> None:
    """Store the concept and complete the task.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Description for logo generation
        theme_description: Description for theme generation
        image_path: Path to the stored image
        image_url: URL of the stored image
        palette_variations: Generated palette variations
        concept_persistence_service: ConceptPersistenceService instance
        task_service: TaskService instance
        task_start_time: Task start timestamp

    Raises:
        Exception: If concept storage fails
    """
    logger = logging.getLogger("concept_storage")

    store_concept_start = time.time()
    try:
        stored_concept = await concept_persistence_service.store_concept(
            {
                "user_id": user_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "image_path": image_path,  # Use the path from the stored image
                "image_url": image_url,
                "color_palettes": palette_variations,
                "is_anonymous": True,
            }
        )
    except Exception as concept_e:
        logger.error(f"Task {task_id}: Error storing concept: {concept_e}")
        if "database" in str(concept_e).lower() or "supabase" in str(concept_e).lower():
            logger.error(f"Task {task_id}: Database error during concept storage: {concept_e}")
            raise Exception(f"Database error during concept storage: {concept_e}")
        raise Exception(f"Storing final concept failed: {concept_e}")

    store_concept_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Concept stored at {store_concept_end:.2f} (Duration: {(store_concept_end - store_concept_start):.2f}s)")

    if not stored_concept:
        raise Exception("Failed to store concept")

    concept_id = stored_concept
    if isinstance(stored_concept, dict):
        concept_id = stored_concept.get("id", stored_concept)

    logger.info(f"Stored concept with ID: {concept_id}")

    # Update task status to completed
    await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_COMPLETED, result_id=concept_id)

    task_end_time = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Completed successfully at {task_end_time:.2f} (Total Duration: {(task_end_time - task_start_time):.2f}s)")
    logger.info(f"Completed task {task_id} successfully")


async def download_original_image(task_id: str, original_image_url: str) -> None:
    """Download and verify the original image exists.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image

    Raises:
        Exception: If download fails
    """
    logger = logging.getLogger("image_downloader")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(original_image_url)
            response.raise_for_status()
        logger.debug(f"Successfully verified original image URL: {original_image_url}")
    except Exception as dl_e:
        raise Exception(f"Failed to download original image: {dl_e}")


async def refine_concept_image(
    task_id: str,
    original_image_url: str,
    refinement_prompt: str,
    logo_description: str,
    theme_description: str,
    concept_service: Any,
) -> bytes:
    """Refine the concept image.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image
        refinement_prompt: Prompt for refinement
        logo_description: Original logo description
        theme_description: Original theme description
        concept_service: ConceptService instance

    Returns:
        bytes: The refined image data

    Raises:
        Exception: If refinement fails
    """
    logger = logging.getLogger("concept_refiner")

    try:
        refinement_result = await concept_service.refine_concept(
            original_image_url=original_image_url,
            refinement_prompt=refinement_prompt,
            logo_description=logo_description,
            theme_description=theme_description,
            strength=0.7,  # Control how much to preserve original image
        )
    except Exception as refine_e:
        raise Exception(f"Image refinement operation failed: {refine_e}")

    if not refinement_result or "image_data" not in refinement_result:
        logger.error(f"Task {task_id}: Failed to refine image - missing image data in result")
        raise Exception("No image data returned from refinement service")

    image_data = refinement_result["image_data"]

    # Ensure we have bytes to return
    if not isinstance(image_data, bytes):
        raise Exception("Refined image data is not in bytes format")

    return image_data


async def store_refined_image(task_id: str, refined_image_data: bytes, user_id: str, logo_description: str, theme_description: str, refinement_prompt: str, image_persistence_service: Any) -> tuple:
    """Store the refined image.

    Args:
        task_id: The ID of the task
        refined_image_data: Refined image data
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: Prompt for refinement
        image_persistence_service: ImagePersistenceService instance

    Returns:
        tuple: (image_path, image_url)

    Raises:
        Exception: If image storage fails
    """
    logger = logging.getLogger("image_storer")

    try:
        result = await image_persistence_service.store_image(
            image_data=refined_image_data,
            user_id=user_id,
            metadata={
                "logo_description": logo_description,
                "theme_description": theme_description,
                "refinement_prompt": refinement_prompt,
            },
        )
    except Exception as store_e:
        logger.error(f"Task {task_id}: Error storing refined image: {store_e}")
        if "database" in str(store_e).lower() or "supabase" in str(store_e).lower():
            logger.error(f"Task {task_id}: Database error during refined image storage: {store_e}")
            raise Exception(f"Database error during refined image storage: {store_e}")
        raise Exception(f"Failed to store refined image: {store_e}")

    refined_image_path = result[0]
    refined_image_url = result[1]

    if not refined_image_path or not refined_image_url:
        logger.error(f"Task {task_id}: Failed to store refined image - missing path or URL")
        raise Exception("Failed to store refined image properly")

    return refined_image_path, refined_image_url


async def store_refined_concept(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    refinement_prompt: str,
    refined_image_path: str,
    refined_image_url: str,
    original_image_url: str,
    palette_variations: list,
    concept_persistence_service: Any,
    task_service: Any,
    task_start_time: float,
) -> None:
    """Store the refined concept and complete the task.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: Prompt for refinement
        refined_image_path: Path to the refined image
        refined_image_url: URL of the refined image
        original_image_url: URL of the original image
        palette_variations: Generated palette variations
        concept_persistence_service: ConceptPersistenceService instance
        task_service: TaskService instance
        task_start_time: Task start timestamp

    Raises:
        Exception: If concept storage fails
    """
    logger = logging.getLogger("refined_concept_storer")

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

        task_end_time = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Completed successfully at {task_end_time:.2f} (Total Duration: {(task_end_time - task_start_time):.2f}s)")
        logger.info(f"Task {task_id}: Completed successfully with result {concept_id}")

    except Exception as concept_e:
        logger.error(f"Task {task_id}: Error storing refined concept: {concept_e}")
        if "database" in str(concept_e).lower() or "supabase" in str(concept_e).lower():
            logger.error(f"Task {task_id}: Database error during refined concept storage: {concept_e}")
            raise Exception(f"Database error during refined concept storage: {concept_e}")
        raise Exception(f"Storing refined concept failed: {concept_e}")


async def process_generation_task(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    num_palettes: int,
    services: ServicesDict,
) -> None:
    """Process a concept generation task.

    Args:
        task_id: The ID of the task to process
        user_id: The ID of the user who created the task
        logo_description: Description of the logo to generate
        theme_description: Description of the theme to generate
        num_palettes: Number of color palettes to generate
        services: Dictionary of initialized services

    Returns:
        None
    """
    concept_service = services["concept_service"]
    task_service = services["task_service"]
    image_service = services["image_service"]
    image_persistence_service = services["image_persistence_service"]
    concept_persistence_service = services["concept_persistence_service"]

    logger = logging.getLogger("concept_generation_worker")
    task_start_time = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Starting at {task_start_time:.2f}")
    logger.info(f"Starting concept generation task {task_id}")

    try:
        # Attempt to claim the task - only proceed if successfully claimed
        claimed_task = await task_service.claim_task_if_pending(task_id=task_id, user_id=user_id)
        if not claimed_task:
            logger.info(f"Task {task_id} could not be claimed (already processed, not pending, or claimed by another worker). Skipping.")
            return

        logger.info(f"[WORKER_TIMING] Task {task_id}: Claimed and marked as PROCESSING at {time.time():.2f} ({(time.time() - task_start_time):.2f}s elapsed)")

        logger.debug(f"Generating concept for task {task_id}")

        # Generate base concept with an image
        concept_response = await generate_base_concept(task_id, logo_description, theme_description, user_id, concept_service)

        # Get or download image data
        image_data = await prepare_image_data(task_id, concept_response)

        img_proc_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Image downloaded/prepared at {img_proc_end:.2f}")

        # Store the image in Supabase
        store_img_start = time.time()
        try:
            result = await image_persistence_service.store_image(
                image_data=image_data,
                user_id=user_id,
                metadata={
                    "logo_description": logo_description,
                    "theme_description": theme_description,
                },
            )
        except Exception as store_e:
            logger.error(f"Task {task_id}: Error storing base image: {store_e}")
            if "database" in str(store_e).lower() or "supabase" in str(store_e).lower():
                logger.error(f"Task {task_id}: Database error during image storage: {store_e}")
                raise Exception(f"Database error during image storage: {store_e}")
            raise Exception(f"Storing base image failed: {store_e}")

        store_img_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Base image stored at {store_img_end:.2f} (Duration: {(store_img_end - store_img_start):.2f}s)")

        image_path = result[0]
        stored_image_url = result[1]

        logger.info(f"Stored image at path: {image_path}")

        # Generate color palettes
        raw_palettes = await generate_color_palettes(task_id, theme_description, logo_description, num_palettes, concept_service)

        # Create palette variations
        palette_variations = await create_palette_variations(task_id, image_data, raw_palettes, user_id, image_service)

        # Store concept and complete task
        await store_concept_and_complete_task(
            task_id=task_id,
            user_id=user_id,
            logo_description=logo_description,
            theme_description=theme_description,
            image_path=image_path,
            image_url=stored_image_url,
            palette_variations=palette_variations,
            concept_persistence_service=concept_persistence_service,
            task_service=task_service,
            task_start_time=task_start_time,
        )

    except Exception as e:
        task_fail_time = time.time()
        error_msg = f"Error in generation task: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        logger.error(f"[WORKER_TIMING] Task {task_id}: FAILED at {task_fail_time:.2f} (Total Duration: {(task_fail_time - task_start_time):.2f}s)")

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
    services: ServicesDict,
) -> None:
    """Process a concept refinement task.

    Args:
        task_id: The ID of the task to process
        user_id: The ID of the user who created the task
        refinement_prompt: Instructions for refining the concept
        original_image_url: URL of the original image to refine
        logo_description: Description of the logo
        theme_description: Description of the theme
        services: Dictionary of initialized services

    Returns:
        None
    """
    concept_service = services["concept_service"]
    task_service = services["task_service"]
    image_service = services["image_service"]
    image_persistence_service = services["image_persistence_service"]
    concept_persistence_service = services["concept_persistence_service"]

    logger = logging.getLogger("concept_refinement_worker")
    task_start_time = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Starting at {task_start_time:.2f}")
    logger.info(f"Starting refinement task {task_id}")

    try:
        # Attempt to claim the task - only proceed if successfully claimed
        claimed_task = await task_service.claim_task_if_pending(task_id=task_id, user_id=user_id)
        if not claimed_task:
            logger.info(f"Task {task_id} could not be claimed (already processed, not pending, or claimed by another worker). Skipping.")
            return

        logger.info(f"[WORKER_TIMING] Task {task_id}: Claimed and marked as PROCESSING at {time.time():.2f} ({(time.time() - task_start_time):.2f}s elapsed)")

        logger.info(f"Starting refinement task {task_id} for user {user_id}")

        # Refine and store the image
        try:
            # First, download and verify the original image
            await download_original_image(task_id, original_image_url)

            # Use concept service to refine the image
            refined_image_data = await refine_concept_image(task_id, original_image_url, refinement_prompt, logo_description, theme_description, concept_service)

            # Store the refined image
            refined_image_path, refined_image_url = await store_refined_image(task_id, refined_image_data, user_id, logo_description, theme_description, refinement_prompt, image_persistence_service)

            # Generate color palettes
            raw_palettes = await generate_color_palettes(task_id, f"{theme_description} {refinement_prompt}", logo_description, 4, concept_service)  # Default number of palettes for refinement

            # Apply color palettes to create variations
            palette_variations = await create_palette_variations(task_id, refined_image_data, raw_palettes, user_id, image_service)

            # Store the refined concept
            await store_refined_concept(
                task_id,
                user_id,
                logo_description,
                theme_description,
                refinement_prompt,
                refined_image_path,
                refined_image_url,
                original_image_url,
                palette_variations,
                concept_persistence_service,
                task_service,
                task_start_time,
            )

        except Exception as process_e:
            # Handle process exceptions with specific error
            error_message = f"Refinement processing failed: {str(process_e)}"
            logger.error(f"Task {task_id}: {error_message}")
            await task_service.update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message=error_message,
            )
            return

    except Exception as e:
        # Top-level exception handling
        task_fail_time = time.time()
        error_msg = f"Error in refinement task: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"Exception traceback: {traceback.format_exc()}")
        logger.error(f"[WORKER_TIMING] Task {task_id}: FAILED at {task_fail_time:.2f} (Total Duration: {(task_fail_time - task_start_time):.2f}s)")

        await task_service.update_task_status(
            task_id=task_id,
            status=TASK_STATUS_FAILED,
            error_message=error_msg,
        )


async def process_pubsub_message(message: Dict[str, Any], services: ServicesDict) -> None:
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
        missing_fields = []
        if not user_id:
            missing_fields.append("user_id")
        if not logo_description:
            missing_fields.append("logo_description")
        if not theme_description:
            missing_fields.append("theme_description")

        if missing_fields:
            error_msg = f"Missing required fields for generation task: {', '.join(missing_fields)}"
            logger.error(f"Task {task_id}: {error_msg}")
            await services["task_service"].update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message=error_msg,
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
        missing_fields = []
        if not user_id:
            missing_fields.append("user_id")
        if not refinement_prompt:
            missing_fields.append("refinement_prompt")
        if not original_image_url:
            missing_fields.append("original_image_url")

        if missing_fields:
            error_msg = f"Missing required fields for refinement task: {', '.join(missing_fields)}"
            logger.error(f"Task {task_id}: {error_msg}")
            await services["task_service"].update_task_status(
                task_id=task_id,
                status=TASK_STATUS_FAILED,
                error_message=error_msg,
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


# Using a sync wrapper function to meet functions_framework requirements
@functions_framework.cloud_event
def handle_pubsub(cloud_event: CloudEvent) -> None:
    """Cloud Function entry point triggered by Pub/Sub CloudEvents.

    Args:
        cloud_event: The CloudEvent object containing the Pub/Sub message
    """
    entry_logger = logging.getLogger("concept-worker-entry")
    task_id_for_log = "UNKNOWN_TASK_ID"

    async def _async_handle_pubsub() -> None:
        nonlocal task_id_for_log

        if SERVICES_GLOBAL is None:
            entry_logger.critical("Global services not initialized. Cannot process event.")
            raise Exception("Worker services failed to initialize globally.")

        # Extract and decode the Pub/Sub message data
        if "message" not in cloud_event.data or "data" not in cloud_event.data["message"]:
            entry_logger.error("Invalid CloudEvent format: Missing message data.")
            return

        message_data_base64 = cloud_event.data["message"]["data"]
        message_data_bytes = base64.b64decode(message_data_base64)
        message = json.loads(message_data_bytes.decode("utf-8"))
        task_id_for_log = message.get("task_id", "UNKNOWN_TASK_ID_IN_PAYLOAD")
        entry_logger.info(f"Processing Pub/Sub message for task ID: {task_id_for_log}")

        # Pass the globally initialized services - cast to ensure mypy understands it's not None at this point
        services = cast(ServicesDict, SERVICES_GLOBAL)
        await process_pubsub_message(message, services)

        entry_logger.info(f"Successfully processed task ID: {task_id_for_log}")

    try:
        # Run the async function using asyncio.run
        asyncio.run(_async_handle_pubsub())
    except Exception as e:
        entry_logger.error(f"FATAL error processing task {task_id_for_log}: {e}", exc_info=True)
        # Re-raising signals failure to the platform for potential retries
        raise
