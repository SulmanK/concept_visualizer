"""Image preparation stage for concept generation tasks.

This module provides functions for preparing image data from concept responses.
"""

import logging
import os
from typing import Any, Dict

import httpx


async def prepare_image_data_from_response(task_id: str, concept_response: Dict[str, Any]) -> bytes:
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
