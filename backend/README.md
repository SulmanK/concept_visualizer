# Concept Visualizer Backend

This directory contains the backend API service for the Concept Visualizer project.

## Setup

### Virtual Environment

The backend uses `uv` for dependency management with a virtual environment contained within this directory:

```bash
# Navigate to the backend directory
cd backend

# Create a virtual environment
uv venv

# Install dependencies
uv pip install -e .
```

### Environment Variables

Copy the example environment file:

```bash
cp .env.example .env
```

Then edit `.env` with your specific configuration.

## Development

### Running the API Server

```bash
# Start the development server
uv run uvicorn app.main:app --reload
```

### Running Tests

```bash
# Run tests
uv run pytest
```

## Project Structure

- `app/` - Main application code
  - `api/` - API routes and endpoints
  - `core/` - Core functionality and config
  - `models/` - Data models
  - `services/` - Business logic
- `docs/` - Documentation
- `tests/` - Test suite
- `.env` - Environment variables (not tracked in git)
- `.env.example` - Example environment file
- `pyproject.toml` - Project configuration and dependencies
