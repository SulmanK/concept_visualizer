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

class ImageProcessingServiceInterface(abc.ABC):
    """Interface for image processing operations."""
    
    @abc.abstractmethod
    async def process_image(
        self, 
        image_data: Union[bytes, BinaryIO, str], 
        operations: List[Dict[str, Any]]
    ) -> bytes:
        """
        Process an image with a series of operations.
        
        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            operations: List of operations to apply to the image
            
        Returns:
            Processed image data as bytes
            
        Raises:
            ImageProcessingError: If processing fails
        """
        pass
    
    @abc.abstractmethod
    def convert_to_format(
        self, 
        image_data: bytes, 
        target_format: str = "png", 
        quality: int = 95
    ) -> bytes:
        """
        Convert an image to a specified format.
        
        Args:
            image_data: Binary image data
            target_format: Target format ('png', 'jpg', 'webp', etc.)
            quality: Quality for lossy formats (0-100)
            
        Returns:
            Converted image as bytes
            
        Raises:
            ImageProcessingError: If conversion fails
        """
        pass
        
    @abc.abstractmethod
    def generate_thumbnail(
        self, 
        image_data: bytes, 
        width: int, 
        height: int, 
        preserve_aspect_ratio: bool = True,
        format: str = "png"
    ) -> bytes:
        """
        Generate a thumbnail from an image.
        
        Args:
            image_data: Binary image data
            width: Target width
            height: Target height
            preserve_aspect_ratio: Whether to preserve the aspect ratio
            format: Output format
            
        Returns:
            Thumbnail image as bytes
            
        Raises:
            ImageProcessingError: If thumbnail generation fails
        """
        pass
        
    @abc.abstractmethod
    async def extract_color_palette(
        self, 
        image_data: bytes, 
        num_colors: int = 5
    ) -> List[str]:
        """
        Extract a color palette from an image.
        
        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract
            
        Returns:
            List of color hex codes
            
        Raises:
            ImageProcessingError: If color extraction fails
        """
        pass
        
    @abc.abstractmethod
    def get_image_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """
        Extract metadata from an image.
        
        Args:
            image_data: Binary image data
            
        Returns:
            Dictionary containing image metadata
            
        Raises:
            ImageProcessingError: If metadata extraction fails
        """
        pass 