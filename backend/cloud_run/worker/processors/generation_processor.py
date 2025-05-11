"""Generation task processor for concept generation tasks.

This module provides the task processor for concept generation tasks.
"""

import asyncio
import time
from typing import Any, Dict, List

import httpx

from app.services.jigsawstack.client import JigsawStackError

from ..stages.concept_storage import store_base_image, store_concept
from ..stages.image_preparation import prepare_image_data_from_response
from ..stages.palette_generation import create_palette_variations, generate_palettes_for_concept
from .base_processor import BaseTaskProcessor


class GenerationTaskProcessor(BaseTaskProcessor):
    """Task processor for concept generation tasks."""

    def __init__(self, task_id: str, user_id: str, message_payload: Dict[str, Any], services: Dict[str, Any]):
        """Initialize the generation task processor.

        Args:
            task_id: The ID of the task to process
            user_id: The ID of the user who created the task
            message_payload: The payload from the Pub/Sub message
            services: Dictionary of service instances
        """
        super().__init__(task_id, user_id, message_payload, services)
        # Extract task-specific fields
        self.logo_description = str(message_payload.get("logo_description", ""))
        self.theme_description = str(message_payload.get("theme_description", ""))
        self.num_palettes = int(message_payload.get("num_palettes", 7))
        self.is_anonymous = bool(message_payload.get("is_anonymous", True))

        # Extract required services
        self.concept_service = services["concept_service"]
        self.image_service = services["image_service"]
        self.image_persistence_service = services["image_persistence_service"]
        self.concept_persistence_service = services["concept_persistence_service"]

    async def _generate_base_image(self) -> Dict[str, Any]:
        """Generate the base concept with image.

        Returns:
            Dict with concept response data

        Raises:
            Exception: If generation fails
        """
        gen_start = time.time()
        self.logger.info(f"Task {self.task_id}: Generating base concept")

        try:
            concept_response = await self.concept_service.generate_concept(
                logo_description=self.logo_description,
                theme_description=self.theme_description,
                user_id=self.user_id,
                skip_persistence=True,  # Skip persistence in the service, we'll handle it here
            )
        except JigsawStackError as jse:
            self.logger.error(f"Task {self.task_id}: JigsawStack API error: {jse}")
            raise Exception(f"Base concept generation failed: JigsawStack API error: {jse}")
        except httpx.TimeoutException as te:
            self.logger.error(f"Task {self.task_id}: Request timeout error: {te}")
            raise Exception(f"Base concept generation failed: API request timed out: {te}")
        except httpx.NetworkError as ne:
            self.logger.error(f"Task {self.task_id}: Network error: {ne}")
            raise Exception(f"Base concept generation failed: Network error: {ne}")
        except Exception as gen_e:
            raise Exception(f"Base concept generation failed: {gen_e}")

        gen_end = time.time()
        self.logger.info(f"[WORKER_TIMING] Task {self.task_id}: Base concept generated at {gen_end:.2f} (Duration: {(gen_end - gen_start):.2f}s)")

        # Log the response keys for debugging
        if concept_response:
            self.logger.debug(f"Concept response keys: {list(concept_response.keys())}")
        else:
            raise Exception("Failed to generate base concept: empty response")

        # Extract the image URL and image data
        image_url = concept_response.get("image_url")

        # Check for valid image_url
        if not image_url:
            self.logger.error(f"Failed to get image_url from concept_response: {concept_response}")
            raise Exception("Failed to generate base concept: missing image_url in response")

        self.logger.debug(f"Generated base concept with image URL: {image_url}")
        return dict(concept_response)

    async def _store_base_image(self, image_data: bytes) -> tuple:
        """Store the base image for the concept.

        Args:
            image_data: Image data as bytes

        Returns:
            Tuple containing image path and URL

        Raises:
            Exception: If storing the image fails
        """
        return await store_base_image(
            task_id=self.task_id,
            image_data=image_data,
            user_id=self.user_id,
            logo_description=self.logo_description,
            theme_description=self.theme_description,
            image_persistence_service=self.image_persistence_service,
        )

    async def _generate_palettes_from_api(self) -> List[dict]:
        """Generate color palettes for the concept.

        Returns:
            List of color palette dictionaries

        Raises:
            Exception: If palette generation fails
        """
        return await generate_palettes_for_concept(
            task_id=self.task_id, theme_desc=self.theme_description, logo_desc=self.logo_description, num=self.num_palettes, concept_service=self.concept_service
        )

    async def _create_variations(self, image_data: bytes, palettes: List[dict]) -> List[dict]:
        """Create palette variations for the concept.

        Args:
            image_data: Image data as bytes
            palettes: List of color palettes

        Returns:
            List of palette variations with URLs

        Raises:
            Exception: If creation of variations fails
        """
        return await create_palette_variations(task_id=self.task_id, image_data=image_data, palettes=palettes, user_id=self.user_id, image_service=self.image_service)

    async def _store_final_concept(self, image_path: str, image_url: str, variations: List[dict]) -> str:
        """Store the final concept in the database.

        Args:
            image_path: Path to the stored image
            image_url: URL of the stored image
            variations: List of palette variations with URLs

        Returns:
            Concept ID

        Raises:
            Exception: If storing the concept fails
        """
        return await store_concept(
            task_id=self.task_id,
            user_id=self.user_id,
            logo_description=self.logo_description,
            theme_description=self.theme_description,
            image_path=image_path,
            image_url=image_url,
            color_palettes=variations,
            is_anonymous=self.is_anonymous,
            concept_persistence_service=self.concept_persistence_service,
        )

    async def process(self) -> None:
        """Process the generation task."""
        self.logger.info(f"Processing generation task {self.task_id}")

        # Attempt to claim the task
        if not await self._claim_task():
            return

        try:
            # Generate the base concept
            concept_response = await self._generate_base_image()

            # Prepare the image data
            image_data = await prepare_image_data_from_response(self.task_id, concept_response)

            # Concurrently store base image and generate palettes
            self.logger.info(f"[WORKER_TIMING] Task {self.task_id}: Starting concurrent base image storage and palette generation")
            concurrent_ops_start_time = time.time()

            store_base_task = asyncio.create_task(self._store_base_image(image_data))
            generate_palettes_task = asyncio.create_task(self._generate_palettes_from_api())

            # Await both tasks and handle potential exceptions
            results = await asyncio.gather(store_base_task, generate_palettes_task, return_exceptions=True)

            # Unpack results and check for errors
            store_img_result, raw_palettes_result = results

            concurrent_ops_end_time = time.time()
            self.logger.info(
                f"[WORKER_TIMING] Task {self.task_id}: Concurrent image store & palette generation finished at {concurrent_ops_end_time:.2f} (Duration: {(concurrent_ops_end_time - concurrent_ops_start_time):.2f}s)"
            )

            if isinstance(store_img_result, Exception):
                self.logger.error(f"Task {self.task_id}: Error during concurrent base image storage: {store_img_result}")
                raise Exception(f"Storing base image failed: {store_img_result}")

            image_path, stored_image_url = store_img_result
            self.logger.info(f"Task {self.task_id}: Base image stored at path: {image_path}")

            if isinstance(raw_palettes_result, Exception):
                self.logger.error(f"Task {self.task_id}: Error during concurrent palette generation: {raw_palettes_result}")
                raise Exception(f"Failed to generate color palettes: {raw_palettes_result}")

            raw_palettes = raw_palettes_result

            # Create palette variations with the image
            variations = await self._create_variations(image_data, raw_palettes)

            # Store the final concept
            concept_id = await self._store_final_concept(image_path, stored_image_url, variations)

            # Update task status to completed
            await self._update_task_completed(concept_id)

        except Exception as e:
            # Update task status to failed
            await self._update_task_failed(f"Error in generation task processing: {str(e)}")
