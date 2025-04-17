"""
Tests for the concept storage API endpoints.

These tests validate the routes for retrieving, storing, and deleting concepts.
"""

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import uuid
import json
from typing import Dict, Any, List

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_concept_persistence_service():
    """Create a mock ConceptPersistenceService for testing."""
    mock_service = AsyncMock()
    
    # Configure default responses
    concept_id = str(uuid.uuid4())
    mock_service.get_concept_detail.return_value = {
        "id": concept_id,
        "logo_description": "Test logo",
        "theme_description": "Test theme",
        "image_url": "https://example.com/concept.png",
        "created_at": "2023-01-01T00:00:00"
    }
    
    mock_service.get_recent_concepts.return_value = [
        {
            "id": str(uuid.uuid4()),
            "logo_description": "Logo 1",
            "theme_description": "Theme 1",
            "image_url": "https://example.com/concept1.png",
            "created_at": "2023-01-01T00:00:00"
        },
        {
            "id": str(uuid.uuid4()),
            "logo_description": "Logo 2",
            "theme_description": "Theme 2",
            "image_url": "https://example.com/concept2.png",
            "created_at": "2023-01-02T00:00:00"
        }
    ]
    
    return mock_service


@pytest.fixture
def mock_image_persistence_service():
    """Create a mock ImagePersistenceService for testing."""
    mock_service = MagicMock()
    
    # Configure default responses
    mock_service.delete_image.return_value = True
    mock_service.get_image_url.return_value = "https://example.com/test-image.png"
    
    return mock_service


def test_get_concept(client, mock_concept_persistence_service):
    """Test retrieving a concept by ID."""
    concept_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Mock the persistence service
    with patch(
        "app.api.routes.concept_storage.get_concept_persistence_service", 
        return_value=mock_concept_persistence_service
    ):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get(f"/api/concepts/{concept_id}", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_concept_persistence_service.get_concept_detail.return_value["id"]
        assert data["logo_description"] == "Test logo"
        
        # Verify the mock was called correctly
        mock_concept_persistence_service.get_concept_detail.assert_called_once_with(concept_id)


def test_get_concept_not_found(client, mock_concept_persistence_service):
    """Test error handling when concept is not found."""
    concept_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Configure mock to return None (not found)
    mock_concept_persistence_service.get_concept_detail.return_value = None
    
    # Mock the persistence service
    with patch(
        "app.api.routes.concept_storage.get_concept_persistence_service", 
        return_value=mock_concept_persistence_service
    ):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get(f"/api/concepts/{concept_id}", headers=headers)
        
        # Verify the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


def test_get_recent_concepts(client, mock_concept_persistence_service):
    """Test retrieving recent concepts."""
    user_id = "user-123"
    
    # Mock the persistence service
    with patch(
        "app.api.routes.concept_storage.get_concept_persistence_service", 
        return_value=mock_concept_persistence_service
    ):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get("/api/concepts/recent", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["logo_description"] == "Logo 1"
        assert data[1]["theme_description"] == "Theme 2"
        
        # Verify the mock was called correctly
        mock_concept_persistence_service.get_recent_concepts.assert_called_once()


def test_delete_concept(client, mock_concept_persistence_service, mock_image_persistence_service):
    """Test deleting a concept."""
    concept_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Configure mock to return a concept with an image
    mock_concept_persistence_service.get_concept_detail.return_value = {
        "id": concept_id,
        "image_path": "user-123/image.png",
        "user_id": user_id
    }
    mock_concept_persistence_service.delete_concept.return_value = True
    
    # Mock both services
    with patch(
        "app.api.routes.concept_storage.get_concept_persistence_service", 
        return_value=mock_concept_persistence_service
    ):
        with patch(
            "app.api.routes.concept_storage.get_image_persistence_service", 
            return_value=mock_image_persistence_service
        ):
            # Add auth headers
            headers = {"Authorization": f"Bearer {user_id}"}
            
            # Make the request
            response = client.delete(f"/api/concepts/{concept_id}", headers=headers)
            
            # Verify the response
            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            
            # Verify the mocks were called correctly
            mock_concept_persistence_service.delete_concept.assert_called_once_with(concept_id)
            mock_image_persistence_service.delete_image.assert_called_once_with("user-123/image.png")


def test_store_concept(client, mock_concept_persistence_service):
    """Test storing a new concept."""
    user_id = "user-123"
    new_concept_id = str(uuid.uuid4())
    
    # Configure mock to return a specific ID for the stored concept
    mock_concept_persistence_service.store_concept.return_value = {"id": new_concept_id}
    
    # Concept data to store
    concept_data = {
        "logo_description": "New test logo",
        "theme_description": "New test theme",
        "image_url": "https://example.com/new-concept.png",
        "image_path": "user-123/new-image.png"
    }
    
    # Mock the persistence service
    with patch(
        "app.api.routes.concept_storage.get_concept_persistence_service", 
        return_value=mock_concept_persistence_service
    ):
        # Add auth headers
        headers = {
            "Authorization": f"Bearer {user_id}",
            "Content-Type": "application/json"
        }
        
        # Make the request
        response = client.post(
            "/api/concepts",
            headers=headers,
            json=concept_data
        )
        
        # Verify the response
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == new_concept_id
        
        # Verify the mock was called correctly
        mock_concept_persistence_service.store_concept.assert_called_once()
        # Check if the user_id was added to the concept data
        call_args = mock_concept_persistence_service.store_concept.call_args[0][0]
        assert call_args["user_id"] == user_id
        assert call_args["logo_description"] == "New test logo" 