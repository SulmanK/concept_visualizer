"""Interface for export services.

This module defines the interface for services that handle exporting concepts and images.
"""

import abc
from typing import Any, BinaryIO, Dict, List, Optional, Union


class ExportServiceInterface(abc.ABC):
    """Interface for export services."""

    @abc.abstractmethod
    async def export_image(
        self,
        image_path: str,
        format: str,
        size: Optional[Dict[str, int]] = None,
        quality: Optional[int] = None,
        user_id: Optional[str] = None,
        include_original: bool = False,
        color_mode: str = "color",
    ) -> Dict[str, Any]:
        """Export an image with specified format and parameters.

        Args:
            image_path: Path or URL of the image to export
            format: Target format (PNG, JPEG, SVG, etc.)
            size: Optional dictionary with width and/or height
            quality: Quality for lossy formats (0-100)
            user_id: Optional user ID for tracking exports
            include_original: Whether to include the original image
            color_mode: Color mode of the export (color, grayscale, etc.)

        Returns:
            Dictionary containing the exported image data and metadata

        Raises:
            ExportError: If export fails
            ResourceNotFoundError: If the image is not found
        """
        pass

    @abc.abstractmethod
    async def export_palette(
        self,
        palette_data: List[str],
        format: str = "png",
        size: Optional[Dict[str, int]] = None,
    ) -> bytes:
        """Export a color palette as an image.

        Args:
            palette_data: List of color values (hex codes)
            format: Target format for the palette image
            size: Optional dictionary with width and/or height

        Returns:
            Binary data of the exported palette image

        Raises:
            ExportError: If export fails
        """
        pass

    @abc.abstractmethod
    async def export_concept_package(
        self,
        concept_id: str,
        user_id: str,
        formats: List[str],
        include_palettes: bool = True,
    ) -> Dict[str, Any]:
        """Export a complete concept package with multiple formats.

        Args:
            concept_id: ID of the concept to export
            user_id: User ID owning the concept
            formats: List of formats to include
            include_palettes: Whether to include palette images

        Returns:
            Dictionary with paths to exported files

        Raises:
            ExportError: If export fails
            ResourceNotFoundError: If the concept is not found
        """
        pass

    @abc.abstractmethod
    async def generate_thumbnail(
        self,
        image_data: Union[bytes, str, BinaryIO],
        width: int,
        height: int,
        format: str = "png",
    ) -> bytes:
        """Generate a thumbnail of an image.

        Args:
            image_data: Image data or path or file-like object
            width: Thumbnail width
            height: Thumbnail height
            format: Output format

        Returns:
            Thumbnail image data

        Raises:
            ExportError: If thumbnail generation fails
        """
        pass
