"""Tests for the TaskService implementation."""

import uuid
from unittest.mock import MagicMock

import pytest

from app.services.task.service import TaskError, TaskNotFoundError, TaskService


@pytest.fixture
def mock_supabase_client() -> MagicMock:
    """Create a mock Supabase client for testing."""
    client = MagicMock()
    client.get_service_role_client.return_value = MagicMock()
    return client


@pytest.fixture
def task_service(mock_supabase_client: MagicMock) -> TaskService:
    """Create a TaskService with a mock client for testing."""
    return TaskService(mock_supabase_client)


@pytest.mark.asyncio
async def test_create_task_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task creation success path."""
    # Arrange
    user_id = str(uuid.uuid4())
    task_type = "concept_generation"
    metadata = {"prompt": "test prompt"}
    task_id = str(uuid.uuid4())

    # Create task object to be returned
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "type": task_type,
        "status": "pending",
        "metadata": metadata,
    }

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the service role client behavior
    service_client = mock_supabase_client.get_service_role_client.return_value
    insert_chain = service_client.table.return_value.insert.return_value

    # Instead of setting execute to an AsyncMock, create a regular function that returns a mock_response
    insert_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.create_task(user_id, task_type, metadata)

    # Assert
    assert insert_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_create_task_fallback_to_regular_client(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task creation when service role client fails."""
    # Arrange
    user_id = str(uuid.uuid4())
    task_type = "concept_generation"
    metadata = {"prompt": "test prompt"}
    task_id = str(uuid.uuid4())

    # Create a mock task object
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "type": task_type,
        "metadata": metadata,
        "status": "pending",
    }

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure service role client to raise an exception
    mock_supabase_client.get_service_role_client.side_effect = Exception("Service role error")

    # Configure the regular client behavior
    insert_chain = mock_supabase_client.client.table.return_value.insert.return_value

    # Set up the execute mock to return the mock response
    insert_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.create_task(user_id, task_type, metadata)

    # Assert
    assert insert_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    mock_supabase_client.client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_create_task_error_empty_result(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task creation when database returns empty result."""
    # Arrange
    user_id = str(uuid.uuid4())
    task_type = "concept_generation"
    metadata = {"prompt": "test prompt"}

    # Create a mock response with empty data
    mock_response = MagicMock()
    mock_response.data = []

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    insert_chain = service_client.table.return_value.insert.return_value

    # Set up the execute mock
    insert_chain.execute = MagicMock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(TaskError) as excinfo:
        await task_service.create_task(user_id, task_type, metadata)

    assert "Failed to create task" in str(excinfo.value)


@pytest.mark.asyncio
async def test_create_task_database_error(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task creation when database operation fails."""
    # Arrange
    user_id = str(uuid.uuid4())
    task_type = "concept_generation"
    metadata = {"prompt": "test prompt"}

    # Configure the service role client to raise exception on execute
    service_client = mock_supabase_client.get_service_role_client.return_value
    insert_chain = service_client.table.return_value.insert.return_value

    # Set up the execute mock to raise an exception
    insert_chain.execute = MagicMock(side_effect=Exception("Database error"))

    # Act & Assert
    with pytest.raises(TaskError) as excinfo:
        await task_service.create_task(user_id, task_type, metadata)

    assert "Failed to create task" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_task_status_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test successful task status update."""
    # Arrange
    task_id = str(uuid.uuid4())
    status = "completed"
    result_id = str(uuid.uuid4())

    # Create task data to be returned
    task_data = {"id": task_id, "status": status, "result_id": result_id}

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    update_chain = service_client.table.return_value.update.return_value
    eq_chain = update_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.update_task_status(task_id, status, result_id)

    # Assert
    assert eq_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_update_task_status_with_error_message(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task status update with error message."""
    # Arrange
    task_id = str(uuid.uuid4())
    status = "failed"
    error_message = "Test error message"

    # Create task data to be returned
    task_data = {"id": task_id, "status": status, "error_message": error_message}

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    update_chain = service_client.table.return_value.update.return_value
    eq_chain = update_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.update_task_status(task_id, status, error_message=error_message)

    # Assert
    assert eq_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_update_task_status_not_found(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task status update when task is not found."""
    # Arrange
    task_id = str(uuid.uuid4())
    status = "completed"

    # Create a response object with empty data
    mock_response = MagicMock()
    mock_response.data = []  # Empty result means task not found

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    update_chain = service_client.table.return_value.update.return_value
    eq_chain = update_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq_chain.execute = MagicMock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(TaskNotFoundError) as excinfo:
        await task_service.update_task_status(task_id, status)

    assert f"Task not found: {task_id}" in str(excinfo.value)
    assert eq_chain.execute.called


@pytest.mark.asyncio
async def test_update_task_status_fallback_to_regular_client(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task status update fallback to regular client when service role fails."""
    # Arrange
    task_id = str(uuid.uuid4())
    status = "completed"

    # Configure service role client to raise an exception
    mock_supabase_client.get_service_role_client.side_effect = Exception("Service role error")

    # Create a response object for the update operation
    task_data = {"id": task_id, "status": status}
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the regular client
    update_chain = mock_supabase_client.client.table.return_value.update.return_value
    eq_chain = update_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.update_task_status(task_id, status)

    # Assert
    assert eq_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    mock_supabase_client.client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_task_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test successful task retrieval."""
    # Arrange
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Create task data to be returned
    task_data = {"id": task_id, "user_id": user_id, "status": "completed"}

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    eq2_chain = eq_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq2_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_task(task_id, user_id)

    # Assert
    assert eq2_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_task_not_found(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task retrieval when task is not found."""
    # Arrange
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Create a response object with empty data
    mock_response = MagicMock()
    mock_response.data = []  # Empty result means task not found

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    eq2_chain = eq_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq2_chain.execute = MagicMock(return_value=mock_response)

    # Act & Assert
    with pytest.raises(TaskNotFoundError) as excinfo:
        await task_service.get_task(task_id, user_id)

    assert f"Task not found: {task_id}" in str(excinfo.value)
    assert eq2_chain.execute.called


@pytest.mark.asyncio
async def test_get_tasks_by_user_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test successful retrieval of tasks by user."""
    # Arrange
    user_id = str(uuid.uuid4())
    tasks = [
        {"id": str(uuid.uuid4()), "user_id": user_id},
        {"id": str(uuid.uuid4()), "user_id": user_id},
    ]

    # Create a mock response with the tasks
    mock_response = MagicMock()
    mock_response.data = tasks

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    order_chain = eq_chain.order.return_value
    limit_chain = order_chain.limit.return_value

    # Set up the execute mock to return the mock response
    limit_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_tasks_by_user(user_id)

    # Assert
    assert limit_chain.execute.called
    assert result == tasks
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_tasks_by_user_with_status_filter(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test retrieval of tasks by user with status filter."""
    # Arrange
    user_id = str(uuid.uuid4())
    status = "completed"
    tasks = [
        {"id": str(uuid.uuid4()), "user_id": user_id, "status": status},
        {"id": str(uuid.uuid4()), "user_id": user_id, "status": status},
    ]

    # Create a mock response with the filtered tasks
    mock_response = MagicMock()
    mock_response.data = tasks

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    order_chain = eq_chain.order.return_value
    limit_chain = order_chain.limit.return_value
    status_eq_chain = limit_chain.eq.return_value

    # Set up the execute mock to return the mock response
    status_eq_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_tasks_by_user(user_id, status=status)

    # Assert
    assert status_eq_chain.execute.called
    assert result == tasks
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_tasks_by_user_with_custom_limit(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test retrieval of tasks by user with custom limit."""
    # Arrange
    user_id = str(uuid.uuid4())
    limit = 5
    tasks = [{"id": str(uuid.uuid4()), "user_id": user_id} for _ in range(limit)]

    # Create a mock response with the tasks
    mock_response = MagicMock()
    mock_response.data = tasks

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    order_chain = eq_chain.order.return_value
    limit_chain = order_chain.limit.return_value

    # Set up the execute mock to return the mock response
    limit_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_tasks_by_user(user_id, limit=limit)

    # Assert
    assert limit_chain.execute.called
    assert result == tasks
    assert len(result) == limit
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_delete_task_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test successful task deletion."""
    # Arrange
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Create a response object for the delete operation
    mock_response = MagicMock()
    mock_response.data = [{"id": task_id}]  # Task that was deleted

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value

    # Set up the execution chain correctly based on the implementation
    # The actual call is:  service_client.table(self.tasks_table).delete().eq("id", task_id).eq("user_id", user_id).execute()
    execute_mock = MagicMock(return_value=mock_response)
    eq2_mock = MagicMock()
    eq2_mock.execute = execute_mock

    eq1_mock = MagicMock()
    eq1_mock.eq.return_value = eq2_mock

    delete_mock = MagicMock()
    delete_mock.eq.return_value = eq1_mock

    table_mock = MagicMock()
    table_mock.delete.return_value = delete_mock

    service_client.table.return_value = table_mock

    # Act
    result = await task_service.delete_task(task_id, user_id)

    # Assert
    assert result is True
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)
    table_mock.delete.assert_called_once()
    delete_mock.eq.assert_called_once_with("id", task_id)
    eq1_mock.eq.assert_called_once_with("user_id", user_id)
    eq2_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_not_found(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task deletion when task is not found."""
    # Arrange
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value

    # Set up the execution chain correctly based on the implementation
    # The actual call is:  service_client.table(self.tasks_table).delete().eq("id", task_id).eq("user_id", user_id).execute()
    mock_response = MagicMock()
    mock_response.data = []  # Empty result means task not found

    execute_mock = MagicMock(return_value=mock_response)
    eq2_mock = MagicMock()
    eq2_mock.execute = execute_mock

    eq1_mock = MagicMock()
    eq1_mock.eq.return_value = eq2_mock

    delete_mock = MagicMock()
    delete_mock.eq.return_value = eq1_mock

    table_mock = MagicMock()
    table_mock.delete.return_value = delete_mock

    service_client.table.return_value = table_mock

    # Act & Assert
    with pytest.raises(TaskNotFoundError) as excinfo:
        await task_service.delete_task(task_id, user_id)

    assert f"Task not found: {task_id}" in str(excinfo.value)
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)
    table_mock.delete.assert_called_once()
    delete_mock.eq.assert_called_once_with("id", task_id)
    eq1_mock.eq.assert_called_once_with("user_id", user_id)
    eq2_mock.execute.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_delete_fails(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task deletion when database operation fails."""
    # Arrange
    task_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    service_client.table.side_effect = Exception("Service client error")

    # Configure the regular client to fail too
    mock_supabase_client.client.table.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(TaskError) as excinfo:
        await task_service.delete_task(task_id, user_id)

    assert "Failed to delete task" in str(excinfo.value)
    # Verify both clients were attempted
    service_client.table.assert_called_once_with(task_service.tasks_table)
    mock_supabase_client.client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_task_by_result_id_success(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test successful task retrieval by result ID."""
    # Arrange
    result_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())
    task_id = str(uuid.uuid4())

    # Create task data to be returned
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "result_id": result_id,
        "status": "completed",
    }

    # Create a mock response with the task data
    mock_response = MagicMock()
    mock_response.data = [task_data]

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    eq2_chain = eq_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq2_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_task_by_result_id(result_id, user_id)

    # Assert
    assert eq2_chain.execute.called
    assert result == task_data
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)


@pytest.mark.asyncio
async def test_get_task_by_result_id_not_found(task_service: TaskService, mock_supabase_client: MagicMock) -> None:
    """Test task retrieval by result ID when task is not found."""
    # Arrange
    result_id = str(uuid.uuid4())
    user_id = str(uuid.uuid4())

    # Create a response object with empty data
    mock_response = MagicMock()
    mock_response.data = []  # Empty result means task not found

    # Configure the service role client
    service_client = mock_supabase_client.get_service_role_client.return_value
    select_chain = service_client.table.return_value.select.return_value
    eq_chain = select_chain.eq.return_value
    eq2_chain = eq_chain.eq.return_value

    # Set up the execute mock to return the mock response
    eq2_chain.execute = MagicMock(return_value=mock_response)

    # Act
    result = await task_service.get_task_by_result_id(result_id, user_id)

    # Assert
    assert eq2_chain.execute.called
    assert result is None
    mock_supabase_client.get_service_role_client.assert_called_once()
    service_client.table.assert_called_once_with(task_service.tasks_table)
