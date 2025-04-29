import logging
import os
from typing import Generator
from unittest.mock import MagicMock, patch

import pytest

# Configure logging
logger = logging.getLogger(__name__)


@pytest.fixture(scope="session", autouse=True)
def mock_settings_from_env() -> Generator[None, None, None]:
    """Mock the settings object with values from environment variables.

    This ensures that CI environment variables are properly used during tests.
    """
    # Create a mock object that looks like the settings object
    mock = MagicMock()

    # Define the attributes from environment variables
    mock.SUPABASE_URL = os.getenv("CONCEPT_SUPABASE_URL", "https://example.supabase.co")
    mock.SUPABASE_KEY = os.getenv("CONCEPT_SUPABASE_KEY", "fake-api-key")
    mock.SUPABASE_SERVICE_ROLE = os.getenv("CONCEPT_SUPABASE_SERVICE_ROLE", "fake-service-role-key")
    mock.SUPABASE_JWT_SECRET = os.getenv("CONCEPT_SUPABASE_JWT_SECRET", "fake-jwt-secret")
    mock.JIGSAWSTACK_API_KEY = os.getenv("CONCEPT_JIGSAWSTACK_API_KEY", "fake-jigsaw-key")
    mock.UPSTASH_REDIS_ENDPOINT = os.getenv("CONCEPT_UPSTASH_REDIS_ENDPOINT", "localhost")
    mock.UPSTASH_REDIS_PASSWORD = os.getenv("CONCEPT_UPSTASH_REDIS_PASSWORD", "password")
    mock.UPSTASH_REDIS_PORT = int(os.getenv("CONCEPT_UPSTASH_REDIS_PORT", "6379"))
    mock.STORAGE_BUCKET_CONCEPT = os.getenv("CONCEPT_STORAGE_BUCKET_CONCEPT", "test-concepts")
    mock.STORAGE_BUCKET_PALETTE = os.getenv("CONCEPT_STORAGE_BUCKET_PALETTE", "test-palettes")
    mock.ENVIRONMENT = os.getenv("CONCEPT_ENVIRONMENT", "test")

    # Database table settings
    mock.DB_TABLE_TASKS = os.getenv("CONCEPT_DB_TABLE_TASKS", "tasks")
    mock.DB_TABLE_CONCEPTS = os.getenv("CONCEPT_DB_TABLE_CONCEPTS", "concepts")
    mock.DB_TABLE_PALETTES = os.getenv("CONCEPT_DB_TABLE_PALETTES", "palettes")

    # Log what we're using
    logger.info(f"Using Supabase URL: {mock.SUPABASE_URL}")
    logger.info(f"Using environment: {mock.ENVIRONMENT}")
    logger.info(f"Using DB tables: tasks={mock.DB_TABLE_TASKS}, concepts={mock.DB_TABLE_CONCEPTS}, palettes={mock.DB_TABLE_PALETTES}")

    # Patch all the places where settings is imported
    patches = [
        patch("app.core.supabase.client.settings", mock),
        patch("app.core.supabase.concept_storage.settings", mock),
        patch("app.core.config.settings", mock),
        patch("app.services.task.service.settings", mock),
    ]

    try:
        # Apply all patches
        for p in patches:
            p.start()
        yield
    finally:
        # Stop all patches
        for p in patches:
            p.stop()
