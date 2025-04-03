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

from .config import settings, get_masked_value


# Configure logging
logger = logging.getLogger(__name__)


class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self, url: str = None, key: str = None, session_id: Optional[str] = None):
        """Initialize Supabase client with configured settings.
        
        Args:
            url: Supabase project URL (defaults to settings.SUPABASE_URL)
            key: Supabase API key (defaults to settings.SUPABASE_KEY)
            session_id: Optional session ID to store for later use
        """
        self.url = url or settings.SUPABASE_URL
        self.key = key or settings.SUPABASE_KEY
        self.logger = logging.getLogger("supabase_client")
        self.session_id = session_id
        
        # Initialize Supabase client (no headers parameter in v1.0.3)
        self.client = create_client(self.url, self.key)
    
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
    
    def create_session_with_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Create a session with a specific ID.
        
        Args:
            session_id: Specific UUID to use for the session
            
        Returns:
            Created session data or None on error
        """
        try:
            # Make sure the session_id is a valid UUID format
            try:
                # Validate by parsing the UUID
                uuid_obj = uuid.UUID(session_id)
                # Ensure it's in the standard string format
                session_id = str(uuid_obj)
            except ValueError:
                self.logger.error(f"Invalid UUID format for session_id: {get_masked_value(session_id)}")
                return None
                
            # Insert the session with the provided ID
            result = self.client.table("sessions").insert({"id": session_id}).execute()
            
            # Log the result for debugging
            if result.data:
                self.logger.info(f"Created session with client-provided ID: {get_masked_value(session_id)}")
            else:
                self.logger.warning(f"No data returned when creating session with ID: {get_masked_value(session_id)}")
                
            return result.data[0] if result.data else None
            
        except Exception as e:
            self.logger.error(f"Error creating session with ID {get_masked_value(session_id)}: {e}")
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
            # Log the session ID being used for the query
            self.logger.info(f"Querying recent concepts with session_id: {get_masked_value(session_id)}")
            
            # Security: Always filter by session_id to ensure users only see their own data
            result = self.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("session_id", session_id).order(
                "created_at", desc=True
            ).limit(limit).execute()
            
            # Log the results for debugging
            if result.data:
                self.logger.info(f"Found {len(result.data)} concepts for session ID {get_masked_value(session_id)}")
                for i, concept in enumerate(result.data):
                    concept_id = concept.get('id')
                    concept_session_id = concept.get('session_id')
                    self.logger.info(f"Concept {i+1}: ID={get_masked_value(concept_id)}, session_id={get_masked_value(concept_session_id)}, base_path={concept.get('base_image_path')}")
            else:
                self.logger.warning(f"No concepts found for session ID {get_masked_value(session_id)}")
                
                # Additional check: Look for all concepts without session filter
                all_results = self.client.table("concepts").select("id, session_id").limit(5).execute()
                if all_results.data:
                    self.logger.info(f"Found {len(all_results.data)} total concepts in database. Sample session IDs:")
                    for i, concept in enumerate(all_results.data):
                        concept_id = concept.get('id')
                        concept_session_id = concept.get('session_id')
                        self.logger.info(f"  - Sample concept {i+1}: ID={get_masked_value(concept_id)}, session_id={get_masked_value(concept_session_id)}")
            
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
            self.logger.error(f"Error retrieving concept detail for concept ID {get_masked_value(concept_id)}: {e}")
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
        
        This method creates a new image with the specified color palette
        using OpenCV color mapping techniques to transform the original image colors
        to the new palette.
        
        Args:
            image_path: Path of the base image in storage
            palette: List of hex color codes
            session_id: Session ID for organizing files
            
        Returns:
            Path of the new image with applied palette
        """
        try:
            # Get the image data from storage
            self.logger.info(f"Downloading image from storage: {image_path}")
            image_data = self.client.storage.from_("concept-images").download(image_path)
            if not image_data:
                self.logger.error("Failed to download image from storage")
                return None
            
            # Import necessary libraries for image processing
            import cv2
            import numpy as np
            from io import BytesIO
            from PIL import Image
            import colorsys
            
            # Convert hex colors to RGB
            def hex_to_rgb(hex_color):
                hex_color = hex_color.lstrip('#')
                return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            
            # Convert RGB to BGR (OpenCV format)
            def rgb_to_bgr(rgb):
                return (rgb[2], rgb[1], rgb[0])
            
            # Convert RGB to HSV for better color manipulation
            def rgb_to_hsv(rgb):
                return colorsys.rgb_to_hsv(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
            
            # Generate a unique filename for the palette version
            file_ext = image_path.split(".")[-1] if "." in image_path else "png"
            unique_filename = f"{session_id}/{uuid.uuid4()}.{file_ext}"
            
            # Load image with OpenCV
            img_array = np.frombuffer(image_data, np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            # Convert to RGB for processing (OpenCV uses BGR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Extract dominant colors from the image
            pixels = img_rgb.reshape(-1, 3)
            
            # Use K-means clustering to find dominant colors
            # Use min(5, len(palette)) clusters to match palette size
            num_clusters = min(5, len(palette))
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, 0.1)
            flags = cv2.KMEANS_RANDOM_CENTERS
            _, labels, centers = cv2.kmeans(pixels.astype(np.float32), num_clusters, None, criteria, 10, flags)
            
            # Convert centers to integers
            dominant_colors = [tuple(map(int, center)) for center in centers]
            
            # Convert palette hex values to RGB
            palette_rgb = [hex_to_rgb(color) for color in palette[:num_clusters]]
            
            # Create a mapping from dominant colors to palette colors
            # Sort both lists by perceived brightness
            def get_brightness(rgb):
                return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
            
            dominant_colors.sort(key=get_brightness)
            palette_rgb.sort(key=get_brightness)
            
            # Create the color mapping
            color_mapping = dict(zip(dominant_colors, palette_rgb))
            
            # Create output image
            recolored = img_rgb.copy()
            
            # For each dominant color, find pixels close to that color and replace
            for orig_color, new_color in color_mapping.items():
                # Create a mask for pixels close to the original color
                tolerance = 30  # Adjust as needed
                mask = cv2.inRange(img_rgb, 
                                np.array([c - tolerance for c in orig_color]), 
                                np.array([c + tolerance for c in orig_color]))
                
                # Replace the colors in the masked region
                recolored[mask > 0] = new_color
            
            # Apply color balancing and blending
            # Convert to HSV for better control
            hsv = cv2.cvtColor(recolored, cv2.COLOR_RGB2HSV)
            
            # Enhance saturation slightly
            hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.2, 0, 255)
            
            # Convert back to RGB
            enhanced = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            
            # Convert back to BGR for OpenCV
            enhanced_bgr = cv2.cvtColor(enhanced, cv2.COLOR_RGB2BGR)
            
            # Encode the image
            _, buffer = cv2.imencode(f'.{file_ext}', enhanced_bgr)
            
            # Upload to Supabase
            self.logger.info(f"Uploading recolored image to palette-images bucket: {unique_filename}")
            result = self.client.storage.from_("palette-images").upload(
                path=unique_filename,
                file=buffer.tobytes(),
                file_options={"content-type": f"image/{file_ext}"}
            )
            
            self.logger.info(f"Successfully created palette variation: {unique_filename}")
            # Return the storage path
            return unique_filename
        except Exception as e:
            self.logger.error(f"Error applying color palette: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
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