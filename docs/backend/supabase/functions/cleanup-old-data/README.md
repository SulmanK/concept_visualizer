# cleanup-old-data Function

## Overview

The `cleanup-old-data` function is a scheduled Edge Function that automatically cleans up old data to manage storage costs and maintain application performance. It performs the following operations:

1. Identifies and updates "stuck" tasks (tasks in processing or pending state for too long)
2. Deletes concepts that are older than 30 days
3. Deletes color variations associated with deleted concepts
4. Deletes tasks associated with deleted concepts
5. Removes image files from storage buckets

## Implementation Details

### Architecture

The function is implemented in TypeScript and deployed as a Supabase Edge Function. It uses the Supabase client to interact with the database and storage buckets.

### File Structure

```
cleanup-old-data/
└── index.ts      # Main implementation
```

### Key Functions

| Function              | Description                                         |
| --------------------- | --------------------------------------------------- |
| `cleanupStuckTasks()` | Updates tasks stuck in processing or pending states |
| `deleteFromStorage()` | Deletes a file from a specified storage bucket      |
| `getTableName()`      | Gets the environment-specific table name (dev/prod) |

## Execution Flow

1. The function is triggered via HTTP POST request (typically by a scheduled cron job)
2. It first cleans up tasks stuck in processing or pending states
3. It then fetches concepts older than 30 days
4. For each old concept, it retrieves and deletes associated color variations
5. It deletes the old concepts from the database
6. It deletes the associated tasks
7. It removes the image files from the storage buckets
8. It returns a report of all deleted/updated items

## Configuration

### Environment Variables

| Variable                    | Description                | Default                |
| --------------------------- | -------------------------- | ---------------------- |
| `SUPABASE_URL`              | Supabase project URL       | (Required)             |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key           | (Required)             |
| `APP_ENVIRONMENT`           | Environment (dev/prod)     | "dev"                  |
| `STORAGE_BUCKET_CONCEPT`    | Concept images bucket name | "concept-images-{env}" |
| `STORAGE_BUCKET_PALETTE`    | Palette images bucket name | "palette-images-{env}" |

### Constants

| Constant                     | Value   | Description                                               |
| ---------------------------- | ------- | --------------------------------------------------------- |
| `PROCESSING_TIMEOUT_MINUTES` | 30      | Minutes after which a processing task is considered stuck |
| `PENDING_TIMEOUT_MINUTES`    | 30      | Minutes after which a pending task is considered stuck    |
| Data retention period        | 30 days | How long concepts are retained before cleanup             |

## Example Response

```json
{
  "message": "Cleanup completed successfully",
  "stuck_tasks_updated": 2,
  "old_concepts_deleted": 15,
  "old_variations_deleted": 105,
  "old_concept_files_deleted": 15,
  "old_variation_files_deleted": 105,
  "old_tasks_deleted": 15
}
```

## Testing

The function can be tested with the [test_cleanup_function.py](../../../../tests/supabase_edge_function/test_cleanup_function.py) script, which:

1. Creates test data with timestamps set in the past
2. Invokes the edge function
3. Verifies that the test data has been properly cleaned up

### Running Tests

```bash
# From the project root
cd backend
python -m tests.supabase_edge_function.test_cleanup_function --env dev --run-cleanup
```

## Deployment

```bash
# From the project root
cd backend/supabase
supabase functions deploy cleanup-old-data --project-ref your-project-ref
```

## Scheduling

This function is designed to be triggered on a regular schedule. This can be implemented using:

1. A cron job on a server that sends a POST request to the function URL
2. Supabase's scheduled functions feature (if available)
3. A third-party scheduler service like GitHub Actions, Zapier, or n8n
