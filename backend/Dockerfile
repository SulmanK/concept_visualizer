# syntax=docker/dockerfile:1               # enables nicer syntax hints

############################
# 1️⃣  COMMON BASE IMAGE
############################
FROM python:3.11-slim AS base

# Fail-fast, no .pyc files
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# --- ✨ NEW: install the native libs cv2 needs ✨ ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1           \
        libglib2.0-0     \
    && rm -rf /var/lib/apt/lists/*


############################
# 2️⃣  BUILD STAGE
############################
FROM base AS builder
WORKDIR /app

# ‘uv’ is your build tool
RUN pip install --no-cache-dir uv

# copy metadata first for better layer caching
COPY pyproject.toml README.md ./

# copy source
COPY app /app/app

# install deps (incl. “.[dev]” extras so tests still work)
RUN uv pip install --system --no-cache -e .[dev]


############################
# 3️⃣  RUNTIME IMAGE
############################
FROM base
WORKDIR /app

# bring in pre-built site-packages + entrypoints
COPY --from=builder /usr/local /usr/local

# bring in source (handy for runtime templates / alembic, etc.)
COPY app /app/app
COPY run.py /app/run.py

EXPOSE 8000
ENV UVICORN_WORKERS=2

# Gunicorn isn’t needed; uvicorn with --workers is fine here
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
