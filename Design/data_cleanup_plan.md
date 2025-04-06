# Data Cleanup Plan: Removing Old Concepts and Color Variations

## Problem Statement

We need to implement an automated process that removes concepts and their associated color variations that are 3 days or older from our Supabase database and storage buckets. This helps manage storage costs and keeps the database optimized.

## Solution Overview

We'll implement a TypeScript-based Supabase Edge Function that:

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

We'll set up a TypeScript-based edge function:

```
/backend/supabase/functions/cleanup-old-data/
  └── index.ts       # TypeScript implementation of the cleanup logic
```

### 2. Database Operations

The function will:

1. Query for concepts older than 3 days
2. Delete associated color variations (due to foreign key constraints)
3. Delete the concept records themselves

We'll use database functions created in SQL:

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

### 3. Storage Cleanup

After database records are deleted, we'll remove the associated files from storage:

1. Extract storage paths from image_path fields
2. Delete files from appropriate storage buckets

```typescript
// Delete concept images
let deletedConceptFiles = 0;
for (const path of conceptPaths) {
  if (path && await deleteFromStorage(STORAGE_BUCKET_CONCEPT, path)) {
    deletedConceptFiles++;
  }
}

// Delete variation images
let deletedVariationFiles = 0;
for (const path of variationPaths) {
  if (path && await deleteFromStorage(STORAGE_BUCKET_PALETTE, path)) {
    deletedVariationFiles++;
  }
}
```

### 4. Scheduling

Deploy as a Supabase Edge Function and use GitHub Actions for scheduling:

- Set up a GitHub Actions workflow with a CRON trigger to run daily
- Log output for monitoring

## Error Handling and Monitoring

- Implement try/catch blocks around critical operations
- Log errors and operation counts
- Create separate sections for different operations to ensure proper error handling

## Implementation

### Edge Function (index.ts)

```typescript
import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from "https://esm.sh/@supabase/supabase-js@2"

// Get environment variables
const supabaseUrl = Deno.env.get('MY_SUPABASE_URL') || '';
const supabaseKey = Deno.env.get('MY_SERVICE_ROLE_KEY') || '';

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

// Storage bucket names from environment variables
const STORAGE_BUCKET_CONCEPT = Deno.env.get('STORAGE_BUCKET_CONCEPT') || '';
const STORAGE_BUCKET_PALETTE = Deno.env.get('STORAGE_BUCKET_PALETTE') || '';

// Function to delete a file from storage
async function deleteFromStorage(bucketName: string, path: string): Promise<boolean> {
  try {
    const { error } = await supabase
      .storage
      .from(bucketName)
      .remove([path]);
    
    if (error) {
      console.error(`Error deleting ${path} from ${bucketName}:`, error.message);
      return false;
    }
    
    console.log(`Deleted ${path} from ${bucketName}`);
    return true;
  } catch (err) {
    console.error(`Failed to delete ${path} from ${bucketName}:`, err);
    return false;
  }
}

serve(async (req) => {
  try {
    console.log("Starting data cleanup process");
    console.log(`Using buckets: ${STORAGE_BUCKET_CONCEPT} and ${STORAGE_BUCKET_PALETTE}`);
    
    // 1. Get concepts older than 3 days
    console.log("Fetching concepts older than 3 days...");
    const { data: oldConcepts, error: conceptsError } = await supabase
      .rpc('get_old_concepts', { days_threshold: 3 });
    
    if (conceptsError) {
      throw new Error(`Error fetching old concepts: ${conceptsError.message}`);
    }
    
    if (!oldConcepts || oldConcepts.length === 0) {
      console.log("No old concepts found");
      return new Response(JSON.stringify({ 
        message: "No old concepts to clean up" 
      }), {
        status: 200,
        headers: { "Content-Type": "application/json" }
      });
    }
    
    const conceptIds = oldConcepts.map(c => c.id);
    const conceptPaths = oldConcepts.map(c => c.image_path).filter(Boolean);
    
    console.log(`Found ${conceptIds.length} concepts to delete`);
    
    // 2. Get variations for those concepts
    console.log("Fetching associated color variations...");
    const { data: variations, error: variationsError } = await supabase
      .rpc('get_variations_for_concepts', { concept_ids: conceptIds });
    
    if (variationsError) {
      throw new Error(`Error fetching variations: ${variationsError.message}`);
    }
    
    const variationPaths = variations ? variations.map(v => v.image_path).filter(Boolean) : [];
    console.log(`Found ${variationPaths.length} color variations to delete`);
    
    // 3. Delete variations from database
    console.log("Deleting color variations from database...");
    const { error: deleteVariationsError } = await supabase
      .rpc('delete_variations_for_concepts', { concept_ids: conceptIds });
    
    if (deleteVariationsError) {
      throw new Error(`Error deleting variations: ${deleteVariationsError.message}`);
    }
    
    // 4. Delete concepts from database
    console.log("Deleting concepts from database...");
    const { error: deleteConceptsError } = await supabase
      .rpc('delete_concepts', { concept_ids: conceptIds });
    
    if (deleteConceptsError) {
      throw new Error(`Error deleting concepts: ${deleteConceptsError.message}`);
    }
    
    // 5. Delete files from storage
    console.log("Deleting files from storage...");
    
    // Delete concept images
    let deletedConceptFiles = 0;
    for (const path of conceptPaths) {
      if (path && await deleteFromStorage(STORAGE_BUCKET_CONCEPT, path)) {
        deletedConceptFiles++;
      }
    }
    
    // Delete variation images
    let deletedVariationFiles = 0;
    for (const path of variationPaths) {
      if (path && await deleteFromStorage(STORAGE_BUCKET_PALETTE, path)) {
        deletedVariationFiles++;
      }
    }
    
    console.log(`Deleted ${deletedConceptFiles}/${conceptPaths.length} concept files`);
    console.log(`Deleted ${deletedVariationFiles}/${variationPaths.length} variation files`);
    
    // Return success response
    return new Response(JSON.stringify({
      message: "Cleanup completed successfully",
      deleted_concepts: conceptIds.length,
      deleted_variations: variationPaths.length,
      deleted_concept_files: deletedConceptFiles,
      deleted_variation_files: deletedVariationFiles
    }), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    });
    
  } catch (error) {
    console.error("Error during cleanup:", error);
    
    return new Response(JSON.stringify({ 
      error: error instanceof Error ? error.message : "Unknown error during cleanup" 
    }), {
      status: 500,
      headers: { "Content-Type": "application/json" }
    });
  }
});
```

