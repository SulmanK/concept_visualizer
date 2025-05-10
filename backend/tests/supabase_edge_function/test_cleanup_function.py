#!/usr/bin/env python
"""Test script for the cleanup-old-data Edge Function.

This script inserts test data with timestamps that should trigger deletion
by the cleanup function (older than 30 days). After inserting the data,
it triggers the edge function and verifies the cleanup process works correctly.
"""

import argparse
import datetime
import io
import json
import logging
import os
import sys
import uuid
from datetime import timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests
from dotenv import load_dotenv
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("cleanup_test")

# No need to modify path, as we're inside the tests directory already
try:
    from app.core.config import settings
    from app.core.supabase.client import SupabaseClient
except ImportError:
    logger.error("Failed to import app modules. Make sure PYTHONPATH is set correctly.")
    sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test the cleanup-old-data Edge Function")
    parser.add_argument("--env", choices=["dev", "prod"], default="dev", help="Environment to test (dev or prod)")
    parser.add_argument("--days", type=int, default=31, help="Days ago to create the test data (default: 31)")
    parser.add_argument("--run-cleanup", action="store_true", help="Run the cleanup function after inserting test data")
    parser.add_argument("--cleanup-only", action="store_true", help="Only run the cleanup function, don't insert test data")
    parser.add_argument("--user-id", help="Existing user ID to use for test data (required for test data creation)")
    parser.add_argument("--skip-images", action="store_true", help="Skip creating test images in storage buckets")
    return parser.parse_args()


def create_supabase_client(environment: str) -> SupabaseClient:
    """Create a Supabase client for the specified environment."""
    if environment == "prod":
        url = os.environ.get("PROD_SUPABASE_URL", settings.SUPABASE_URL)
        key = os.environ.get("PROD_SUPABASE_SERVICE_ROLE_KEY", settings.SUPABASE_SERVICE_ROLE)
    else:
        url = os.environ.get("DEV_SUPABASE_URL", settings.SUPABASE_URL)
        key = os.environ.get("DEV_SUPABASE_SERVICE_ROLE_KEY", settings.SUPABASE_SERVICE_ROLE)

    return SupabaseClient(url=url, key=key)


def get_table_name(base_name: str, environment: str) -> str:
    """Get the environment-specific table name."""
    suffix = "_prod" if environment == "prod" else "_dev"
    return f"{base_name}{suffix}"


def get_storage_bucket_names(environment: str) -> Tuple[str, str]:
    """Get the storage bucket names based on environment.

    Args:
        environment: The environment (dev or prod)

    Returns:
        Tuple of (concept_bucket, palette_bucket)
    """
    if environment == "prod":
        concept_bucket = os.environ.get("PROD_STORAGE_BUCKET_CONCEPT", f"concept-images-{environment}")
        palette_bucket = os.environ.get("PROD_STORAGE_BUCKET_PALETTE", f"palette-images-{environment}")
    else:
        concept_bucket = os.environ.get("DEV_STORAGE_BUCKET_CONCEPT", f"concept-images-{environment}")
        palette_bucket = os.environ.get("DEV_STORAGE_BUCKET_PALETTE", f"palette-images-{environment}")

    return concept_bucket, palette_bucket


def create_dummy_image(width: int = 100, height: int = 100, color: str = "blue") -> bytes:
    """Create a simple colored dummy image.

    Args:
        width: Image width in pixels
        height: Image height in pixels
        color: Color name for the image

    Returns:
        Image bytes
    """
    # Create a colored image
    img = Image.new("RGB", (width, height), color)

    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)

    return img_bytes.getvalue()


def upload_dummy_image(supabase_client: SupabaseClient, bucket_name: str, path: str) -> bool:
    """Upload a dummy image to Supabase storage.

    Args:
        supabase_client: The Supabase client
        bucket_name: Storage bucket name
        path: Path within the bucket

    Returns:
        True if successful, False otherwise
    """
    try:
        # Create dummy image
        image_bytes = create_dummy_image()

        # Upload to Supabase
        response = supabase_client.client.storage.from_(bucket_name).upload(path, image_bytes, {"content-type": "image/png"})

        if hasattr(response, "error") and response.error:
            logger.error(f"Error uploading image to {bucket_name}/{path}: {response.error}")
            return False

        logger.info(f"Uploaded dummy image to {bucket_name}/{path}")
        return True
    except Exception as e:
        logger.error(f"Error uploading image: {e}")
        return False


