"""Constants used throughout the application.

This module defines constants used throughout the application to
avoid hardcoding values and ensure consistency.
"""

from .config import settings

# Task Statuses
TASK_STATUS_PENDING = "pending"
TASK_STATUS_PROCESSING = "processing"
TASK_STATUS_COMPLETED = "completed"
TASK_STATUS_FAILED = "failed"

# Task Types
TASK_TYPE_GENERATION = "concept_generation"
TASK_TYPE_REFINEMENT = "concept_refinement"

# Bucket Names
BUCKET_NAME_CONCEPTS = settings.STORAGE_BUCKET_CONCEPT
BUCKET_NAME_PALETTES = settings.STORAGE_BUCKET_PALETTE

# Rate Limit Keys/Strings were removed - these should be defined in api/middleware/rate_limit_apply.py
