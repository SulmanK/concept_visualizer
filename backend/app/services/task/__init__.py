"""
Task service module.

This module provides services for managing background tasks.
"""

from app.core.supabase.client import get_supabase_client
from app.services.task.interface import TaskServiceInterface
from app.services.task.service import TaskService

__all__ = [
    "TaskService",
    "TaskServiceInterface",
    "get_task_service"
]

def get_task_service() -> TaskServiceInterface:
    """
    Factory function to create a TaskService instance.
    
    Returns:
        TaskServiceInterface: Configured task service
    """
    client = get_supabase_client()
    return TaskService(client) 