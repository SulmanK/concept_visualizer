"""Interface for image processing and generation services."""

import abc
from io import BytesIO
from typing import Any, BinaryIO, Dict, List, Optional, Tuple, Union

from fastapi import UploadFile


class ImageServiceInterface(abc.ABC):
    """Interface for services that process and manipulate images."""

    @abc.abstractmethod
    async def process_image(self, image_data: Union[bytes, BytesIO, str], operations: List[Dict[str, Any]]) -> bytes:
        """Process an image with a series of operations.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            operations: List of operations to apply to the image

        Returns:
            Processed image data as bytes

        Raises:
            ImageError: If processing fails
        """
        pass

    @abc.abstractmethod
    def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        user_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False,
    ) -> Tuple[str, str]:
        """Store an image and return its path and signed URL.

        Args:
            image_data: Image data as bytes, BytesIO, or UploadFile
            user_id: User ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image

        Returns:
            Tuple[str, str]: (image_path, image_url)

        Raises:
            ImageError: If storage fails
        """
        pass

    @abc.abstractmethod
    def convert_to_format(self, image_data: bytes, target_format: str = "png", quality: int = 95) -> bytes:
        """Convert an image to a specified format.

        Args:
            image_data: Binary image data
            target_format: Target format ('png', 'jpg', 'webp', etc.)
            quality: Quality for lossy formats (0-100)

        Returns:
            Converted image as bytes

        Raises:
            ImageError: If conversion fails
        """
        pass

    @abc.abstractmethod
    def generate_thumbnail(
        self,
        image_data: bytes,
        width: int,
        height: int,
        preserve_aspect_ratio: bool = True,
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail from an image.

        Args:
            image_data: Binary image data
            width: Target width
            height: Target height
            preserve_aspect_ratio: Whether to preserve the aspect ratio
            format: Output format

        Returns:
            Thumbnail image as bytes

        Raises:
            ImageError: If thumbnail generation fails
        """
        pass

    @abc.abstractmethod
    async def extract_color_palette(self, image_data: bytes, num_colors: int = 5) -> List[str]:
        """Extract a color palette from an image.

        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract

        Returns:
            List of color hex codes

        Raises:
            ImageError: If color extraction fails
        """
        pass

    @abc.abstractmethod
    async def create_palette_variations(
        self,
        base_image_data: bytes,
        palettes: List[Dict[str, Any]],
        user_id: str,
        blend_strength: float = 0.75,
    ) -> List[Dict[str, Any]]:
        """Create variations of an image with different color palettes.

        Args:
            base_image_data: Binary image data of the base image
            palettes: List of color palette dictionaries
            user_id: Current user ID
            blend_strength: How strongly to apply the new colors (0.0-1.0)

        Returns:
            List of palettes with added image_path and image_url fields

        Raises:
            ImageError: If applying palettes fails
        """
        pass

    @abc.abstractmethod
    async def apply_palette_to_image(self, image_data: bytes, palette_colors: list, blend_strength: float = 0.75) -> bytes:
        """Apply a color palette to an image.

        Args:
            image_data: Binary image data
            palette_colors: List of hex color codes
            blend_strength: Strength of the palette application (0-1)

        Returns:
            Processed image data as bytes

        Raises:
            ImageError: If processing fails
        """
        pass

    @abc.abstractmethod
    async def get_image_async(self, image_url_or_path: str) -> bytes:
        """Asynchronously get image data from a URL or path.

        Args:
            image_url_or_path: URL or storage path of the image

        Returns:
            Image data as bytes

        Raises:
            ImageError: If retrieval fails
        """
        pass


class ImageProcessingServiceInterface(abc.ABC):
    """Interface for image processing services."""

    @abc.abstractmethod
    async def process_image(self, image_data: Union[bytes, BytesIO, str], operations: List[Dict[str, Any]]) -> bytes:
        """Process an image with a series of operations.

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
    def convert_to_format(self, image_data: bytes, target_format: str = "png", quality: int = 95) -> bytes:
        """Convert an image to a specified format.

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
    async def convert_format(
        self,
        image_data: Union[bytes, BinaryIO, str],
        target_format: str,
        quality: Optional[int] = None,
    ) -> bytes:
        """Convert an image to a specified format with async support.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            target_format: Target format ('png', 'jpg', 'webp', etc.)
            quality: Quality for lossy formats (0-100)

        Returns:
            Converted image as bytes

        Raises:
            ImageProcessingError: If conversion fails
        """
        pass

    @abc.abstractmethod
    async def resize_image(
        self,
        image_data: Union[bytes, BytesIO, str],
        width: int,
        height: Optional[int] = None,
        maintain_aspect_ratio: bool = True,
    ) -> bytes:
        """Resize an image to specified dimensions.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            width: Target width
            height: Optional target height (calculated from width if None)
            maintain_aspect_ratio: Whether to maintain aspect ratio

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
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail from an image.

        Args:
            image_data: Binary image data
            width: Target width
            height: Target height
            preserve_aspect_ratio: Whether to preserve the aspect ratio
            format: Output format ('png', 'jpg', etc.)

        Returns:
            Thumbnail image as bytes

        Raises:
            ImageProcessingError: If thumbnail generation fails
        """
        pass

    @abc.abstractmethod
    async def extract_color_palette(self, image_data: bytes, num_colors: int = 5) -> List[str]:
        """Extract a color palette from an image.

        Args:
            image_data: Binary image data
            num_colors: Number of colors to extract

        Returns:
            List of hex color codes

        Raises:
            ImageProcessingError: If color extraction fails
        """
        pass

    @abc.abstractmethod
    def get_image_metadata(self, image_data: bytes) -> Dict[str, Any]:
        """Get metadata from an image.

        Args:
            image_data: Binary image data

        Returns:
            Dictionary containing image metadata (format, size, mode, etc.)

        Raises:
            ImageProcessingError: If metadata extraction fails
        """
        pass

    @abc.abstractmethod
    async def apply_palette(
        self,
        image_data: Union[bytes, BytesIO, str],
        palette_colors: List[str],
        blend_strength: float = 0.75,
    ) -> bytes:
        """Apply a color palette to an image.

        Args:
            image_data: Image data as bytes, BytesIO, or URL string
            palette_colors: List of hex color codes
            blend_strength: Strength of the palette application (0-1)

        Returns:
            Processed image as bytes

        Raises:
            ImageProcessingError: If palette application fails
        """
        pass
