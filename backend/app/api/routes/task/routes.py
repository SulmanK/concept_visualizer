"""Task management API routes.

This module provides endpoints for managing background tasks.
"""

import logging
import traceback
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response

from app.api.dependencies import CommonDependencies
from app.api.errors import ResourceNotFoundError, ServiceUnavailableError
from app.core.config import settings
from app.models.task.response import TaskResponse
from app.services.task.service import TaskNotFoundError
from app.utils.security.mask import mask_id

# Configure logging
logger = logging.getLogger("task_api")

router = APIRouter()


@router.get("", response_model=List[TaskResponse])
async def get_tasks(
    request: Request,
    status: Optional[str] = Query(None, description="Filter tasks by status"),
    limit: int = Query(10, ge=1, le=50, description="Maximum number of tasks to return"),
    commons: CommonDependencies = Depends(),
) -> List[TaskResponse]:
    """Get a list of tasks for the authenticated user.

    Args:
        request: The FastAPI request object
        status: Optional status to filter by
        limit: Maximum number of tasks to return
        commons: Common dependencies including services

    Returns:
        List of tasks for the authenticated user

    Raises:
        HTTPException: If user is not authenticated (401)
        ServiceUnavailableError: If there is an error retrieving tasks
    """
    try:
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Get tasks from task service
        tasks = await commons.task_service.get_tasks_by_user(user_id=user_id, status=status, limit=limit)

        # Convert task data to response model format
        return [
            TaskResponse(
                task_id=task["id"],
                status=task["status"],
                message=f"Task is {task['status']}",
                type=str(task.get("type", "")),  # Ensure type is always a string
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at"),
                completed_at=task.get("completed_at"),
                result_id=task.get("result_id"),
                image_url=task.get("image_url"),
                error_message=task.get("error_message"),
                metadata=task.get("metadata", {}),
            )
            for task in tasks
        ]
    except Exception as e:
        logger.error(f"Error retrieving tasks: {str(e)}")
        if settings.ENVIRONMENT == "development":
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
        else:
            logger.debug("Enable development mode to see full traceback")
        raise ServiceUnavailableError(detail=f"Error retrieving tasks: {str(e)}")


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
) -> TaskResponse:
    """Get details of a specific task.

    Args:
        task_id: ID of the task to retrieve
        request: The FastAPI request object
        commons: Common dependencies including services

    Returns:
        Task details

    Raises:
        HTTPException: If user is not authenticated (401)
        ResourceNotFoundError: If the task is not found
        ServiceUnavailableError: If there is an error retrieving the task
    """
    try:
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Get task from task service
        try:
            task = await commons.task_service.get_task(task_id, user_id)

            # Convert task data to response model
            return TaskResponse(
                task_id=task["id"],
                status=task["status"],
                message=f"Task is {task['status']}",
                type=str(task.get("type", "")),  # Ensure type is always a string
                created_at=task.get("created_at"),
                updated_at=task.get("updated_at"),
                completed_at=task.get("completed_at"),
                result_id=task.get("result_id"),
                image_url=task.get("image_url"),
                error_message=task.get("error_message"),
                metadata=task.get("metadata", {}),
            )
        except TaskNotFoundError:
            # If not found in task service, return not found
            raise ResourceNotFoundError(detail=f"Task with ID {mask_id(task_id)} not found")

    except ResourceNotFoundError:
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error retrieving task: {str(e)}")
        if settings.ENVIRONMENT == "development":
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
        else:
            logger.debug("Enable development mode to see full traceback")
        raise ServiceUnavailableError(detail=f"Error retrieving task: {str(e)}")


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    request: Request,
    commons: CommonDependencies = Depends(),
) -> Response:
    """Delete a task.

    Args:
        task_id: ID of the task to delete
        request: The FastAPI request object
        commons: Common dependencies including services

    Returns:
        204 No Content on success

    Raises:
        HTTPException: If user is not authenticated (401)
        ResourceNotFoundError: If the task is not found
        ServiceUnavailableError: If there is an error deleting the task
    """
    try:
        # Get user ID from commons (which gets it from auth middleware)
        user_id = commons.user_id
        if not user_id:
            raise HTTPException(status_code=401, detail="Authentication required")

        # Delete task
        try:
            await commons.task_service.delete_task(task_id, user_id)
            return Response(status_code=204)
        except TaskNotFoundError:
            # If not found in task service, return not found
            raise ResourceNotFoundError(detail=f"Task with ID {mask_id(task_id)} not found")

    except ResourceNotFoundError:
        # Re-raise specific errors
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {str(e)}")
        if settings.ENVIRONMENT == "development":
            logger.debug(f"Exception traceback: {traceback.format_exc()}")
        else:
            logger.debug("Enable development mode to see full traceback")
        raise ServiceUnavailableError(detail=f"Error deleting task: {str(e)}")
