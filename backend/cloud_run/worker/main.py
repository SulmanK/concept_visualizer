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
from typing import Any, Dict, Optional

import functions_framework
from cloudevents.http import CloudEvent

from app.core.config import settings
from app.core.constants import TASK_STATUS_FAILED, TASK_TYPE_GENERATION, TASK_TYPE_REFINEMENT
from app.core.supabase.client import SupabaseClient
from app.services.concept.service import ConceptService
from app.services.image.processing_service import ImageProcessingService
from app.services.image.service import ImageService
from app.services.jigsawstack.client import JigsawStackClient
from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.persistence.image_persistence_service import ImagePersistenceService
from app.services.task.service import TaskService

from .processors.base_processor import BaseTaskProcessor
from .processors.generation_processor import GenerationTaskProcessor
from .processors.refinement_processor import RefinementTaskProcessor

# Configure logging for Google Cloud Functions
log_level_str = os.environ.get("CONCEPT_LOG_LEVEL", "INFO").upper()
log_level = getattr(logging, log_level_str, logging.INFO)

# Configure root logger for Google Cloud Logging compatibility
root_logger = logging.getLogger()
root_logger.setLevel(log_level)

# Remove any existing handlers to avoid conflicts
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Create console handler with structured format for Google Cloud Logging
console_handler = logging.StreamHandler()
console_handler.setLevel(log_level)

# Use structured format that works well with Google Cloud Logging
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
console_handler.setFormatter(formatter)
root_logger.addHandler(console_handler)

# Ensure we capture all levels including DEBUG if needed
if log_level == logging.DEBUG:
    console_handler.setLevel(logging.DEBUG)

logger = logging.getLogger("concept-worker-main")
logger.info(f"Logging configured at level: {log_level_str}")

# Type for our services dictionary
ServicesDict = Dict[str, Any]

# Global service instances
SERVICES_GLOBAL: Optional[Dict[str, Any]] = None

# Retry configuration for service initialization
INITIALIZATION_RETRIES = 3
INITIALIZATION_DELAY = 2  # seconds


def initialize_services_with_retry() -> None:
    """Initialize services with retry logic for cold start resilience."""
    global SERVICES_GLOBAL

    for attempt in range(1, INITIALIZATION_RETRIES + 1):
        try:
            logger.info(f"Attempting service initialization (attempt {attempt}/{INITIALIZATION_RETRIES})")

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
            logger.info(f"Global services initialized successfully on attempt {attempt}")
            return
        except Exception as e:
            logger.warning(f"Service initialization attempt {attempt} failed: {e}")
            if attempt < INITIALIZATION_RETRIES:
                delay = INITIALIZATION_DELAY * attempt  # Exponential backoff
                logger.info(f"Retrying service initialization in {delay} seconds...")
                time.sleep(delay)
            else:
                logger.critical(f"Failed to initialize services after {INITIALIZATION_RETRIES} attempts")
                SERVICES_GLOBAL = None
                raise


# Initialize on module import - global service initialization with retry
logger.info("Initializing services globally for worker instance...")
try:
    initialize_services_with_retry()
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


async def process_pubsub_message(message: Dict[str, Any], services: ServicesDict) -> None:
    """Process a Pub/Sub message.

    Args:
        message: The Pub/Sub message to process
        services: The global services dictionary
    """
    task_type = message.get("task_type")
    task_id = message.get("task_id")
    user_id = message.get("user_id")

    logger.info(f"[TASK {task_id}] Starting message processing - Type: {task_type}, User: {user_id}")

    if not task_id or not user_id:
        logger.error(f"[TASK {task_id}] VALIDATION ERROR: Missing required task_id or user_id. Task_id: {task_id}, User_id: {user_id}")
        # Optionally, try to update task status to FAILED if task_id is known
        if task_id and "task_service" in services:
            try:
                await services["task_service"].update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message="Core task information missing in message payload (task_id or user_id)")
                logger.info(f"[TASK {task_id}] Updated task status to FAILED due to missing required fields")
            except Exception as e:
                logger.error(f"[TASK {task_id}] Failed to update task status: {e}")
        return

    processor: Optional[BaseTaskProcessor] = None

    logger.info(f"[TASK {task_id}] Validating task type: {task_type}")

    if task_type == TASK_TYPE_GENERATION:
        # Validate required fields for generation
        logo_description = message.get("logo_description")
        theme_description = message.get("theme_description")
        if not logo_description or not theme_description:
            error_msg = "Missing logo/theme description for generation task."
            logger.error(f"[TASK {task_id}] VALIDATION ERROR: {error_msg}")
            try:
                await services["task_service"].update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=error_msg)
                logger.info(f"[TASK {task_id}] Updated task status to FAILED due to validation error")
            except Exception as e:
                logger.error(f"[TASK {task_id}] Failed to update task status: {e}")
            return
        logger.info(f"[TASK {task_id}] Creating GenerationTaskProcessor")
        processor = GenerationTaskProcessor(task_id, user_id, message, services)

    elif task_type == TASK_TYPE_REFINEMENT:
        # Validate required fields for refinement
        refinement_prompt = message.get("refinement_prompt")
        original_image_url = message.get("original_image_url")
        if not refinement_prompt or not original_image_url:
            error_msg = "Missing prompt/original URL for refinement task."
            logger.error(f"[TASK {task_id}] VALIDATION ERROR: {error_msg}")
            try:
                await services["task_service"].update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=error_msg)
                logger.info(f"[TASK {task_id}] Updated task status to FAILED due to validation error")
            except Exception as e:
                logger.error(f"[TASK {task_id}] Failed to update task status: {e}")
            return
        logger.info(f"[TASK {task_id}] Creating RefinementTaskProcessor")
        processor = RefinementTaskProcessor(task_id, user_id, message, services)
    else:
        error_msg = f"Unknown task type: {task_type}"
        logger.error(f"[TASK {task_id}] VALIDATION ERROR: {error_msg}")
        try:
            await services["task_service"].update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=error_msg)
            logger.info(f"[TASK {task_id}] Updated task status to FAILED due to unknown task type")
        except Exception as e:
            logger.error(f"[TASK {task_id}] Failed to update task status: {e}")
        return

    if processor:
        logger.info(f"[TASK {task_id}] Starting processor execution")
        try:
            await processor.process()
            logger.info(f"[TASK {task_id}] Processor completed successfully")
        except Exception as e:
            logger.error(f"[TASK {task_id}] PROCESSOR ERROR: {e}")
            logger.error(f"[TASK {task_id}] Exception type: {type(e).__name__}")
            logger.error(f"[TASK {task_id}] Full traceback:\n{traceback.format_exc()}")
            # Re-raise to propagate the error up
            raise
    else:
        logger.error(f"[TASK {task_id}] ERROR: No processor created")


