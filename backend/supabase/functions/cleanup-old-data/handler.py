#!/usr/bin/env python3
import os
import json
import logging
from typing import List, Dict, Any, Tuple
from datetime import datetime, timedelta
import requests

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cleanup-old-data")

# Supabase connection info - changed environment variable names to avoid SUPABASE_ prefix
MY_SUPABASE_URL = os.environ.get("MY_SUPABASE_URL")
MY_SERVICE_ROLE_KEY = os.environ.get("MY_SERVICE_ROLE_KEY")
STORAGE_BUCKET_CONCEPT = "concept-images"
STORAGE_BUCKET_PALETTE = "palette-images"

if not MY_SUPABASE_URL or not MY_SERVICE_ROLE_KEY:
    logger.error("Missing Supabase credentials")
    raise ValueError("MY_SUPABASE_URL and MY_SERVICE_ROLE_KEY must be provided")

# Helper function to make REST API calls to Supabase
def supabase_request(method: str, endpoint: str, data=None, params=None) -> dict:
    """Make a request to Supabase REST API.
    
    Args:
        method: HTTP method (GET, POST, DELETE, etc.)
        endpoint: API endpoint path
        data: Request body data
        params: Query parameters
        
    Returns:
        JSON response as dictionary
    """
    url = f"{MY_SUPABASE_URL}{endpoint}"
    headers = {
        "apikey": MY_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {MY_SERVICE_ROLE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    response = requests.request(
        method=method,
        url=url,
        headers=headers,
        json=data,
        params=params
    )
    
    if response.status_code >= 400:
        logger.error(f"Error {response.status_code}: {response.text}")
        response.raise_for_status()
    
    if response.content:
        return response.json()
    return {}

# Storage functions
def delete_from_storage(bucket: str, path: str) -> bool:
    """Delete a file from Supabase storage.
    
    Args:
        bucket: Storage bucket name
        path: Path to file within bucket
        
    Returns:
        True if deletion was successful, False otherwise
    """
    try:
        endpoint = f"/storage/v1/object/{bucket}/{path}"
        supabase_request("DELETE", endpoint)
        logger.info(f"Deleted from {bucket}: {path}")
        return True
    except Exception as e:
        logger.error(f"Failed to delete from {bucket}: {path}, Error: {str(e)}")
        return False

def main():
    """Main cleanup function."""
    try:
        # 1. Get concepts older than 3 days
        logger.info("Fetching concepts older than 3 days...")
        rpc_endpoint = "/rest/v1/rpc/get_old_concepts"
        old_concepts = supabase_request("POST", rpc_endpoint, data={
            "days_threshold": 3
        })
        
        if not old_concepts:
            logger.info("No old concepts found")
            return
        
        concept_ids = [concept["id"] for concept in old_concepts]
        concept_paths = [concept["image_path"] for concept in old_concepts]
        
        logger.info(f"Found {len(concept_ids)} concepts to delete")
        
        # 2. Get associated color variations
        logger.info("Fetching associated color variations...")
        rpc_endpoint = "/rest/v1/rpc/get_variations_for_concepts"
        variations = supabase_request("POST", rpc_endpoint, data={
            "concept_ids": concept_ids
        })
        
        variation_paths = [var["image_path"] for var in variations]
        logger.info(f"Found {len(variation_paths)} color variations to delete")
        
        # 3. Delete color variations from database
        logger.info("Deleting color variations from database...")
        rpc_endpoint = "/rest/v1/rpc/delete_variations_for_concepts"
        supabase_request("POST", rpc_endpoint, data={
            "concept_ids": concept_ids
        })
        
        # 4. Delete concepts from database
        logger.info("Deleting concepts from database...")
        rpc_endpoint = "/rest/v1/rpc/delete_concepts"
        supabase_request("POST", rpc_endpoint, data={
            "concept_ids": concept_ids
        })
        
        # 5. Delete files from storage
        deleted_concept_files = 0
        for path in concept_paths:
            if path and delete_from_storage(STORAGE_BUCKET_CONCEPT, path):
                deleted_concept_files += 1
                
        deleted_variation_files = 0
        for path in variation_paths:
            if path and delete_from_storage(STORAGE_BUCKET_PALETTE, path):
                deleted_variation_files += 1
        
        logger.info(f"Deleted {deleted_concept_files}/{len(concept_paths)} concept files")
        logger.info(f"Deleted {deleted_variation_files}/{len(variation_paths)} variation files")
        
        print(json.dumps({
            "deleted_concepts": len(concept_ids),
            "deleted_variations": len(variation_paths),
            "deleted_concept_files": deleted_concept_files,
            "deleted_variation_files": deleted_variation_files
        }))
        
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise

if __name__ == "__main__":
    main() 