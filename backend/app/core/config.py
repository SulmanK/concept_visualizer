"""
Application configuration module.

This module defines the settings for the Concept Visualizer API.
"""

import logging
import os
from typing import List
from pathlib import Path

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
    """
    Application settings loaded from environment variables.
    
    Attributes:
        API_PREFIX: Prefix for all API endpoints
        CORS_ORIGINS: List of allowed origins for CORS
        JIGSAWSTACK_API_KEY: API key for JigsawStack
        JIGSAWSTACK_API_URL: Base URL for JigsawStack API
        SUPABASE_URL: URL for Supabase project
        SUPABASE_KEY: API key (anon or service role) for Supabase
        LOG_LEVEL: Log level for the application
        ENVIRONMENT: Environment the application is running in
        UPSTASH_REDIS_ENDPOINT: Endpoint for Upstash Redis
        UPSTASH_REDIS_PASSWORD: Password for Upstash Redis
        UPSTASH_REDIS_PORT: Port for Upstash Redis
    """
    
    # API settings
    API_PREFIX: str = "/api"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000", 
        "http://localhost:5173"
    ]
    
    # JigsawStack API settings
    JIGSAWSTACK_API_KEY: str = "dummy_key"
    JIGSAWSTACK_API_URL: str = "https://api.jigsawstack.com"
    
    # Supabase settings
    SUPABASE_URL: str = "https://your-project-id.supabase.co"
    SUPABASE_KEY: str = "your-api-key"
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Environment settings
    ENVIRONMENT: str = "development"
    
    # Upstash Redis settings
    UPSTASH_REDIS_ENDPOINT: str = "your-redis-url.upstash.io"
    UPSTASH_REDIS_PASSWORD: str = "your-redis-password"
    UPSTASH_REDIS_PORT: int = 6379
    
    # Configure Pydantic to use environment variables
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="CONCEPT_",
        case_sensitive=True,
    )
    
    def validate_required_settings(self):
        """
        Validate that all required settings are properly configured.
        
        Raises:
            EnvironmentVariableError: If a required setting is missing or has its default value
        """
        # JigsawStack is required for the API to function
        if self.JIGSAWSTACK_API_KEY == "dummy_key":
            logger.error("Missing required environment variable: CONCEPT_JIGSAWSTACK_API_KEY")
            raise EnvironmentVariableError(
                message="JigsawStack API key is required",
                variable_name="CONCEPT_JIGSAWSTACK_API_KEY"
            )
        
        # Supabase is required for session and data storage
        if self.SUPABASE_URL == "https://your-project-id.supabase.co":
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_URL")
            raise EnvironmentVariableError(
                message="Supabase URL is required",
                variable_name="CONCEPT_SUPABASE_URL"
            )
            
        if self.SUPABASE_KEY == "your-api-key":
            logger.error("Missing required environment variable: CONCEPT_SUPABASE_KEY")
            raise EnvironmentVariableError(
                message="Supabase key is required",
                variable_name="CONCEPT_SUPABASE_KEY"
            )
        
        # Redis is optional, so we don't validate it here

    def __init__(self, **kwargs):
        """Initialize settings and validate in non-development environments."""
        super().__init__(**kwargs)
        
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
                    details={"environment": self.ENVIRONMENT}
                )


# Create a settings instance
try:
    settings = Settings()
    
    # Safely log configuration with masked sensitive information
    logger.info(f"Application running in {settings.ENVIRONMENT} environment")
    logger.info(f"API configured with prefix: {settings.API_PREFIX}")
    logger.info(f"CORS origins: {settings.CORS_ORIGINS}")
except Exception as e:
    logger.critical(f"Failed to load configuration: {str(e)}")
    # In a production environment, we might want to exit the application here
    # since continuing with invalid configuration could lead to security issues
    if os.getenv("CONCEPT_ENVIRONMENT") not in ["development", "test"]:
        raise ConfigurationError(
            message=f"Fatal configuration error: {str(e)}",
            details={"hint": "Check your environment variables and .env file"}
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
    logger.debug(f"Redis endpoint: {get_masked_value(settings.UPSTASH_REDIS_ENDPOINT, 8)}")
    logger.debug(f"Redis password: {get_masked_value(settings.UPSTASH_REDIS_PASSWORD)}") 