@functions_framework.cloud_event
def handle_pubsub(cloud_event: CloudEvent) -> None:
    """Handle a Pub/Sub CloudEvent.

    This is the entry point for the Cloud Function.

    Args:
        cloud_event: The CloudEvent from Pub/Sub
    """
    logger.info("=== Cloud Function invoked: handle_pubsub ===")

    # Define an internal async helper function
    async def _async_handle_pubsub() -> None:
        logger.info("Starting async message processing")

        # Process the Pub/Sub event asynchronously
        if SERVICES_GLOBAL is None:
            logger.warning("SERVICES_GLOBAL is None, attempting to re-initialize services")
            try:
                initialize_services_with_retry()
            except Exception as e:
                logger.critical(f"Failed to re-initialize services during message processing: {e}")
                return

            if SERVICES_GLOBAL is None:
                logger.critical("SERVICES_GLOBAL is still None after re-initialization, cannot process message")
                return

        # Extract the message data
        try:
            logger.debug("Extracting message data from CloudEvent")
            event_data = cloud_event.data
            if "message" not in event_data:
                logger.error("ERROR: No message field in event data")
                logger.error(f"Event data keys: {list(event_data.keys()) if event_data else 'None'}")
                return

            # Extract and decode the message
            message_data = event_data["message"]
            if "data" not in message_data:
                logger.error("ERROR: No data field in message data")
                logger.error(f"Message data keys: {list(message_data.keys()) if message_data else 'None'}")
                return

            # Base64 decode the message data
            encoded_data = message_data["data"]
            decoded_data = base64.b64decode(encoded_data).decode("utf-8")
            logger.debug(f"Successfully decoded message data: {decoded_data[:200]}...")

            message_payload = json.loads(decoded_data)
            task_id = message_payload.get("task_id", "unknown")
            task_type = message_payload.get("task_type", "unknown")

            logger.info(f"Processing Pub/Sub message - Task ID: {task_id}, Type: {task_type}")
            logger.debug(f"Full message payload: {message_payload}")

            # Process the message
            await process_pubsub_message(message_payload, SERVICES_GLOBAL)

            logger.info(f"Successfully completed processing for task {task_id}")

        except json.JSONDecodeError as je:
            logger.error(f"JSON DECODE ERROR: {je}")
            logger.error(f"Raw decoded data: {decoded_data if 'decoded_data' in locals() else 'Not available'}")
        except Exception as e:
            logger.error(f"CRITICAL ERROR processing Pub/Sub message: {e}")
            logger.error(f"Exception type: {type(e).__name__}")
            logger.error(f"Full traceback:\n{traceback.format_exc()}")
            # Re-raise to ensure Cloud Functions sees this as a failure
            raise

    # Run the async function
    try:
        asyncio.run(_async_handle_pubsub())
        logger.info("=== Cloud Function completed successfully ===")
    except Exception as e:
        logger.critical(f"FATAL ERROR in handle_pubsub: {e}")
        logger.critical(f"Exception type: {type(e).__name__}")
        logger.critical(f"Full exception traceback:\n{traceback.format_exc()}")
        # Re-raising signals failure to the platform for potential retries
        raise
