"""Tests for the concept generation and refinement endpoints."""

import datetime
import unittest.mock as mock
import uuid
from typing import Any, Dict, Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.jigsawstack.client import JigsawStackClient

client = TestClient(app)


@pytest.fixture
def mock_jigsawstack_client() -> Generator[MagicMock, None, None]:
    """Mock JigsawStackClient to avoid real API calls during tests."""
    with mock.patch("backend.app.services.concept_service.get_jigsawstack_client") as mocked_factory:
        mocked_client = mock.AsyncMock(spec=JigsawStackClient)
        mocked_factory.return_value = mocked_client
        yield mocked_client


@pytest.fixture
def sample_generation_response() -> Dict[str, Any]:
    """Generate a sample response for concept generation."""
    return {
        "image_url": "https://example.com/image.png",
        "color_palette": {
            "primary": "#4F46E5",
            "secondary": "#818CF8",
            "accent": "#EEF2FF",
            "background": "#FFFFFF",
            "text": "#1E1B4B",
            "additional_colors": ["#C7D2FE", "#E0E7FF"],
        },
        "generation_id": str(uuid.uuid4()),
        "created_at": datetime.datetime.utcnow().isoformat(),
    }


@pytest.mark.asyncio
async def test_generate_concept(mock_jigsawstack_client: MagicMock, sample_generation_response: Dict[str, Any]) -> None:
    """Test concept generation endpoint with valid input."""
    # Mock the generate_image method
    mock_jigsawstack_client.generate_image.return_value = sample_generation_response["image_url"]

    # Mock the generate_color_palette method
    mock_jigsawstack_client.generate_color_palette.return_value = [
        sample_generation_response["color_palette"]["primary"],
        sample_generation_response["color_palette"]["secondary"],
        sample_generation_response["color_palette"]["accent"],
        sample_generation_response["color_palette"]["background"],
        sample_generation_response["color_palette"]["text"],
        *sample_generation_response["color_palette"]["additional_colors"],
    ]

    # Test valid request
    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "A modern tech logo with abstract shapes",
            "theme_description": "Professional blue theme with gradients",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check structure of response
    assert "image_url" in data
    assert "color_palette" in data
    assert "generation_id" in data
    assert "created_at" in data

    # Check color palette structure
    assert "primary" in data["color_palette"]
    assert "secondary" in data["color_palette"]
    assert "accent" in data["color_palette"]
    assert "background" in data["color_palette"]
    assert "text" in data["color_palette"]
    assert "additional_colors" in data["color_palette"]

    # Verify the mocked client was called with expected arguments
    mock_jigsawstack_client.generate_image.assert_called_once()
    mock_jigsawstack_client.generate_color_palette.assert_called_once()


@pytest.mark.asyncio
async def test_generate_concept_with_invalid_inputs(
    mock_jigsawstack_client: MagicMock,
) -> None:
    """Test concept generation endpoint with invalid inputs."""
    # Test empty logo description
    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "",
            "theme_description": "Professional blue theme with gradients",
        },
    )
    assert response.status_code == 422

    # Test too short logo description
    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "Logo",
            "theme_description": "Professional blue theme with gradients",
        },
    )
    assert response.status_code == 422

    # Test empty theme description
    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "A modern tech logo with abstract shapes",
            "theme_description": "",
        },
    )
    assert response.status_code == 422

    # Test too short theme description
    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "A modern tech logo with abstract shapes",
            "theme_description": "Blue",
        },
    )
    assert response.status_code == 422

    # Test missing fields
    response = client.post(
        "/api/concepts/generate",
        json={"logo_description": "A modern tech logo with abstract shapes"},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_generate_concept_handles_service_errors(
    mock_jigsawstack_client: MagicMock,
) -> None:
    """Test that the generate concept endpoint handles service errors properly."""
    # Mock service to raise an exception
    mock_jigsawstack_client.generate_image.side_effect = Exception("API Connection Error")

    response = client.post(
        "/api/concepts/generate",
        json={
            "logo_description": "A modern tech logo with abstract shapes",
            "theme_description": "Professional blue theme with gradients",
        },
    )

    assert response.status_code == 500
    assert "detail" in response.json()


@pytest.mark.asyncio
async def test_refine_concept(mock_jigsawstack_client: MagicMock, sample_generation_response: Dict[str, Any]) -> None:
    """Test concept refinement endpoint with valid input."""
    # Mock the refine_image method
    mock_jigsawstack_client.refine_image.return_value = sample_generation_response["image_url"]

    # Mock the generate_color_palette method
    mock_jigsawstack_client.generate_color_palette.return_value = [
        sample_generation_response["color_palette"]["primary"],
        sample_generation_response["color_palette"]["secondary"],
        sample_generation_response["color_palette"]["accent"],
        sample_generation_response["color_palette"]["background"],
        sample_generation_response["color_palette"]["text"],
        *sample_generation_response["color_palette"]["additional_colors"],
    ]

    # Test valid request
    response = client.post(
        "/api/concepts/refine",
        json={
            "original_image_url": "https://example.com/original.png",
            "logo_description": "An improved tech logo with smoother shapes",
            "theme_description": "More vibrant blue theme with brighter gradients",
            "refinement_prompt": "Make the logo more modern and professional",
            "preserve_aspects": ["layout", "colors"],
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Check structure of response
    assert "image_url" in data
    assert "color_palette" in data
    assert "generation_id" in data
    assert "created_at" in data
    assert "original_image_url" in data
    assert "refinement_prompt" in data

    # Verify the mocked client was called with expected arguments
    mock_jigsawstack_client.refine_image.assert_called_once()
    mock_jigsawstack_client.generate_color_palette.assert_called_once()


@pytest.mark.asyncio
async def test_refine_concept_with_invalid_inputs(
    mock_jigsawstack_client: MagicMock,
) -> None:
    """Test concept refinement endpoint with invalid inputs."""
    # Test invalid URL
    response = client.post(
        "/api/concepts/refine",
        json={
            "original_image_url": "not-a-url",
            "refinement_prompt": "Make the logo more modern",
        },
    )
    assert response.status_code == 422

    # Test missing original image URL
    response = client.post("/api/concepts/refine", json={"refinement_prompt": "Make the logo more modern"})
    assert response.status_code == 422

    # Test missing refinement prompt
    response = client.post(
        "/api/concepts/refine",
        json={"original_image_url": "https://example.com/original.png"},
    )
    assert response.status_code == 422

    # Test too short refinement prompt
    response = client.post(
        "/api/concepts/refine",
        json={
            "original_image_url": "https://example.com/original.png",
            "refinement_prompt": "Fix",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_refine_concept_handles_service_errors(
    mock_jigsawstack_client: MagicMock,
) -> None:
    """Test that the refine concept endpoint handles service errors properly."""
    # Mock service to raise an exception
    mock_jigsawstack_client.refine_image.side_effect = Exception("API Connection Error")

    response = client.post(
        "/api/concepts/refine",
        json={
            "original_image_url": "https://example.com/original.png",
            "refinement_prompt": "Make the logo more modern and professional",
        },
    )

    assert response.status_code == 500
    assert "detail" in response.json()
