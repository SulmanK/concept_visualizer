# cleanup-old-data Implementation Details

This document provides a detailed explanation of the code in the `cleanup-old-data` Edge Function.

## Code Structure

The function is structured as follows:

1. **Imports and Configuration**: Setting up dependencies and environment variables
2. **Utility Functions**: Helper functions for table names and storage operations
3. **Task Cleanup Logic**: Function to handle stuck tasks
4. **Main Handler**: The main function that handles the HTTP request and orchestrates the cleanup process

## Imports and Configuration

```typescript
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import {
  createClient,
  SupabaseClient,
} from "https://esm.sh/@supabase/supabase-js@2.39.8";

// Environment Variables
const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const appEnvironment = Deno.env.get("APP_ENVIRONMENT") ?? "dev";

// Storage bucket names
const STORAGE_BUCKET_CONCEPT =
  Deno.env.get("STORAGE_BUCKET_CONCEPT") || `concept-images-${appEnvironment}`;
const STORAGE_BUCKET_PALETTE =
  Deno.env.get("STORAGE_BUCKET_PALETTE") || `palette-images-${appEnvironment}`;

// Task status constants
const TASK_STATUS = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
  CANCELED: "canceled",
};

// Create Supabase admin client
const supabaseAdmin: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceRoleKey,
);
```

## Utility Functions

### Table Name Helper

This function ensures that the correct environment-specific table names are used:

```typescript
function getTableName(
  baseName: "tasks" | "concepts" | "color_variations",
): string {
  const suffix = appEnvironment === "prod" ? "_prod" : "_dev";
  if (baseName === "tasks") return `tasks${suffix}`;
  if (baseName === "concepts") return `concepts${suffix}`;
  if (baseName === "color_variations") return `color_variations${suffix}`;
  throw new Error(`Invalid base table name: ${baseName}`);
}
```

### Storage File Deletion

This function deletes a file from a storage bucket:

```typescript
async function deleteFromStorage(
  bucketName: string,
  path: string,
): Promise<boolean> {
  try {
    const { error } = await supabaseAdmin.storage
      .from(bucketName)
      .remove([path]);
    if (error) {
      console.error(
        `Error deleting ${path} from ${bucketName}:`,
        error.message,
      );
      return false;
    }
    console.log(`Deleted ${path} from ${bucketName}`);
    return true;
  } catch (err) {
    console.error(`Failed to delete ${path} from ${bucketName}:`, err);
    return false;
  }
}
```

## Task Cleanup Logic

The `cleanupStuckTasks` function handles tasks that have been stuck in processing or pending states for too long:

```typescript
async function cleanupStuckTasks(
  processingTimeoutMinutes: number,
  pendingTimeoutMinutes: number,
): Promise<number> {
  const now = new Date();
  // Calculate cutoff timestamps
  const processingCutoff = new Date(
    now.getTime() - processingTimeoutMinutes * 60 * 1000,
  ).toISOString();
  const pendingCutoff = new Date(
    now.getTime() - pendingTimeoutMinutes * 60 * 1000,
  ).toISOString();
  let stuckTasksUpdated = 0;
  const tasksTable = getTableName("tasks");

  // Handle stuck processing tasks
  console.log(
    `Looking for tasks stuck in processing older than ${processingCutoff}...`,
  );
  const { data: stuckProcessingTasks, error: processingError } =
    await supabaseAdmin
      .from(tasksTable)
      .select("id")
      .eq("status", TASK_STATUS.PROCESSING)
      .lt("updated_at", processingCutoff);

  if (
    !processingError &&
    stuckProcessingTasks &&
    stuckProcessingTasks.length > 0
  ) {
    // Update tasks stuck in processing
    for (const task of stuckProcessingTasks) {
      const { error: updateError } = await supabaseAdmin
        .from(tasksTable)
        .update({
          status: TASK_STATUS.FAILED,
          error_message: `Task timed out after being in processing for over ${processingTimeoutMinutes} minutes.`,
          updated_at: new Date().toISOString(),
        })
        .eq("id", task.id);

      if (!updateError) {
        stuckTasksUpdated++;
      }
    }
  }

  // Handle stuck pending tasks (similar logic, using created_at instead)
  // ...

  return stuckTasksUpdated;
}
```

