"""
Supabase client module.

This module provides a client for interacting with Supabase for data persistence,
session management, and image storage.
"""

import logging
import uuid
import io
import requests
from typing import List, Dict, Optional, Any, Union
from PIL import Image
from supabase import create_client, Client

from .config import settings


# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self, url: str = None, key: str = None, session_id: Optional[str] = None):
        """Initialize Supabase client with configured settings.
        
        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase API key (defaults to settings.SUPABASE_KEY)
            session_id: Optional session ID to include in request headers
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.logger = logging.getLogger("supabase_client")
        
        # Initialize headers with session ID if provided
        headers = {}
        if session_id:
            headers["x-session-id"] = session_id
            
        self.client = create_client(self.url, self.key, headers=headers)
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID.
        
        Args:
            session_id: UUID of the session to retrieve
            
        Returns:
            Session data or None if not found
        """
        try:
            result = self.client.table("sessions").select("*").eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving session: {e}")
            return None
    
    def create_session(self) -> Optional[Dict[str, Any]]:
        """Create a new session.
        
        Returns:
            New session data with ID
        """
        try:
            result = self.client.table("sessions").insert({}).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None
    
    def update_session_activity(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Update session's last_active_at timestamp.
        
        Args:
            session_id: UUID of the session to update
            
        Returns:
            Updated session data or None on error
        """
        try:
            result = self.client.table("sessions").update(
                {"last_active_at": "now()"}
            ).eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error updating session activity: {e}")
            return None
    
    def store_concept(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a new concept.
        
        Args:
            concept_data: Dictionary with concept details including:
                - session_id: UUID of the session
                - logo_description: User's logo description
                - theme_description: User's theme description
                - base_image_path: Path to the base image in Supabase Storage
            
        Returns:
            Created concept data or None on error
        """
        try:
            result = self.client.table("concepts").insert(concept_data).execute()
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
            
        Returns:
            Created color variation data or None on error
        """
        try:
            result = self.client.table("color_variations").insert(variations).execute()
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
            # Security: Always filter by session_id to ensure users only see their own data
            result = self.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("session_id", session_id).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
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
            result = self.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("id", concept_id).eq("session_id", session_id).execute()
            
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving concept detail: {e}")
            return None
    
    async def upload_image_from_url(self, image_url: str, bucket: str, session_id: str) -> Optional[str]:
        """Download an image from URL and upload to Supabase Storage.
        
        Args:
            image_url: URL of the image to download
            bucket: Storage bucket name ('concept-images' or 'palette-images')
            session_id: Session ID for organizing files
            
        Returns:
            Storage path of the uploaded image or None on error
        """
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()
            
            # Generate a unique filename
            file_ext = "png"  # Default extension
            content_type = response.headers.get("Content-Type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                file_ext = "jpg"
            elif "png" in content_type:
                file_ext = "png"
            
            # Security: Create path with session_id as the first folder segment
            # This ensures data isolation through folder structure
            unique_filename = f"{session_id}/{uuid.uuid4()}.{file_ext}"
            
            # Upload to Supabase Storage
            result = self.client.storage.from_(bucket).upload(
                path=unique_filename,
                file=response.content,
                file_options={
                    "content-type": content_type or "image/png"
                }
            )
            
            # Return the storage path
            return unique_filename
            
        except Exception as e:
            self.logger.error(f"Error uploading image from URL: {e}")
            return None
    
    def get_image_url(self, path: str, bucket: str) -> Optional[str]:
        """Get the public URL for an image in Supabase Storage.
        
        Args:
            path: Path of the image in storage
            bucket: Storage bucket name
            
        Returns:
            Public URL for the image
        """
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            self.logger.error(f"Error getting image URL: {e}")
            return None
    
    async def apply_color_palette(self, image_path: str, palette: List[str], session_id: str) -> Optional[str]:
        """Apply a color palette to an image and store the result.
        
        This is a basic implementation that would need enhancement for production.
        For MVP, it simply transfers the original image.
        
        Args:
            image_path: Path of the base image in storage
            palette: List of hex color codes
            session_id: Session ID for organizing files
            
        Returns:
            Path of the new image with applied palette
        """
        try:
            # For MVP, we'll just copy the original image
            # In a full implementation, we would apply the palette
            original_url = self.get_image_url(image_path, "concept-images")
            if not original_url:
                return None
                
            # Upload (for now, just the same image) to palette-images bucket
            return await self.upload_image_from_url(
                original_url, 
                "palette-images", 
                session_id
            )
        except Exception as e:
            self.logger.error(f"Error applying color palette: {e}")
            return None
    
    def delete_all_color_variations(self, session_id: str) -> bool:
        """Delete all color variations for a session.
        
        Args:
            session_id: Session ID to limit deletion scope
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # First get concept IDs for this session
            concepts = self.client.table("concepts").select("id").eq("session_id", session_id).execute()
            if not concepts.data:
                return True  # No concepts found, nothing to delete
                
            # Create a list of concept IDs
            concept_ids = [concept["id"] for concept in concepts.data]
            
            # Delete all color variations for these concepts
            self.client.table("color_variations").delete().in_("concept_id", concept_ids).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting color variations: {e}")
            return False
    
    def delete_all_concepts(self, session_id: str) -> bool:
        """Delete all concepts for a session.
        
        Note: This will cascade delete associated color variations.
        
        Args:
            session_id: Session ID to limit deletion scope
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all concepts for this session
            self.client.table("concepts").delete().eq("session_id", session_id).execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting concepts: {e}")
            return False
    
    def delete_all_sessions(self) -> bool:
        """Delete all sessions.
        
        CAUTION: This will delete all sessions data.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete all sessions
            self.client.table("sessions").delete().execute()
            return True
        except Exception as e:
            self.logger.error(f"Error deleting sessions: {e}")
            return False
    
    def delete_all_storage_objects(self, bucket: str, session_id: Optional[str] = None) -> bool:
        """Delete all objects from a storage bucket.
        
        Args:
            bucket: Storage bucket name
            session_id: Optional session ID to limit deletion to a specific session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            prefix = f"{session_id}/" if session_id else ""
            response = self.client.storage.from_(bucket).list(path=prefix)
            
            # Delete each file
            for file in response:
                file_path = file.get("name")
                if file_path:
                    self.client.storage.from_(bucket).remove([file_path])
            
            return True
        except Exception as e:
            self.logger.error(f"Error deleting storage objects: {e}")
            return False
    
    def purge_all_data(self, session_id: Optional[str] = None) -> bool:
        """Delete all data from the database and storage.
        
        CAUTION: This is a destructive operation that will delete all data.
        
        Args:
            session_id: Optional session ID to limit purge to a specific session
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Delete storage objects first
            buckets = ["concept-images", "palette-images"]
            for bucket in buckets:
                self.delete_all_storage_objects(bucket, session_id)
            
            if session_id:
                # Delete just the specified session data
                self.delete_all_concepts(session_id)
                self.client.table("sessions").delete().eq("id", session_id).execute()
            else:
                # Delete all data
                self.delete_all_color_variations(None)
                self.delete_all_concepts(None)
                self.delete_all_sessions()
            
            return True
        except Exception as e:
            self.logger.error(f"Error purging all data: {e}")
            return False


def get_supabase_client(session_id: Optional[str] = None) -> SupabaseClient:
    """Factory function to get Supabase client.
    
    Args:
        session_id: Optional session ID to include in request headers
        
    Returns:
        Configured SupabaseClient instance
    """
    return SupabaseClient(session_id=session_id) 