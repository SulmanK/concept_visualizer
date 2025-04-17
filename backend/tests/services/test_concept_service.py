"""
Unit tests for the ConceptService class.

These tests validate the core logic of the ConceptService by mocking
external dependencies like JigsawStack API and Supabase.
"""

import unittest
from unittest.mock import MagicMock, AsyncMock, patch
import pytest
from typing import Dict, List, Any, Tuple, Optional
import os
import json

from app.services.concept.service import ConceptService
from app.core.exceptions import ConceptError
from app.models.concept.response import GenerationResponse, ColorPalette


@pytest.fixture
def mock_jigsawstack_client():
    """Create a mock JigsawStack client."""
    client = AsyncMock()
    client.generate_image = AsyncMock(return_value={"url": "https://example.com/test_image.png"})
    return client


@pytest.fixture
def mock_image_service():
    """Create a mock ImageService."""
    service = AsyncMock()
    service.create_palette_variations = AsyncMock(return_value=[
        {"palette_id": "pal1", "image_url": "https://example.com/variation1.png"},
        {"palette_id": "pal2", "image_url": "https://example.com/variation2.png"},
    ])
    return service


@pytest.fixture
def mock_concept_persistence():
    """Create a mock ConceptPersistenceService."""
    service = AsyncMock()
    service.store_concept = AsyncMock(return_value="concept-123")
    return service


@pytest.fixture
def mock_image_persistence():
    """Create a mock ImagePersistenceService."""
    service = MagicMock()
    service.store_image = MagicMock(
        return_value=("test/image/path.png", "https://example.com/stored_image.png")
    )
    return service


@pytest.fixture
def concept_service(
    mock_jigsawstack_client,
    mock_image_service,
    mock_concept_persistence,
    mock_image_persistence
):
    """Create a ConceptService with mock dependencies."""
    return ConceptService(
        client=mock_jigsawstack_client,
        image_service=mock_image_service,
        concept_persistence_service=mock_concept_persistence,
        image_persistence_service=mock_image_persistence
    )


