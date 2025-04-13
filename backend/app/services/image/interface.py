"""
Interface for image processing and generation services.
"""

import abc
from typing import List, Dict, Any, Tuple, Optional, Union, BinaryIO

from app.models.concept.response import PaletteVariation


class ImageServiceInterface(abc.ABC):
    """Interface for services that generate and process images."""
    
    @abc.abstractmethod
    async def generate_and_store_image(
        self, prompt: str, user_id: str, style: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate an image based on prompt and store it.
        
        Args:
            prompt: Text description for image generation
            user_id: User ID for storage path
            style: Optional style parameter
            
        Returns:
            Tuple of (storage_path, image_url)
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
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
    ) -> Tuple[str, str]:
        """
        Refine an existing image based on prompt and store it.
        
        Args:
            prompt: Text description for refinement
            original_image_url: URL of the original image
            user_id: User ID for storage path
            strength: Control how much to preserve of the original image (0.0-1.0)
            
        Returns:
            Tuple of (storage_path, image_url)
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If refinement fails due to API errors
            StorageError: If storing the image fails
        """
        pass
    
    @abc.abstractmethod
    async def create_palette_variations(
        self, 
        image_path: str, 
        palettes: List[Dict[str, Any]], 
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Create color variations of an image using different palettes.
        
        Args:
            image_path: Path to the base image
            palettes: List of palette dictionaries with name, colors, description
            user_id: User ID for storage paths
            
        Returns:
            List of dictionaries with palette info and image URLs
            
        Raises:
            ImageProcessingError: If processing the image fails
            StorageError: If storing the variations fails
        """
        pass
    
    @abc.abstractmethod
    async def process_image(
        self, 
        image_data: bytes, 
        format: str = "PNG", 
        size: Optional[Tuple[int, int]] = None,
        base64_encode: bool = False
    ) -> bytes:
        """
        Process image data with basic operations like format conversion and resizing.
        
        Args:
            image_data: Raw image bytes
            format: Target format (PNG, JPEG, etc.)
            size: Optional (width, height) tuple for resizing
            base64_encode: Whether to return base64 encoded data
            
        Returns:
            Processed image bytes
            
        Raises:
            ImageProcessingError: If processing the image fails
        """
        pass
    
    @abc.abstractmethod
    async def store_image(
        self, 
        image_data: bytes, 
        storage_path: str, 
        content_type: str = "image/png"
    ) -> Tuple[str, str]:
        """
        Store image data in the storage backend.
        
        Args:
            image_data: Raw image bytes
            storage_path: Path for storing the image
            content_type: MIME content type
            
        Returns:
            Tuple of (storage_path, image_url)
            
        Raises:
            StorageError: If storing the image fails
        """
        pass


class ImageProcessingServiceInterface(abc.ABC):
    """Interface for image processing services."""
    
    @abc.abstractmethod
    async def convert_format(
        self,
        image_data: Union[bytes, BinaryIO, str],
        target_format: str,
        quality: Optional[int] = None
    ) -> bytes:
        """
        Convert an image to a different format.
        
        Args:
            image_data: Image data as bytes, file-like object, or path/URL
            target_format: Format to convert to (PNG, JPEG, etc.)
            quality: Quality level for lossy formats (0-100)
            
        Returns:
            Converted image as bytes
            
        Raises:
            ImageProcessingError: If conversion fails
        """
        pass
    
    @abc.abstractmethod
    async def resize_image(
        self,
        image_data: Union[bytes, BinaryIO, str],
        width: int,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True
    ) -> bytes:
        """
        Resize an image to specified dimensions.
        
        Args:
            image_data: Image data as bytes, file-like object, or path/URL
            width: Target width in pixels
            height: Target height in pixels (optional if maintaining aspect ratio)
            maintain_aspect_ratio: Whether to preserve the aspect ratio
            
        Returns:
            Resized image as bytes
            
        Raises:
            ImageProcessingError: If resizing fails
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