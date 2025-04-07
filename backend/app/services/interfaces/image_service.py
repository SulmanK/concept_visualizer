"""
Interface for image processing and storage services.
"""

import abc
from typing import Dict, List, Optional, Union, Tuple, BinaryIO, Any

class ImageServiceInterface(abc.ABC):
    """Interface for image processing and storage services."""
    
    @abc.abstractmethod
    async def generate_and_store_image(self, prompt: str, user_id: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Generate an image based on a prompt and store it in Supabase.
        
        Args:
            prompt: Image generation prompt
            user_id: Current user ID
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
            
        Raises:
            ImageProcessingError: If image generation fails
            StorageError: If storing the image fails
        """
        pass
    
    @abc.abstractmethod
    async def refine_and_store_image(
        self, 
        prompt: str, 
        original_image_url: str, 
        user_id: str,
        strength: float = 0.7
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Refine an image based on a prompt and store the result in Supabase.
        
        Args:
            prompt: Refinement prompt
            original_image_url: URL of the original image
            user_id: Current user ID
            strength: How much to change the original (0.0-1.0)
            
        Returns:
            Tuple of (storage_path, signed_url) or (None, None) on error
            
        Raises:
            ImageProcessingError: If image refinement fails
            StorageError: If storing the image fails
        """
        pass
    
    @abc.abstractmethod
    async def create_palette_variations(
        self, 
        base_image_path: str, 
        palettes: List[Dict[str, Any]], 
        user_id: str,
        blend_strength: float = 0.75
    ) -> List[Dict[str, Any]]:
        """
        Create variations of an image with different color palettes.
        
        Args:
            base_image_path: Storage path of the base image
            palettes: List of color palette dictionaries
            user_id: Current user ID
            blend_strength: How strongly to apply the new colors (0.0-1.0)
            
        Returns:
            List of palettes with added image_path and image_url fields
            
        Raises:
            ImageProcessingError: If applying palettes fails
            StorageError: If storing the variations fails
        """
        pass 