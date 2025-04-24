"""Response models for task-related API endpoints.

This module defines Pydantic models for structuring responses from
task management endpoints.
"""

from typing import Any, Dict, Optional

from pydantic import Field

from ..common.base import APIBaseModel


class TaskResponse(APIBaseModel):
    """Response model for task creation and status updates."""

    task_id: str = Field(..., description="Unique task identifier")
    status: str = Field(..., description="Current task status (pending, processing, completed, failed)")
    type: str = Field(..., description="Task type (e.g., concept_generation, concept_refinement)")
    message: str = Field(..., description="Human-readable status message")

    created_at: Optional[str] = Field(None, description="Task creation timestamp")
    updated_at: Optional[str] = Field(None, description="Last status update timestamp")
    completed_at: Optional[str] = Field(None, description="Task completion timestamp")

    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Task-specific metadata (e.g., prompt info)")

    result_id: Optional[str] = Field(
        None,
        description="ID of the result resource (e.g., concept ID for generation tasks)",
    )

    image_url: Optional[str] = Field(None, description="URL of the generated image (for completed tasks)")

    error_message: Optional[str] = Field(None, description="Error message if the task failed")
