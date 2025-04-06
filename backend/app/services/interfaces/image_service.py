"""
Interface for image processing and storage services.
"""

import abc
from typing import Dict, List, Optional, Union, Tuple, BinaryIO

class ImageServiceInterface(abc.ABC):
    """Interface for image processing and storage services."""
    
    @abc.abstractmethod
    async def process_image(
        self, 
        image_data: Union[bytes, BinaryIO], 
        operations: List[Dict]
    ) -> bytes:
        """
        Process an image with a series of operations.
        
        Args:
            image_data: Binary image data or file-like object
            operations: List of operations to apply, each as a dict with operation type and params
            
        Returns:
            Processed image data as bytes
            
        Raises:
            ImageProcessingError: If processing fails
        """
        pass
    
    @abc.abstractmethod
    async def store_image(
        self, 
        image_data: bytes, 
        concept_id: str, 
        image_type: str
    ) -> str:
        """
        Store an image and return its URL.
        
        Args:
            image_data: Binary image data
            concept_id: ID of the concept the image is associated with
            image_type: Type of image (original, refined, thumbnail)
            
        Returns:
            Signed URL of the stored image
            
        Raises:
            StorageError: If storing fails
        """
        pass
    
    @abc.abstractmethod
    async def get_image(self, image_url: str) -> bytes:
        """
        Retrieve an image from its URL.
        
        Args:
            image_url: URL of the image to retrieve
            
        Returns:
            Binary image data
            
        Raises:
            ImageRetrievalError: If image retrieval fails
        """
        pass
    
    @abc.abstractmethod
    async def convert_to_format(
        self, 
        image_data: bytes, 
        target_format: str
    ) -> bytes:
        """
        Convert an image to a different format.
        
        Args:
            image_data: Binary image data
            target_format: Target format (png, jpg, svg, etc.)
            
        Returns:
            Converted image data
            
        Raises:
            ImageConversionError: If conversion fails
        """
        pass
    
    @abc.abstractmethod
    async def generate_thumbnail(
        self, 
        image_data: bytes, 
        width: int, 
        height: int
    ) -> bytes:
        """
        Generate a thumbnail from an image.
        
        Args:
            image_data: Binary image data
            width: Thumbnail width
            height: Thumbnail height
            
        Returns:
            Thumbnail image data
            
        Raises:
            ImageProcessingError: If thumbnail generation fails
        """
        pass
    
    @abc.abstractmethod
    async def extract_color_palette(
        self, 
        image_data: bytes, 
        num_colors: int = 8
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