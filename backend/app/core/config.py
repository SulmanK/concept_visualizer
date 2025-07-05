"""Application configuration module.

This module defines the settings for the Concept Visualizer API.
"""

import logging
import os
from pathlib import Path
from typing import Any, List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.exceptions import ConfigurationError, EnvironmentVariableError

# Configure logging
logger = logging.getLogger(__name__)

# Get the path to the .env file
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BACKEND_DIR / ".env"

# Log the env file path and check if it exists
logger.info(f"Looking for .env file at: {ENV_FILE}")
logger.info(f".env file exists: {ENV_FILE.exists()}")


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes:
        API_PREFIX: Prefix for all API endpoints
        CORS_ORIGINS: List of allowed origins for CORS
        JIGSAWSTACK_API_KEY: API key for JigsawStack
        JIGSAWSTACK_API_URL: Base URL for JigsawStack API
        SUPABASE_URL: URL for Supabase project
        SUPABASE_KEY: API key (anon or service role) for Supabase
        SUPABASE_JWT_SECRET: Secret key for generating Supabase-compatible JWTs
        SUPABASE_SERVICE_ROLE: Service role key for Supabase with elevated permissions
        LOG_LEVEL: Log level for the application
        ENVIRONMENT: Environment the application is running in
        UPSTASH_REDIS_ENDPOINT: Endpoint for Upstash Redis
        UPSTASH_REDIS_PASSWORD: Password for Upstash Redis
        UPSTASH_REDIS_PORT: Port for Upstash Redis
        STORAGE_BUCKET_PALETTE: Name of the storage bucket for palettes
        STORAGE_BUCKET_CONCEPT: Name of the storage bucket for concepts
        RATE_LIMITING_ENABLED: Flag to enable/disable rate limiting
        DB_TABLE_TASKS: Name of the tasks table in the database
        DB_TABLE_CONCEPTS: Name of the concepts table in the database
        DB_TABLE_PALETTES: Name of the palettes table in the database
        PUB_SUB_TOPIC_ID: Topic ID for Google Cloud Pub/Sub
        PUB_SUB_PROJECT_ID: Project ID for Google Cloud Pub/Sub
        SIGNED_URL_EXPIRY_SECONDS: Signed URL expiration time in seconds
    """

    # API settings
    API_PREFIX: str = "/api"

    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "https://*.vercel.app"]

    # JigsawStack API settings
    JIGSAWSTACK_API_KEY: str = "dummy_key"
    JIGSAWSTACK_API_URL: str = "https://api.jigsawstack.com"

    # Supabase settings
    SUPABASE_URL: str = "https://your-project-id.supabase.co"
    SUPABASE_KEY: str = "your-api-key"
    SUPABASE_JWT_SECRET: str = ""  # JWT secret for generating tokens
    SUPABASE_SERVICE_ROLE: str = ""  # Service role key with elevated permissions

    # Storage bucket settings
    STORAGE_BUCKET_PALETTE: str = "your-bucket-name"
    STORAGE_BUCKET_CONCEPT: str = "your-bucket-name"

    # Signed URL expiration time: 31 days in seconds (2,678,400 seconds)
    SIGNED_URL_EXPIRY_SECONDS: int = 31 * 24 * 60 * 60  # 31 days

    # Database table settings
    DB_TABLE_TASKS: str = "tasks"
    DB_TABLE_CONCEPTS: str = "concepts"
    DB_TABLE_PALETTES: str = "palettes"

    # Logging settings
    LOG_LEVEL: str = "INFO"

    # Environment settings
    ENVIRONMENT: str = "development"

    # Upstash Redis settings
    UPSTASH_REDIS_ENDPOINT: str = ""  # Host without protocol (e.g., "relevant-stud-56361.upstash.io")
    UPSTASH_REDIS_PASSWORD: str = ""  # Redis password
    UPSTASH_REDIS_PORT: int = 6379  # Redis port, usually 6379

    # Rate limiting settings
    RATE_LIMITING_ENABLED: bool = True

    # Google Cloud Pub/Sub settings
    PUB_SUB_TOPIC_ID: str = "concept-tasks"
    PUB_SUB_PROJECT_ID: str = "your-project-id"

    # Image processing settings
    # Recommended values by environment:
    # - Cloud Run (limited resources): CONCURRENCY_LIMIT=1, TIMEOUT=180-240s
    # - High-memory instances (4GB+ RAM): CONCURRENCY_LIMIT=2-3, TIMEOUT=120s
    # - Powerful servers (8GB+ RAM, 4+ CPU): CONCURRENCY_LIMIT=4-6, TIMEOUT=90s
    PALETTE_PROCESSING_CONCURRENCY_LIMIT: int = 4  # Max concurrent palette variations to process (1=sequential, better for Cloud Run)
    PALETTE_PROCESSING_TIMEOUT_SECONDS: int = 540  # Timeout for individual palette processing in seconds

    # Configure Pydantic to use environment variables
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="CONCEPT_",
        case_sensitive=True,
    )

    def validate_required_settings(self) -> None:
        """Validate that all required settings are properly configured.

        Raises:
            EnvironmentVariableError: If a required setting is missing or has its default value
        """
        # JigsawStack is required for the API to function
        if self.JIGSAWSTACK_API_KEY == "dummy_key":
            logger.error("Missing required environment variable: CONCEPT_JIGSAWSTACK_API_KEY")
            raise EnvironmentVariableError(
                message="JigsawStack API key is required",
                variable_name="CONCEPT_JIGSAWSTACK_API_KEY",
            )

        # Supabase is required for session and data storage
        if self.SUPABASE_URL == "https://your-project-id.supabase.co":
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_URL")
            raise EnvironmentVariableError(message="Supabase URL is required", variable_name="CONCEPT_SUPABASE_URL")

        if self.SUPABASE_KEY == "your-api-key":
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_KEY")
            raise EnvironmentVariableError(message="Supabase key is required", variable_name="CONCEPT_SUPABASE_KEY")

        # Check for essential JWT and service role settings
        if not self.SUPABASE_JWT_SECRET:
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_JWT_SECRET")
            raise EnvironmentVariableError(
                message="Supabase JWT secret is required for token generation",
                variable_name="CONCEPT_SUPABASE_JWT_SECRET",
            )

        if not self.SUPABASE_SERVICE_ROLE:
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_SERVICE_ROLE")
            raise EnvironmentVariableError(
                message="Supabase service role key is required for administrative operations",
                variable_name="CONCEPT_SUPABASE_SERVICE_ROLE",
            )

        # Check for storage bucket settings
        if not self.STORAGE_BUCKET_CONCEPT:
            logger.error("Missing required environment variable: CONCEPT_STORAGE_BUCKET_CONCEPT")
            raise EnvironmentVariableError(
                message="Storage bucket name for concepts is required",
                variable_name="CONCEPT_STORAGE_BUCKET_CONCEPT",
            )

        if not self.STORAGE_BUCKET_PALETTE:
            logger.error("Missing required environment variable: CONCEPT_STORAGE_BUCKET_PALETTE")
            raise EnvironmentVariableError(
                message="Storage bucket name for palettes is required",
                variable_name="CONCEPT_STORAGE_BUCKET_PALETTE",
            )

        # Database table validation is not required as they have sensible defaults
        # But we should log if they're using custom table names
        if self.DB_TABLE_TASKS != "tasks":
            logger.info(f"Using custom tasks table name: {self.DB_TABLE_TASKS}")
        if self.DB_TABLE_CONCEPTS != "concepts":
            logger.info(f"Using custom concepts table name: {self.DB_TABLE_CONCEPTS}")
        if self.DB_TABLE_PALETTES != "palettes":
            logger.info(f"Using custom palettes table name: {self.DB_TABLE_PALETTES}")

        # Redis is required for rate limiting if enabled
        if self.RATE_LIMITING_ENABLED:
            if not self.UPSTASH_REDIS_ENDPOINT:
                logger.error("Missing required environment variable: CONCEPT_UPSTASH_REDIS_ENDPOINT")
                raise EnvironmentVariableError(
                    message="Redis endpoint is required when rate limiting is enabled",
                    variable_name="CONCEPT_UPSTASH_REDIS_ENDPOINT",
                )

            if not self.UPSTASH_REDIS_PASSWORD:
                logger.error("Missing required environment variable: CONCEPT_UPSTASH_REDIS_PASSWORD")
                raise EnvironmentVariableError(
                    message="Redis password is required when rate limiting is enabled",
                    variable_name="CONCEPT_UPSTASH_REDIS_PASSWORD",
                )

    def validate_redis_settings(self) -> Optional[str]:
        """Validate Redis settings and return any issues found.

        Returns:
            Error message if validation fails, None otherwise
        """
        if not self.RATE_LIMITING_ENABLED:
            return None

        if not self.UPSTASH_REDIS_ENDPOINT:
            return "Redis endpoint is missing"

        if not self.UPSTASH_REDIS_PASSWORD:
            return "Redis password is missing"

        # Validate format of Redis endpoint (shouldn't have protocol)
        if "://" in self.UPSTASH_REDIS_ENDPOINT:
            return "Redis endpoint should not include protocol (e.g., 'redis://')"

        return None

    def __init__(self, **kwargs: Any) -> None:
        """Initialize settings and validate in non-development environments."""
        super().__init__(**kwargs)

        # Check Redis settings regardless of environment
        redis_error = self.validate_redis_settings()
        if redis_error:
            logger.warning(f"Redis configuration issue: {redis_error}")
            logger.warning("Rate limiting will fall back to in-memory storage")

        # Only validate in production and staging environments
        # This allows development to proceed without all services configured
        if self.ENVIRONMENT not in ["development", "test"]:
            try:
                self.validate_required_settings()
            except EnvironmentVariableError as e:
                # Re-raise with additional context for non-development environments
                raise ConfigurationError(
                    message=f"Configuration error in {self.ENVIRONMENT} environment: {e.message}",
                    config_key=e.variable_name,
                    details={"environment": self.ENVIRONMENT},
                )


# Create a settings instance
try:
    settings = Settings()

    # Safely log configuration with masked sensitive information
    logger.info(f"Application running in {settings.ENVIRONMENT} environment")
    logger.info(f"API configured with prefix: {settings.API_PREFIX}")
    logger.info(f"Rate limiting enabled: {settings.RATE_LIMITING_ENABLED}")

    # Move detailed CORS config to debug, make sure origins are properly masked if they contain sensitive data
    if isinstance(settings.CORS_ORIGINS, list) and len(settings.CORS_ORIGINS) > 5:
        # If there are many origins, just log the count to avoid verbose logs
        logger.debug(f"CORS configured with {len(settings.CORS_ORIGINS)} origins")
    else:
        logger.debug(f"CORS origins: {settings.CORS_ORIGINS}")
except Exception as e:
    logger.critical(f"Failed to load configuration: {str(e)}")
    # In a production environment, we might want to exit the application here
    # since continuing with invalid configuration could lead to security issues
    if os.getenv("CONCEPT_ENVIRONMENT") not in ["development", "test"]:
        raise ConfigurationError(
            message=f"Fatal configuration error: {str(e)}",
            config_key="CONFIGURATION_FILE",
            details={"hint": "Check your environment variables and .env file"},
        )
    settings = Settings()  # Use defaults in development


# Safely log configuration with masked sensitive information
def get_masked_value(value: str, visible_chars: int = 4) -> str:
    """Return a masked string showing only the first few characters."""
    if not value or len(value) <= visible_chars:
        return "[EMPTY]" if not value else "[TOO_SHORT]"
    return f"{value[:visible_chars]}{'*' * min(8, len(value) - visible_chars)}"


# Masked logging of sensitive configuration
if settings.LOG_LEVEL == "DEBUG":
    logger.debug(f"JigsawStack API key: {get_masked_value(settings.JIGSAWSTACK_API_KEY)}")
    logger.debug(f"JigsawStack API URL: {settings.JIGSAWSTACK_API_URL}")
    logger.debug(f"Supabase URL: {get_masked_value(settings.SUPABASE_URL, 8)}")
    logger.debug(f"Supabase key: {get_masked_value(settings.SUPABASE_KEY)}")
    logger.debug(f"Supabase JWT secret: {get_masked_value(settings.SUPABASE_JWT_SECRET)}")
    logger.debug(f"Supabase service role: {get_masked_value(settings.SUPABASE_SERVICE_ROLE)}")
    logger.debug(f"Redis endpoint: {get_masked_value(settings.UPSTASH_REDIS_ENDPOINT, 8)}")
    logger.debug(f"Redis password: {get_masked_value(settings.UPSTASH_REDIS_PASSWORD)}")
    logger.debug(f"Storage bucket (palette): {get_masked_value(settings.STORAGE_BUCKET_PALETTE, 3)}")
    logger.debug(f"Storage bucket (concept): {get_masked_value(settings.STORAGE_BUCKET_CONCEPT, 3)}")
    logger.debug(f"DB table (tasks): {settings.DB_TABLE_TASKS}")
    logger.debug(f"DB table (concepts): {settings.DB_TABLE_CONCEPTS}")
    logger.debug(f"DB table (palettes): {settings.DB_TABLE_PALETTES}")
