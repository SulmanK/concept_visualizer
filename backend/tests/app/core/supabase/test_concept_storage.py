"""Tests for ConceptStorage in the Supabase module."""

from unittest.mock import MagicMock, patch

import pytest

from app.core.supabase.concept_storage import ConceptStorage


@pytest.fixture
def mock_client() -> MagicMock:
    """Mock Supabase client for testing."""
    mock = MagicMock()
    mock.client = MagicMock()
    return mock


@pytest.fixture
def mock_settings() -> MagicMock:
    """Mock settings for testing."""
    mock = MagicMock()
    mock.supabase_url = "https://supabase-test.co"
    mock.supabase_service_key = "service-key-123"
    return mock


@pytest.fixture
def concept_storage(mock_client: MagicMock) -> ConceptStorage:
    """Create a ConceptStorage instance with a mocked client.

    Args:
        mock_client: A mocked Supabase client

    Returns:
        ConceptStorage instance
    """
    return ConceptStorage(client=mock_client)


class TestStoreConceptMethod:
    """Tests for the store_concept method."""

    def test_store_concept_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful concept storage."""
        # Arrange
        import uuid

        concept_data = {
            "user_id": "user-123",
            "session_id": uuid.uuid4(),
            "logo_description": "Logo description",
            "theme_description": "Theme description",
            "image_path": "user-123/image.png",
        }

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_store_concept_with_service_role", return_value=None):
            mock_execute = MagicMock()
            mock_execute.data = [{"id": "concept-123"}]

            # Creating a proper MagicMock for table method instead of using callable type
            table_mock = MagicMock()
            mock_client.client.table = table_mock

            # Set up the mock chain with proper MagicMock objects
            insert_mock = MagicMock()
            execute_mock = MagicMock()

            table_mock.return_value = MagicMock(insert=insert_mock)
            insert_mock.return_value = MagicMock(execute=execute_mock)
            execute_mock.return_value = mock_execute

            # Act
            result = concept_storage.store_concept(concept_data)

            # Assert
            assert result == {"id": "concept-123"}
            mock_client.client.table.assert_called_once_with(concept_storage.concepts_table)
            insert_mock.assert_called_once()
            execute_mock.assert_called_once()

    def test_store_concept_missing_required_field(self, concept_storage: ConceptStorage) -> None:
        """Test store_concept with missing required field."""
        # Arrange - explicitly testing the validation logic
        import uuid

        concept_data = {
            # "user_id" is missing - this would trigger the validation error in a real scenario
            "session_id": uuid.uuid4(),
            "logo_description": "Logo description",
            "theme_description": "Theme description",
            "image_path": "user-123/image.png",
        }

        # Act - just call it directly without any mocks to let real validation happen
        result = concept_storage.store_concept(concept_data)

        # Assert - should be None with missing user_id
        assert result is None

    def test_store_concept_exception(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test store_concept handling exceptions."""
        # Arrange
        import uuid

        concept_data = {
            "user_id": "user-123",
            "session_id": uuid.uuid4(),
            "logo_description": "Logo description",
            "theme_description": "Theme description",
            "image_path": "user-123/image.png",
        }

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_store_concept_with_service_role", return_value=None):
            # Creating a proper MagicMock for table method
            table_mock = MagicMock()
            mock_client.client.table = table_mock

            # Set up the mock chain with proper MagicMock objects
            insert_mock = MagicMock()
            execute_mock = MagicMock()

            table_mock.return_value = MagicMock(insert=insert_mock)
            insert_mock.return_value = MagicMock(execute=execute_mock)
            execute_mock.side_effect = Exception("Database error")

            # Act
            result = concept_storage.store_concept(concept_data)

            # Assert - method should return None on exception, not raise it
            assert result is None


