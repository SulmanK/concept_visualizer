"""
Task service implementation.

This module provides services for managing background tasks.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from app.core.supabase.client import SupabaseClient
from app.services.interfaces.task_service import TaskServiceInterface
from app.utils.security.mask import mask_id

# Custom exceptions
class TaskError(Exception):
    """Base exception for task-related errors."""
    
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class TaskNotFoundError(TaskError):
    """Exception raised when a task is not found."""
    
    def __init__(self, task_id: str):
        self.task_id = task_id
        message = f"Task with ID {mask_id(task_id)} not found"
        super().__init__(message)


class TaskService(TaskServiceInterface):
    """Service for managing background tasks."""
    
    def __init__(self, client: SupabaseClient):
        """
        Initialize task service with Supabase client.
        
        Args:
            client: Supabase client for interacting with the database
        """
        self.client = client
        self.logger = logging.getLogger("task_service")
    
    async def create_task(
        self, 
        user_id: str, 
        task_type: str, 
        metadata: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Create a new task record.
        
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
            self.logger.info(f"Creating task of type '{task_type}' for user {masked_user_id}")
            
            # Prepare task data
            task_data = {
                "id": task_id,
                "created_at": now,
                "updated_at": now,
                "user_id": user_id,
                "type": task_type,
                "status": "pending",
                "metadata": metadata or {}
            }
            
            # Insert into database
            result = self.client.client.table("tasks").insert(task_data).execute()
            
            # Check if insertion was successful
            if not result.data or len(result.data) == 0:
                raise TaskError(f"Failed to create task of type '{task_type}'")
                
            task = result.data[0]
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
        error_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Update the status of a task.
        
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
            self.logger.info(f"Updating task {masked_task_id} status to '{status}'")
            
            # Prepare update data
            update_data = {
                "updated_at": datetime.utcnow().isoformat(),
                "status": status
            }
            
            # Add result_id if provided
            if result_id:
                update_data["result_id"] = result_id
                
            # Add error_message if provided
            if error_message:
                update_data["error_message"] = error_message
            
            # Update in database
            result = self.client.client.table("tasks") \
                .update(update_data) \
                .eq("id", task_id) \
                .execute()
            
            # Check if update was successful
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)
                
            task = result.data[0]
            self.logger.info(f"Successfully updated task {masked_task_id} status to '{status}'")
            
            return task
            
        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error updating task {masked_task_id}: {str(e)}")
            raise TaskError(f"Failed to update task: {str(e)}")
    
    async def get_task(self, task_id: str, user_id: str) -> Dict[str, Any]:
        """
        Get a task by ID.
        
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
            self.logger.info(f"Getting task {masked_task_id} for user {masked_user_id}")
            
            # Query database
            result = self.client.client.table("tasks") \
                .select("*") \
                .eq("id", task_id) \
                .eq("user_id", user_id) \
                .execute()
            
            # Check if task exists
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)
                
            task = result.data[0]
            self.logger.info(f"Successfully retrieved task {masked_task_id}")
            
            return task
            
        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error getting task {mask_id(task_id)}: {str(e)}")
            raise TaskError(f"Failed to retrieve task: {str(e)}")
    
    async def get_tasks_by_user(
        self, 
        user_id: str, 
        status: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Get tasks for a user.
        
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
            status_filter = f" with status '{status}'" if status else ""
            self.logger.info(f"Getting tasks for user {masked_user_id}{status_filter}")
            
            # Start query
            query = self.client.client.table("tasks") \
                .select("*") \
                .eq("user_id", user_id) \
                .order("created_at", desc=True) \
                .limit(limit)
            
            # Add status filter if provided
            if status:
                query = query.eq("status", status)
            
            # Execute query
            result = query.execute()
            
            # Check result
            if not result.data:
                return []
                
            tasks = result.data
            self.logger.info(f"Retrieved {len(tasks)} tasks for user {masked_user_id}")
            
            return tasks
            
        except Exception as e:
            self.logger.error(f"Error getting tasks for user {mask_id(user_id)}: {str(e)}")
            raise TaskError(f"Failed to retrieve tasks: {str(e)}")
    
    async def delete_task(self, task_id: str, user_id: str) -> bool:
        """
        Delete a task.
        
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
            self.logger.info(f"Deleting task {masked_task_id} for user {masked_user_id}")
            
            # First check if task exists and belongs to user
            result = self.client.client.table("tasks") \
                .select("id") \
                .eq("id", task_id) \
                .eq("user_id", user_id) \
                .execute()
            
            # Check if task exists
            if not result.data or len(result.data) == 0:
                raise TaskNotFoundError(task_id)
            
            # Delete from database
            result = self.client.client.table("tasks") \
                .delete() \
                .eq("id", task_id) \
                .eq("user_id", user_id) \
                .execute()
            
            # Check if deletion was successful
            if not result.data or len(result.data) == 0:
                raise TaskError(f"Failed to delete task {masked_task_id}")
                
            self.logger.info(f"Successfully deleted task {masked_task_id}")
            
            return True
            
        except TaskNotFoundError:
            # Re-raise TaskNotFoundError
            raise
        except Exception as e:
            self.logger.error(f"Error deleting task {mask_id(task_id)}: {str(e)}")
            raise TaskError(f"Failed to delete task: {str(e)}")
            
    async def get_task_by_result_id(self, result_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by its result ID.
        
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
            self.logger.info(f"Getting task for result {masked_result_id} and user {masked_user_id}")
            
            # Query database
            result = self.client.client.table("tasks") \
                .select("*") \
                .eq("result_id", result_id) \
                .eq("user_id", user_id) \
                .execute()
            
            # Check if task exists
            if not result.data or len(result.data) == 0:
                self.logger.info(f"No task found for result {masked_result_id}")
                return None
                
            task = result.data[0]
            self.logger.info(f"Successfully retrieved task for result {masked_result_id}")
            
            return task
            
        except Exception as e:
            self.logger.error(f"Error getting task for result {mask_id(result_id)}: {str(e)}")
            raise TaskError(f"Failed to retrieve task: {str(e)}") 