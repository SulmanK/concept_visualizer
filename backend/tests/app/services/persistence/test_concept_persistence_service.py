"""
Tests for ConceptPersistenceService.

This module tests the ConceptPersistenceService class which is responsible for
storing and retrieving concept data using ConceptStorage.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
import uuid
from typing import Dict, Any, List
import requests

from app.services.persistence.concept_persistence_service import (
    ConceptPersistenceService,
    PersistenceError,
    NotFoundError,
)
from app.core.exceptions import DatabaseTransactionError
from app.core.supabase.concept_storage import ConceptStorage


class TestConceptPersistenceService:
    """Tests for the ConceptPersistenceService class."""

    @pytest.fixture
    def mock_concept_storage(self):
        """Create a mock ConceptStorage."""
        storage = MagicMock(spec=ConceptStorage)
        
        # Set up synchronous mocks
        storage.store_concept = MagicMock(return_value={"id": "concept-123"})
        storage.store_color_variations = MagicMock(return_value=[{"id": "var-1"}, {"id": "var-2"}])
        storage.get_concept_detail = MagicMock()  # Will be set in tests
        storage.get_recent_concepts = MagicMock()  # Will be set in tests
        storage.get_variations_by_concept_ids = MagicMock()  # Will be set in tests
        storage.delete_all_concepts = MagicMock()  # Will be set in tests
        storage.get_concept_by_task_id = MagicMock()  # Will be set in tests
        
        return storage

    @pytest.fixture
    def mock_client(self):
        """Create a mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client, mock_concept_storage):
        """Create a ConceptPersistenceService with mocks."""
        service = ConceptPersistenceService(mock_client)
        service.concept_storage = mock_concept_storage
        return service

    @pytest.mark.asyncio
    async def test_store_concept_success(self, service, mock_concept_storage):
        """Test successful concept storage."""
        # Setup test data
        concept_data = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue and minimalist theme",
            "image_path": "user-123/image.png",
            "image_url": "https://example.com/image.png",
            "color_palettes": [
                {
                    "name": "Blue Palette",
                    "description": "A blue color palette",
                    "colors": ["#0000FF", "#000088", "#0000AA"],
                    "image_path": "user-123/palette1.png",
                    "image_url": "https://example.com/palette1.png"
                },
                {
                    "name": "Green Palette",
                    "description": "A green color palette",
                    "colors": ["#00FF00", "#008800", "#00AA00"],
                    "image_path": "user-123/palette2.png",
                    "image_url": "https://example.com/palette2.png"
                }
            ]
        }

        # Call the method
        concept_id = await service.store_concept(concept_data)

        # Verify the storage methods were called with correct data
        mock_concept_storage.store_concept.assert_called_once()
        store_concept_call = mock_concept_storage.store_concept.call_args[0][0]
        assert store_concept_call["user_id"] == "user-123"
        assert store_concept_call["logo_description"] == "A modern tech logo"
        assert store_concept_call["theme_description"] == "Blue and minimalist theme"
        assert store_concept_call["image_path"] == "user-123/image.png"

        # Verify color variations storage
        mock_concept_storage.store_color_variations.assert_called_once()
        variations_call = mock_concept_storage.store_color_variations.call_args[0][0]
        assert len(variations_call) == 2
        assert variations_call[0]["concept_id"] == "concept-123"
        assert variations_call[0]["palette_name"] == "Blue Palette"
        assert variations_call[1]["palette_name"] == "Green Palette"

        # Verify the concept ID is returned
        assert concept_id == "concept-123"

    @pytest.mark.asyncio
    async def test_store_concept_no_color_palettes(self, service, mock_concept_storage):
        """Test concept storage without color palettes."""
        # Setup test data without color palettes
        concept_data = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue and minimalist theme",
            "image_path": "user-123/image.png"
        }

        # Call the method
        concept_id = await service.store_concept(concept_data)

        # Verify the storage methods were called correctly
        mock_concept_storage.store_concept.assert_called_once()
        
        # Verify color variations storage was not called
        mock_concept_storage.store_color_variations.assert_not_called()

        # Verify the concept ID is returned
        assert concept_id == "concept-123"

    @pytest.mark.asyncio
    async def test_store_concept_storage_error(self, service, mock_concept_storage):
        """Test handling of storage errors."""
        # Setup ConceptStorage.store_concept to fail
        mock_concept_storage.store_concept.return_value = None

        # Setup test data
        concept_data = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue theme",
            "image_path": "user-123/image.png"
        }

        # Call the method and expect PersistenceError
        with pytest.raises(PersistenceError) as excinfo:
            await service.store_concept(concept_data)

        # Verify error message
        assert "Failed to store concept" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_store_concept_variations_error(self, service, mock_concept_storage):
        """Test handling of variations storage errors with transaction rollback."""
        # Setup ConceptStorage.store_color_variations to fail
        mock_concept_storage.store_color_variations.return_value = None

        # Mock _delete_concept for cleanup
        original_delete_concept = service._delete_concept
        
        # Create a spy to track calls without affecting functionality
        delete_concept_spy = AsyncMock(side_effect=lambda concept_id: True)
        service._delete_concept = delete_concept_spy

        # Setup test data with color palettes
        concept_data = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue theme",
            "image_path": "user-123/image.png",
            "color_palettes": [
                {
                    "name": "Blue Palette",
                    "colors": ["#0000FF"],
                    "image_path": "user-123/palette1.png"
                }
            ]
        }

        # Call the method and expect DatabaseTransactionError
        with pytest.raises(DatabaseTransactionError) as excinfo:
            await service.store_concept(concept_data)

        # Verify error message
        assert "Failed to store color variations" in str(excinfo.value)
        
        # Verify cleanup was attempted
        delete_concept_spy.assert_called_with("concept-123")
        
        # Restore the original method
        service._delete_concept = original_delete_concept

    @pytest.mark.asyncio
    async def test_store_concept_variations_exception(self, service, mock_concept_storage):
        """Test handling of exceptions during variations storage with transaction rollback."""
        # Setup ConceptStorage.store_color_variations to raise an exception
        mock_concept_storage.store_color_variations.side_effect = ValueError("Test error")

        # Mock _delete_concept for cleanup
        service._delete_concept = AsyncMock(return_value=True)

        # Setup test data with color palettes
        concept_data = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue theme",
            "image_path": "user-123/image.png",
            "color_palettes": [
                {
                    "name": "Blue Palette",
                    "colors": ["#0000FF"],
                    "image_path": "user-123/palette1.png"
                }
            ]
        }

        # Call the method and expect DatabaseTransactionError
        with pytest.raises(DatabaseTransactionError) as excinfo:
            await service.store_concept(concept_data)

        # Verify error message
        assert "Error storing color variations" in str(excinfo.value)
        assert "Test error" in str(excinfo.value)
        
        # Verify cleanup was attempted
        service._delete_concept.assert_called_once_with("concept-123")

    @pytest.mark.asyncio
    async def test_delete_concept(self, service):
        """Test _delete_concept method."""
        # Mock the requests module
        with patch('requests.delete') as mock_delete:
            # Setup mock response
            mock_response = MagicMock()
            mock_response.status_code = 204
            mock_delete.return_value = mock_response
            
            # Mock service role key
            service.supabase.settings = MagicMock()
            service.supabase.settings.SUPABASE_SERVICE_ROLE = "service-role-key"
            service.supabase.settings.SUPABASE_URL = "https://example.supabase.co"

            # Call the method
            result = await service._delete_concept("concept-123")
            
            # Verify requests.delete was called with correct parameters
            mock_delete.assert_called_once()
            args, kwargs = mock_delete.call_args
            assert args[0] == "https://example.supabase.co/rest/v1/concepts?id=eq.concept-123"
            assert kwargs["headers"]["apikey"] == "service-role-key"
            assert kwargs["headers"]["Authorization"] == "Bearer service-role-key"
            
            # Verify result
            assert result is True

    @pytest.mark.asyncio
    async def test_delete_concept_error(self, service):
        """Test _delete_concept method with error response."""
        # Mock the requests module
        with patch('requests.delete') as mock_delete:
            # Setup mock response with error status
            mock_response = MagicMock()
            mock_response.status_code = 500
            mock_response.text = "Internal Server Error"
            mock_delete.return_value = mock_response
            
            # Mock service role key
            service.supabase.settings = MagicMock()
            service.supabase.settings.SUPABASE_SERVICE_ROLE = "service-role-key"
            service.supabase.settings.SUPABASE_URL = "https://example.supabase.co"

            # Call the method
            result = await service._delete_concept("concept-123")
            
            # Verify result is False due to error status
            assert result is False

    @pytest.mark.asyncio
    async def test_get_concept_detail_success(self, service, mock_concept_storage):
        """Test successful retrieval of concept detail."""
        # Setup mock to return plain data, not a coroutine
        mock_concept_detail = {
            "id": "concept-123",
            "user_id": "user-123",
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/concept-123/image.png",
            "variations": [
                {"id": "var-1", "palette_name": "Blue"}
            ]
        }
        mock_concept_storage.get_concept_detail.return_value = mock_concept_detail
        
        # Call the method
        result = await service.get_concept_detail("concept-123", "user-123")
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_detail.assert_called_once_with("concept-123", "user-123")
        
        # Verify result is correct
        assert result["id"] == "concept-123"
        assert result["user_id"] == "user-123"
        assert "variations" in result

    @pytest.mark.asyncio
    async def test_get_concept_detail_not_found(self, service, mock_concept_storage):
        """Test concept detail not found case."""
        # Setup the mock to return None
        mock_concept_storage.get_concept_detail.return_value = None
        
        # Call the method and expect NotFoundError
        with pytest.raises(NotFoundError):
            await service.get_concept_detail("nonexistent", "user-123")
            
        # Verify the storage method was called
        mock_concept_storage.get_concept_detail.assert_called_once_with("nonexistent", "user-123")

    @pytest.mark.asyncio
    async def test_get_concept_detail_wrong_user(self, service, mock_concept_storage):
        """Test concept detail security with wrong user."""
        # Setup mock to return None for wrong user
        mock_concept_storage.get_concept_detail.return_value = None
        
        # Call the method with wrong user and expect NotFoundError
        with pytest.raises(NotFoundError):
            await service.get_concept_detail("concept-123", "wrong-user")
            
        # Verify the correct parameters were passed
        mock_concept_storage.get_concept_detail.assert_called_once_with("concept-123", "wrong-user")

    @pytest.mark.asyncio
    async def test_get_recent_concepts_success(self, service, mock_concept_storage):
        """Test successful retrieval of recent concepts."""
        # Setup synchronous return values for mocks
        mock_concept_storage.get_recent_concepts.return_value = [
            {"id": "concept-123", "user_id": "user-123"},
            {"id": "concept-456", "user_id": "user-123"}
        ]
        mock_concept_storage.get_variations_by_concept_ids.return_value = {
            "concept-123": [{"id": "var-1", "palette_name": "Blue"}],
            "concept-456": [{"id": "var-2", "palette_name": "Red"}]
        }
        
        # Call the method
        result = await service.get_recent_concepts("user-123", 10)
        
        # Verify the storage methods were called correctly
        mock_concept_storage.get_recent_concepts.assert_called_once_with("user-123", 10)
        mock_concept_storage.get_variations_by_concept_ids.assert_called_once_with(["concept-123", "concept-456"])
        
        # Verify result structure
        assert len(result) == 2
        assert result[0]["id"] == "concept-123"
        assert len(result[0]["color_variations"]) == 1
        assert result[0]["color_variations"][0]["id"] == "var-1"

    @pytest.mark.asyncio
    async def test_get_recent_concepts_none_found(self, service, mock_concept_storage):
        """Test recent concepts with none found."""
        # Setup mock to return empty list
        mock_concept_storage.get_recent_concepts.return_value = []
        
        # Call the method
        result = await service.get_recent_concepts("user-123", 10)
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_recent_concepts.assert_called_once_with("user-123", 10)
        
        # Verify empty result
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_delete_all_concepts_success(self, service, mock_concept_storage):
        """Test successful deletion of all concepts."""
        # Setup mock to return True
        mock_concept_storage.delete_all_concepts.return_value = True
        
        # Call the method
        result = await service.delete_all_concepts("user-123")
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.delete_all_concepts.assert_called_once_with("user-123")
        
        # Verify the result is True
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_all_concepts_failure(self, service, mock_concept_storage):
        """Test deletion of all concepts with failure."""
        # Setup mock to return False
        mock_concept_storage.delete_all_concepts.return_value = False
        
        # Call the method
        result = await service.delete_all_concepts("user-123")
        
        # Verify the storage method was called
        mock_concept_storage.delete_all_concepts.assert_called_once_with("user-123")
        
        # Verify the result is False
        assert result is False

    @pytest.mark.asyncio
    async def test_get_concept_by_task_id_success(self, service, mock_concept_storage):
        """Test successful retrieval of concept by task ID."""
        # Setup mock to return concept data
        concept_data = {
            "id": "concept-123", 
            "user_id": "user-123",
            "task_id": "task-123"
        }
        mock_concept_storage.get_concept_by_task_id.return_value = concept_data
        
        # Call the method
        result = await service.get_concept_by_task_id("task-123", "user-123")
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_by_task_id.assert_called_once_with("task-123", "user-123")
        
        # Verify result is as expected
        assert result["id"] == "concept-123"
        assert result["user_id"] == "user-123"
        assert result["task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_get_concept_by_task_id_not_found(self, service, mock_concept_storage):
        """Test retrieval of concept by task ID when not found."""
        # Setup mock to return None
        mock_concept_storage.get_concept_by_task_id.return_value = None
        
        # Call the method
        result = await service.get_concept_by_task_id("nonexistent-task", "user-123")
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_by_task_id.assert_called_once_with("nonexistent-task", "user-123")
        
        # Verify result is None
        assert result is None
        
    @pytest.mark.asyncio
    async def test_get_concept_by_task_id_wrong_user(self, service, mock_concept_storage):
        """Test retrieval of concept by task ID with wrong user."""
        # Setup mock to return None for wrong user
        mock_concept_storage.get_concept_by_task_id.return_value = None
        
        # Call the method
        result = await service.get_concept_by_task_id("task-123", "wrong-user")
        
        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_by_task_id.assert_called_once_with("task-123", "wrong-user")
        
        # Verify result is None
        assert result is None 