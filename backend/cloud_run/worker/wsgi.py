"""WSGI app for Cloud Run to handle health checks properly."""

import logging
import os
import sys

from flask import Flask

# Ensure the app module can be imported
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("concept-worker-wsgi")

# Create Flask app
app = Flask(__name__)


@app.route("/", methods=["GET"])
def health_check() -> tuple[dict[str, str], int]:
    """Health check endpoint for Cloud Run."""
    logger.info("Health check request received")
    return {"status": "healthy", "service": "concept-worker"}, 200


@app.route("/_ah/warmup", methods=["GET"])
def warmup() -> tuple[dict[str, str], int]:
    """Warmup endpoint for Cloud Run."""
    logger.info("Warmup request received")
    return {"status": "warmed_up"}, 200


if __name__ == "__main__":
    # Get port from environment variable (set by Cloud Run)
    PORT = int(os.getenv("PORT", "8080"))
    logger.info(f"Starting WSGI server on port {PORT}")
    app.run(host="0.0.0.0", port=PORT)
