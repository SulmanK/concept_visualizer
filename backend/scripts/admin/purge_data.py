#!/usr/bin/env python
"""Data purging utility for the Concept Visualizer backend.

This script provides functionality to purge data from Supabase
for a specific user ID or all data in the system.
"""

import argparse
import asyncio
import logging
from typing import Optional

from app.core.exceptions import DatabaseError, StorageError
from app.core.supabase.client import get_supabase_client
from app.core.supabase.concept_storage import ConceptStorage
from app.core.supabase.image_storage import ImageStorage
from app.utils.security.mask import mask_id

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("purge_data")


async def purge_data(user_id: Optional[str] = None) -> bool:
    """Purge all data for a user or all data in the system.

    WARNING: This is a destructive operation! Use with caution.

    Args:
        user_id: Optional user ID to purge only data for this user

    Returns:
        True if successful, False otherwise
    """
    # Get client and storage services
    supabase_client = get_supabase_client()
    concept_storage = ConceptStorage(supabase_client)
    image_storage = ImageStorage(supabase_client)

    try:
        if user_id:
            logger.warning(f"Purging all data for user ID {mask_id(user_id)}")

            try:
                # Delete storage objects first (no DB constraints)
                image_storage.delete_all_storage_objects("concepts", user_id)
            except Exception as e:
                logger.error(f"Error deleting storage objects: {str(e)}")
                raise StorageError(
                    message=f"Failed to delete storage objects for user: {str(e)}",
                    operation="delete_all",
                    bucket="concepts",
                    path=user_id,
                )

            try:
                # Delete concepts (and color_variations via cascading delete)
                concept_storage.delete_all_concepts(user_id)
            except Exception as e:
                logger.error(f"Error deleting concepts: {str(e)}")
                raise DatabaseError(
                    message=f"Failed to delete concepts: {str(e)}",
                    operation="delete",
                    table="concepts",
                )

            # Session will remain unless explicitly deleted
            logger.info(f"Successfully purged all data for user ID {mask_id(user_id)}")
        else:
            logger.warning("PURGING ALL DATA FROM THE SYSTEM!")

            try:
                # Delete all storage objects
                image_storage.delete_all_storage_objects("concepts")
            except Exception as e:
                logger.error(f"Error deleting all storage objects: {str(e)}")
                raise StorageError(
                    message=f"Failed to delete all storage objects: {str(e)}",
                    operation="delete_all",
                    bucket="concepts",
                )

            try:
                # Delete all concepts (and color_variations via cascading delete)
                supabase_client.client.table("concepts").delete().execute()
            except Exception as e:
                logger.error(f"Error deleting all concepts: {str(e)}")
                raise DatabaseError(
                    message=f"Failed to delete all concepts: {str(e)}",
                    operation="delete",
                    table="concepts",
                )

            logger.warning("Successfully purged ALL data from the system")

        return True
    except (DatabaseError, StorageError):
        # Re-raise these specific exceptions
        raise
    except Exception as e:
        logger.error(f"Unexpected error purging data: {str(e)}")
        raise DatabaseError(
            message=f"Unexpected error during data purge: {str(e)}",
            details={"user_id": mask_id(user_id) if user_id else "all_users"},
        )


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Purge data from Supabase storage and database")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--user-id", help="User ID to purge data for")
    group.add_argument(
        "--all",
        action="store_true",
        help="Purge ALL data from the system (use with extreme caution!)",
    )
    return parser.parse_args()


async def main() -> int:
    """Main entry point for the script."""
    args = parse_args()

    try:
        if args.all:
            if input("Are you SURE you want to delete ALL data? This cannot be undone! Type 'YES' to confirm: ") == "YES":
                await purge_data(None)
                logger.info("All data has been purged from the system")
            else:
                logger.info("Operation cancelled")
        else:
            # Purge data for a specific user
            user_id = args.user_id
            if input(f"Are you sure you want to delete all data for user {mask_id(user_id)}? Type 'YES' to confirm: ") == "YES":
                await purge_data(user_id)
                logger.info(f"All data for user {mask_id(user_id)} has been purged")
            else:
                logger.info("Operation cancelled")
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
