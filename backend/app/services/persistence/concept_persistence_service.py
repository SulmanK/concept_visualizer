"""Concept persistence service implementation.

This module provides services for storing and retrieving concepts from Supabase.
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.exceptions import DatabaseTransactionError
from app.core.supabase.client import SupabaseClient
from app.core.supabase.concept_storage import ConceptStorage
from app.services.persistence.interface import ConceptPersistenceServiceInterface
from app.utils.security.mask import mask_id, mask_path


class PersistenceError(Exception):
    """Exception raised for persistence errors."""

    def __init__(self, message: str):
        """Initialize with error message.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exception raised when a resource is not found."""

    def __init__(self, message: str):
        """Initialize with error message.

        Args:
            message: Error message
        """
        self.message = message
        super().__init__(self.message)


class ConceptPersistenceService(ConceptPersistenceServiceInterface):
    """Service for storing and retrieving concepts."""

    def __init__(self, client: SupabaseClient):
        """Initialize the concept persistence service.

        Args:
            client: Supabase client instance
        """
        self.supabase = client
        self.concept_storage = ConceptStorage(client)
        self.logger = logging.getLogger("concept_persistence_service")

    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """Store a concept and return its ID.

        Args:
            concept_data: Concept data to store, including:
                - user_id: User ID to associate with the concept
                - logo_description: User's logo description
                - theme_description: User's theme description
                - image_path: Path to the generated base image
                - image_url: URL to the generated base image (optional)
                - color_palettes: Optional list of color palette dictionaries

        Returns:
            ID of the stored concept

        Raises:
            PersistenceError: If storage fails
            DatabaseTransactionError: If a multi-step operation fails and cleanup is required
        """
        try:
            # Extract required fields
            user_id = concept_data.get("user_id")
            image_path = concept_data.get("image_path")
            logo_description = concept_data.get("logo_description", "")
            theme_description = concept_data.get("theme_description", "")
            color_palettes = concept_data.get("color_palettes", [])

            # Mask sensitive information for logging
            masked_user_id = mask_id(user_id) if user_id else "None"

            # Create the concept data for storage
            self.logger.info(f"Storing concept for user: {masked_user_id}")
            core_concept_data = {
                "user_id": user_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "image_path": image_path,  # Keep as image_path for compatibility with ConceptStorage
                "is_anonymous": concept_data.get("is_anonymous", True),
                "image_url": concept_data.get("image_url", None),  # Use pre-generated URL if provided
            }

            # Store the concept using ConceptStorage component
            concept = self.concept_storage.store_concept(core_concept_data)
            if not concept:
                self.logger.error("Failed to store concept")
                raise PersistenceError("Failed to store concept")

            concept_id = str(concept["id"])  # Explicit cast to str
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Stored concept with ID: {masked_concept_id}")

            # Insert color variations if provided
            if color_palettes:
                variations = []
                for palette in color_palettes:
                    palette_path = palette.get("image_path")
                    masked_palette_path = mask_path(palette_path) if palette_path else None
                    self.logger.debug(f"Adding palette variation: {palette.get('name')}, path: {masked_palette_path}")

                    variation = {
                        "concept_id": concept_id,
                        "palette_name": palette.get("name"),
                        "colors": palette.get("colors"),
                        "description": palette.get("description"),
                        "image_path": palette.get("image_path"),
                        "image_url": palette.get("image_url"),  # Use pre-generated URL if provided
                    }

                    variations.append(variation)

                try:
                    variations_result = self.concept_storage.store_color_variations(variations)
                    if not variations_result:
                        # Color variations storage failed, we need to clean up the concept
                        self.logger.error(f"Failed to store color variations for concept {masked_concept_id}. Cleaning up...")

                        # Attempt to delete the concept
                        cleanup_successful = await self._delete_concept(concept_id)

                        # Log cleanup result
                        if cleanup_successful:
                            self.logger.info(f"Successfully cleaned up concept {masked_concept_id} after variations storage failure")
                        else:
                            self.logger.error(f"Failed to clean up concept {masked_concept_id} after variations storage failure")

                        # Raise an error indicating the transaction failed but cleanup was attempted
                        cleanup_status = "successful" if cleanup_successful else "failed"
                        raise DatabaseTransactionError(
                            message=f"Failed to store color variations. Concept cleanup was {cleanup_status}.",
                            operation="insert",
                            table="color_variations",
                            details={
                                "concept_id": masked_concept_id,
                                "cleanup_successful": cleanup_successful,
                            },
                        )

                    self.logger.info(f"Stored {len(variations_result)} color variations")
                except Exception as e:
                    # Error during variations storage, attempt to clean up the concept
                    self.logger.error(f"Error storing color variations for concept {masked_concept_id}: {str(e)}. Cleaning up...")

                    # Attempt to delete the concept
                    cleanup_successful = await self._delete_concept(concept_id)

                    # Log cleanup result and re-raise with cleanup information
                    cleanup_msg = "Cleanup " + ("successful" if cleanup_successful else "failed")
                    self.logger.info(f"Color variations error cleanup: {cleanup_msg}")

                    # Raise a transaction error that includes original error and cleanup status
                    raise DatabaseTransactionError(
                        message=f"Error storing color variations: {str(e)}. {cleanup_msg}.",
                        operation="insert",
                        table="color_variations",
                        details={
                            "concept_id": masked_concept_id,
                            "cleanup_successful": cleanup_successful,
                            "original_error": str(e),
                        },
                    )

            return concept_id

        except DatabaseTransactionError:
            # Re-raise transaction errors
            raise
        except Exception as e:
            self.logger.error(f"Error in store_concept: {e}")
            raise PersistenceError(f"Failed to store concept: {str(e)}")

    async def _delete_concept(self, concept_id: str) -> bool:
        """Helper method to delete a concept as part of transaction cleanup.

        Args:
            concept_id: ID of the concept to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Attempting to delete concept {masked_concept_id} during transaction cleanup")

            # Delete directly using the Supabase client since ConceptStorage doesn't have delete_concept
            try:
                # First delete any color variations to avoid constraint violations
                service_client = self.supabase.get_service_role_client()
                if service_client:
                    service_client.table("color_variations").delete().eq("concept_id", concept_id).execute()
                    service_client.table("concepts").delete().eq("id", concept_id).execute()
                else:
                    self.supabase.client.table("color_variations").delete().eq("concept_id", concept_id).execute()
                    self.supabase.client.table("concepts").delete().eq("id", concept_id).execute()

                self.logger.info(f"Successfully deleted concept {masked_concept_id} during cleanup")
                return True
            except Exception as e:
                self.logger.error(f"Failed to delete concept during cleanup: {str(e)}")
                return False

        except Exception as e:
            self.logger.error(f"Error deleting concept during cleanup: {e}")
            return False

    async def get_concept_detail(self, concept_id: str, user_id: str) -> Dict[str, Any]:
        """Get detailed information about a concept.

        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for authorization

        Returns:
            Concept data including color variations

        Raises:
            NotFoundError: If the concept doesn't exist or doesn't belong to the user
            PersistenceError: If retrieval fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Getting concept detail for concept: {masked_concept_id}")

            # Get concept data without generating image URLs - caller must use ImagePersistenceService for URLs
            concept_data = self.concept_storage.get_concept_detail(concept_id, user_id)

            if not concept_data:
                self.logger.warning(f"Concept {masked_concept_id} not found for user {mask_id(user_id)}")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")

            return concept_data

        except NotFoundError:
            # Re-raise NotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error in get_concept_detail: {e}")
            raise PersistenceError(f"Failed to retrieve concept: {str(e)}")

    async def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent concepts for a user.

        Args:
            user_id: User ID to fetch concepts for
            limit: Maximum number of concepts to return

        Returns:
            List of concept summaries ordered by most recent first

        Raises:
            PersistenceError: If retrieval fails
        """
        try:
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Getting recent concepts for user: {masked_user_id}")

            # Get recent concepts from storage - caller must use ImagePersistenceService for URLs
            concepts = self.concept_storage.get_recent_concepts(user_id, limit)

            # Extract all concept IDs for batch fetching variations
            if concepts:
                concept_ids = [concept["id"] for concept in concepts]

                # Batch fetch all variations for these concepts at once
                variations_by_concept = self.concept_storage.get_variations_by_concept_ids(concept_ids)

                # Attach variations to their respective concepts
                for concept in concepts:
                    concept_id = concept["id"]
                    concept["color_variations"] = variations_by_concept.get(concept_id, [])

            # Return the concepts with their variations
            return concepts

        except Exception as e:
            self.logger.error(f"Error in get_recent_concepts: {e}")
            raise PersistenceError(f"Failed to retrieve recent concepts: {str(e)}")

    async def delete_all_concepts(self, user_id: str) -> bool:
        """Delete all concepts belonging to a user.

        Args:
            user_id: User ID for authorization

        Returns:
            True if deletion was successful, False otherwise

        Raises:
            PersistenceError: If deletion fails
        """
        try:
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Deleting all concepts for user: {masked_user_id}")

            # Delete all concepts from storage
            result = self.concept_storage.delete_all_concepts(user_id)

            # Note: Image deletion should be handled separately by the caller using ImagePersistenceService

            return result

        except Exception as e:
            self.logger.error(f"Error in delete_all_concepts: {e}")
            raise PersistenceError(f"Failed to delete concepts: {str(e)}")

    async def get_concept_by_task_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Find a concept associated with a specific task.

        Args:
            task_id: Task ID to search for
            user_id: User ID for authorization

        Returns:
            Concept data if found, None otherwise

        Raises:
            PersistenceError: If retrieval fails
        """
        try:
            masked_task_id = mask_id(task_id)
            self.logger.info(f"Getting concept with task ID: {masked_task_id}")

            # Get concept from storage
            concept = self.concept_storage.get_concept_by_task_id(task_id, user_id)

            # Return the concept as is - no URL generation
            return concept

        except Exception as e:
            self.logger.error(f"Error in get_concept_by_task_id: {e}")
            raise PersistenceError(f"Failed to retrieve concept by task ID: {str(e)}")
