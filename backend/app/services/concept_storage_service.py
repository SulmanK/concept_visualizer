"""
Concept storage service.

This module provides services for storing and retrieving concepts
from Supabase.
"""

import logging
import uuid
from typing import List, Dict, Optional, Any

from fastapi import Depends

from ..core.supabase import get_supabase_client, SupabaseClient
from ..core.supabase.concept_storage import ConceptStorage
from ..core.supabase.image_storage import ImageStorage
from ..models.concept import ColorPalette, ConceptSummary, ConceptDetail
from ..utils.security.mask import mask_id, mask_path


# Configure logging
logger = logging.getLogger(__name__)


class ConceptStorageService:
    """Service for storing and retrieving concepts."""
    
    def __init__(self, supabase_client: SupabaseClient = Depends(get_supabase_client)):
        """Initialize concept storage service with a Supabase client.
        
        Args:
            supabase_client: Client for interacting with Supabase
        """
        self.supabase_client = supabase_client
        self.concept_storage = ConceptStorage(supabase_client)
        self.image_storage = ImageStorage(supabase_client)
        self.logger = logging.getLogger("concept_storage_service")
    
    async def store_concept(
        self,
        session_id: str,
        logo_description: str,
        theme_description: str,
        base_image_path: str,
        color_palettes: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Store a new concept and its color variations.
        
        Args:
            session_id: Session ID to associate with the concept
            logo_description: User's logo description
            theme_description: User's theme description
            base_image_path: Path to the generated base image in Supabase Storage
            color_palettes: List of color palette dictionaries with image_path fields
            
        Returns:
            Created concept data or None on error
        """
        try:
            # Mask sensitive information
            masked_session = mask_id(session_id)
            
            # Insert concept
            self.logger.info(f"Storing concept for session: {masked_session}")
            concept_data = {
                "session_id": session_id,
                "logo_description": logo_description,
                "theme_description": theme_description,
                "base_image_path": base_image_path
            }
            
            concept = self.concept_storage.store_concept(concept_data)
            if not concept:
                self.logger.error("Failed to store concept")
                return None
            
            masked_concept_id = mask_id(concept['id'])
            self.logger.info(f"Stored concept with ID: {masked_concept_id}")
            
            # Insert color variations
            variations = []
            for palette in color_palettes:
                masked_palette_path = mask_path(palette["image_path"])
                self.logger.debug(f"Adding palette variation: {palette['name']}, path: {masked_palette_path}")
                
                variation = {
                    "concept_id": concept["id"],
                    "palette_name": palette["name"],
                    "colors": palette["colors"],
                    "description": palette.get("description"),
                    "image_path": palette["image_path"]  # Path to the palette-specific image in Storage
                }
                variations.append(variation)
            
            variations_result = self.concept_storage.store_color_variations(variations)
            
            # Return full concept with variations
            if variations_result:
                self.logger.info(f"Stored {len(variations_result)} color variations")
                concept["color_variations"] = variations_result
                return concept
            return concept
            
        except Exception as e:
            self.logger.error(f"Error in store_concept: {e}")
            return None
    
    async def get_recent_concepts(self, session_id: str, limit: int = 10) -> List[ConceptSummary]:
        """Get recent concepts for a session.
        
        Args:
            session_id: Session ID to get concepts for
            limit: Maximum number of concepts to return
            
        Returns:
            List of concept summaries with their variations
        """
        try:
            masked_session = mask_id(session_id)
            self.logger.info(f"Getting recent concepts for session: {masked_session}")
            concepts = self.concept_storage.get_recent_concepts(session_id, limit)
            
            # Convert to ConceptSummary model
            summaries = []
            for concept_data in concepts:
                # Mask sensitive paths
                masked_concept_id = mask_id(concept_data['id'])
                masked_base_path = mask_path(concept_data["base_image_path"])
                self.logger.debug(f"Processing concept: {masked_concept_id}, base path: {masked_base_path}")
                
                # Add authenticated URLs for all images
                base_image_url = await self.image_storage.authenticate_url(
                    concept_data["base_image_path"], 
                    session_id
                )
                
                # Process color variations 
                variations = []
                if "color_variations" in concept_data and concept_data["color_variations"]:
                    for variation in concept_data["color_variations"]:
                        image_url = await self.image_storage.authenticate_url(
                            variation["image_path"], 
                            session_id,
                            is_palette=True
                        )
                        
                        variations.append(ColorPalette(
                            name=variation["palette_name"],
                            colors=variation["colors"],
                            description=variation.get("description"),
                            image_url=image_url,
                            image_path=variation["image_path"]
                        ))
                
                # Create ConceptSummary object
                summary = ConceptSummary(
                    id=uuid.UUID(concept_data["id"]),
                    created_at=concept_data["created_at"],
                    logo_description=concept_data["logo_description"],
                    theme_description=concept_data["theme_description"],
                    base_image_url=base_image_url,
                    base_image_path=concept_data["base_image_path"],
                    color_variations=variations
                )
                
                summaries.append(summary)
            
            self.logger.info(f"Found {len(summaries)} recent concepts")
            return summaries
            
        except Exception as e:
            self.logger.error(f"Error in get_recent_concepts: {e}")
            return []
    
    async def get_concept_detail(self, concept_id: str, session_id: str) -> Optional[ConceptDetail]:
        """Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            session_id: Session ID for security validation
            
        Returns:
            Concept detail object or None if not found
        """
        try:
            masked_concept_id = mask_id(concept_id)
            masked_session = mask_id(session_id)
            
            self.logger.info(f"Getting concept detail for concept: {masked_concept_id}, session: {masked_session}")
            concept_data = self.concept_storage.get_concept_detail(concept_id, session_id)
            
            if not concept_data:
                self.logger.warning(f"Concept {masked_concept_id} not found or access denied")
                return None
                
            # Add authenticated URLs for all images
            base_image_url = await self.image_storage.authenticate_url(
                concept_data["base_image_path"], 
                session_id
            )
            
            # Process color variations 
            variations = []
            if "color_variations" in concept_data and concept_data["color_variations"]:
                for variation in concept_data["color_variations"]:
                    image_url = await self.image_storage.authenticate_url(
                        variation["image_path"], 
                        session_id,
                        is_palette=True
                    )
                    
                    variations.append(ColorPalette(
                        name=variation["palette_name"],
                        colors=variation["colors"],
                        description=variation.get("description"),
                        image_url=image_url,
                        image_path=variation["image_path"]
                    ))
            
            # Create ConceptDetail object
            detail = ConceptDetail(
                id=uuid.UUID(concept_data["id"]),
                created_at=concept_data["created_at"],
                logo_description=concept_data["logo_description"],
                theme_description=concept_data["theme_description"],
                base_image_url=base_image_url,
                base_image_path=concept_data["base_image_path"],
                color_variations=variations
            )
            
            return detail
            
        except Exception as e:
            self.logger.error(f"Error in get_concept_detail: {e}")
            return None


# Dependency function for FastAPI routes
async def get_concept_storage_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client)
) -> ConceptStorageService:
    """Factory function for ConceptStorageService.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        Configured ConceptStorageService instance
    """
    return ConceptStorageService(supabase_client) 