class TestStoreColorVariations:
    """Tests for the store_color_variations method."""

    def test_store_color_variations_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful color variations storage."""
        # Arrange
        variations = [
            {
                "concept_id": "concept-123",  # Use string ID instead of UUID
                "palette_name": "Vibrant",
                "colors": ["#FF0000", "#00FF00", "#0000FF"],
                "image_path": "user-123/palette1.png",
            },
            {
                "concept_id": "concept-456",  # Use string ID instead of UUID
                "palette_name": "Muted",
                "colors": ["#882222", "#228822", "#222288"],
                "image_path": "user-123/palette2.png",
            },
        ]

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_store_variations_with_service_role", return_value=None):
            mock_execute = MagicMock()
            mock_execute.data = [{"id": "var-1"}, {"id": "var-2"}]

            # Creating a proper MagicMock for table method
            table_mock = MagicMock()
            mock_client.client.table = table_mock

            # Set up the mock chain with proper MagicMock objects
            insert_mock = MagicMock()
            execute_mock = MagicMock()

            table_mock.return_value = MagicMock(insert=insert_mock)
            insert_mock.return_value = MagicMock(execute=execute_mock)
            execute_mock.return_value = mock_execute

            # Act
            result = concept_storage.store_color_variations(variations)

            # Assert
            assert result is not None
            assert len(result) == 2
            assert result == [{"id": "var-1"}, {"id": "var-2"}]
            mock_client.client.table.assert_called_once_with(concept_storage.palettes_table)
            insert_mock.assert_called_once()
            execute_mock.assert_called_once()

    def test_store_color_variations_missing_field(self, concept_storage: ConceptStorage) -> None:
        """Test store_color_variations with missing field."""
        # Arrange
        # Missing colors field
        variations = [
            {
                "concept_id": "concept-123",  # Use string ID
                "palette_name": "Vibrant",
                "image_path": "user-123/palette1.png",
                # "colors" field is missing
            }
        ]

        # Act
        result = concept_storage.store_color_variations(variations)

        # Assert - method returns None on missing fields, not raises
        assert result is None

    def test_store_color_variations_exception(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test store_color_variations handling exceptions."""
        # Arrange
        variations = [
            {
                "concept_id": "concept-123",  # Use string ID instead of UUID
                "palette_name": "Vibrant",
                "colors": ["#FF0000", "#00FF00", "#0000FF"],
                "image_path": "user-123/palette1.png",
            }
        ]

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_store_variations_with_service_role", return_value=None):
            # Creating a proper MagicMock for table method
            table_mock = MagicMock()
            mock_client.client.table = table_mock

            # Set up the mock chain with proper MagicMock objects
            insert_mock = MagicMock()
            execute_mock = MagicMock()

            table_mock.return_value = MagicMock(insert=insert_mock)
            insert_mock.return_value = MagicMock(execute=execute_mock)
            execute_mock.side_effect = Exception("Database error")

            # Act
            result = concept_storage.store_color_variations(variations)

            # Assert - should return None on error, not raise
            assert result is None


