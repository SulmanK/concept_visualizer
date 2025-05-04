# Use an official Python runtime as a parent image
FROM python:3.11-slim as builder

WORKDIR /app

# Install uv
RUN pip install uv

# Copy pyproject.toml for dependency resolution
COPY pyproject.toml pyproject.toml
COPY README.md README.md

# Copy application code
COPY app /app/app

# Install dependencies, including the app itself in editable mode
RUN uv pip install --system --no-cache -e .[dev]

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app /app/app
COPY run.py /app/run.py

# Expose the port the app runs on
EXPOSE 8000

# Set default number of workers
ENV UVICORN_WORKERS=2

# Command to run the application using Uvicorn with multiple workers
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers ${UVICORN_WORKERS}"]