def create_test_data(supabase_client: SupabaseClient, environment: str, days_ago: int, user_id: str) -> Dict[str, Optional[str]]:
    """Create test data with an old timestamp."""
    # Generate IDs
    task_id = str(uuid.uuid4())
    concept_id = str(uuid.uuid4())

    # Create tables names
    tasks_table = get_table_name("tasks", environment)
    concepts_table = get_table_name("concepts", environment)

    # Get bucket names
    concept_bucket, palette_bucket = get_storage_bucket_names(environment)

    # Set created_at timestamp to days_ago
    created_at = (datetime.datetime.now() - timedelta(days=days_ago)).isoformat()

    # Create image paths
    concept_image_path = f"{user_id}/test_concept_{uuid.uuid4().hex[:8]}.png"
    palette_image_path = f"{user_id}/test_palette_{uuid.uuid4().hex[:8]}.png"

    # Insert task
    logger.info(f"Inserting test task with ID {task_id} created {days_ago} days ago")
    task_data = {
        "id": task_id,
        "user_id": user_id,
        "status": "completed",
        "type": "generate_concept",
        "created_at": created_at,
        "updated_at": created_at,
        "result_id": concept_id,
    }

    response = supabase_client.client.table(tasks_table).insert(task_data).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Error inserting task: {response.error}")

    # Insert concept
    logger.info(f"Inserting test concept with ID {concept_id} created {days_ago} days ago")
    concept_data = {
        "id": concept_id,
        "user_id": user_id,
        "logo_description": "Test logo for cleanup testing",
        "theme_description": "Test theme for cleanup testing",
        "created_at": created_at,
        "updated_at": created_at if "updated_at" in get_table_columns(supabase_client, concepts_table) else None,
        "image_path": concept_image_path,
        "is_anonymous": True,
    }

    # Remove any None values from the data
    concept_data = {k: v for k, v in concept_data.items() if v is not None}

    response = supabase_client.client.table(concepts_table).insert(concept_data).execute()
    if hasattr(response, "error") and response.error:
        raise Exception(f"Error inserting concept: {response.error}")

    # Create a color variation record if the table exists
    variations_table = get_table_name("color_variations", environment)
    variation_id = None

    try:
        # Check if the variations table exists
        if get_table_columns(supabase_client, variations_table):
            variation_id = str(uuid.uuid4())
            logger.info(f"Inserting test color variation with ID {variation_id}")
            variation_data = {
                "id": variation_id,
                "concept_id": concept_id,
                "palette_name": "Test Palette",
                "colors": json.dumps(["#FF5733", "#33FF57", "#3357FF"]),  # JSON array of hex colors
                "image_path": palette_image_path,
            }

            response = supabase_client.client.table(variations_table).insert(variation_data).execute()
            if hasattr(response, "error") and response.error:
                logger.warning(f"Error inserting color variation: {response.error}")
                variation_id = None  # Reset if failed
    except Exception as e:
        logger.warning(f"Skipping color variation creation: {e}")

    # Upload dummy images to storage buckets
    try:
        # Upload concept image
        upload_dummy_image(supabase_client, concept_bucket, concept_image_path)

        # Upload palette image if we have a variation
        if variation_id:
            upload_dummy_image(supabase_client, palette_bucket, palette_image_path)
    except Exception as e:
        logger.warning(f"Error uploading dummy images: {e}")

    return {
        "user_id": user_id,
        "task_id": task_id,
        "concept_id": concept_id,
        "variation_id": variation_id,
        "concept_image_path": concept_image_path,
        "palette_image_path": palette_image_path if variation_id else None,
    }


def get_table_columns(supabase_client: SupabaseClient, table_name: str) -> List[str]:
    """Get the column names for a table.

    Args:
        supabase_client: The Supabase client
        table_name: The name of the table

    Returns:
        List of column names
    """
    try:
        # Try to get a single row to see column names
        response = supabase_client.client.table(table_name).select("*").limit(1).execute()
        if response.data and len(response.data) > 0:
            return list(response.data[0].keys())
        return []
    except Exception:
        # If that fails, return an empty list
        return []


def run_cleanup_function(environment: str) -> Dict[str, Any]:
    """Run the cleanup edge function and return the response."""
    # Get the appropriate URL and key for the environment
    if environment == "prod":
        url = "https://pstdcfittpjhxzynbdbu.supabase.co/functions/v1/cleanup-old-data"
        key = os.environ.get("PROD_SUPABASE_ANON_KEY")
    else:
        url = "https://ksuxhgigxymqoqmxekic.supabase.co/functions/v1/cleanup-old-data"
        key = os.environ.get("DEV_SUPABASE_ANON_KEY")

    if not key:
        raise ValueError(f"No API key found for {environment} environment")

    logger.info(f"Running cleanup function for {environment} environment")
    response = requests.post(
        url,
        headers={"Authorization": f"Bearer {key}"},
    )

    try:
        response.raise_for_status()
        result: Dict[str, Any] = response.json()
        return result
    except Exception as e:
        logger.error(f"Error running cleanup function: {e}")
        logger.error(f"Response: {response.text}")
        raise


