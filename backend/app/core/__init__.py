"""Core application module.

This module contains core application components including configuration,
exceptions, middleware, and factory functions.
"""

from app.core.config import settings

from .supabase import SupabaseClient, get_supabase_client

__all__ = ["settings"]
