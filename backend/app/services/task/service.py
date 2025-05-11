"""Task service implementation.

This module provides services for managing background tasks.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, cast

from app.core.config import settings
from app.core.constants import TASK_STATUS_PENDING, TASK_STATUS_PROCESSING  # Import the constants
from app.core.supabase.client import SupabaseClient
from app.services.task.interface import TaskServiceInterface
from app.utils.security.mask import mask_id

# Custom exceptions


class TaskError(Exception):
    """Base exception for task-related errors."""

    def __init__(self, message: str):
        """Initialize with error message.

        Args:
            message: The error message
        """
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    """Exception raised when a task cannot be found."""

    def __init__(self, task_id: str):
        """Initialize with task ID.

        Args:
            task_id: ID of the task that was not found
        """
        self.task_id = task_id
        message = f"Task not found: {task_id}"
        super().__init__(message)


class TaskService(TaskServiceInterface):
    """Service for managing background tasks."""

    def __init__(self, client: SupabaseClient):
        """Initialize task service with Supabase client.

        Args:
            client: Supabase client for interacting with the database
        """
        self.client = client
        self.logger = logging.getLogger("task_service")
        self.tasks_table = settings.DB_TABLE_TASKS

    async def create_task(self, user_id: str, task_type: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Create a new task record.

        Args:
            user_id: ID of the user who owns the task
            task_type: Type of task (e.g. 'concept_generation', 'concept_refinement')
            metadata: Optional metadata associated with the task

        Returns:
            Task data including the generated task ID

        Raises:
            TaskError: If creation fails
        """
        try:
            # Set initial task values
            task_id = str(uuid.uuid4())
            now = datetime.utcnow().isoformat()

            # Mask user ID for logging
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Creating task of type '{task_type}' for user {masked_user_id}")

            # Prepare task data
            task_data = {
                "id": task_id,
                "created_at": now,
                "updated_at": now,
                "user_id": user_id,
                "type": task_type,
                "status": "pending",
                "metadata": metadata or {},
            }

            # Insert using service role client to bypass RLS policies
            try:
                service_client = self.client.get_service_role_client()
                result = service_client.table(self.tasks_table).insert(task_data).execute()
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                # Fallback to regular client if service role client not available
                result = self.client.client.table(self.tasks_table).insert(task_data).execute()

            # Check if insertion was successful
            if not result.data or len(result.data) == 0:
                raise TaskError(f"Failed to create task of type '{task_type}'")

            task = cast(Dict[str, Any], result.data[0])
            masked_task_id = mask_id(task["id"])
            self.logger.info(f"Successfully created task {masked_task_id} of type '{task_type}'")

            return task

        except Exception as e:
            self.logger.error(f"Error creating task: {str(e)}")
            raise TaskError(f"Failed to create task: {str(e)}")

    async def update_task_status(
        self,
        task_id: str,
        status: str,
        result_id: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Update the status of a task.

        Args:
            task_id: ID of the task to update
            status: New status ('processing', 'completed', 'failed')
            result_id: Optional ID of the result entity (e.g. concept_id)
            error_message: Optional error message if status is 'failed'

        Returns:
            Updated task data

        Raises:
            TaskNotFoundError: If task not found
            TaskError: If update fails
        """
        try:
            # Mask task ID for logging
            masked_task_id = mask_id(task_id)
            self.logger.debug(f"Updating task {masked_task_id} status to '{status}'")

            # Prepare update data
            now = datetime.utcnow().isoformat()
            update_data = {
                "updated_at": now,
                "status": status,
            }

            # Add result_id if provided
            if result_id:
                update_data["result_id"] = result_id

            # Add error_message if provided, sanitize to remove problematic characters
            if error_message:
                # Sanitize error message to remove any non-printable characters
                sanitized_error = "".join(c if c.isprintable() else " " for c in error_message)
                update_data["error_message"] = sanitized_error

            # Update using service role client to bypass RLS policies
            try:
                service_client = self.client.get_service_role_client()
                result = service_client.table(self.tasks_table).update(update_data).eq("id", task_id).execute()
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                # Fallback to regular client if service role client not available
                result = self.client.client.table(self.tasks_table).update(update_data).eq("id", task_id).execute()

            # Check if update was successful
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)

            task = cast(Dict[str, Any], result.data[0])
            self.logger.info(f"Successfully updated task {masked_task_id} status to '{status}'")

            return task

        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error updating task {masked_task_id}: {str(e)}")
            raise TaskError(f"Failed to update task: {str(e)}")

    async def get_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """Get a task by ID.

        Args:
            task_id: ID of the task to retrieve
            user_id: ID of the user who owns the task

        Returns:
            Task data

        Raises:
            TaskNotFoundError: If task not found
            TaskError: If retrieval fails
        """
        try:
            # Mask IDs for logging
            masked_task_id = mask_id(task_id)
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Getting task {masked_task_id} for user {masked_user_id}")

            # Query database - use service role client to bypass RLS if available
            try:
                service_client = self.client.get_service_role_client()
                result = service_client.table(self.tasks_table).select("*").eq("id", task_id).eq("user_id", user_id).execute()
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                result = self.client.client.table(self.tasks_table).select("*").eq("id", task_id).eq("user_id", user_id).execute()

            # Check if task exists
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)

            task = cast(Dict[str, Any], result.data[0])
            self.logger.debug(f"Successfully retrieved task {masked_task_id}")

            return task

        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error getting task {masked_task_id}: {str(e)}")
            raise TaskError(f"Failed to retrieve task: {str(e)}")

    async def get_tasks_by_user(self, user_id: str, status: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get tasks for a user.

        Args:
            user_id: ID of the user who owns the tasks
            status: Optional status to filter by
            limit: Maximum number of tasks to return

        Returns:
            List of task data

        Raises:
            TaskError: If retrieval fails
        """
        try:
            # Mask user ID for logging
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Getting tasks for user {masked_user_id} with status '{status or 'any'}'")

            # Get service role client if available for RLS bypass
            try:
                service_client = self.client.get_service_role_client()
                query = service_client.table(self.tasks_table).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit)
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                query = self.client.client.table(self.tasks_table).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(limit)

            # Filter by status if provided
            if status:
                query = query.eq("status", status)

            # Execute query
            result = query.execute()

            tasks = cast(List[Dict[str, Any]], result.data)
            task_count = len(tasks)
            self.logger.debug(f"Retrieved {task_count} tasks for user {masked_user_id}")

            return tasks

        except Exception as e:
            self.logger.error(f"Error getting tasks for user {masked_user_id}: {str(e)}")
            raise TaskError(f"Failed to retrieve tasks: {str(e)}")

    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """Delete a task.

        Args:
            task_id: ID of the task to delete
            user_id: ID of the user who owns the task

        Returns:
            True if successfully deleted

        Raises:
            TaskNotFoundError: If task not found
            TaskError: If deletion fails
        """
        try:
            # Mask IDs for logging
            masked_task_id = mask_id(task_id)
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Deleting task {masked_task_id} for user {masked_user_id}")

            # Delete using service role client to bypass RLS if available
            try:
                service_client = self.client.get_service_role_client()
                result = service_client.table(self.tasks_table).delete().eq("id", task_id).eq("user_id", user_id).execute()
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                result = self.client.client.table(self.tasks_table).delete().eq("id", task_id).eq("user_id", user_id).execute()

            # Check if deletion was successful
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)

            self.logger.info(f"Successfully deleted task {masked_task_id}")
            return True

        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error deleting task {masked_task_id}: {str(e)}")
            raise TaskError(f"Failed to delete task: {str(e)}")

    async def get_task_by_result_id(self, result_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a task by result ID.

        Args:
            result_id: ID of the result entity (e.g. concept_id)
            user_id: ID of the user who owns the task

        Returns:
            Task data or None if not found

        Raises:
            TaskError: If retrieval fails
        """
        try:
            # Mask IDs for logging
            masked_result_id = mask_id(result_id)
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Getting task for result {masked_result_id} and user {masked_user_id}")

            # Query database - use service role client to bypass RLS if available
            try:
                service_client = self.client.get_service_role_client()
                result = service_client.table(self.tasks_table).select("*").eq("result_id", result_id).eq("user_id", user_id).execute()
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                result = self.client.client.table(self.tasks_table).select("*").eq("result_id", result_id).eq("user_id", user_id).execute()

            # Check if task exists
            if not result.data or len(result.data) == 0:
                self.logger.debug(f"No task found for result {masked_result_id}")
                return None

            task = cast(Dict[str, Any], result.data[0])
            masked_task_id = mask_id(task["id"])
            self.logger.debug(f"Successfully retrieved task {masked_task_id} for result {masked_result_id}")

            return task

        except Exception as e:
            self.logger.error(f"Error getting task for result {masked_result_id}: {str(e)}")
            raise TaskError(f"Failed to retrieve task by result: {str(e)}")

    async def claim_task_if_pending(self, task_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Atomically claim a task by updating its status from pending to processing.

        Args:
            task_id: ID of the task to claim
            user_id: ID of the user who owns the task

        Returns:
            Task data if successfully claimed, None otherwise

        Raises:
            TaskError: If claim operation fails
        """
        try:
            # Mask IDs for logging
            masked_task_id = mask_id(task_id)
            masked_user_id = mask_id(user_id)
            self.logger.debug(f"Attempting to claim task {masked_task_id} for user {masked_user_id}")

            # Prepare update data
            now = datetime.utcnow().isoformat()
            update_data = {"status": TASK_STATUS_PROCESSING, "updated_at": now}

            # Use service role client to bypass RLS if available
            try:
                service_client = self.client.get_service_role_client()
                # Explicitly request to return all columns after update
                result = (
                    service_client.table(self.tasks_table).update(update_data).eq("id", task_id).eq("user_id", user_id).eq("status", TASK_STATUS_PENDING).execute()  # Only update if status is pending
                )
            except Exception as e:
                self.logger.warning(f"Failed to use service role client: {str(e)}, falling back to regular client")
                # Fallback to regular client if service role client not available
                result = (
                    self.client.client.table(self.tasks_table)
                    .update(update_data)
                    .eq("id", task_id)
                    .eq("user_id", user_id)
                    .eq("status", TASK_STATUS_PENDING)  # Only update if status is pending
                    .execute()
                )

            # Check if any rows were affected by the update
            rows_affected = 0
            if hasattr(result, "count") and result.count is not None:
                rows_affected = result.count
            elif result.data:
                rows_affected = len(result.data)

            if rows_affected > 0:
                self.logger.info(f"Successfully claimed task {masked_task_id}")
                # Return the updated task data
                if result.data and len(result.data) > 0:
                    return cast(Dict[str, Any], result.data[0])

                # If we don't have the task data from the update, fetch it
                # This should rarely happen with proper returning clause
                return await self.get_task(task_id, user_id)
            else:
                # Task couldn't be claimed - log the failure but don't query for status
                # This avoids an unnecessary database read that's only for logging
                self.logger.info(f"Could not claim task {masked_task_id}. Task is not in PENDING state or does not exist.")
                return None

        except Exception as e:
            self.logger.error(f"Error claiming task {masked_task_id}: {str(e)}")
            raise TaskError(f"Failed to claim task: {str(e)}")
