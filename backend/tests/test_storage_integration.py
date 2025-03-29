#!/usr/bin/env python
"""Test script for Supabase storage integration.

This script tests the Supabase storage integration by:
1. Uploading a test image to Supabase Storage
2. Retrieving its public URL
3. Applying a color palette to the image and storing the result

Run this script with: uv run scripts/test_storage_integration.py
"""

import asyncio
import sys
import uuid
import logging
from pathlib import Path

# Add parent directory to path so we can import from backend
sys.path.append(str(Path(__file__).resolve().parent.parent))

from backend.app.core.supabase import SupabaseClient
from backend.app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("storage_test")


async def test_storage_integration():
    """Test Supabase storage integration."""
    logger.info("Starting Supabase storage integration test")
    
    # Create a Supabase client
    supabase_client = SupabaseClient(
        url=settings.SUPABASE_URL,
        key=settings.SUPABASE_KEY
    )
    
    # Generate a test session ID
    session_id = str(uuid.uuid4())
    logger.info(f"Using test session ID: {session_id}")
    
    # 1. Test uploading an image from a URL
    test_image_url = "https://picsum.photos/512/512"  # Random image from Lorem Picsum
    logger.info(f"Uploading image from URL: {test_image_url}")
    
    try:
        storage_path = await supabase_client.upload_image_from_url(
            test_image_url,
            "concept-images",
            session_id
        )
        
        if not storage_path:
            logger.error("Failed to upload image")
            return
            
        logger.info(f"Successfully uploaded image to path: {storage_path}")
        
        # 2. Get the public URL for the image
        logger.info("Getting public URL for the image")
        public_url = supabase_client.get_image_url(storage_path, "concept-images")
        
        if not public_url:
            logger.error("Failed to get public URL")
            return
            
        logger.info(f"Public URL for image: {public_url}")
        logger.info("Verify this URL works by opening it in a browser")
        
        # 3. Test applying a color palette
        logger.info("Testing color palette application")
        palette_colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3"]
        
        palette_path = await supabase_client.apply_color_palette(
            storage_path,
            palette_colors,
            session_id
        )
        
        if not palette_path:
            logger.error("Failed to apply color palette")
            return
            
        logger.info(f"Successfully applied palette to image: {palette_path}")
        
        # 4. Get the public URL for the palette variation
        palette_url = supabase_client.get_image_url(palette_path, "palette-images")
        
        if not palette_url:
            logger.error("Failed to get palette variation URL")
            return
            
        logger.info(f"Public URL for palette variation: {palette_url}")
        logger.info("Verify this URL works by opening it in a browser")
        
        # Test succeeded
        logger.info("Storage integration test completed successfully!")
        logger.info(f"Session images can be found in {session_id}/ folders in both buckets")
        
    except Exception as e:
        logger.error(f"Error during test: {e}")
        return


if __name__ == "__main__":
    logger.info("Running Supabase storage integration test")
    asyncio.run(test_storage_integration()) 