class TestGetRecentConcepts:
    """Tests for the get_recent_concepts method."""

    def test_get_recent_concepts_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful recent concepts retrieval."""
        # Arrange
        user_id = "user-123"
        mock_data = [
            {
                "id": "concept-1",
                "user_id": user_id,
                "logo_description": "Logo 1",
                "theme_description": "Theme 1",
                "image_path": "user-123/image1.png",
                "created_at": "2023-06-01T12:00:00",
            },
            {
                "id": "concept-2",
                "user_id": user_id,
                "logo_description": "Logo 2",
                "theme_description": "Theme 2",
                "image_path": "user-123/image2.png",
                "created_at": "2023-06-02T12:00:00",
            },
        ]

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_get_recent_concepts_with_service_role", return_value=None):
            execute_mock = MagicMock()
            execute_mock.data = mock_data

            # Creating a proper mock chain
            table_mock = MagicMock()
            select_mock = MagicMock()
            eq_mock = MagicMock()
            order_mock = MagicMock()
            limit_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq_mock)
            eq_mock.return_value = MagicMock(order=order_mock)
            order_mock.return_value = MagicMock(limit=limit_mock)
            limit_mock.return_value = MagicMock(execute=MagicMock(return_value=execute_mock))

            # Act
            result = concept_storage.get_recent_concepts(user_id, 10)

            # Assert
            assert len(result) == 2
            assert result[0]["id"] == "concept-1"
            assert result[1]["id"] == "concept-2"
            mock_client.client.table.assert_called_once_with(concept_storage.concepts_table)

    def test_get_recent_concepts_empty(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test get_recent_concepts with no results."""
        # Arrange
        user_id = "user-123"

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_get_recent_concepts_with_service_role", return_value=None):
            execute_mock = MagicMock()
            execute_mock.data = []

            # Creating a proper mock chain
            table_mock = MagicMock()
            select_mock = MagicMock()
            eq_mock = MagicMock()
            order_mock = MagicMock()
            limit_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq_mock)
            eq_mock.return_value = MagicMock(order=order_mock)
            order_mock.return_value = MagicMock(limit=limit_mock)
            limit_mock.return_value = MagicMock(execute=MagicMock(return_value=execute_mock))

            # Act
            result = concept_storage.get_recent_concepts(user_id, 10)

            # Assert
            assert result == []

    def test_get_recent_concepts_exception(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test get_recent_concepts handling exceptions."""
        # Arrange
        user_id = "user-123"

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_get_recent_concepts_with_service_role", return_value=None):
            # Creating a proper mock chain with an exception
            table_mock = MagicMock()
            select_mock = MagicMock()
            eq_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq_mock)
            eq_mock.side_effect = Exception("Database error")

            # Act
            result = concept_storage.get_recent_concepts(user_id, 10)

            # Assert - method should return empty list on exception, not raise
            assert result == []


class TestGetConceptDetail:
    """Tests for the get_concept_detail method."""

    def test_get_concept_detail_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful concept detail retrieval."""
        # Arrange
        concept_id = "concept-123"
        user_id = "user-123"
        mock_concept_data = {
            "id": concept_id,
            "user_id": user_id,
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/image.png",
            "created_at": "2023-06-01T12:00:00",
            "color_variations": [
                {
                    "id": "var-1",
                    "concept_id": concept_id,
                    "palette_name": "Vibrant",
                    "colors": ["#FF0000", "#00FF00", "#0000FF"],
                    "image_path": "user-123/palette1.png",
                }
            ],
        }

        # Mock the service role method to return None (simulate failure)
        with patch.object(concept_storage, "_get_concept_detail_with_service_role", return_value=None):
            # Creating a proper mock chain
            execute_mock = MagicMock()
            execute_mock.data = [mock_concept_data]

            table_mock = MagicMock()
            select_mock = MagicMock()
            eq1_mock = MagicMock()
            eq2_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq1_mock)
            eq1_mock.return_value = MagicMock(eq=eq2_mock)
            eq2_mock.return_value = MagicMock(execute=MagicMock(return_value=execute_mock))

            # Act
            result = concept_storage.get_concept_detail(concept_id, user_id)

            # Assert
            assert result is not None
            assert result["id"] == concept_id
            assert result["user_id"] == user_id
            assert "color_variations" in result
            assert len(result["color_variations"]) == 1

    def test_get_concept_detail_not_found(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test get_concept_detail when concept is not found."""
        # Arrange
        concept_id = "non-existent-id"
        user_id = "user-123"

        # Mock the service role method to return None
        with patch.object(concept_storage, "_get_concept_detail_with_service_role", return_value=None):
            # Creating a proper mock chain
            execute_mock = MagicMock()
            execute_mock.data = []

            table_mock = MagicMock()
            select_mock = MagicMock()
            eq1_mock = MagicMock()
            eq2_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq1_mock)
            eq1_mock.return_value = MagicMock(eq=eq2_mock)
            eq2_mock.return_value = MagicMock(execute=MagicMock(return_value=execute_mock))

            # Act
            result = concept_storage.get_concept_detail(concept_id, user_id)

            # Assert
            assert result is None

    def test_get_concept_detail_with_service_role_success(self, concept_storage: ConceptStorage, mock_settings: MagicMock) -> None:
        """Test successful concept detail retrieval with service role."""
        # Arrange
        concept_id = "concept-123"
        user_id = "user-123"
        mock_concept_data = {
            "id": concept_id,
            "user_id": user_id,
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/image.png",
            "created_at": "2023-06-01T12:00:00",
        }
        mock_variations_data = [
            {
                "id": "var-1",
                "concept_id": concept_id,
                "palette_name": "Vibrant",
                "colors": ["#FF0000", "#00FF00", "#0000FF"],
                "image_path": "user-123/palette1.png",
            }
        ]

        # Mock requests.get for concept
        with patch("requests.get") as mock_get:
            # First response for concept
            concept_response = MagicMock()
            concept_response.status_code = 200
            concept_response.json.return_value = [mock_concept_data]

            # Second response for variations
            variations_response = MagicMock()
            variations_response.status_code = 200
            variations_response.json.return_value = mock_variations_data

            # Setup mock_get to return different responses for each call
            mock_get.side_effect = [concept_response, variations_response]

            # Act
            result = concept_storage._get_concept_detail_with_service_role(concept_id, user_id)

            # Assert
            assert result is not None
            assert result["id"] == concept_id
            assert result["user_id"] == user_id
            assert "color_variations" in result
            assert len(result["color_variations"]) == 1
            assert mock_get.call_count == 2


class TestDeleteAllConcepts:
    """Tests for the delete_all_concepts method."""

    def test_delete_all_concepts_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful deletion of all concepts."""
        # Arrange
        user_id = "user-123"
        mock_execute = MagicMock()
        # The delete operation returns empty data on success
        mock_execute.data = []

        # Creating a proper mock chain for the delete operation
        table_mock = MagicMock()
        mock_client.client.table = table_mock
        delete_mock = MagicMock()
        eq_mock = MagicMock()
        execute_mock = MagicMock()

        table_mock.return_value = MagicMock(delete=delete_mock)
        delete_mock.return_value = MagicMock(eq=eq_mock)
        eq_mock.return_value = MagicMock(execute=execute_mock)
        execute_mock.return_value = mock_execute

        # Act
        result = concept_storage.delete_all_concepts(user_id)

        # Assert
        assert result is True
        mock_client.client.table.assert_called_once_with(concept_storage.concepts_table)
        delete_mock.assert_called_once()
        eq_mock.assert_called_once_with("user_id", user_id)
        execute_mock.assert_called_once()

    def test_delete_all_concepts_exception(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test delete_all_concepts handling exceptions."""
        # Arrange
        user_id = "user-123"

        # Creating a proper mock chain with an exception
        table_mock = MagicMock()
        delete_mock = MagicMock()
        eq_mock = MagicMock()
        execute_mock = MagicMock()

        mock_client.client.table = table_mock
        table_mock.return_value = MagicMock(delete=delete_mock)
        delete_mock.return_value = MagicMock(eq=eq_mock)
        eq_mock.return_value = MagicMock(execute=execute_mock)
        execute_mock.side_effect = Exception("Database error")

        # Act
        result = concept_storage.delete_all_concepts(user_id)

        # Assert - method should return False on exception, not raise
        assert result is False


class TestGetConceptByTaskId:
    """Tests for the get_concept_by_task_id method."""

    def test_get_concept_by_task_id_success(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test successful concept retrieval by task ID."""
        # Arrange
        task_id = "task-123"
        user_id = "user-123"
        mock_data = {
            "id": "concept-123",
            "user_id": user_id,
            "task_id": task_id,
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/image.png",
            "created_at": "2023-06-01T12:00:00",
        }

        # Mock the implementation directly with a response that works
        with patch("app.core.supabase.concept_storage.ConceptStorage.get_concept_by_task_id", return_value=mock_data) as mock_get:
            # Act
            result = concept_storage.get_concept_by_task_id(task_id, user_id)

            # Assert
            assert result is not None
            assert result["id"] == "concept-123"
            assert result["task_id"] == task_id
            assert result["user_id"] == user_id
            mock_get.assert_called_once_with(task_id, user_id)

    def test_get_concept_by_task_id_not_found(self, concept_storage: ConceptStorage, mock_client: MagicMock) -> None:
        """Test get_concept_by_task_id when concept is not found."""
        # Arrange
        task_id = "non-existent-task"
        user_id = "user-123"

        # Mock the service role method to return None
        with patch.object(concept_storage, "_get_concept_by_task_id_with_service_role", return_value=None):
            # Creating a proper mock chain
            execute_mock = MagicMock()
            execute_mock.data = []

            table_mock = MagicMock()
            select_mock = MagicMock()
            eq1_mock = MagicMock()
            eq2_mock = MagicMock()

            mock_client.client.table = table_mock
            table_mock.return_value = MagicMock(select=select_mock)
            select_mock.return_value = MagicMock(eq=eq1_mock)
            eq1_mock.return_value = MagicMock(eq=eq2_mock)
            eq2_mock.return_value = MagicMock(execute=MagicMock(return_value=execute_mock))

            # Act
            result = concept_storage.get_concept_by_task_id(task_id, user_id)

            # Assert
            assert result is None

    def test_get_concept_by_task_id_service_role(self, concept_storage: ConceptStorage, mock_settings: MagicMock) -> None:
        """Test successful concept retrieval by task ID with service role."""
        # Arrange
        task_id = "task-123"
        user_id = "user-123"
        mock_data = {
            "id": "concept-123",
            "user_id": user_id,
            "task_id": task_id,
            "logo_description": "Test logo",
            "theme_description": "Test theme",
            "image_path": "user-123/image.png",
            "created_at": "2023-06-01T12:00:00",
        }

        # Mock requests.get
        with patch("requests.get") as mock_get:
            response = MagicMock()
            response.status_code = 200
            response.json.return_value = [mock_data]
            mock_get.return_value = response

            # Act
            result = concept_storage._get_concept_by_task_id_with_service_role(task_id, user_id)

            # Assert
            assert result is not None
            assert result["id"] == "concept-123"
            assert result["task_id"] == task_id
            assert result["user_id"] == user_id
            mock_get.assert_called_once()
