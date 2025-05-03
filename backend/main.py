"""Main entry point for Cloud Function deployment.

This file imports and re-exports the handle_pubsub function from the
cloud_run/worker/main.py file so that the Cloud Function deployment can
find it in the expected location.
"""

# Import and re-export the handler function
from cloud_run.worker.main import handle_pubsub

# Define what symbols this module exports
__all__ = ["handle_pubsub"]
