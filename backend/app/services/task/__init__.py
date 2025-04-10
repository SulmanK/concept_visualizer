"""
Task service module.

This module provides services for managing background tasks.
"""

from app.core.supabase.client import get_supabase_client
from app.services.task.service import TaskService

def get_task_service() -> TaskService:
    """
    Factory function to create a TaskService instance.
    
    Returns:
        TaskService: Configured task service
    """
    client = get_supabase_client()
    return TaskService(client) 