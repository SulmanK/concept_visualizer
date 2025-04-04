"""
Concept storage service implementation.

This module provides services for storing and retrieving concepts from Supabase.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any

from app.core.supabase.client import SupabaseClient
from app.core.supabase.concept_storage import ConceptStorage
from app.core.supabase.image_storage import ImageStorage
from app.models.concept import ColorPalette, ConceptSummary, ConceptDetail
from app.services.interfaces import StorageServiceInterface
from app.utils.security.mask import mask_id, mask_path


class ConceptStorageService(StorageServiceInterface):
    """Service for storing and retrieving concepts."""
    
    def __init__(self, client: SupabaseClient):
        """
        Initialize concept storage service with a Supabase client.
        
        Args:
            client: Client for interacting with Supabase
        """
        self.supabase_client = client
        self.concept_storage = ConceptStorage(client)
        self.image_storage = ImageStorage(client)
        self.logger = logging.getLogger("concept_storage_service")
    
    async def store_concept(self, concept_data: Dict[str, Any]) -> str:
        """
        Store a concept and return its ID.
        
        Args:
            concept_data: Concept data to store, including:
                - session_id: Session ID to associate with the concept
                - logo_description: User's logo description
                - theme_description: User's theme description
                - base_image_path: Path to the generated base image
                - color_palettes: Optional list of color palette dictionaries
                
        Returns:
            ID of the stored concept
            
        Raises:
            StorageError: If storage fails
        """
        try:
            # Extract required fields
            session_id = concept_data.get("session_id")
            base_image_path = concept_data.get("base_image_path")
            logo_description = concept_data.get("logo_description", "")
            theme_description = concept_data.get("theme_description", "")
            color_palettes = concept_data.get("color_palettes", [])
            
            # Mask sensitive information for logging
            masked_session = mask_id(session_id) if session_id else "None"
            
            # Create the concept data for storage
            self.logger.info(f"Storing concept for session: {masked_session}")
            core_concept_data = {
                "session_id": session_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "base_image_path": base_image_path
            }
            
            # Store the concept
            concept = self.concept_storage.store_concept(core_concept_data)
            if not concept:
                self.logger.error("Failed to store concept")
                raise StorageError("Failed to store concept")
            
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
                    variations.append(variation)
                
                variations_result = self.concept_storage.store_color_variations(variations)
                self.logger.info(f"Stored {len(variations_result)} color variations")
            
            return concept["id"]
            
        except Exception as e:
            self.logger.error(f"Error in store_concept: {e}")
            raise StorageError(f"Failed to store concept: {str(e)}")
    
    async def get_concept(self, concept_id: str) -> Dict[str, Any]:
        """
        Retrieve a concept by ID.
        
        Args:
            concept_id: ID of the concept to retrieve
            
        Returns:
            Concept data
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If retrieval fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Getting concept detail for concept: {masked_concept_id}")
            
            concept_data = self.concept_storage.get_concept_by_id(concept_id)
            
            if not concept_data:
                self.logger.warning(f"Concept {masked_concept_id} not found")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")
            
            # Add public URLs for images
            base_image_url = self.image_storage.get_image_url(
                concept_data["base_image_path"], 
                "concept-images"
            )
            concept_data["base_image_url"] = base_image_url
            
            # Process color variations 
            if "color_variations" in concept_data and concept_data["color_variations"]:
                for variation in concept_data["color_variations"]:
                    image_url = self.image_storage.get_image_url(
                        variation["image_path"], 
                        "palette-images"
                    )
                    variation["image_url"] = image_url
            
            return concept_data
            
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error in get_concept: {e}")
            raise StorageError(f"Failed to retrieve concept: {str(e)}")
    
    async def update_concept(self, concept_id: str, concept_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update a concept.
        
        Args:
            concept_id: ID of the concept to update
            concept_data: Updated data
            
        Returns:
            Updated concept data
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If update fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Updating concept: {masked_concept_id}")
            
            # Check if concept exists
            existing = self.concept_storage.get_concept_by_id(concept_id)
            if not existing:
                self.logger.warning(f"Concept {masked_concept_id} not found for update")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")
            
            # Update the concept
            updated = self.concept_storage.update_concept(concept_id, concept_data)
            if not updated:
                raise StorageError(f"Failed to update concept {masked_concept_id}")
            
            # If there are color_palettes in the update data, handle them
            if "color_palettes" in concept_data and concept_data["color_palettes"]:
                variations = []
                for palette in concept_data["color_palettes"]:
                    variation = {
                        "concept_id": concept_id,
                        "palette_name": palette.get("name"),
                        "colors": palette.get("colors"),
                        "description": palette.get("description"),
                        "image_path": palette.get("image_path")
                    }
                    variations.append(variation)
                
                # Remove existing variations and add new ones
                self.concept_storage.delete_color_variations(concept_id)
                self.concept_storage.store_color_variations(variations)
            
            # Return the updated concept with variations
            return await self.get_concept(concept_id)
            
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error in update_concept: {e}")
            raise StorageError(f"Failed to update concept: {str(e)}")
    
    async def delete_concept(self, concept_id: str) -> bool:
        """
        Delete a concept.
        
        Args:
            concept_id: ID of the concept to delete
            
        Returns:
            True if deleted successfully
            
        Raises:
            NotFoundError: If concept not found
            StorageError: If deletion fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            self.logger.info(f"Deleting concept: {masked_concept_id}")
            
            # Check if concept exists
            existing = self.concept_storage.get_concept_by_id(concept_id)
            if not existing:
                self.logger.warning(f"Concept {masked_concept_id} not found for deletion")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")
            
            # Delete color variations first
            self.concept_storage.delete_color_variations(concept_id)
            
            # Delete concept
            success = self.concept_storage.delete_concept(concept_id)
            if not success:
                raise StorageError(f"Failed to delete concept {masked_concept_id}")
            
            # Delete associated images
            try:
                base_path = existing["base_image_path"]
                self.image_storage.delete_image(base_path, "concept-images")
                
                # Delete variation images
                if "color_variations" in existing and existing["color_variations"]:
                    for variation in existing["color_variations"]:
                        self.image_storage.delete_image(
                            variation["image_path"], 
                            "palette-images"
                        )
            except Exception as img_error:
                # Log but don't fail if image deletion fails
                self.logger.warning(f"Error deleting images for concept {masked_concept_id}: {img_error}")
            
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error in delete_concept: {e}")
            raise StorageError(f"Failed to delete concept: {str(e)}")
    
    async def list_concepts(
        self, 
        session_id: Optional[str] = None, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List concepts, optionally filtered by session.
        
        Args:
            session_id: Optional session ID to filter by
            limit: Maximum number of concepts to return
            offset: Number of concepts to skip
            
        Returns:
            List of concept data
            
        Raises:
            StorageError: If retrieval fails
        """
        try:
            masked_session = mask_id(session_id) if session_id else "None"
            self.logger.info(f"Listing concepts for session: {masked_session}, limit: {limit}, offset: {offset}")
            
            if session_id:
                concepts = self.concept_storage.get_recent_concepts(session_id, limit, offset)
            else:
                concepts = self.concept_storage.get_recent_concepts(None, limit, offset)
            
            # Add public URLs for all images
            for concept in concepts:
                base_image_url = self.image_storage.get_image_url(
                    concept["base_image_path"], 
                    "concept-images"
                )
                concept["base_image_url"] = base_image_url
                
                # Process color variations 
                if "color_variations" in concept and concept["color_variations"]:
                    for variation in concept["color_variations"]:
                        image_url = self.image_storage.get_image_url(
                            variation["image_path"], 
                            "palette-images"
                        )
                        variation["image_url"] = image_url
            
            self.logger.info(f"Found {len(concepts)} concepts")
            return concepts
            
        except Exception as e:
            self.logger.error(f"Error in list_concepts: {e}")
            raise StorageError(f"Failed to list concepts: {str(e)}")
    
    async def associate_with_session(
        self, 
        concept_id: str, 
        session_id: str
    ) -> bool:
        """
        Associate a concept with a session.
        
        Args:
            concept_id: ID of the concept
            session_id: ID of the session
            
        Returns:
            True if association successful
            
        Raises:
            NotFoundError: If concept or session not found
            StorageError: If association fails
        """
        try:
            masked_concept_id = mask_id(concept_id)
            masked_session = mask_id(session_id)
            self.logger.info(f"Associating concept {masked_concept_id} with session {masked_session}")
            
            # Check if concept exists
            existing = self.concept_storage.get_concept_by_id(concept_id)
            if not existing:
                self.logger.warning(f"Concept {masked_concept_id} not found for association")
                raise NotFoundError(f"Concept with ID {masked_concept_id} not found")
            
            # Update the session ID
            success = self.concept_storage.update_concept(concept_id, {"session_id": session_id})
            if not success:
                raise StorageError(f"Failed to associate concept {masked_concept_id} with session {masked_session}")
            
            return True
            
        except NotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"Error in associate_with_session: {e}")
            raise StorageError(f"Failed to associate concept with session: {str(e)}")


# Custom exception classes
class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


class NotFoundError(Exception):
    """Raised when a requested resource is not found."""
    pass 