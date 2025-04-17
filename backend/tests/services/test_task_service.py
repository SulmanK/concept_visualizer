"""
Unit tests for the TaskService class.

These tests validate the task management functionality by mocking
Supabase database interactions.
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import datetime
import uuid
from typing import Dict, List, Any, Optional

from app.services.task.service import TaskService, TaskError, TaskNotFoundError
from app.core.supabase.client import SupabaseClient


class MockSupabaseResponse:
    """Mock for Supabase response object."""
    
    def __init__(self, data):
        self.data = data


class MockSupabaseQuery:
    """Mock for Supabase query builder."""
    
    def __init__(self, return_data=None):
        self.return_data = return_data
        self.conditions = []
    
    def insert(self, data):
        """Mock insert method."""
        self.data = data
        return self
    
    def update(self, data):
        """Mock update method."""
        self.data = data
        return self
    
    def select(self, *args):
        """Mock select method."""
        self.select_columns = args
        return self
    
    def eq(self, column, value):
        """Mock equality filter."""
        self.conditions.append((column, value))
        return self
    
    def limit(self, limit_val):
        """Mock limit method."""
        self.limit_value = limit_val
        return self
        
    def order(self, column, option=None):
        """Mock order method."""
        self.order_column = column
        self.order_option = option
        return self
        
    def execute(self):
        """Mock execute method to return data."""
        return MockSupabaseResponse(self.return_data)


@pytest.fixture
def mock_supabase_client():
    """Create a mock Supabase client."""
    client = MagicMock()
    
    # Mock the table method to return a query builder
    service_role_client = MagicMock()
    service_role_client.table = MagicMock(return_value=MockSupabaseQuery())
    
    client.get_service_role_client = MagicMock(return_value=service_role_client)
    client.client = MagicMock()
    client.client.table = MagicMock(return_value=MockSupabaseQuery())
    
    return client


@pytest.fixture
def task_service(mock_supabase_client):
    """Create a TaskService with a mock Supabase client."""
    return TaskService(client=mock_supabase_client)


class TestTaskService:
    """Test suite for TaskService."""
    
    @pytest.mark.asyncio
    async def test_create_task_success(self, task_service, mock_supabase_client):
        """Test creating a task successfully."""
        # Arrange
        user_id = "user-123"
        task_type = "concept_generation"
        metadata = {"key": "value"}
        
        task_id = str(uuid.uuid4())
        created_task = {
            "id": task_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "type": task_type,
            "status": "pending",
            "metadata": metadata
        }
        
        # Configure the mock to return the created task
        service_role_client = mock_supabase_client.get_service_role_client()
        table_query = MockSupabaseQuery(return_data=[created_task])
        service_role_client.table.return_value = table_query
        
        # Act
        result = await task_service.create_task(
            user_id=user_id,
            task_type=task_type,
            metadata=metadata
        )
        
        # Assert
        assert result == created_task
        service_role_client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_create_task_fallback_to_regular_client(self, task_service, mock_supabase_client):
        """Test fallback to regular client when service role client fails."""
        # Arrange
        user_id = "user-123"
        task_type = "concept_generation"
        metadata = {"key": "value"}
        
        task_id = str(uuid.uuid4())
        created_task = {
            "id": task_id,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "type": task_type,
            "status": "pending",
            "metadata": metadata
        }
        
        # Configure service role client to raise an exception
        service_role_client = mock_supabase_client.get_service_role_client()
        service_role_client.table.side_effect = Exception("Service role client error")
        
        # Configure regular client to return the created task
        table_query = MockSupabaseQuery(return_data=[created_task])
        mock_supabase_client.client.table.return_value = table_query
        
        # Act
        result = await task_service.create_task(
            user_id=user_id,
            task_type=task_type,
            metadata=metadata
        )
        
        # Assert
        assert result == created_task
        service_role_client.table.assert_called_once_with("tasks")
        mock_supabase_client.client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_create_task_error(self, task_service, mock_supabase_client):
        """Test error handling when task creation fails."""
        # Arrange
        user_id = "user-123"
        task_type = "concept_generation"
        
        # Configure both clients to return empty data
        service_role_client = mock_supabase_client.get_service_role_client()
        service_role_client.table.return_value = MockSupabaseQuery(return_data=[])
        
        # Act & Assert
        with pytest.raises(TaskError, match="Failed to create task of type"):
            await task_service.create_task(
                user_id=user_id,
                task_type=task_type
            )
    
    @pytest.mark.asyncio
    async def test_update_task_status_success(self, task_service, mock_supabase_client):
        """Test updating task status successfully."""
        # Arrange
        task_id = str(uuid.uuid4())
        status = "completed"
        result_id = "result-123"
        
        updated_task = {
            "id": task_id,
            "status": status,
            "result_id": result_id,
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Configure the mock to return the updated task
        service_role_client = mock_supabase_client.get_service_role_client()
        table_query = MockSupabaseQuery(return_data=[updated_task])
        service_role_client.table.return_value = table_query
        
        # Act
        result = await task_service.update_task_status(
            task_id=task_id,
            status=status,
            result_id=result_id
        )
        
        # Assert
        assert result == updated_task
        service_role_client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_update_task_status_not_found(self, task_service, mock_supabase_client):
        """Test error when updating a non-existent task."""
        # Arrange
        task_id = str(uuid.uuid4())
        status = "completed"
        
        # Configure the mock to return empty data (task not found)
        service_role_client = mock_supabase_client.get_service_role_client()
        table_query = MockSupabaseQuery(return_data=[])
        service_role_client.table.return_value = table_query
        
        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await task_service.update_task_status(
                task_id=task_id,
                status=status
            )
    
    @pytest.mark.asyncio
    async def test_get_task_success(self, task_service, mock_supabase_client):
        """Test retrieving a task successfully."""
        # Arrange
        task_id = str(uuid.uuid4())
        user_id = "user-123"
        
        task_data = {
            "id": task_id,
            "user_id": user_id,
            "type": "concept_generation",
            "status": "completed",
            "result_id": "result-123",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        # Configure client to return the task
        client = mock_supabase_client.client
        table_query = MockSupabaseQuery(return_data=[task_data])
        client.table.return_value = table_query
        
        # Act
        result = await task_service.get_task(task_id=task_id, user_id=user_id)
        
        # Assert
        assert result == task_data
        client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_get_task_not_found(self, task_service, mock_supabase_client):
        """Test error when retrieving a non-existent task."""
        # Arrange
        task_id = str(uuid.uuid4())
        user_id = "user-123"
        
        # Configure client to return empty data
        client = mock_supabase_client.client
        table_query = MockSupabaseQuery(return_data=[])
        client.table.return_value = table_query
        
        # Act & Assert
        with pytest.raises(TaskNotFoundError):
            await task_service.get_task(task_id=task_id, user_id=user_id)
    
    @pytest.mark.asyncio
    async def test_get_tasks_by_user(self, task_service, mock_supabase_client):
        """Test retrieving multiple tasks for a user."""
        # Arrange
        user_id = "user-123"
        tasks = [
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "concept_generation",
                "status": "completed",
                "created_at": datetime.utcnow().isoformat()
            },
            {
                "id": str(uuid.uuid4()),
                "user_id": user_id,
                "type": "concept_refinement",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
        ]
        
        # Configure client to return the tasks
        client = mock_supabase_client.client
        table_query = MockSupabaseQuery(return_data=tasks)
        client.table.return_value = table_query
        
        # Act
        result = await task_service.get_tasks_by_user(user_id=user_id)
        
        # Assert
        assert result == tasks
        client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_delete_task_success(self, task_service, mock_supabase_client):
        """Test deleting a task successfully."""
        # Arrange
        task_id = str(uuid.uuid4())
        user_id = "user-123"
        
        deleted_task = {
            "id": task_id,
            "user_id": user_id,
            "status": "deleted"
        }
        
        # Configure client to return the deleted task
        service_role_client = mock_supabase_client.get_service_role_client()
        table_query = MockSupabaseQuery(return_data=[deleted_task])
        service_role_client.table.return_value = table_query
        
        # Act
        result = await task_service.delete_task(task_id=task_id, user_id=user_id)
        
        # Assert
        assert result is True
        service_role_client.table.assert_called_once_with("tasks")
    
    @pytest.mark.asyncio
    async def test_delete_task_not_found(self, task_service, mock_supabase_client):
        """Test when trying to delete a non-existent task."""
        # Arrange
        task_id = str(uuid.uuid4())
        user_id = "user-123"
        
        # Configure client to return empty data
        service_role_client = mock_supabase_client.get_service_role_client()
        table_query = MockSupabaseQuery(return_data=[])
        service_role_client.table.return_value = table_query
        
        # Act
        result = await task_service.delete_task(task_id=task_id, user_id=user_id)
        
        # Assert
        assert result is False
        service_role_client.table.assert_called_once_with("tasks") 