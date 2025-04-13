"""
Concept persistence service implementation.

This module provides services for storing and retrieving concepts from Supabase.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any

from app.core.supabase.client import SupabaseClient
from app.core.supabase.concept_storage import ConceptStorage
from app.core.supabase.image_storage import ImageStorage
from app.models.concept.domain import ColorPalette, ConceptSummary, ConceptDetail
from app.services.persistence.interface import ConceptPersistenceServiceInterface
from app.utils.security.mask import mask_id, mask_path


class PersistenceError(Exception):
    """Exception raised for persistence errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class NotFoundError(Exception):
    """Exception raised when a resource is not found."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ConceptPersistenceService(ConceptPersistenceServiceInterface):
    """Service for storing and retrieving concepts."""
    
    def __init__(self, client: SupabaseClient):
        """
        Initialize the concept persistence service.
        
        Args:
            client: Supabase client instance
        """
        self.supabase = client
        self.concept_storage = ConceptStorage(client)
        self.image_storage = ImageStorage(client)
        self.logger = logging.getLogger("concept_persistence_service")
    
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """
        Store a concept and return its ID.
        
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
        """
        try:
            # Extract required fields
            user_id = concept_data.get("user_id")
            image_path = concept_data.get("image_path")
            image_url = concept_data.get("image_url")
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
                "image_path": image_path,
                "is_anonymous": concept_data.get("is_anonymous", True)
            }
            
            # Add image_url if provided
            if image_url:
                core_concept_data["image_url"] = image_url
            
            # Store the concept
            concept = self.concept_storage.store_concept(core_concept_data)
            if not concept:
                self.logger.error("Failed to store concept")
                raise PersistenceError("Failed to store concept")
            
            masked_concept_id = mask_id(concept['id'])
            self.logger.info(f"Stored concept with ID: {masked_concept_id}")
            
            # Insert color variations if provided
            if color_palettes:
                variations = []
                for palette in color_palettes:
                    masked_palette_path = mask_path(palette.get("image_path", ""))
                    self.logger.debug(f"Adding palette variation: {palette.get('name')}, path: {masked_palette_path}")
                    
                    variation = {
                        "concept_id": concept["id"],
                        "palette_name": palette.get("name"),
                        "colors": palette.get("colors"),
                        "description": palette.get("description"),
                        "image_path": palette.get("image_path")
                    }
                    
                    # Add image_url if provided
                    if palette.get("image_url"):
                        variation["image_url"] = palette.get("image_url")
                        
                    variations.append(variation)
                
                variations_result = self.concept_storage.store_color_variations(variations)
                self.logger.info(f"Stored {len(variations_result)} color variations")
            
            return concept["id"]
            
        except Exception as e:
            self.logger.error(f"Error in store_concept: {e}")
            raise PersistenceError(f"Failed to store concept: {str(e)}")
    
    async def get_concept_detail(self, concept_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            user_id: User ID for security validation
            
        Returns:
            Concept detail data
            
        Raises:
            NotFoundError: If concept not found
            PersistenceError: If retrieval fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Getting concept detail for concept: {masked_concept_id}")
            
            concept_data = self.concept_storage.get_concept_detail(concept_id, user_id)
            
            if not concept_data:
                self.logger.warning(f"Concept {masked_concept_id} not found for user {mask_id(user_id)}")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")
            
            # Add signed URLs for images
            base_image_url = self.image_storage.get_image_url(
                concept_data["base_image_path"], 
                "concept-images"
            )
            concept_data["base_image_url"] = base_image_url
            
            # Process color variations 
            if "color_variations" in concept_data and concept_data["color_variations"]:
                for variation in concept_data["color_variations"]:
                    image_path = variation.get("image_path")
                    if image_path:
                        variation["image_url"] = self.image_storage.get_image_url(
                            image_path, 
                            "palette-images"
                        )
            
            return concept_data
            
        except NotFoundError:
            # Re-raise NotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error in get_concept_detail: {e}")
            raise PersistenceError(f"Failed to retrieve concept: {str(e)}")
    
    async def get_recent_concepts(self, user_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent concepts for a user.
        
        Args:
            user_id: User ID to retrieve concepts for
            limit: Maximum number of concepts to return
            
        Returns:
            List of recent concepts
            
        Raises:
            PersistenceError: If retrieval fails
        """
        try:
            masked_user_id = mask_id(user_id)
            self.logger.info(f"Getting recent concepts for user: {masked_user_id}")
            
            # Get recent concepts from storage
            concepts = self.concept_storage.get_recent_concepts(user_id, limit)
            
            # Process concepts to include image URLs
            result = []
            for concept in concepts:
                summary = {
                    "id": concept.get("id"),
                    "logo_description": concept.get("logo_description"),
                    "theme_description": concept.get("theme_description"),
                    "created_at": concept.get("created_at"),
                }
                
                # Add image URL
                image_path = concept.get("base_image_path")
                if image_path:
                    summary["image_path"] = image_path
                    summary["image_url"] = self.image_storage.get_image_url(
                        image_path, 
                        "concept-images"
                    )
                
                result.append(summary)
                
            return result
            
        except Exception as e:
            self.logger.error(f"Error getting recent concepts: {e}")
            raise PersistenceError(f"Failed to retrieve recent concepts: {str(e)}")
    
    async def delete_all_concepts(self, user_id: str) -> bool:
        """
        Delete all concepts for a user.
        
        Args:
            user_id: User ID to delete concepts for
            
        Returns:
            True if successful
            
        Raises:
            PersistenceError: If deletion fails
        """
        try:
            masked_user_id = mask_id(user_id)
            self.logger.warning(f"Deleting all concepts for user: {masked_user_id}")
            
            # Delete all concepts
            deleted = self.concept_storage.delete_concepts(user_id)
            
            self.logger.info(f"Deleted {deleted} concepts for user: {masked_user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting concepts: {e}")
            raise PersistenceError(f"Failed to delete concepts: {str(e)}")
    
    async def get_concept_by_task_id(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a concept by its task ID.
        
        Args:
            task_id: Task ID to retrieve the concept for
            user_id: User ID for security validation
            
        Returns:
            Concept data if found, None otherwise
            
        Raises:
            PersistenceError: If retrieval fails
        """
        try:
            masked_task_id = mask_id(task_id)
            self.logger.info(f"Getting concept by task ID: {masked_task_id}")
            
            # Get the concept from storage
            concept = self.concept_storage.get_concept_by_task_id(task_id, user_id)
            
            # If no concept found, return None
            if not concept:
                self.logger.info(f"No concept found for task ID: {masked_task_id}")
                return None
                
            # Add signed URL for image
            image_path = concept.get("base_image_path")
            if image_path:
                concept["base_image_url"] = self.image_storage.get_image_url(
                    image_path, 
                    "concept-images"
                )
                
            return concept
            
        except Exception as e:
            self.logger.error(f"Error getting concept by task ID: {e}")
            raise PersistenceError(f"Failed to retrieve concept by task ID: {str(e)}") 