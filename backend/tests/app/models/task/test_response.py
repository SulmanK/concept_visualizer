"""Tests for task response models."""

from typing import Any, Dict

from app.models.task.response import TaskResponse


class TestTaskResponse:
    """Tests for the TaskResponse model."""

    def test_valid_task_response(self) -> None:
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
                "theme_description": "Professional blue theme",
            },
            result_id="concept-456",
            image_url="https://example.com/image.png",
            error_message=None,
        )
        assert response.task_id == "task-123"
        assert response.status == "completed"
        assert response.type == "concept_generation"
        assert response.message == "Concept generation completed successfully"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert response.updated_at == "2023-01-01T12:05:00Z"
        assert response.completed_at == "2023-01-01T12:05:00Z"
        # Check metadata with type checking
        meta = response.metadata or {}
        assert meta.get("logo_description") == "A modern tech logo"
        assert meta.get("theme_description") == "Professional blue theme"
        assert response.result_id == "concept-456"
        assert response.image_url == "https://example.com/image.png"
        assert response.error_message is None

    def test_failed_task_response(self) -> None:
        """Test creating a failed TaskResponse."""
        response = TaskResponse(
            task_id="task-123",
            status="failed",
            type="concept_generation",
            message="Concept generation failed",
            created_at="2023-01-01T12:00:00Z",
            updated_at="2023-01-01T12:05:00Z",
            completed_at=None,
            metadata={
                "logo_description": "A modern tech logo",
                "theme_description": "Professional blue theme",
            },
            result_id=None,
            image_url=None,
            error_message="Failed to connect to image generation service",
        )
        assert response.task_id == "task-123"
        assert response.status == "failed"
        assert response.type == "concept_generation"
        assert response.message == "Concept generation failed"
        assert response.created_at == "2023-01-01T12:00:00Z"
        assert response.updated_at == "2023-01-01T12:05:00Z"
        assert response.completed_at is None
        # Check metadata with type checking
        meta = response.metadata or {}
        assert meta.get("logo_description") == "A modern tech logo"
        assert response.error_message == "Failed to connect to image generation service"
        assert response.result_id is None
        assert response.image_url is None

    def test_minimal_task_response(self) -> None:
        """Test creating a minimal TaskResponse."""
        response = TaskResponse(
            task_id="task-123",
            status="pending",
            type="concept_generation",
            message="Task queued",
            created_at=None,
            updated_at=None,
            completed_at=None,
            result_id=None,
            image_url=None,
            error_message=None,
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

    def test_task_response_with_complex_metadata(self) -> None:
        """Test TaskResponse with complex nested metadata."""
        complex_metadata: Dict[str, Any] = {
            "original_concept": {
                "id": "concept-789",
                "image_url": "https://example.com/original.png",
            },
            "refinement_options": {
                "preserve_aspects": ["colors", "layout"],
                "refinement_prompt": "Make it more minimalist",
            },
            "user_preferences": {"style": "modern", "colors": ["blue", "green"]},
        }

        response = TaskResponse(
            task_id="task-123",
            status="processing",
            type="concept_refinement",
            message="Refining concept",
            created_at=None,
            updated_at=None,
            completed_at=None,
            metadata=complex_metadata,
            result_id=None,
            image_url=None,
            error_message=None,
        )
        assert response.task_id == "task-123"
        assert response.status == "processing"
        assert response.type == "concept_refinement"
        assert response.message == "Refining concept"

        # Check metadata with type checking
        meta = response.metadata or {}
        original_concept = meta.get("original_concept", {})
        refinement_options = meta.get("refinement_options", {})
        user_preferences = meta.get("user_preferences", {})

        assert original_concept.get("id") == "concept-789"
        assert refinement_options.get("preserve_aspects") == ["colors", "layout"]
        assert user_preferences.get("style") == "modern"
