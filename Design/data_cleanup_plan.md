# Data Cleanup Plan: Removing Old Concepts and Color Variations

## Problem Statement

We need to implement an automated process that removes concepts and their associated color variations that are 3 days or older from our Supabase database and storage buckets. This helps manage storage costs and keeps the database optimized.

## Solution Overview

We'll implement a Python-based Supabase Edge Function that:

1. Queries the database for concepts older than 3 days
2. Deletes associated color variations from the database
3. Deletes the concept records from the database
4. Removes associated files from storage buckets

## Database Schema

Based on the current schema:

```sql
-- Concepts table
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  session_id UUID REFERENCES sessions(id) NOT NULL,
  logo_description TEXT NOT NULL,
  theme_description TEXT NOT NULL,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT -- Full signed URL of the image
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT -- Full signed URL of the image
);
```

## Implementation Plan

### 1. Create a Supabase Edge Function

We'll set up a Python-based edge function:

```
/backend/functions/cleanup-old-data/
  ├── index.ts       # Entry point wrapper for the edge function
  └── handler.py     # Python implementation of the cleanup logic
```

### 2. Database Operations

The function will:

1. Query for concepts older than 3 days
2. Delete associated color variations (due to foreign key constraints)
3. Delete the concept records themselves

```python
# SQL query to get old concepts
sql_query = """
SELECT id, image_path 
FROM concepts 
WHERE created_at < NOW() - INTERVAL '3 days'
"""

# SQL query to get associated color variations
sql_variations_query = """
SELECT id, image_path 
FROM color_variations 
WHERE concept_id = ANY($1)
"""

# SQL to delete color variations
sql_delete_variations = """
DELETE FROM color_variations 
WHERE concept_id = ANY($1)
"""

# SQL to delete concepts
sql_delete_concepts = """
DELETE FROM concepts 
WHERE id = ANY($1)
"""
```

### 3. Storage Cleanup

After database records are deleted, we'll remove the associated files from storage:

1. Extract storage paths from image_path fields
2. Delete files from appropriate storage buckets

```python
# Delete concept images
for concept_path in concept_paths:
    # Parse session_id and file path
    supabase.storage.from_('concept-images').remove(concept_path)

# Delete color variation images
for variation_path in variation_paths:
    # Parse session_id and file path
    supabase.storage.from_('palette-images').remove(variation_path)
```

### 4. Scheduling

Deploy as a Supabase Edge Function that runs on a schedule:

- Set up a CRON trigger to run daily
- Log output for monitoring

## Error Handling and Monitoring

- Implement try/except blocks around critical operations
- Log errors and operation counts
- Create separate transactions for different steps to ensure partial completion if errors occur

## Implementation

### Edge Function Entry Point (index.ts)

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

