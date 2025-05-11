"""Concept storage stage for concept generation tasks.

This module provides functions for storing concepts in the database.
"""

import logging
import time
from typing import Any, Dict, List, Tuple, cast


async def store_base_image(task_id: str, image_data: bytes, user_id: str, logo_description: str, theme_description: str, image_persistence_service: Any) -> Tuple[str, str]:
    """Store the base image for a concept.

    Args:
        task_id: The ID of the task
        image_data: Image data as bytes
        user_id: User ID
        logo_description: Logo description
        theme_description: Theme description
        image_persistence_service: ImagePersistenceService instance

    Returns:
        Tuple containing image path and URL

    Raises:
        Exception: If storing the image fails
    """
    logger = logging.getLogger("image_storage")

    store_start = time.time()
    logger.info(f"Task {task_id}: Storing base image, size: {len(image_data)} bytes")

    try:
        # Store the image
        result = await image_persistence_service.store_image(
            image_data=image_data,
            user_id=user_id,
            metadata={
                "logo_description": logo_description,
                "theme_description": theme_description,
            },
        )

        if not result or len(result) != 2:
            raise Exception("Invalid result from store_image")

        image_path, image_url = result

        if not image_path or not image_url:
            raise Exception("Missing image path or URL in store_image result")

        store_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Base image stored at {store_end:.2f} (Duration: {(store_end - store_start):.2f}s)")
        logger.debug(f"Task {task_id}: Stored image at path: {image_path}, URL: {image_url}")

        return image_path, image_url

    except Exception as e:
        logger.error(f"Task {task_id}: Error storing base image: {e}")
        raise Exception(f"Storing base image failed: {e}")


async def store_concept(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    image_path: str,
    image_url: str,
    color_palettes: List[Dict[str, Any]],
    is_anonymous: bool,
    concept_persistence_service: Any,
) -> str:
    """Store concept data in the database.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Logo description
        theme_description: Theme description
        image_path: Path to the stored image
        image_url: URL of the stored image
        color_palettes: List of color palettes with variation URLs
        is_anonymous: Whether the concept is anonymous
        concept_persistence_service: ConceptPersistenceService instance

    Returns:
        Concept ID

    Raises:
        Exception: If storing the concept fails
    """
    logger = logging.getLogger("concept_storage")

    store_concept_start = time.time()
    logger.info(f"Task {task_id}: Storing concept data with {len(color_palettes)} palette variations")

    try:
        stored_concept_data = await concept_persistence_service.store_concept(
            {
                "user_id": user_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "image_path": image_path,
                "image_url": image_url,
                "color_palettes": color_palettes,
                "is_anonymous": is_anonymous,
                "task_id": task_id,  # Link concept to task
            }
        )

        if not stored_concept_data:
            raise Exception("ConceptPersistenceService.store_concept returned None/empty")

        concept_id = cast(str, stored_concept_data)  # Explicitly cast to str
        logger.info(f"Task {task_id}: Stored concept with ID: {concept_id}")

        store_concept_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Concept data stored at {store_concept_end:.2f} (Duration: {(store_concept_end - store_concept_start):.2f}s)")

        return concept_id

    except Exception as e:
        logger.error(f"Task {task_id}: Error storing concept data: {e}")
        raise Exception(f"Storing concept data failed: {e}")