## Main Handler Logic

The main function handles the HTTP request and orchestrates the entire cleanup process:

```typescript
serve(async (req: Request) => {
  // Ensure POST method
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    console.log("Starting data cleanup process...");

    // 1. Clean up stuck tasks
    const PROCESSING_TIMEOUT_MINUTES = 30;
    const PENDING_TIMEOUT_MINUTES = 30;
    const stuckTasksCount = await cleanupStuckTasks(
      PROCESSING_TIMEOUT_MINUTES,
      PENDING_TIMEOUT_MINUTES,
    );

    // 2. Get concepts older than 30 days
    const conceptsTable = getTableName("concepts");
    const { data: oldConcepts, error: conceptsError } = await supabaseAdmin
      .from(conceptsTable)
      .select("id, image_path")
      .lt(
        "created_at",
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      );

    if (conceptsError) {
      throw new Error(`Error fetching old concepts: ${conceptsError.message}`);
    }

    // Initialize counters
    let deletedConceptsCount = 0;
    let deletedVariationsCount = 0;
    let deletedConceptFilesCount = 0;
    let deletedVariationFilesCount = 0;
    let deletedTasksCount = 0;

    if (oldConcepts && oldConcepts.length > 0) {
      deletedConceptsCount = oldConcepts.length;
      const conceptIds = oldConcepts.map((c) => c.id);
      const conceptPaths = oldConcepts
        .map((c) => c.image_path)
        .filter(Boolean) as string[];

      // 3. Get variations for those concepts
      const variationsTable = getTableName("color_variations");
      const { data: variations, error: variationsError } = await supabaseAdmin
        .from(variationsTable)
        .select("id, image_path")
        .in("concept_id", conceptIds);

      // Process variations
      const variationPaths = variations
        ? (variations.map((v) => v.image_path).filter(Boolean) as string[])
        : [];
      deletedVariationsCount = variationPaths.length;

      // 4. Delete variations from database
      // 5. Delete concepts from database
      // 5.5 Delete associated tasks
      // 6. Delete files from storage
      // ... (implementation details)
    }

    // Return success response with stats
    return new Response(
      JSON.stringify({
        message: "Cleanup completed successfully",
        stuck_tasks_updated: stuckTasksCount,
        old_concepts_deleted: deletedConceptsCount,
        old_variations_deleted: deletedVariationsCount,
        old_concept_files_deleted: deletedConceptFilesCount,
        old_variation_files_deleted: deletedVariationFilesCount,
        old_tasks_deleted: deletedTasksCount || 0,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      },
    );
  } catch (error) {
    // Handle errors
    console.error("Error during cleanup:", error);
    return new Response(
      JSON.stringify({
        error:
          error instanceof Error
            ? error.message
            : "Unknown error during cleanup",
      }),
      { status: 500, headers: { "Content-Type": "application/json" } },
    );
  }
});
```

## Error Handling

The function implements robust error handling at multiple levels:

1. **Individual Operations**: Each database operation catches and logs specific errors
2. **Function-Level Try/Catch**: The main handler has a top-level try/catch to handle unexpected errors
3. **Error Responses**: All errors are returned as structured JSON responses

## Logging

Extensive logging is used throughout the function to track progress and aid in debugging:

- **Start of Process**: Logs when the cleanup process begins
- **Table Information**: Logs which tables are being used
- **Operation Counts**: Logs the number of items found, processed, and deleted
- **Errors**: Logs detailed error messages and stack traces where appropriate
- **Completion**: Logs a summary of actions performed
