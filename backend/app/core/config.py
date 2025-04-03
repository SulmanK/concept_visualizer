"""
Application configuration module.

This module defines the settings for the Concept Visualizer API.
"""

import logging
from typing import List
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


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


# Create a settings instance
settings = Settings()

# Safely log configuration with masked sensitive information
def get_masked_value(value: str, visible_chars: int = 4) -> str:
    """Return a masked string showing only the first few characters."""
    if not value or len(value) <= visible_chars:
        return "[EMPTY]" if not value else "[TOO_SHORT]"
    return f"{value[:visible_chars]}{'*' * min(8, len(value) - visible_chars)}"

# Log configuration with masked sensitive data
logger.info(f"Application running in {settings.ENVIRONMENT} environment")
logger.info(f"API configured with prefix: {settings.API_PREFIX}")
logger.info(f"CORS origins: {settings.CORS_ORIGINS}")

# Masked logging of sensitive configuration
if settings.LOG_LEVEL == "DEBUG":
    logger.debug(f"JigsawStack API key: {get_masked_value(settings.JIGSAWSTACK_API_KEY)}")
    logger.debug(f"JigsawStack API URL: {settings.JIGSAWSTACK_API_URL}")
    logger.debug(f"Supabase URL: {get_masked_value(settings.SUPABASE_URL, 8)}")
    logger.debug(f"Supabase key: {get_masked_value(settings.SUPABASE_KEY)}")
    logger.debug(f"Redis endpoint: {get_masked_value(settings.UPSTASH_REDIS_ENDPOINT, 8)}")
    logger.debug(f"Redis password: {get_masked_value(settings.UPSTASH_REDIS_PASSWORD)}") 