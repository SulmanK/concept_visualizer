"""
Application configuration module.

This module defines the settings for the Concept Visualizer API.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        API_PREFIX: Prefix for all API endpoints
        CORS_ORIGINS: List of allowed origins for CORS
        JIGSAWSTACK_API_KEY: API key for JigsawStack
        JIGSAWSTACK_API_URL: Base URL for JigsawStack API
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
    
    # Logging settings
    LOG_LEVEL: str = "INFO"
    
    # Configure Pydantic to use environment variables
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="CONCEPT_",
        case_sensitive=True,
    )


# Create a settings instance
settings = Settings() 