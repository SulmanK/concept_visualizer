"""
Tests for common base models.
"""

import pytest
from pydantic import ValidationError, Field
from app.models.common.base import APIBaseModel, ErrorResponse


class SampleModel(APIBaseModel):
    """Sample model for testing the base class."""
    
    name: str = Field(..., description="Name field")
    count: int = Field(0, description="Count field")


class TestAPIBaseModel:
    """Tests for the APIBaseModel base class."""

    def test_valid_model(self):
        """Test creating a valid model extending APIBaseModel."""
        model = SampleModel(name="Test")
        assert model.name == "Test"
        assert model.count == 0

    def test_validate_assignment(self):
        """Test validation happens on field assignment."""
        model = SampleModel(name="Test")
        
        # This should work
        model.name = "New Name"
        assert model.name == "New Name"
        
        # This should fail validation
        with pytest.raises(ValidationError):
            model.count = "not an integer"

    def test_dict_conversion(self):
        """Test conversion to dictionary."""
        model = SampleModel(name="Test", count=5)
        model_dict = model.model_dump()  # In Pydantic v2 it's model_dump
        assert isinstance(model_dict, dict)
        assert model_dict["name"] == "Test"
        assert model_dict["count"] == 5

    def test_json_conversion(self):
        """Test conversion to JSON."""
        model = SampleModel(name="Test", count=5)
        model_json = model.model_dump_json()  # In Pydantic v2 it's model_dump_json
        assert isinstance(model_json, str)
        assert '"name":"Test"' in model_json
        assert '"count":5' in model_json


class TestErrorResponse:
    """Tests for the ErrorResponse model."""

    def test_valid_error(self):
        """Test creating a valid ErrorResponse."""
        error = ErrorResponse(
            detail="Resource not found",
            code="NOT_FOUND",
            status_code=404,
            path="/api/concepts/123"
        )
        assert error.detail == "Resource not found"
        assert error.code == "NOT_FOUND"
        assert error.status_code == 404
        assert error.path == "/api/concepts/123"

    def test_minimal_error(self):
        """Test creating a minimal ErrorResponse."""
        error = ErrorResponse(
            detail="Internal server error",
            code="INTERNAL_ERROR",
            status_code=500
        )
        assert error.detail == "Internal server error"
        assert error.code == "INTERNAL_ERROR"
        assert error.status_code == 500
        assert error.path is None

    def test_serialization(self):
        """Test serialization of ErrorResponse to dict and JSON."""
        error = ErrorResponse(
            detail="Bad request",
            code="VALIDATION_ERROR",
            status_code=400,
            path="/api/concepts"
        )
        
        # Dict serialization
        error_dict = error.model_dump()
        assert error_dict["detail"] == "Bad request"
        assert error_dict["code"] == "VALIDATION_ERROR"
        assert error_dict["status_code"] == 400
        assert error_dict["path"] == "/api/concepts"
        
        # JSON serialization
        error_json = error.model_dump_json()
        assert isinstance(error_json, str)
        assert '"detail":"Bad request"' in error_json
        assert '"code":"VALIDATION_ERROR"' in error_json
        assert '"status_code":400' in error_json 