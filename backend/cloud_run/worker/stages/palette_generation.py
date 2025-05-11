"""Palette generation stage for concept generation tasks.

This module provides functions for generating color palettes for concepts.
"""

import logging
import time
from typing import Any, Dict, List, cast

from app.services.jigsawstack.client import JigsawStackError


async def generate_palettes_for_concept(task_id: str, theme_desc: str, logo_desc: str, num: int, concept_service: Any) -> List[Dict[str, Any]]:
    """Generate color palettes for a concept.

    Args:
        task_id: The ID of the task
        theme_desc: Theme description for palette generation
        logo_desc: Logo description for palette generation
        num: Number of palettes to generate
        concept_service: ConceptService instance

    Returns:
        List of color palette dictionaries

    Raises:
        Exception: If palette generation fails
    """
    logger = logging.getLogger("palette_generator")

    palette_start = time.time()
    logger.info(f"Task {task_id}: Generating {num} color palettes")
    try:
        palettes = await concept_service.generate_color_palettes(
            theme_description=theme_desc,
            logo_description=logo_desc,
            num_palettes=num,
        )
    except JigsawStackError as jse:
        logger.error(f"Task {task_id}: JigsawStack API error generating palettes: {jse}")
        raise Exception(f"Color palette generation failed: JigsawStack API error: {jse}")
    except Exception as gen_e:
        logger.error(f"Task {task_id}: Error generating color palettes: {gen_e}")
        raise Exception(f"Color palette generation failed: {gen_e}")

    palette_end = time.time()
    logger.info(f"[WORKER_TIMING] Task {task_id}: Color palettes generated at {palette_end:.2f} (Duration: {(palette_end - palette_start):.2f}s)")

    if not palettes or not isinstance(palettes, list):
        logger.error(f"Task {task_id}: Invalid palettes response: {palettes}")
        raise Exception("Color palette generation failed: Invalid response")

    logger.info(f"Task {task_id}: Generated {len(palettes)} color palettes")
    return cast(List[Dict[str, Any]], palettes)


async def create_palette_variations(
    task_id: str,
    image_data: bytes,
    palettes: List[Dict[str, Any]],
    user_id: str,
    image_service: Any,
) -> List[Dict[str, Any]]:
    """Create image variations using the given palettes.

    Args:
        task_id: The ID of the task
        image_data: Image data as bytes
        palettes: List of color palettes
        user_id: User ID
        image_service: ImageService instance

    Returns:
        List of palette variations with URLs

    Raises:
        Exception: If creation of variations fails
    """
    logger = logging.getLogger("variation_creator")

    variation_start = time.time()
    logger.info(f"Task {task_id}: Creating {len(palettes)} palette variations")

    try:
        # Use the create_palette_variations method from ImageService
        palette_variations = await image_service.create_palette_variations(
            base_image_data=image_data,
            palettes=palettes,
            user_id=user_id,
            blend_strength=0.75,
        )

        if not palette_variations:
            raise Exception("Failed to create any palette variations")

        variation_end = time.time()
        logger.info(f"[WORKER_TIMING] Task {task_id}: Created {len(palette_variations)} palette variations at {variation_end:.2f} (Duration: {(variation_end - variation_start):.2f}s)")

        return cast(List[Dict[str, Any]], palette_variations)

    except Exception as e:
        logger.error(f"Task {task_id}: Error creating palette variations: {e}")
        # Check for specific error types in the error message
        if "memory" in str(e).lower():
            logger.error(f"Task {task_id}: Memory error during variation creation: {e}")
            raise Exception(f"Failed to create palette variations: Memory error: {str(e)}")
        elif "timeout" in str(e).lower():
            logger.error(f"Task {task_id}: Timeout during variation creation: {e}")
            raise Exception(f"Failed to create palette variations: Operation timed out: {str(e)}")
        raise Exception(f"Creating palette variations failed: {str(e)}")
