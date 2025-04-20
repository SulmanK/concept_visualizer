# Backend Documentation

This directory contains comprehensive documentation for the backend of the Concept Visualizer application. The backend is built using FastAPI and follows a layered architecture.

## Directory Structure

- [API](api/README.md): API routes, middleware, dependencies, and error handling
- [Core](core/README.md): Core infrastructure including configuration, exceptions, and service integrations
- [Models](models/README.md): Data models used throughout the application
- [Services](services/README.md): Business logic and external service integrations
- [Utils](utils/README.md): Utility functions and helpers

## Main Application

- [Main Application](main.md): The entry point of the FastAPI application

## Architecture

The backend follows a layered architecture with strict separation between components:

1. **API Layer**: Handles HTTP requests/responses, routing, and input validation
2. **Service Layer**: Contains business logic and orchestrates use cases
3. **External Services**: Integrations with external APIs and services
4. **Models**: Defines data structures and validation
5. **Core**: Application configuration, logging, and exception handling
6. **Utils**: Helper functions and utilities

## Dependencies

- FastAPI: Modern, high-performance web framework
- Pydantic: Data validation and settings management
- Supabase: Database and storage
- Redis: Rate limiting and caching
- JigsawStack API: External image generation service 