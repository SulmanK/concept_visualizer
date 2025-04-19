"""
Tests for task response models.
"""

import pytest
from pydantic import ValidationError
from app.models.task.response import TaskResponse


class TestTaskResponse:
    """Tests for the TaskResponse model."""

    def test_valid_task_response(self):
        """Test creating a valid TaskResponse."""
        response = TaskResponse(
            task_id="task-123",
            status="completed",
            type="concept_generation",
            message="Concept generation completed successfully",
            created_at="2023-01-01T12:00:00Z",
            updated_at="2023-01-01T12:05:00Z",
            completed_at="2023-01-01T12:05:00Z",
            metadata={
                "logo_description": "A modern tech logo",
                "theme_description": "Professional blue theme"
            },
            result_id="concept-456",
            image_url="https://example.com/image.png"
        )
        assert response.task_id == "task-123"
        assert response.status == "completed"
        assert response.type == "concept_generation"
        assert response.message == "Concept generation completed successfully"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert response.updated_at == "2023-01-01T12:05:00Z"
        assert response.completed_at == "2023-01-01T12:05:00Z"
        assert response.metadata["logo_description"] == "A modern tech logo"
        assert response.metadata["theme_description"] == "Professional blue theme"
        assert response.result_id == "concept-456"
        assert response.image_url == "https://example.com/image.png"
        assert response.error_message is None

    def test_failed_task_response(self):
        """Test creating a failed TaskResponse."""
        response = TaskResponse(
            task_id="task-123",
            status="failed",
            type="concept_generation",
            message="Concept generation failed",
            created_at="2023-01-01T12:00:00Z",
            updated_at="2023-01-01T12:05:00Z",
            metadata={
                "logo_description": "A modern tech logo",
                "theme_description": "Professional blue theme"
            },
            error_message="Failed to connect to image generation service"
        )
        assert response.task_id == "task-123"
        assert response.status == "failed"
        assert response.type == "concept_generation"
        assert response.message == "Concept generation failed"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert response.updated_at == "2023-01-01T12:05:00Z"
        assert response.completed_at is None
        assert response.metadata["logo_description"] == "A modern tech logo"
        assert response.error_message == "Failed to connect to image generation service"
        assert response.result_id is None
        assert response.image_url is None

    def test_minimal_task_response(self):
        """Test creating a minimal TaskResponse."""
        response = TaskResponse(
            task_id="task-123",
            status="pending",
            type="concept_generation",
            message="Task queued"
        )
        assert response.task_id == "task-123"
        assert response.status == "pending"
        assert response.type == "concept_generation"
        assert response.message == "Task queued"
        assert response.created_at is None
        assert response.updated_at is None
        assert response.completed_at is None
        assert response.metadata == {}
        assert response.result_id is None
        assert response.image_url is None
        assert response.error_message is None

    def test_task_response_with_complex_metadata(self):
        """Test TaskResponse with complex nested metadata."""
        response = TaskResponse(
            task_id="task-123",
            status="processing",
            type="concept_refinement",
            message="Refining concept",
            metadata={
                "original_concept": {
                    "id": "concept-789",
                    "image_url": "https://example.com/original.png"
                },
                "refinement_options": {
                    "preserve_aspects": ["colors", "layout"],
                    "refinement_prompt": "Make it more minimalist"
                },
                "user_preferences": {
                    "style": "modern",
                    "colors": ["blue", "green"]
                }
            }
        )
        assert response.task_id == "task-123"
        assert response.status == "processing"
        assert response.type == "concept_refinement"
        assert response.message == "Refining concept"
        assert response.metadata["original_concept"]["id"] == "concept-789"
        assert response.metadata["refinement_options"]["preserve_aspects"] == ["colors", "layout"]
        assert response.metadata["user_preferences"]["style"] == "modern" 