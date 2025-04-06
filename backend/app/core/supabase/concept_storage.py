"""
Concept storage operations for Supabase.

This module provides functionality for managing concept data in Supabase.
"""

import logging
from typing import List, Dict, Optional, Any

from .client import SupabaseClient
from ...utils.security.mask import mask_id, mask_path


# Configure logging
logger = logging.getLogger(__name__)


class ConceptStorage:
    """Handles concept-related operations in Supabase."""
    
    def __init__(self, client: SupabaseClient):
        """Initialize with a Supabase client.
        
        Args:
            client: Configured SupabaseClient instance
        """
        self.client = client
        self.logger = logging.getLogger("supabase_concept")
    
    def store_concept(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a new concept.
        
        Args:
            concept_data: Dictionary with concept details including:
                - session_id: UUID of the session
                - logo_description: User's logo description
                - theme_description: User's theme description
                - image_path: Path to the base image in Supabase Storage
                - image_url: Optional URL to the base image (signed URL)
            
        Returns:
            Created concept data or None on error
        """
        try:
            result = self.client.client.table("concepts").insert(concept_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error storing concept: {e}")
            return None
    
    def store_color_variations(self, variations: List[Dict[str, Any]]) -> Optional[List[Dict[str, Any]]]:
        """Store color variations for a concept.
        
        Args:
            variations: List of color variation dictionaries, each containing:
                - concept_id: UUID of the parent concept
                - palette_name: Name of the color palette
                - colors: JSONB array of hex color codes
                - description: Optional description of the palette
                - image_path: Path to the palette variation image in Storage
                - image_url: Optional URL to the variation image (signed URL)
            
        Returns:
            Created color variation data or None on error
        """
        try:
            result = self.client.client.table("color_variations").insert(variations).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Error storing color variations: {e}")
            return None
    
    def get_recent_concepts(self, session_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent concepts for a session.
        
        Args:
            session_id: UUID of the session
            limit: Maximum number of concepts to return
            
        Returns:
            List of concepts with their variations
        """
        try:
            # Log the session ID being used for the query
            self.logger.info(f"Querying recent concepts with session_id: {mask_id(session_id)}")
            
            # Security: Always filter by session_id to ensure users only see their own data
            result = self.client.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("session_id", session_id).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            # Log the results for debugging
            if result.data:
                self.logger.info(f"Found {len(result.data)} concepts for session ID {mask_id(session_id)}")
                for i, concept in enumerate(result.data):
                    concept_id = concept.get('id')
                    concept_session_id = concept.get('session_id')
                    base_path = concept.get('base_image_path')
                    masked_base_path = mask_path(base_path) if base_path else "none"
                    self.logger.info(f"Concept {i+1}: ID={mask_id(concept_id)}, session_id={mask_id(concept_session_id)}, base_path={masked_base_path}")
            else:
                self.logger.warning(f"No concepts found for session ID {mask_id(session_id)}")
                
                # Additional check: Look for all concepts without session filter
                all_results = self.client.client.table("concepts").select("id, session_id").limit(5).execute()
                if all_results.data:
                    self.logger.info(f"Found {len(all_results.data)} total concepts in database. Sample session IDs:")
                    for i, concept in enumerate(all_results.data):
                        concept_id = concept.get('id')
                        concept_session_id = concept.get('session_id')
                        self.logger.info(f"  - Sample concept {i+1}: ID={mask_id(concept_id)}, session_id={mask_id(concept_session_id)}")
            
            return result.data
        except Exception as e:
            self.logger.error(f"Error retrieving recent concepts: {e}")
            return []
    
    def get_concept_detail(self, concept_id: str, session_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            session_id: Session ID for security validation
            
        Returns:
            Concept detail data or None if not found
        """
        try:
            # Query the concept with security check for session_id
            result = self.client.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("id", concept_id).eq("session_id", session_id).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving concept details: {e}")
            return None
    
    def delete_all_color_variations(self, session_id: str) -> bool:
        """Delete all color variations for a session.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get all concept IDs for this session
            concepts_result = self.client.client.table("concepts").select(
                "id"
            ).eq("session_id", session_id).execute()
            
            if not concepts_result.data:
                self.logger.info(f"No concepts found for session ID {mask_id(session_id)}")
                return True
                
            # Extract concept IDs
            concept_ids = [concept.get('id') for concept in concepts_result.data]
            
            # Delete all color variations for these concepts
            for concept_id in concept_ids:
                self.client.client.table("color_variations").delete().eq("concept_id", concept_id).execute()
                
            return True
        except Exception as e:
            self.logger.error(f"Error deleting color variations: {e}")
            return False
    
    def delete_all_concepts(self, session_id: str) -> bool:
        """Delete all concepts for a session.
        
        Args:
            session_id: UUID of the session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Due to foreign key constraints, this will also delete color variations
            self.client.client.table("concepts").delete().eq("session_id", session_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting concepts: {e}")
            return False 