## GitHub Actions Workflow for Scheduling (.github/workflows/schedule-cleanup.yml)

```yaml
name: Schedule Data Cleanup

on:
  schedule:
    # Run at midnight every day (UTC)
    - cron: '0 0 * * *'
  
  # Allow manual triggering for testing
  workflow_dispatch:

jobs:
  call-cleanup-function:
    runs-on: ubuntu-latest
    
    steps:
      - name: Call Cleanup Edge Function
        run: |
          curl -L -X POST 'https://pstdcfittpjhxzynbdbu.supabase.co/functions/v1/cleanup-old-data' \
            -H 'Authorization: Bearer ${{ secrets.SUPABASE_ANON_KEY }}' \
            -H 'Content-Type: application/json'
      
      - name: Log completion
        if: ${{ success() }}
        run: echo "Data cleanup function executed successfully"
      
      - name: Log failure
        if: ${{ failure() }}
        run: echo "Failed to execute data cleanup function"
```

## Deployment Steps

1. Create the SQL functions in Supabase
2. Create the edge function file:
   - `backend/supabase/functions/cleanup-old-data/index.ts`
3. Deploy the edge function:
   ```bash
   cd backend
   supabase functions deploy cleanup-old-data --project-ref pstdcfittpjhxzynbdbu --no-verify-jwt
   ```
4. Set up environment variables:
   ```bash
   supabase secrets set MY_SUPABASE_URL=<your-supabase-url>
   supabase secrets set MY_SERVICE_ROLE_KEY=<your-service-role-key>
   supabase secrets set STORAGE_BUCKET_CONCEPT=<your-concept-bucket>
   supabase secrets set STORAGE_BUCKET_PALETTE=<your-palette-bucket>
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
2. Review GitHub Actions execution logs
3. Consider implementing a notification system for cleanup operations

## Next Steps

After implementing this solution:

1. Monitor the logs to ensure proper execution
2. Consider implementing a notification system for cleanup operations
3. Create a manual trigger endpoint for on-demand cleanup
4. Add configurable cleanup timeframe (e.g., admin setting for retention period)

## Conclusion

This implementation will automatically clean up old concepts and their color variations from both the database and storage, helping to keep the application's storage footprint minimal and cost-effective. 