class TestConceptService:
    """Test suite for ConceptService."""
    
    @pytest.mark.asyncio
    async def test_generate_concept_without_persistence(self, concept_service, mock_jigsawstack_client):
        """Test generating a concept without persisting it."""
        # Arrange
        logo_description = "Test logo with a stylized tree"
        theme_description = "Modern, blue, minimalist design"
        
        # Act
        result = await concept_service.generate_concept(
            logo_description=logo_description,
            theme_description=theme_description
        )
        
        # Assert
        assert result["image_url"] == "https://example.com/test_image.png"
        assert result["logo_description"] == logo_description
        assert result["theme_description"] == theme_description
        assert result["concept_id"] is None
        assert result["image_path"] is None
        
        # Verify the client was called with the correct parameters
        mock_jigsawstack_client.generate_image.assert_called_once_with(
            prompt=logo_description,
            width=512,
            height=512
        )
    
    @pytest.mark.asyncio
    async def test_generate_concept_with_persistence(
        self, 
        concept_service, 
        mock_jigsawstack_client,
        mock_image_persistence,
        mock_concept_persistence
    ):
        """Test generating a concept with persistence enabled."""
        # Arrange
        logo_description = "Test logo with a stylized tree"
        theme_description = "Modern, blue, minimalist design"
        user_id = "user-123"
        
        # Mock the _download_image method to return dummy image data
        with patch.object(
            concept_service, 
            '_download_image', 
            AsyncMock(return_value=b'fake_image_data')
        ) as mock_download:
            # Act
            result = await concept_service.generate_concept(
                logo_description=logo_description,
                theme_description=theme_description,
                user_id=user_id
            )
            
            # Assert
            assert result["image_url"] == "https://example.com/stored_image.png"
            assert result["logo_description"] == logo_description
            assert result["theme_description"] == theme_description
            assert result["concept_id"] == "concept-123"
            assert result["image_path"] == "test/image/path.png"
            
            # Verify image was downloaded
            mock_download.assert_called_once_with("https://example.com/test_image.png")
            
            # Verify image was stored
            mock_image_persistence.store_image.assert_called_once_with(
                image_data=b'fake_image_data',
                user_id=user_id,
                metadata={
                    "logo_description": logo_description,
                    "theme_description": theme_description
                }
            )
            
            # Verify concept was stored
            mock_concept_persistence.store_concept.assert_called_once()
            
    @pytest.mark.asyncio
    async def test_generate_concept_with_error(self, concept_service, mock_jigsawstack_client):
        """Test that errors are properly raised when image generation fails."""
        # Arrange
        mock_jigsawstack_client.generate_image = AsyncMock(return_value={})  # No URL in response
        
        # Act & Assert
        with pytest.raises(ConceptError, match="No image URL returned"):
            await concept_service.generate_concept(
                logo_description="Test logo",
                theme_description="Test theme"
            )
    
    @pytest.mark.asyncio
    async def test_generate_concept_with_palettes(
        self, 
        concept_service, 
        mock_jigsawstack_client, 
        mock_image_service
    ):
        """Test generating a concept with multiple palette variations."""
        # Arrange
        logo_description = "Test logo"
        theme_description = "Test theme"
        
        # Mock generate_concept to return a valid base concept
        with patch.object(
            concept_service,
            'generate_concept',
            AsyncMock(return_value={
                "image_url": "https://example.com/base_concept.png",
                "logo_description": logo_description,
                "theme_description": theme_description
            })
        ) as mock_generate:
            # Mock palette generator to return test palettes
            with patch.object(
                concept_service.palette_generator,
                'generate_palettes',
                AsyncMock(return_value=[
                    {"name": "Palette 1", "colors": ["#123456", "#789ABC"]},
                    {"name": "Palette 2", "colors": ["#ABCDEF", "#012345"]}
                ])
            ) as mock_palettes:
                # Mock _download_image to avoid actual HTTP requests
                with patch.object(
                    concept_service,
                    '_download_image',
                    AsyncMock(return_value=b'fake_image_data')
                ) as mock_download:
                    # Act
                    base_concept, variations = await concept_service.generate_concept_with_palettes(
                        logo_description=logo_description,
                        theme_description=theme_description,
                        num_palettes=2,
                        user_id="user-123"
                    )
                    
                    # Assert
                    assert base_concept["image_url"] == "https://example.com/base_concept.png"
                    assert len(variations) == 2
                    assert variations[0]["palette_id"] == "pal1"
                    assert variations[1]["image_url"] == "https://example.com/variation2.png"
                    
                    # Verify mock calls
                    mock_generate.assert_called_once()
                    mock_palettes.assert_called_once_with(
                        theme_description=theme_description,
                        logo_description=logo_description,
                        num_palettes=2
                    )
                    mock_download.assert_called_once()
                    mock_image_service.create_palette_variations.assert_called_once()

    @pytest.mark.asyncio
    async def test_refine_concept(self, concept_service):
        """Test refining an existing concept."""
        # Arrange
        image_url = "https://example.com/original.png"
        refinement_prompt = "Make the logo more vibrant"
        
        # Mock _download_image to return dummy data
        with patch.object(
            concept_service,
            '_download_image',
            AsyncMock(return_value=b'original_image_data')
        ):
            # Mock the refiner's refine_image method
            with patch.object(
                concept_service.refiner,
                'refine_image',
                AsyncMock(return_value={"url": "https://example.com/refined.png"})
            ) as mock_refine:
                # Act
                with patch.object(
                    concept_service.image_persistence,
                    'store_image',
                    MagicMock(return_value=("refined/path.png", "https://example.com/stored_refined.png"))
                ):
                    result = await concept_service.refine_concept(
                        original_image_url=image_url,
                        logo_description="Original logo",
                        theme_description="Original theme",
                        refinement_prompt=refinement_prompt,
                        preserve_aspects=["layout", "style"],
                        user_id="user-123"
                    )
                    
                    # Assert
                    assert isinstance(result, dict)
                    assert "image_url" in result
                    
                    # Verify the refiner was called
                    mock_refine.assert_called_once()

    @pytest.mark.asyncio
    async def test_download_image(self, concept_service):
        """Test the _download_image method."""
        # Arrange
        image_url = "https://example.com/test.png"
        mock_response = MagicMock()
        mock_response.read = AsyncMock(return_value=b'test_image_data')
        
        # Act
        with patch('httpx.AsyncClient.get', AsyncMock(return_value=mock_response)):
            result = await concept_service._download_image(image_url)
            
            # Assert
            assert result == b'test_image_data'
            
    @pytest.mark.asyncio
    async def test_download_image_error(self, concept_service):
        """Test error handling in the _download_image method."""
        # Arrange
        image_url = "https://example.com/test.png"
        
        # Act & Assert
        with patch('httpx.AsyncClient.get', AsyncMock(side_effect=Exception("Connection error"))):
            result = await concept_service._download_image(image_url)
            assert result is None 