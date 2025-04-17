"""
Tests for the task API endpoints.

These tests validate the task routes for retrieving task status and updates.
"""

from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
import uuid

from app.main import app
from app.services.task.service import TaskService, TaskNotFoundError


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_task_service():
    """Create a mock TaskService for testing."""
    mock_service = AsyncMock(spec=TaskService)
    
    # Configure default responses
    task_id = str(uuid.uuid4())
    mock_service.get_task.return_value = {
        "id": task_id,
        "status": "completed",
        "created_at": "2023-01-01T00:00:00",
        "updated_at": "2023-01-01T00:01:00",
        "user_id": "user-123",
        "type": "concept_generation",
        "result_id": "result-123"
    }
    
    mock_service.get_tasks_by_user.return_value = [
        {
            "id": str(uuid.uuid4()),
            "status": "completed",
            "created_at": "2023-01-01T00:00:00",
            "user_id": "user-123",
            "type": "concept_generation"
        },
        {
            "id": str(uuid.uuid4()),
            "status": "pending",
            "created_at": "2023-01-02T00:00:00",
            "user_id": "user-123",
            "type": "concept_refinement"
        }
    ]
    
    return mock_service


def test_get_task(client, mock_task_service):
    """Test retrieving a specific task by ID."""
    task_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Mock the get_task_service function to return our mock
    with patch("app.api.routes.task.get_task_service", return_value=mock_task_service):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get(f"/api/tasks/{task_id}", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == mock_task_service.get_task.return_value["id"]
        assert data["status"] == "completed"
        
        # Verify the mock was called correctly
        mock_task_service.get_task.assert_called_once_with(task_id=task_id, user_id=user_id)


def test_get_task_not_found(client, mock_task_service):
    """Test error handling when task is not found."""
    task_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Configure mock to raise NotFoundError
    mock_task_service.get_task.side_effect = TaskNotFoundError(task_id)
    
    # Mock the get_task_service function
    with patch("app.api.routes.task.get_task_service", return_value=mock_task_service):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get(f"/api/tasks/{task_id}", headers=headers)
        
        # Verify the response
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


def test_get_user_tasks(client, mock_task_service):
    """Test retrieving all tasks for a user."""
    user_id = "user-123"
    
    # Mock the get_task_service function
    with patch("app.api.routes.task.get_task_service", return_value=mock_task_service):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.get("/api/tasks", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["status"] == "completed"
        assert data[1]["status"] == "pending"
        
        # Verify the mock was called correctly
        mock_task_service.get_tasks_by_user.assert_called_once_with(
            user_id=user_id,
            status=None,
            limit=10
        )


def test_get_user_tasks_with_status_filter(client, mock_task_service):
    """Test retrieving user tasks with status filtering."""
    user_id = "user-123"
    
    # Mock the get_task_service function
    with patch("app.api.routes.task.get_task_service", return_value=mock_task_service):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request with status filter
        response = client.get("/api/tasks?status=completed", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        
        # Verify the mock was called with the correct filter
        mock_task_service.get_tasks_by_user.assert_called_once_with(
            user_id=user_id,
            status="completed",
            limit=10
        )


def test_delete_task(client, mock_task_service):
    """Test deleting a task."""
    task_id = str(uuid.uuid4())
    user_id = "user-123"
    
    # Configure mock to return success
    mock_task_service.delete_task.return_value = True
    
    # Mock the get_task_service function
    with patch("app.api.routes.task.get_task_service", return_value=mock_task_service):
        # Add auth headers
        headers = {"Authorization": f"Bearer {user_id}"}
        
        # Make the request
        response = client.delete(f"/api/tasks/{task_id}", headers=headers)
        
        # Verify the response
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        
        # Verify the mock was called correctly
        mock_task_service.delete_task.assert_called_once_with(
            task_id=task_id, 
            user_id=user_id
        )


def test_unauthorized_access(client):
    """Test that endpoints require authentication."""
    task_id = str(uuid.uuid4())
    
    # Try to access without auth headers
    response = client.get(f"/api/tasks/{task_id}")
    
    # Should return 401 Unauthorized or 403 Forbidden
    assert response.status_code in (401, 403) 