def verify_deletion(supabase_client: SupabaseClient, environment: str, ids: Dict[str, Optional[str]]) -> bool:
    """Verify that the test data was deleted."""
    tasks_table = get_table_name("tasks", environment)
    concepts_table = get_table_name("concepts", environment)
    variations_table = get_table_name("color_variations", environment)

    # Check if concept exists
    response = supabase_client.client.table(concepts_table).select("id").eq("id", ids["concept_id"]).execute()
    concept_exists = response.data and len(response.data) > 0

    # Check if task exists
    response = supabase_client.client.table(tasks_table).select("id").eq("id", ids["task_id"]).execute()
    task_exists = response.data and len(response.data) > 0

    # Check if variation exists (if we created one)
    variation_exists = False
    if ids.get("variation_id"):
        response = supabase_client.client.table(variations_table).select("id").eq("id", ids["variation_id"]).execute()
        variation_exists = response.data and len(response.data) > 0

    # Check storage files
    concept_bucket, palette_bucket = get_storage_bucket_names(environment)

    # Check if concept image exists
    concept_image_exists = False
    if ids.get("concept_image_path"):
        try:
            # Try to get image URL which will fail if it doesn't exist
            supabase_client.client.storage.from_(concept_bucket).get_public_url(ids["concept_image_path"])
            concept_image_exists = True
        except Exception:
            concept_image_exists = False

    # Check if palette image exists
    palette_image_exists = False
    if ids.get("palette_image_path"):
        try:
            # Try to get image URL which will fail if it doesn't exist
            supabase_client.client.storage.from_(palette_bucket).get_public_url(ids["palette_image_path"])
            palette_image_exists = True
        except Exception:
            palette_image_exists = False

    if concept_exists or task_exists or variation_exists or concept_image_exists or palette_image_exists:
        logger.warning("Test data was not fully deleted:")
        logger.warning(f"  - Concept exists: {concept_exists}")
        logger.warning(f"  - Task exists: {task_exists}")
        logger.warning(f"  - Variation exists: {variation_exists}")
        logger.warning(f"  - Concept image exists: {concept_image_exists}")
        logger.warning(f"  - Palette image exists: {palette_image_exists}")
        return False
    else:
        logger.info("All test data was successfully deleted")
        return True


def main() -> None:
    """Main function."""
    # Load environment variables
    load_dotenv()

    # Parse arguments
    args = parse_args()
    environment = args.env
    days_ago = args.days

    logger.info(f"Testing cleanup function in {environment} environment")

    # Create Supabase client
    supabase_client = create_supabase_client(environment)

    ids = None
    if not args.cleanup_only:
        # Check if user ID is provided for test data creation
        if not args.user_id:
            logger.error("User ID is required for creating test data. Use --user-id parameter.")
            sys.exit(1)

        # Create test data
        if args.skip_images:
            logger.info("Skipping image creation in storage buckets (--skip-images flag used)")
            # Override the upload_dummy_image function to do nothing
            global upload_dummy_image
            original_upload_function = upload_dummy_image

            # Define a dummy function that always returns success
            def dummy_upload(*args: Any, **kwargs: Any) -> bool:
                return True

            # Replace the upload function temporarily
            upload_dummy_image = dummy_upload

            # Create test data
            ids = create_test_data(supabase_client, environment, days_ago, args.user_id)

            # Restore the original function
            upload_dummy_image = original_upload_function
        else:
            # Create test data with images
            ids = create_test_data(supabase_client, environment, days_ago, args.user_id)

        logger.info(f"Created test data: {json.dumps(ids, indent=2)}")

    if args.run_cleanup or args.cleanup_only:
        # Run cleanup function
        result = run_cleanup_function(environment)
        logger.info(f"Cleanup function result: {json.dumps(result, indent=2)}")

        # Verify deletion if we created test data
        if ids:
            success = verify_deletion(supabase_client, environment, ids)
            if success:
                logger.info("✅ Cleanup function is working correctly")
            else:
                logger.error("❌ Cleanup function failed to delete test data")
    else:
        logger.info("Test data created but cleanup function was not run. " "Run with --run-cleanup to test the function.")


if __name__ == "__main__":
    main()
