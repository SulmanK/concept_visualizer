"""Tests for ConceptPersistenceService.

This module tests the ConceptPersistenceService class which is responsible for
storing and retrieving concept data using ConceptStorage.
"""

# Type ignore comment for mypy to ignore method assignment errors
# mypy: disable-error-code="method-assign"

from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from app.core.config import settings
from app.core.exceptions import DatabaseTransactionError
from app.core.supabase.concept_storage import ConceptStorage
from app.services.persistence.concept_persistence_service import ConceptPersistenceService, NotFoundError, PersistenceError


class TestConceptPersistenceService:
    """Tests for the ConceptPersistenceService class."""

    @pytest.fixture
    def mock_concept_storage(self) -> MagicMock:
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
    def mock_client(self) -> MagicMock:
        """Create a mock Supabase client."""
        client = MagicMock()
        return client

    @pytest.fixture
    def service(self, mock_client: MagicMock, mock_concept_storage: MagicMock) -> ConceptPersistenceService:
        """Create a ConceptPersistenceService with mocks."""
        service = ConceptPersistenceService(mock_client)
        service.concept_storage = mock_concept_storage
        # To make testing easier, create a mock supabase object
        service.supabase = MagicMock()
        service.supabase.get_service_role_client = MagicMock()
        return service

    @pytest.mark.asyncio
    async def test_store_concept_success(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test successful concept storage."""
        # Setup test data
        concept_data: Dict[str, Any] = {
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
                    "image_url": "https://example.com/palette1.png",
                },
                {
                    "name": "Green Palette",
                    "description": "A green color palette",
                    "colors": ["#00FF00", "#008800", "#00AA00"],
                    "image_path": "user-123/palette2.png",
                    "image_url": "https://example.com/palette2.png",
                },
            ],
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
    async def test_store_concept_no_color_palettes(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test concept storage without color palettes."""
        # Setup test data without color palettes
        concept_data: Dict[str, Any] = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue and minimalist theme",
            "image_path": "user-123/image.png",
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
    async def test_store_concept_storage_error(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test handling of storage errors."""
        # Setup ConceptStorage.store_concept to fail
        mock_concept_storage.store_concept.return_value = None

        # Setup test data
        concept_data: Dict[str, Any] = {
            "user_id": "user-123",
            "logo_description": "A modern tech logo",
            "theme_description": "Blue theme",
            "image_path": "user-123/image.png",
        }

        # Call the method and expect PersistenceError
        with pytest.raises(PersistenceError) as excinfo:
            await service.store_concept(concept_data)

        # Verify error message
        assert "Failed to store concept" in str(excinfo.value)

    @pytest.mark.asyncio
    async def test_store_concept_variations_error(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test handling of variations storage errors with transaction rollback."""
        # Setup ConceptStorage.store_color_variations to fail
        mock_concept_storage.store_color_variations.return_value = None

        # Create a spy to track calls without affecting functionality
        delete_concept_spy = AsyncMock(side_effect=lambda concept_id: True)

        # Use monkeypatching with patch to avoid method assignment errors
        with patch.object(service, "_delete_concept", new=delete_concept_spy):
            # Setup test data with color palettes
            concept_data: Dict[str, Any] = {
                "user_id": "user-123",
                "logo_description": "A modern tech logo",
                "theme_description": "Blue theme",
                "image_path": "user-123/image.png",
                "color_palettes": [
                    {
                        "name": "Blue Palette",
                        "colors": ["#0000FF"],
                        "image_path": "user-123/palette1.png",
                    }
                ],
            }

            # Call the method and expect DatabaseTransactionError
            with pytest.raises(DatabaseTransactionError) as excinfo:
                await service.store_concept(concept_data)

            # Verify error message
            assert "Failed to store color variations" in str(excinfo.value)

            # Verify cleanup was attempted
            delete_concept_spy.assert_called_with("concept-123")

    @pytest.mark.asyncio
    async def test_store_concept_variations_exception(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test handling of exceptions during variations storage with transaction rollback."""
        # Setup ConceptStorage.store_color_variations to raise an exception
        mock_concept_storage.store_color_variations.side_effect = ValueError("Test error")

        # Create a mock for the _delete_concept method
        delete_concept_mock = AsyncMock(return_value=True)

        # Use monkeypatching with patch to avoid method assignment errors
        with patch.object(service, "_delete_concept", new=delete_concept_mock):
            # Setup test data with color palettes
            concept_data: Dict[str, Any] = {
                "user_id": "user-123",
                "logo_description": "A modern tech logo",
                "theme_description": "Blue theme",
                "image_path": "user-123/image.png",
                "color_palettes": [
                    {
                        "name": "Blue Palette",
                        "colors": ["#0000FF"],
                        "image_path": "user-123/palette1.png",
                    }
                ],
            }

            # Call the method and expect DatabaseTransactionError
            with pytest.raises(DatabaseTransactionError) as excinfo:
                await service.store_concept(concept_data)

            # Verify error message
            assert "Error storing color variations" in str(excinfo.value)
            assert "Test error" in str(excinfo.value)

            # Verify cleanup was attempted
            delete_concept_mock.assert_called_once_with("concept-123")

    @pytest.mark.asyncio
    async def test_delete_concept(self, service: ConceptPersistenceService) -> None:
        """Test _delete_concept method."""
        # Create mock objects for Supabase client chain
        mock_service_client = MagicMock()

        # Create mock for color_variations table
        mock_var_table = MagicMock()
        mock_var_delete = MagicMock()
        mock_var_eq = MagicMock()
        mock_var_execute = MagicMock()

        # Create mock for concepts table
        mock_concept_table = MagicMock()
        mock_concept_delete = MagicMock()
        mock_concept_eq = MagicMock()
        mock_concept_execute = MagicMock()

        # Set up the chain for the color_variations table
        mock_var_table.delete.return_value = mock_var_delete
        mock_var_delete.eq.return_value = mock_var_eq
        mock_var_eq.execute.return_value = mock_var_execute

        # Set up the chain for the concepts table
        mock_concept_table.delete.return_value = mock_concept_delete
        mock_concept_delete.eq.return_value = mock_concept_eq
        mock_concept_eq.execute.return_value = mock_concept_execute

        # Set up the table side effect
        def table_side_effect(table_name: str) -> MagicMock:
            if table_name == settings.DB_TABLE_PALETTES:
                return mock_var_table
            elif table_name == settings.DB_TABLE_CONCEPTS:
                return mock_concept_table
            return MagicMock()

        # Set the table side effect
        mock_service_client.table.side_effect = table_side_effect

        # Mock the service role client - ensure it returns a proper MagicMock
        mock_get_service_role = MagicMock()
        mock_get_service_role.return_value = mock_service_client
        # Set it on the service.supabase
        service.supabase.get_service_role_client = mock_get_service_role

        # Call the method
        result = await service._delete_concept("concept-123")

        # Verify that service client was obtained
        mock_get_service_role.assert_called_once()

        # Verify table calls
        assert mock_service_client.table.call_count == 2
        mock_service_client.table.assert_any_call(settings.DB_TABLE_PALETTES)
        mock_service_client.table.assert_any_call(settings.DB_TABLE_CONCEPTS)

        # Verify delete calls
        mock_var_delete.eq.assert_called_once_with("concept_id", "concept-123")
        mock_concept_delete.eq.assert_called_once_with("id", "concept-123")

        # Verify execute calls
        mock_var_eq.execute.assert_called_once()
        mock_concept_eq.execute.assert_called_once()

        # Verify the result
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_concept_error(self, service: ConceptPersistenceService) -> None:
        """Test _delete_concept method with error response."""
        # Create mock objects for Supabase client chain
        mock_service_client = MagicMock()

        # Set up mock table method to handle multiple calls
        mock_variations_delete = MagicMock()
        mock_concepts_delete = MagicMock()

        # Set up the mock chain to raise an exception for variations table
        mock_variations_eq = MagicMock()
        mock_variations_eq.execute.side_effect = Exception("Database error")
        mock_variations_delete.eq.return_value = mock_variations_eq
        mock_variations_delete.delete.return_value = mock_variations_delete

        # Set up the mock chain for concepts table (won't be called due to exception)
        mock_concepts_eq = MagicMock()
        mock_concepts_eq.execute.return_value = None
        mock_concepts_delete.eq.return_value = mock_concepts_eq
        mock_concepts_delete.delete.return_value = mock_concepts_delete

        # Set up table method to return different mocks depending on the argument
        def table_side_effect(table_name: str) -> MagicMock:
            if table_name == settings.DB_TABLE_PALETTES:
                return mock_variations_delete
            elif table_name == settings.DB_TABLE_CONCEPTS:
                return mock_concepts_delete
            return MagicMock()

        mock_service_client.table.side_effect = table_side_effect

        # Mock the service role client - ensure it returns a proper MagicMock
        mock_get_service_role = MagicMock()
        mock_get_service_role.return_value = mock_service_client
        # Set it on the service.supabase
        service.supabase.get_service_role_client = mock_get_service_role

        # Call the method
        result = await service._delete_concept("concept-123")

        # Verify that service role client was called
        mock_get_service_role.assert_called_once()

        # Verify that both table methods were called
        mock_service_client.table.assert_any_call(settings.DB_TABLE_PALETTES)

        # Verify that only the variations table methods were called completely
        mock_variations_delete.eq.assert_called_once_with("concept_id", "concept-123")
        mock_variations_eq.execute.assert_called_once()

        # Concepts table methods should not be called due to exception
        mock_concepts_delete.eq.assert_not_called()

        # Verify the result
        assert result is False, "Should return False when an exception occurs"

    @pytest.mark.asyncio
    async def test_get_concept_detail_success(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test successful retrieval of concept detail."""
        # Setup mock to return plain data, not a coroutine
        mock_concept_detail: Dict[str, Any] = {
            "id": "concept-123",
            "user_id": "user-123",
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/concept-123/image.png",
            "variations": [{"id": "var-1", "palette_name": "Blue"}],
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
    async def test_get_concept_detail_not_found(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test concept detail not found case."""
        # Setup the mock to return None
        mock_concept_storage.get_concept_detail.return_value = None

        # Call the method and expect NotFoundError
        with pytest.raises(NotFoundError):
            await service.get_concept_detail("nonexistent", "user-123")

        # Verify the storage method was called
        mock_concept_storage.get_concept_detail.assert_called_once_with("nonexistent", "user-123")

    @pytest.mark.asyncio
    async def test_get_concept_detail_wrong_user(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test concept detail security with wrong user."""
        # Setup mock to return None for wrong user
        mock_concept_storage.get_concept_detail.return_value = None

        # Call the method with wrong user and expect NotFoundError
        with pytest.raises(NotFoundError):
            await service.get_concept_detail("concept-123", "wrong-user")

        # Verify the correct parameters were passed
        mock_concept_storage.get_concept_detail.assert_called_once_with("concept-123", "wrong-user")

    @pytest.mark.asyncio
    async def test_get_recent_concepts_success(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test successful retrieval of recent concepts."""
        # Setup synchronous return values for mocks
        mock_concept_storage.get_recent_concepts.return_value = [
            {"id": "concept-123", "user_id": "user-123"},
            {"id": "concept-456", "user_id": "user-123"},
        ]
        mock_concept_storage.get_variations_by_concept_ids.return_value = {
            "concept-123": [{"id": "var-1", "palette_name": "Blue"}],
            "concept-456": [{"id": "var-2", "palette_name": "Red"}],
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
    async def test_get_recent_concepts_none_found(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
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
    async def test_delete_all_concepts_success(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
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
    async def test_delete_all_concepts_failure(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
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
    async def test_get_concept_by_task_id_success(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test successful retrieval of concept by task ID."""
        # Setup mock to return concept data
        concept_data: Dict[str, Any] = {
            "id": "concept-123",
            "user_id": "user-123",
            "task_id": "task-123",
        }
        mock_concept_storage.get_concept_by_task_id.return_value = concept_data

        # Call the method
        result = await service.get_concept_by_task_id("task-123", "user-123")

        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_by_task_id.assert_called_once_with("task-123", "user-123")

        # Verify result is as expected
        assert result is not None  # Tell mypy the result is not None
        if result is not None:  # Use conditional check instead of cast
            assert result["id"] == "concept-123"
            assert result["user_id"] == "user-123"
            assert result["task_id"] == "task-123"

    @pytest.mark.asyncio
    async def test_get_concept_by_task_id_not_found(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
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
    async def test_get_concept_by_task_id_wrong_user(self, service: ConceptPersistenceService, mock_concept_storage: MagicMock) -> None:
        """Test retrieval of concept by task ID with wrong user."""
        # Setup mock to return None for wrong user
        mock_concept_storage.get_concept_by_task_id.return_value = None

        # Call the method
        result = await service.get_concept_by_task_id("task-123", "wrong-user")

        # Verify the storage method was called with correct parameters
        mock_concept_storage.get_concept_by_task_id.assert_called_once_with("task-123", "wrong-user")

        # Verify result is None
        assert result is None
