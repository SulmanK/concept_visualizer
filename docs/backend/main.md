# Main Application Module

The `main.py` module serves as the entry point for the Concept Visualizer API backend. It initializes the FastAPI application using a factory pattern.

## Overview

The main module is intentionally kept simple, delegating the application creation to a factory function. This approach:

- Improves testability by allowing different configurations to be injected
- Keeps the entry point clean and focused
- Follows the separation of concerns principle

## Code Structure

```python
"""
Main application entry point for the Concept Visualizer API.

This module initializes the FastAPI application using a factory function.
"""

from app.core.factory import create_app


# Create the FastAPI application using the factory function
app = create_app()
```

## Usage

The application instance created here is what deployment platforms (like Uvicorn, Gunicorn, or containerization tools) will use to serve the API.

### Running the Application

```bash
# Using uvicorn directly
uvicorn app.main:app --reload

# Using the configured script
uv run dev
```

## Related Documentation

- [Factory Module](core/factory.md): Details about the application factory and configuration
- [API Router](api/router.md): The main API router that connects all endpoints 