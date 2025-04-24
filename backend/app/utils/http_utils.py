"""HTTP utility functions.

This module provides utility functions for working with HTTP requests.
"""

import logging

import httpx

from app.utils.security.mask import mask_url

logger = logging.getLogger(__name__)


async def download_image(url: str) -> bytes:
    """Download an image from a URL.

    Args:
        url: URL of the image to download

    Returns:
        Image data as bytes

    Raises:
        Exception: If download fails
    """
    try:
        # Mask URL for logging (only show domain or first part)
        masked_url = mask_url(url)
        logger.debug(f"Downloading image from URL: {masked_url}")
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Raise exception for 4XX/5XX responses

            # Get content and validate it's not empty
            content = response.content
            if not content:
                raise ValueError("Downloaded image is empty")

            logger.debug(f"Successfully downloaded image, size: {len(content)} bytes")
            return content
    except Exception as e:
        logger.error(f"Error downloading image from {masked_url}: {str(e)}")
        raise
