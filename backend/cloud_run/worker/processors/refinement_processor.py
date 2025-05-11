"""Refinement task processor for concept refinement tasks.

This module provides the task processor for concept refinement tasks.
"""

from typing import Any, Dict

from ..stages.refinement import download_original_image, refine_concept_image, store_refined_concept, store_refined_image
from .base_processor import BaseTaskProcessor


class RefinementTaskProcessor(BaseTaskProcessor):
    """Task processor for concept refinement tasks."""

    def __init__(self, task_id: str, user_id: str, message_payload: Dict[str, Any], services: Dict[str, Any]):
        """Initialize the refinement task processor.

        Args:
            task_id: The ID of the task to process
            user_id: The ID of the user who created the task
            message_payload: The payload from the Pub/Sub message
            services: Dictionary of service instances
        """
        super().__init__(task_id, user_id, message_payload, services)
        # Extract task-specific fields
        self.refinement_prompt = str(message_payload.get("refinement_prompt", ""))
        self.original_image_url = str(message_payload.get("original_image_url", ""))
        self.logo_description = str(message_payload.get("logo_description", ""))
        self.theme_description = str(message_payload.get("theme_description", ""))

        # Extract required services
        self.concept_service = services["concept_service"]
        self.image_service = services["image_service"]
        self.image_persistence_service = services["image_persistence_service"]
        self.concept_persistence_service = services["concept_persistence_service"]

    async def _download_original(self) -> bytes:
        """Download the original image for refinement.

        Returns:
            bytes: The image data

        Raises:
            Exception: If downloading the image fails
        """
        return await download_original_image(task_id=self.task_id, original_image_url=self.original_image_url)

    async def _refine_image(self) -> bytes:
        """Refine the image based on the refinement prompt.

        Returns:
            bytes: The refined image data

        Raises:
            Exception: If refinement fails
        """
        return await refine_concept_image(
            task_id=self.task_id,
            original_image_url=self.original_image_url,
            refinement_prompt=self.refinement_prompt,
            logo_description=self.logo_description,
            theme_description=self.theme_description,
            concept_service=self.concept_service,
        )

    async def _store_refined_image(self, refined_image_data: bytes) -> tuple:
        """Store the refined image.

        Args:
            refined_image_data: The refined image data

        Returns:
            Tuple containing image path and URL

        Raises:
            Exception: If storing the image fails
        """
        return await store_refined_image(
            task_id=self.task_id,
            refined_image_data=refined_image_data,
            user_id=self.user_id,
            logo_description=self.logo_description,
            theme_description=self.theme_description,
            refinement_prompt=self.refinement_prompt,
            image_persistence_service=self.image_persistence_service,
        )

    async def _store_refined_concept_data(self, refined_image_path: str, refined_image_url: str) -> str:
        """Store the refined concept data.

        Args:
            refined_image_path: Path to the stored refined image
            refined_image_url: URL of the stored refined image

        Returns:
            Concept ID

        Raises:
            Exception: If storing the concept data fails
        """
        return await store_refined_concept(
            task_id=self.task_id,
            user_id=self.user_id,
            logo_description=self.logo_description,
            theme_description=self.theme_description,
            refinement_prompt=self.refinement_prompt,
            refined_image_path=refined_image_path,
            refined_image_url=refined_image_url,
            original_image_url=self.original_image_url,
            concept_persistence_service=self.concept_persistence_service,
        )

    async def process(self) -> None:
        """Process the refinement task."""
        self.logger.info(f"Processing refinement task {self.task_id}")

        # Attempt to claim the task
        if not await self._claim_task():
            return

        try:
            # Refine the image
            refined_image_data = await self._refine_image()

            # Store the refined image
            refined_image_path, refined_image_url = await self._store_refined_image(refined_image_data)
            self.logger.info(f"Task {self.task_id}: Refined image stored at path: {refined_image_path}")

            # Store the refined concept data
            concept_id = await self._store_refined_concept_data(refined_image_path, refined_image_url)

            # Update task status to completed
            await self._update_task_completed(concept_id)

        except Exception as e:
            # Update task status to failed
            await self._update_task_failed(f"Error in refinement task processing: {str(e)}")
