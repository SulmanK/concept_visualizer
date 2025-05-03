"""Shim for Cloud Functions deployment.

This file re-exports the handle_pubsub function from the cloud_run.worker.main module
to allow Cloud Functions to find the entry point in the expected location.
"""

from cloud_run.worker.main import handle_pubsub  # noqa: F401
