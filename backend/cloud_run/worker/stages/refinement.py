"""Refinement stages for concept refinement tasks.

This module provides functions for refining concept images.
"""

import logging
import time
from typing import Any, Tuple, cast

import httpx

from app.services.jigsawstack.client import JigsawStackError


async def download_original_image(task_id: str, original_image_url: str) -> bytes:
    """Download the original image for refinement.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image

    Returns:
        bytes: The image data

    Raises:
        Exception: If downloading the image fails
    """
    logger = logging.getLogger("image_downloader")

    logger.info(f"Task {task_id}: Downloading original image from: {original_image_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(original_image_url)
            response.raise_for_status()
            image_data = response.content

        if not image_data or not isinstance(image_data, bytes):
            raise Exception("No valid image data downloaded")

        logger.info(f"Task {task_id}: Downloaded original image, size: {len(image_data)} bytes")
        return image_data
    except Exception as e:
        logger.error(f"Task {task_id}: Error downloading original image: {e}")
        raise Exception(f"Failed to download original image: {e}")


async def refine_concept_image(
    task_id: str,
    original_image_url: str,
    refinement_prompt: str,
    logo_description: str,
    theme_description: str,
    concept_service: Any,
) -> bytes:
    """Refine a concept image based on a refinement prompt.

    Args:
        task_id: The ID of the task
        original_image_url: URL of the original image
        refinement_prompt: User's refinement instructions
        logo_description: Original logo description
        theme_description: Original theme description
        concept_service: ConceptService instance

    Returns:
        bytes: The refined image data

    Raises:
        Exception: If refinement fails
    """
    logger = logging.getLogger("image_refiner")

    refine_start = time.time()
    logger.info(f"Task {task_id}: Refining image with prompt: {refinement_prompt}")

    try:
        refined_concept = await concept_service.refine_concept(
            original_image_url=original_image_url,
            refinement_prompt=refinement_prompt,
            logo_description=logo_description,
            theme_description=theme_description,
            skip_persistence=True,  # We'll handle persistence separately
            strength=0.7,  # Control how much to preserve original image
        )
    except JigsawStackError as jse:
        logger.error(f"Task {task_id}: JigsawStack API error in refinement: {jse}")
        raise Exception(f"Image refinement failed: JigsawStack API error: {jse}")
    except Exception as e:
        logger.error(f"Task {task_id}: Error refining image: {e}")
        raise Exception(f"Image refinement failed: {e}")

    refine_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Image refined at {refine_end:.2f} (Duration: {(refine_end - refine_start):.2f}s)")

    # Extract the image data
    refined_image_data = refined_concept.get("image_data")
    if not refined_image_data or not isinstance(refined_image_data, bytes):
        # Try to get the image URL and download it
        refined_image_url = refined_concept.get("image_url")
        if refined_image_url:
            logger.info(f"Task {task_id}: No image data in refined concept, downloading from URL: {refined_image_url}")
            try:
                async with httpx.AsyncClient() as client:
                    response = await client.get(refined_image_url)
                    response.raise_for_status()
                    refined_image_data = response.content
            except Exception as e:
                logger.error(f"Task {task_id}: Error downloading refined image: {e}")
                raise Exception(f"Failed to download refined image: {e}")
        else:
            raise Exception("No image data or URL in refined concept response")

    logger.info(f"Task {task_id}: Refined image obtained, size: {len(refined_image_data)} bytes")
    return cast(bytes, refined_image_data)


async def store_refined_image(
    task_id: str, refined_image_data: bytes, user_id: str, logo_description: str, theme_description: str, refinement_prompt: str, image_persistence_service: Any
) -> Tuple[str, str]:
    """Store the refined image.

    Args:
        task_id: The ID of the task
        refined_image_data: The refined image data
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: User's refinement instructions
        image_persistence_service: ImagePersistenceService instance

    Returns:
        Tuple containing image path and URL

    Raises:
        Exception: If storing the image fails
    """
    logger = logging.getLogger("image_storage")

    store_start = time.time()
    logger.info(f"Task {task_id}: Storing refined image, size: {len(refined_image_data)} bytes")

    try:
        # Store the refined image
        result = await image_persistence_service.store_image(
            image_data=refined_image_data,
            user_id=user_id,
            metadata={
                "logo_description": logo_description,
                "theme_description": theme_description,
                "refinement_prompt": refinement_prompt,
                "task_id": task_id,
                "is_refinement": True,
            },
        )

        if not result or len(result) != 2:
            raise Exception("Invalid result from store_image")

        image_path, image_url = result

        if not image_path or not image_url:
            raise Exception("Missing image path or URL in store_image result")

        store_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Refined image stored at {store_end:.2f} (Duration: {(store_end - store_start):.2f}s)")
        logger.debug(f"Task {task_id}: Stored refined image at path: {image_path}, URL: {image_url}")

        return image_path, image_url

    except Exception as e:
        logger.error(f"Task {task_id}: Error storing refined image: {e}")
        raise Exception(f"Storing refined image failed: {e}")


async def store_refined_concept(
    task_id: str,
    user_id: str,
    logo_description: str,
    theme_description: str,
    refinement_prompt: str,
    refined_image_path: str,
    refined_image_url: str,
    original_image_url: str,
    concept_persistence_service: Any,
) -> str:
    """Store refined concept data in the database.

    Args:
        task_id: The ID of the task
        user_id: User ID
        logo_description: Original logo description
        theme_description: Original theme description
        refinement_prompt: User's refinement instructions
        refined_image_path: Path to the stored refined image
        refined_image_url: URL of the stored refined image
        original_image_url: URL of the original image
        concept_persistence_service: ConceptPersistenceService instance

    Returns:
        Concept ID

    Raises:
        Exception: If storing the concept fails
    """
    logger = logging.getLogger("concept_storage")

    store_concept_start = time.time()
    logger.info(f"Task {task_id}: Storing refined concept data")

    try:
        stored_concept_data = await concept_persistence_service.store_concept(
            {
                "user_id": user_id,
                "logo_description": logo_description,
                "theme_description": f"{theme_description} {refinement_prompt}",
                "image_path": refined_image_path,
                "image_url": refined_image_url,
                "color_palettes": [],  # Empty list since we're not generating variations
                "is_anonymous": True,
                "refinement_prompt": refinement_prompt,
                "original_image_url": original_image_url,
                "task_id": task_id,  # Link concept to task
            }
        )

        if not stored_concept_data:
            raise Exception("ConceptPersistenceService.store_concept returned None/empty")

        concept_id = cast(str, stored_concept_data)  # Explicitly cast to str
        logger.info(f"Task {task_id}: Stored refined concept with ID: {concept_id}")

        store_concept_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Refined concept data stored at {store_concept_end:.2f} (Duration: {(store_concept_end - store_concept_start):.2f}s)")

        return concept_id

    except Exception as e:
        logger.error(f"Task {task_id}: Error storing refined concept data: {e}")
        if "database" in str(e).lower() or "supabase" in str(e).lower():
            logger.error(f"Task {task_id}: Database error during refined concept storage: {e}")
            raise Exception(f"Database error during refined concept storage: {e}")
        raise Exception(f"Storing refined concept data failed: {e}")
