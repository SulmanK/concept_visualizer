"""
Concept service implementation.

This module implements the ConceptService class which integrates the specialized
concept generation, refinement, and palette generation modules.
"""

import logging
import httpx
import uuid
from typing import List, Optional, Dict, Any, Tuple
import os

from app.core.exceptions import ConceptError
from app.models.response import GenerationResponse, ColorPalette
from app.services.interfaces import (
    ConceptServiceInterface,
    ImageServiceInterface,
    ConceptPersistenceServiceInterface,
    ImagePersistenceServiceInterface
)
from app.services.jigsawstack.client import JigsawStackClient
from app.services.concept.generation import ConceptGenerator
from app.services.concept.refinement import ConceptRefiner
from app.services.concept.palette import PaletteGenerator
from app.utils.security.mask import mask_id


class ConceptService(ConceptServiceInterface):
    """Service for generating and refining visual concepts."""

    def __init__(
        self, 
        client: JigsawStackClient,
        image_service: Optional[ImageServiceInterface] = None,
        concept_persistence_service: Optional[ConceptPersistenceServiceInterface] = None,
        image_persistence_service: Optional[ImagePersistenceServiceInterface] = None
    ):
        """
        Initialize the concept service with specialized components.
        
        Args:
            client: The JigsawStack API client
            image_service: Service for image processing
            concept_persistence_service: Service for concept persistence
            image_persistence_service: Service for image persistence
        """
        self.client = client
        self.image_service = image_service
        self.concept_persistence = concept_persistence_service
        self.image_persistence = image_persistence_service
        self.logger = logging.getLogger("concept_service")
        
        # Initialize specialized components
        self.generator = ConceptGenerator(client)
        self.refiner = ConceptRefiner(client)
        self.palette_generator = PaletteGenerator(client)

    async def generate_concept(
        self,
        logo_description: str,
        theme_description: str,
        user_id: Optional[str] = None,
        skip_persistence: bool = False
    ) -> Dict[str, Any]:
        """
        Generate a new concept image based on text descriptions and store it if user_id provided.
        
        Args:
            logo_description: Text description of the logo
            theme_description: Text description of the theme
            user_id: Optional user ID to associate with the stored concept
            skip_persistence: If True, skip storing the concept in the database
            
        Returns:
            Dictionary containing the concept details (image URL, path, etc.)
            
        Raises:
            ConceptError: If image generation or storage fails
        """
        try:
            self.logger.info(f"Generating concept with logo_description='{logo_description}', theme_description='{theme_description}'")
            
            # Combine the descriptions into a single prompt
            combined_prompt = f"Create a professional logo with the following description: {logo_description}. Theme: {theme_description}"
            
            # Generate the image using the JigsawStack client
            image_response = await self.client.generate_image(
                prompt=combined_prompt,
                width=512,
                height=512
            )
            
            # Extract the image URL from the response
            if not image_response or "url" not in image_response:
                self.logger.error("No image URL returned from image generation service")
                raise ConceptError("No image URL returned from image generation service")
            
            image_url = image_response.get("url")
            self.logger.info(f"Image generated successfully: {image_url}")
            
            # If a user ID is provided, store the concept
            image_path = None
            concept_id = None
            stored_image_url = None
            
            if user_id:
                # Download the image
                try:
                    image_content = await self._download_image(image_url)
                    
                    # Store the image using the persistence service
                    image_path, stored_image_url = self.image_persistence.store_image(
                        image_data=image_content,
                        user_id=user_id,
                        metadata={
                            "logo_description": logo_description,
                            "theme_description": theme_description
                        }
                    )
                    
                    # Store the concept in the database only if not skipped
                    if not skip_persistence and self.concept_persistence:
                        concept_data = {
                            "user_id": user_id,
                            "logo_description": logo_description,
                            "theme_description": theme_description,
                            "image_path": image_path,
                            "image_url": stored_image_url
                        }
                        concept_id = await self.concept_persistence.store_concept(concept_data)
                        self.logger.info(f"Stored concept {concept_id} for user {user_id}")
                    
                except Exception as e:
                    self.logger.error(f"Failed to store generated image or concept: {str(e)}")
                    # We don't raise here as we still want to return the generated image
            
            # Create the response
            response = {
                "image_url": stored_image_url or image_url,  # Use stored URL if available
                "image_path": image_path,
                "concept_id": concept_id,
                "logo_description": logo_description,
                "theme_description": theme_description
            }
            
            return response
        except Exception as e:
            self.logger.error(f"Failed to generate concept: {str(e)}")
            raise ConceptError(f"Failed to generate concept: {str(e)}")

    async def generate_concept_with_palettes(
        self, 
        logo_description: str, 
        theme_description: str, 
        num_palettes: int = 3,
        user_id: Optional[str] = None
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Generate a concept with multiple palette variations, each with its own image.
        
        Args:
            logo_description: Description of the logo to generate
            theme_description: Description of the theme/color scheme
            num_palettes: Number of palette variations to generate
            user_id: Optional user ID for persisting the concept
            
        Returns:
            Tuple of (base_concept, variations): 
            - base_concept: The base generated concept
            - variations: List of palette variations with image URLs
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during concept generation
        """
        self.logger.info(f"Generating concept with {num_palettes} palette variations")
        
        # First, generate the base concept
        base_concept = await self.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description,
            user_id=user_id
        )
        
        # Then, generate additional palettes
        palettes = await self.palette_generator.generate_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes
        )
        
        variations = []
        
        # If we have the necessary services, create variations with different palettes
        if self.image_service and self.image_persistence and user_id:
            try:
                # Download the base image
                base_image_data = await self._download_image(base_concept["image_url"])
                
                # Check if we need to find the concept_id
                concept_id = None
                if self.concept_persistence:
                    # This is a simplified approach - in a real system, you might
                    # need a more robust way to find the concept that was just created
                    # Here we're assuming the base concept was stored in generate_concept
                    pass
                
                # Generate variations using the image service
                if base_image_data and palettes:
                    # Create variations with the image service
                    variations = await self.image_service.create_palette_variations(
                        base_image_data=base_image_data,
                        palettes=palettes,
                        user_id=user_id,
                        blend_strength=0.75  # Default blend strength
                    )
                    
                    # If we have a concept_id and concept persistence service,
                    # update the concept with the variations
                    if concept_id and self.concept_persistence:
                        # In a real implementation, you would update the concept record
                        # to include these variations
                        pass
                    
            except Exception as e:
                self.logger.error(f"Error creating palette variations: {str(e)}")
                # Continue with the operation, return what we have
        
        return base_concept, variations

    async def refine_concept(
        self,
        original_image_url: str,
        logo_description: Optional[str],
        theme_description: Optional[str],
        refinement_prompt: str,
        preserve_aspects: List[str],
        user_id: Optional[str] = None
    ) -> GenerationResponse:
        """
        Refine an existing concept based on provided instructions.
        
        Args:
            original_image_url: URL of the original image to refine
            logo_description: Updated description of the logo (optional)
            theme_description: Updated description of the theme (optional)
            refinement_prompt: Specific instructions for refinement
            preserve_aspects: Aspects of the original design to preserve
            user_id: Optional user ID for persisting the refined concept
            
        Returns:
            GenerationResponse: The refined concept with image URL and color palette
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If refinement fails due to API errors
            ConceptError: If there is an error during concept refinement
        """
        self.logger.info(f"Refining concept with prompt: {refinement_prompt}")
        
        # Use the refiner component to refine the concept
        response = await self.refiner.refine(
            original_image_url=original_image_url,
            logo_description=logo_description,
            theme_description=theme_description,
            refinement_prompt=refinement_prompt,
            preserve_aspects=preserve_aspects
        )
        
        # If user_id is provided and we have persistence services, store the refined concept
        if user_id and self.image_persistence and self.concept_persistence:
            try:
                # First, we need to get the image data from the URL
                image_url = response.image_url
                image_data = await self._download_image(image_url)
                
                # Then store the image
                image_path, stored_image_url = self.image_persistence.store_image(
                    image_data=image_data,
                    user_id=user_id,
                    metadata={
                        "logo_description": logo_description if logo_description else "",
                        "theme_description": theme_description if theme_description else "",
                        "refinement_prompt": refinement_prompt,
                        "is_refinement": True
                    }
                )
                
                # Now store the concept with the stored image info
                concept_data = {
                    "user_id": user_id,
                    "logo_description": logo_description if logo_description else "",
                    "theme_description": theme_description if theme_description else "",
                    "image_path": image_path,
                    "image_url": stored_image_url,
                    "color_palettes": [{
                        "name": "Refined Palette",
                        "colors": response.color_palette,
                        "description": "Color palette for the refined concept"
                    }],
                    "is_refinement": True,
                    "refinement_prompt": refinement_prompt,
                    "original_image_url": original_image_url
                }
                
                concept_id = await self.concept_persistence.store_concept(concept_data)
                self.logger.info(f"Stored refined concept with ID: {mask_id(concept_id)} for user: {mask_id(user_id)}")
                
                # Update the response to use our stored image URL
                response.image_url = stored_image_url
                
            except Exception as e:
                self.logger.error(f"Error storing refined concept: {str(e)}")
                # Don't fail the operation if storage fails, just log it
                # We still return the original response
        
        return response

    async def generate_color_palettes(
        self, 
        theme_description: str, 
        logo_description: Optional[str] = None,
        num_palettes: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Generate multiple color palettes based on a theme description.
        
        Args:
            theme_description: Description of the theme/color scheme
            logo_description: Optional description of the logo to help contextualize
            num_palettes: Number of palettes to generate
            
        Returns:
            List of palette dictionaries, each containing name, colors, and description
            
        Raises:
            JigsawStackConnectionError: If connection to the API fails
            JigsawStackAuthenticationError: If authentication fails
            JigsawStackGenerationError: If generation fails due to API errors
            ConceptError: If there is an error during palette generation
        """
        self.logger.info(f"Generating {num_palettes} color palettes for: {theme_description}")
        
        # Delegate to specialized palette generator component
        return await self.palette_generator.generate_palettes(
            theme_description=theme_description,
            logo_description=logo_description,
            num_palettes=num_palettes
        ) 
    
    async def apply_palette_to_concept(
        self,
        concept_image_url: str,
        palette_colors: List[str],
        user_id: Optional[str] = None,
        blend_strength: float = 0.75
    ) -> Tuple[str, str]:
        """
        Apply a color palette to an existing concept image.
        
        Args:
            concept_image_url: URL of the concept image
            palette_colors: List of hex color codes to apply
            user_id: Optional user ID for persisting the result
            blend_strength: Strength of the palette application (0-1)
            
        Returns:
            Tuple of (image_path, image_url) for the colorized image
            
        Raises:
            ConceptError: If applying the palette fails
        """
        self.logger.info("Applying palette to concept image")
        
        if not self.image_service or not self.image_persistence:
            raise ConceptError("Image service and persistence service required for palette application")
        
        try:
            # Download the image
            image_data = await self._download_image(concept_image_url)
            
            # Apply the palette
            colorized_image = await self.image_service.apply_palette_to_image(
                image_data=image_data,
                palette_colors=palette_colors,
                blend_strength=blend_strength
            )
            
            # Store the result if we have a user_id
            if user_id:
                # Generate a unique filename
                filename = f"palette_variation_{uuid.uuid4()}.png"
                
                # Store the colorized image
                image_path, image_url = self.image_persistence.store_image(
                    image_data=colorized_image,
                    user_id=user_id,
                    file_name=filename,
                    metadata={
                        "is_palette_variation": True,
                        "palette_colors": palette_colors
                    },
                    is_palette=True
                )
                
                return image_path, image_url
            else:
                # We don't have a user ID, so we can't store it
                raise ConceptError("User ID required to store palette application results")
                
        except Exception as e:
            self.logger.error(f"Error applying palette to concept: {str(e)}")
            raise ConceptError(f"Failed to apply palette to concept: {str(e)}")
    
    async def _download_image(self, image_url: str) -> Optional[bytes]:
        """
        Download an image from a URL or read from a local file path.
        
        Args:
            image_url: URL of the image to download, or file:// URL for local files
            
        Returns:
            Image data as bytes, or None if download fails
        """
        try:
            # Handle local file:// URLs by reading the file directly
            if image_url.startswith("file://"):
                # Extract the file path from the URL
                file_path = image_url[7:]  # Remove the "file://" prefix
                
                # Check if the file exists
                if not os.path.exists(file_path):
                    self.logger.error(f"Local file not found: {file_path}")
                    return None
                
                # Read the file
                with open(file_path, "rb") as f:
                    image_data = f.read()
                    
                self.logger.info("Read image data from local file")
                return image_data
                
            # For remote URLs, use httpx to download
            async with httpx.AsyncClient() as client:
                response = await client.get(image_url)
                response.raise_for_status()
                return response.content
        except Exception as e:
            self.logger.error(f"Error downloading image from {image_url}: {str(e)}")
            return None 