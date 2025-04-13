"""
Tests for the ConceptPersistenceService.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

from app.services.persistence.concept_persistence_service import ConceptPersistenceService
from app.services.interfaces.concept_persistence_service import ConceptPersistenceServiceInterface


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    client = MagicMock()
    
    # Mock the table method to return a chain of methods
    table_mock = MagicMock()
    client.table.return_value = table_mock
    
    # Mock the storage functionality
    storage_mock = MagicMock()
    client.storage.from_.return_value = storage_mock
    
    return client


@pytest.fixture
def persistence_service(mock_supabase_client):
    """Create a ConceptPersistenceService instance with a mock client."""
    return ConceptPersistenceService(mock_supabase_client)


@pytest.mark.asyncio
async def test_store_concept(persistence_service, mock_supabase_client):
    """Test storing a concept in the database."""
    # Setup mock response
    mock_table = mock_supabase_client.table.return_value
    execute_mock = MagicMock()
    execute_mock.execute.return_value.data = [{"id": "test-id"}]
    mock_table.insert.return_value = execute_mock
    
    # Call the method
    concept_data = {
        "logo_description": "Test logo",
        "theme_description": "Test theme",
        "palette": [{"hex": "#FF0000", "name": "Red"}],
        "session_id": "test-session-id"
    }
    result = await persistence_service.store_concept(concept_data)
    
    # Verify
    assert result["id"] == "test-id"
    mock_table.insert.assert_called_once()
    execute_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_concept_detail(persistence_service, mock_supabase_client):
    """Test retrieving concept details."""
    # Setup mock response
    mock_table = mock_supabase_client.table.return_value
    execute_mock = MagicMock()
    execute_mock.execute.return_value.data = [{
        "id": "test-id",
        "logo_description": "Test logo",
        "theme_description": "Test theme",
        "palette": [{"hex": "#FF0000", "name": "Red"}],
        "created_at": "2023-01-01T00:00:00"
    }]
    
    # Chain of method calls
    mock_table.select.return_value.eq.return_value = execute_mock
    
    # Call the method
    result = await persistence_service.get_concept_detail("test-id")
    
    # Verify
    assert result["id"] == "test-id"
    assert result["logo_description"] == "Test logo"
    assert result["theme_description"] == "Test theme"
    mock_table.select.assert_called_once()
    execute_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_recent_concepts(persistence_service, mock_supabase_client):
    """Test retrieving recent concepts."""
    # Setup mock response
    mock_table = mock_supabase_client.table.return_value
    execute_mock = MagicMock()
    execute_mock.execute.return_value.data = [
        {
            "id": "test-id-1",
            "logo_description": "Test logo 1",
            "created_at": "2023-01-01T00:00:00"
        },
        {
            "id": "test-id-2",
            "logo_description": "Test logo 2",
            "created_at": "2023-01-02T00:00:00"
        }
    ]
    
    # Chain of method calls for session concepts
    mock_table.select.return_value.eq.return_value.order.return_value.limit.return_value = execute_mock
    
    # Call the method
    result = await persistence_service.get_recent_concepts(session_id="test-session-id", limit=5)
    
    # Verify
    assert len(result) == 2
    assert result[0]["id"] == "test-id-1"
    assert result[1]["id"] == "test-id-2"
    mock_table.select.assert_called_once()
 