const handler = async (_req: Request) => {
  try {
    // Run the Python script
    const command = new Deno.Command("python3", {
      args: ["handler.py"],
      stdout: "piped",
      stderr: "piped",
    });
    
    const process = command.spawn();
    const output = await process.output();
    const outStr = new TextDecoder().decode(output.stdout);
    const errStr = new TextDecoder().decode(output.stderr);
    
    if (errStr) {
      console.error("Error running cleanup script:", errStr);
      return new Response(JSON.stringify({ error: errStr }), {
        status: 500,
        headers: { "Content-Type": "application/json" }
      });
    }
    
    return new Response(JSON.stringify({ message: "Cleanup completed", details: outStr }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
  } catch (error) {
    console.error("Failed to run cleanup script:", error);
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
}

serve(handler);
```

### Python Handler (handler.py)

```python
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

# Supabase connection info
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
STORAGE_BUCKET_CONCEPT = "concept-images"
STORAGE_BUCKET_PALETTE = "palette-images"

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    logger.error("Missing Supabase credentials")
    raise ValueError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be provided")

# Helper function to make REST API calls to Supabase
def supabase_request(method: str, endpoint: str, data=None, params=None) -> dict:
    """Make a request to Supabase REST API."""
    url = f"{SUPABASE_URL}{endpoint}"
    headers = {
        "apikey": SUPABASE_SERVICE_ROLE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
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
    """Delete a file from Supabase storage."""
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
```

## Database Function Setup

We need to create stored procedures in Supabase to efficiently query and delete data:

```sql
-- Function to get concepts older than specified days
CREATE OR REPLACE FUNCTION get_old_concepts(days_threshold INT)
RETURNS TABLE (id UUID, image_path TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.image_path
    FROM concepts c
    WHERE c.created_at < NOW() - (days_threshold * INTERVAL '1 day');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get color variations for specific concepts
CREATE OR REPLACE FUNCTION get_variations_for_concepts(concept_ids UUID[])
RETURNS TABLE (id UUID, image_path TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT cv.id, cv.image_path
    FROM color_variations cv
    WHERE cv.concept_id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to delete color variations for specific concepts
CREATE OR REPLACE FUNCTION delete_variations_for_concepts(concept_ids UUID[])
RETURNS VOID AS $$
BEGIN
    DELETE FROM color_variations
    WHERE concept_id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to delete specified concepts
CREATE OR REPLACE FUNCTION delete_concepts(concept_ids UUID[])
RETURNS VOID AS $$
BEGIN
    DELETE FROM concepts
    WHERE id = ANY(concept_ids);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
```

## Deployment Steps

1. Create the SQL functions in Supabase
2. Create the edge function files:
   - `backend/supabase/functions/cleanup-old-data/index.ts`
   - `backend/supabase/functions/cleanup-old-data/handler.py`
3. Deploy the edge function:
   ```bash
   cd backend/edge-functions
   supabase functions deploy cleanup-old-data --no-verify-jwt
   ```
4. Set up environment variables:
   ```bash
   supabase secrets set MY_SUPABASE_URL=<your-supabase-url>
   supabase secrets set MY_SERVICE_ROLE_KEY=<your-service-role-key>
   ```
5. Schedule the function to run daily:
    GitHub Actions

    To ensure secure access to your Supabase Edge Function, you need to add your Supabase anon key as a GitHub secret:

    1. Go to your GitHub repository
    2. Click on "Settings" tab
    3. In the left sidebar, click on "Secrets and variables" > "Actions"
    4. Click on "New repository secret"
    5. Enter the following information:
    - Name: `SUPABASE_ANON_KEY`
    - Value: ``
    6. Click "Add secret"

    ## Understanding the Workflow

    The GitHub Actions workflow `.github/workflows/schedule-cleanup.yml` does the following:

    1. Runs at midnight UTC every day (`0 0 * * *`)
    2. Makes an HTTP POST request to your Supabase Edge Function
    3. Uses the Supabase anon key for authentication
    4. Logs the success or failure of the function call


## Testing the Implementation

Before scheduling the function, test it manually:

1. Insert test data that's older than 3 days:

```sql
-- Insert test data with a timestamp older than 3 days
INSERT INTO sessions (id, created_at)
VALUES (uuid_generate_v4(), NOW() - INTERVAL '4 days');

-- Get the session id
DO $$
DECLARE
    test_session_id UUID;
    test_concept_id UUID;
BEGIN
    SELECT id INTO test_session_id FROM sessions
    ORDER BY created_at ASC LIMIT 1;
    
    -- Insert a test concept
    INSERT INTO concepts (
        session_id, logo_description, theme_description, 
        image_path, image_url, created_at
    )
    VALUES (
        test_session_id, 'Test logo', 'Test theme',
        'test_path.png', 'test_url', NOW() - INTERVAL '4 days'
    )
    RETURNING id INTO test_concept_id;
    
    -- Insert a test color variation
    INSERT INTO color_variations (
        concept_id, palette_name, colors, description,
        image_path, image_url
    )
    VALUES (
        test_concept_id, 'Test palette', '["#FF0000", "#00FF00", "#0000FF"]',
        'Test description', 'test_variation_path.png', 'test_variation_url'
    );
END $$;
```

2. Call the `get_old_concepts` function to verify it's working:

```sql
SELECT * FROM get_old_concepts(3);
```

3. Manually invoke the edge function:

```bash
curl -i --request POST 'https://<your-project-ref>.supabase.co/functions/v1/cleanup-old-data' \
  --header 'Authorization: Bearer <your-anon-key>'
```

4. Verify that the test data has been deleted:

```sql
-- Check if test data is gone
SELECT COUNT(*) FROM concepts WHERE created_at < NOW() - INTERVAL '3 days';
SELECT COUNT(*) FROM color_variations WHERE concept_id NOT IN (SELECT id FROM concepts);
```

## Monitoring

To monitor the function's execution:

1. View the function logs in the Supabase dashboard
2. Set up alerts for function failures
3. Consider implementing a reporting mechanism that sends an email or notification with cleanup statistics

## Next Steps

After implementing this solution:

1. Monitor the logs to ensure proper execution
2. Consider implementing a notification system for cleanup operations
3. Create a manual trigger endpoint for on-demand cleanup
4. Add configurable cleanup timeframe (e.g., admin setting for retention period)

## Conclusion

This implementation will automatically clean up old concepts and their color variations from both the database and storage, helping to keep the application's storage footprint minimal and cost-effective. 