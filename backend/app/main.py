"""Main application entry point for the Concept Visualizer API.

This module initializes the FastAPI application using a factory function.
"""

from app.core.factory import create_app

# Create the FastAPI application using the factory function
app = create_app()
