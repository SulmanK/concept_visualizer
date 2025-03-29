"""
Test Supabase storage integration.

This module tests the integration between the backend and Supabase Storage.
"""

import pytest
import os
import uuid
import httpx
from unittest.mock import patch, MagicMock

from backend.app.core.supabase import SupabaseClient
from backend.app.services.image_service import ImageService


@pytest.fixture
def supabase_client():
    """Create a mock Supabase client for testing."""
    with patch('backend.app.core.supabase.create_client') as mock_create_client:
        client = SupabaseClient(url="https://example.supabase.co", key="fake_key")
        # Set up mock storage responses
        storage_mock = MagicMock()
        client.client.storage.from_.return_value = storage_mock
        storage_mock.upload.return_value = {"Key": "test_upload_success"}
        storage_mock.get_public_url.return_value = "https://example.com/public/test-image.png"
        
        yield client


@pytest.fixture
def image_service(supabase_client):
    """Create a mock image service for testing."""
    with patch('backend.app.services.jigsawstack.client.JigsawStackClient') as mock_jigsawstack:
        jigsawstack_client = mock_jigsawstack.return_value
        jigsawstack_client.generate_image.return_value = "https://example.com/generated-image.png"
        jigsawstack_client.refine_image.return_value = "https://example.com/refined-image.png"
        
        service = ImageService(supabase_client, jigsawstack_client)
        yield service


@pytest.mark.asyncio
async def test_upload_image_from_url(supabase_client):
    """Test uploading an image from a URL to Supabase Storage."""
    with patch('requests.get') as mock_get:
        # Mock the HTTP response
        mock_response = MagicMock()
        mock_response.content = b"fake image content"
        mock_response.headers = {"Content-Type": "image/png"}
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        # Test uploading
        session_id = str(uuid.uuid4())
        result = await supabase_client.upload_image_from_url(
            "https://example.com/test-image.png",
            "concept-images",
            session_id
        )
        
        # Verify results
        assert result is not None
        assert session_id in result
        assert ".png" in result
        
        # Verify correct method calls
        mock_get.assert_called_once_with(
            "https://example.com/test-image.png", 
            timeout=10
        )
        supabase_client.client.storage.from_.assert_called_once_with("concept-images")
        supabase_client.client.storage.from_().upload.assert_called_once()


@pytest.mark.asyncio
async def test_get_image_url(supabase_client):
    """Test getting a public URL for an image in Supabase Storage."""
    # Test getting URL
    result = supabase_client.get_image_url("test/image.png", "concept-images")
    
    # Verify results
    assert result == "https://example.com/public/test-image.png"
    
    # Verify correct method calls
    supabase_client.client.storage.from_.assert_called_once_with("concept-images")
    supabase_client.client.storage.from_().get_public_url.assert_called_once_with("test/image.png")


@pytest.mark.asyncio
async def test_generate_and_store_image(image_service):
    """Test generating an image and storing it in Supabase."""
    # Test the full flow
    session_id = str(uuid.uuid4())
    storage_path, public_url = await image_service.generate_and_store_image(
        "A modern logo with blue and green colors",
        session_id
    )
    
    # Verify results
    assert storage_path is not None
    assert public_url is not None
    assert public_url == "https://example.com/public/test-image.png"
    
    # Verify JigsawStack was called
    image_service.jigsawstack_client.generate_image.assert_called_once()
    
    # Verify storage upload was called
    image_service.supabase_client.client.storage.from_.assert_called()


@pytest.mark.asyncio
async def test_create_palette_variations(image_service, supabase_client):
    """Test creating palette variations and storing them."""
    # Mock apply_color_palette
    async def mock_apply_palette(*args, **kwargs):
        return f"{args[2]}/palette-variation.png"
    
    supabase_client.apply_color_palette = mock_apply_palette
    
    # Test creating variations
    session_id = str(uuid.uuid4())
    palettes = [
        {"name": "Vibrant", "colors": ["#FF0000", "#00FF00", "#0000FF"]},
        {"name": "Pastel", "colors": ["#FFCCCC", "#CCFFCC", "#CCCCFF"]}
    ]
    
    results = await image_service.create_palette_variations(
        "original/image.png",
        palettes,
        session_id
    )
    
    # Verify results
    assert len(results) == 2
    assert "image_path" in results[0]
    assert "image_url" in results[0]
    assert session_id in results[0]["image_path"]
    assert results[0]["name"] == "Vibrant"
    assert results[1]["name"] == "Pastel"


if __name__ == "__main__":
    pytest.main(["-xvs", __file__]) 