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
    
    # Configure Pydantic to use environment variables
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        env_prefix="CONCEPT_",
        case_sensitive=True,
    )


# Create a settings instance
settings = Settings()

# Log the API key for debugging (first 10 chars only)
api_key_prefix = settings.JIGSAWSTACK_API_KEY[:10]
logger.info(f"JigsawStack API key prefix: {api_key_prefix}...")

# Log the Supabase URL for debugging
supabase_url = settings.SUPABASE_URL
logger.info(f"Supabase URL: {supabase_url}") 