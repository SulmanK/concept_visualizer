"""
Interface for task management services.
"""

import abc
from typing import Any, Dict, List, Optional


class TaskServiceInterface(abc.ABC):
    """Interface for services that handle task management."""
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
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
        pass
    
    @abc.abstractmethod
    async def get_task_by_result_id(self, result_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a task by result ID.
        
        Args:
            result_id: ID of the result entity (e.g. concept_id)
            user_id: ID of the user who owns the task
            
        Returns:
            Task data if found, None otherwise
            
        Raises:
            TaskError: If retrieval fails
        """
        pass
    
    @abc.abstractmethod
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
        pass 