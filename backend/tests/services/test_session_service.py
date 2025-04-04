"""
Tests for the SessionManager.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from fastapi import Response, Cookie
import json

from app.services.session.manager import SessionManager
from app.services.interfaces import SessionServiceInterface


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client for testing."""
    client = MagicMock()
    
    # Mock the table method to return a chain of methods
    table_mock = MagicMock()
    client.table.return_value = table_mock
    
    return client


@pytest.fixture
def mock_response():
    """Create a mock FastAPI response for testing."""
    return MagicMock(spec=Response)


@pytest.fixture
def session_manager(mock_supabase_client):
    """Create a SessionManager instance with a mock client."""
    return SessionManager(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_session(session_manager, mock_supabase_client):
    """Test creating a new session."""
    # Setup mock response
    mock_table = mock_supabase_client.table.return_value
    execute_mock = MagicMock()
    session_id = "test-session-id"
    execute_mock.execute.return_value.data = [{"id": session_id, "created_at": "2023-01-01T00:00:00"}]
    mock_table.insert.return_value = execute_mock
    
    # Call the method
    result = await session_manager.create_session()
    
    # Verify
    assert result["id"] == session_id
    mock_table.insert.assert_called_once()
    execute_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_session(session_manager, mock_supabase_client):
    """Test retrieving a session."""
    # Setup mock response
    mock_table = mock_supabase_client.table.return_value
    execute_mock = MagicMock()
    session_id = "test-session-id"
    execute_mock.execute.return_value.data = [{
        "id": session_id,
        "client_id": "test-client-id",
        "created_at": "2023-01-01T00:00:00",
        "last_active_at": "2023-01-01T01:00:00",
        "data": json.dumps({"test": "data"})
    }]
    
    # Chain of method calls
    mock_table.select.return_value.eq.return_value = execute_mock
    
    # For the update call
    update_execute_mock = MagicMock()
    update_execute_mock.execute.return_value.data = [{
        "id": session_id,
        "last_active_at": "2023-01-01T02:00:00"
    }]
    mock_table.update.return_value.eq.return_value = update_execute_mock
    
    # Call the method
    result = await session_manager.get_session(session_id)
    
    # Verify
    assert result["id"] == session_id
    assert result["data"] == {"test": "data"}
    mock_table.select.assert_called_once()
    execute_mock.execute.assert_called_once()
    mock_table.update.assert_called_once()


@pytest.mark.asyncio
async def test_get_or_create_session_existing(session_manager):
    """Test getting or creating a session when the session already exists."""
    # Mock the get_session method
    session_manager.get_session = AsyncMock()
    session_manager.get_session.return_value = {
        "id": "existing-session-id",
        "data": {"existing": "data"}
    }
    
    # Call the method
    result = await session_manager.get_or_create_session("existing-session-id")
    
    # Verify
    assert result["id"] == "existing-session-id"
    assert result["data"] == {"existing": "data"}
    session_manager.get_session.assert_called_once_with("existing-session-id")


@pytest.mark.asyncio
async def test_get_or_create_session_new(session_manager):
    """Test getting or creating a session when the session doesn't exist."""
    # Mock the get_session method to raise an exception
    session_manager.get_session = AsyncMock()
    session_manager.get_session.side_effect = Exception("Session not found")
    
    # Mock the create_session method
    session_manager.create_session = AsyncMock()
    session_manager.create_session.return_value = {
        "id": "new-session-id",
        "data": {}
    }
    
    # Call the method
    result = await session_manager.get_or_create_session(None)
    
    # Verify
    assert result["id"] == "new-session-id"
    session_manager.create_session.assert_called_once()


@pytest.mark.asyncio
async def test_set_session_cookie(session_manager, mock_response):
    """Test setting a session cookie in the response."""
    session_id = "test-session-id"
    
    # Call the method
    session_manager.set_session_cookie(mock_response, session_id)
    
    # Verify
    mock_response.set_cookie.assert_called_once()
    # Check that the cookie is set with the correct name and value
    call_args = mock_response.set_cookie.call_args[1]
    assert call_args["key"] == "concept_session"
    assert call_args["value"] == session_id 