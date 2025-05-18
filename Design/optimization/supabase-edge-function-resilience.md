**Feedback on Your Existing Design Plan (the TypeScript snippet):**

1.  **Correct Logic:** The core logic for identifying stuck "processing" tasks (based on `updated_at`) and stuck "pending" tasks (based on `created_at`) is sound. Using different time fields for these statuses is appropriate.
2.  **Clear Error Messages:** The `error_message` you're setting for failed tasks is informative.
3.  **Supabase Client:** The plan to use an admin client (`supabaseAdminClient`) is correct, as this function needs to operate across user data and bypass RLS for administrative cleanup. The existing Edge Function already initializes `supabase` using the service role key, which is what you need.
4.  **`getTableName("tasks")`:** This is a crucial part. Your Python backend uses `settings.DB_TABLE_TASKS` which resolves to `tasks_dev` or `tasks_prod`. Your Edge Function will need similar logic.
5.  **`TASK_STATUS` Constants:** You'll need to define these constants (e.g., `PENDING`, `PROCESSING`, `FAILED`) within your Edge Function, similar to how they are in your Python backend.
6.  **Timeout Parameters:** Passing `processingTimeoutMinutes` and `pendingTimeoutMinutes` makes the function flexible.

**Integration into `backend/supabase/functions/cleanup-old-data/index.ts`:**

Here's how you can integrate your new `cleanupStuckTasks` logic into the existing Edge Function, along with necessary additions:

**Consolidated `backend/supabase/functions/cleanup-old-data/index.ts`:**

```typescript
// @deno-types="npm:@supabase/supabase-js@2.39.8"
import { createClient, SupabaseClient } from "npm:@supabase/supabase-js@2.39.8";
import { serve } from "https://deno.land/std@0.177.0/http/server.ts";

// --- Environment Variables & Configuration ---
const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? ""; // Standard Supabase env var
const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? ""; // Standard Supabase env var
const appEnvironment = Deno.env.get("APP_ENVIRONMENT") ?? "dev"; // Custom: 'dev' or 'prod'

// Create Supabase admin client
const supabaseAdmin: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceRoleKey,
);

// Storage bucket names (keep your existing logic for these)
const STORAGE_BUCKET_CONCEPT =
  Deno.env.get("STORAGE_BUCKET_CONCEPT") || `concept-images-${appEnvironment}`;
const STORAGE_BUCKET_PALETTE =
  Deno.env.get("STORAGE_BUCKET_PALETTE") || `palette-images-${appEnvironment}`;

// --- Task Status Constants (mirror Python backend) ---
const TASK_STATUS = {
  PENDING: "pending",
  PROCESSING: "processing",
  COMPLETED: "completed",
  FAILED: "failed",
  CANCELED: "canceled", // If you use this
};

// --- Table Name Utility ---
// Gets the correct table name based on the environment (e.g., tasks_dev or tasks_prod)
function getTableName(
  baseName: "tasks" | "concepts" | "color_variations",
): string {
  const suffix = appEnvironment === "prod" ? "_prod" : "_dev";
  if (baseName === "tasks") return `tasks${suffix}`;
  if (baseName === "concepts") return `concepts${suffix}`;
  if (baseName === "color_variations") return `color_variations${suffix}`;
  throw new Error(`Invalid base table name: ${baseName}`);
}

// --- Existing `deleteFromStorage` function (keep as is) ---
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

// --- Your Enhanced `cleanupStuckTasks` Function ---
async function cleanupStuckTasks(
  // supabaseAdminClient is already defined globally as supabaseAdmin
  processingTimeoutMinutes: number,
  pendingTimeoutMinutes: number,
): Promise<number> {
  const now = new Date();
  const processingCutoff = new Date(
    now.getTime() - processingTimeoutMinutes * 60 * 1000,
  ).toISOString();
  const pendingCutoff = new Date(
    now.getTime() - pendingTimeoutMinutes * 60 * 1000,
  ).toISOString();
  let stuckTasksUpdated = 0;
  const tasksTable = getTableName("tasks");

  console.log(
    `Looking for tasks stuck in processing older than ${processingCutoff} in table ${tasksTable}...`,
  );
  // Find tasks stuck in "processing"
  const { data: stuckProcessingTasks, error: processingError } =
    await supabaseAdmin
      .from(tasksTable)
      .select("id")
      .eq("status", TASK_STATUS.PROCESSING)
      .lt("updated_at", processingCutoff);

  if (processingError) {
    console.error(
      "Error fetching stuck processing tasks:",
      processingError.message,
    );
  } else if (stuckProcessingTasks && stuckProcessingTasks.length > 0) {
    console.log(
      `Found ${stuckProcessingTasks.length} tasks stuck in processing.`,
    );
    for (const task of stuckProcessingTasks) {
      const { error: updateError } = await supabaseAdmin
        .from(tasksTable)
        .update({
          status: TASK_STATUS.FAILED,
          error_message: `Task timed out after being in processing for over ${processingTimeoutMinutes} minutes.`,
          updated_at: new Date().toISOString(),
        })
        .eq("id", task.id);
      if (updateError) {
        console.error(
          `Error failing stuck processing task ${task.id}:`,
          updateError.message,
        );
      } else {
        stuckTasksUpdated++;
      }
    }
  } else {
    console.log("No tasks found stuck in processing.");
  }

  console.log(
    `Looking for tasks stuck in pending older than ${pendingCutoff} in table ${tasksTable}...`,
  );
  // Find tasks stuck in "pending"
  const { data: stuckPendingTasks, error: pendingError } = await supabaseAdmin
    .from(tasksTable)
    .select("id")
    .eq("status", TASK_STATUS.PENDING)
    .lt("created_at", pendingCutoff); // Use created_at for pending tasks

  if (pendingError) {
    console.error("Error fetching stuck pending tasks:", pendingError.message);
  } else if (stuckPendingTasks && stuckPendingTasks.length > 0) {
    console.log(`Found ${stuckPendingTasks.length} tasks stuck in pending.`);
    for (const task of stuckPendingTasks) {
      const { error: updateError } = await supabaseAdmin
        .from(tasksTable)
        .update({
          status: TASK_STATUS.FAILED,
          error_message: `Task remained pending for over ${pendingTimeoutMinutes} minutes and was not picked up.`,
          updated_at: new Date().toISOString(),
        })
        .eq("id", task.id);
      if (updateError) {
        console.error(
          `Error failing stuck pending task ${task.id}:`,
          updateError.message,
        );
      } else {
        stuckTasksUpdated++;
      }
    }
  } else {
    console.log("No tasks found stuck in pending.");
  }

  if (stuckTasksUpdated > 0) {
    console.log(`Marked ${stuckTasksUpdated} stuck tasks as failed.`);
  }
  return stuckTasksUpdated;
}

// --- Main `serve` Function ---
serve(async (req: Request) => {
  // Ensure this is a POST request if you have security policies or specific triggers
  if (req.method !== "POST") {
    return new Response(JSON.stringify({ error: "Method Not Allowed" }), {
      status: 405,
      headers: { "Content-Type": "application/json" },
    });
  }

  try {
    console.log("Starting data cleanup process...");
    console.log(`Application Environment: ${appEnvironment}`);
    console.log(`Using tasks table: ${getTableName("tasks")}`);
    console.log(`Using concepts table: ${getTableName("concepts")}`);
    console.log(`Using variations table: ${getTableName("color_variations")}`);

    // 1. Clean up stuck tasks (your new logic)
    const PROCESSING_TIMEOUT_MINUTES = 30; // e.g., if function timeout is 9 min, allow 30 min.
    const PENDING_TIMEOUT_MINUTES = 30; // e.g., if a task is pending for 30 min, assume it's stuck.
    const stuckTasksCount = await cleanupStuckTasks(
      PROCESSING_TIMEOUT_MINUTES,
      PENDING_TIMEOUT_MINUTES,
    );
    console.log(`Processed stuck tasks. Count updated: ${stuckTasksCount}`);

    // 2. Get concepts older than 3 days (your existing logic, adapted for dynamic table names)
    console.log("Fetching concepts older than 3 days...");
    const conceptsTable = getTableName("concepts");
    const { data: oldConcepts, error: conceptsError } = await supabaseAdmin
      .from(conceptsTable)
      .select("id, image_path") // Select only necessary fields
      .lt(
        "created_at",
        new Date(Date.now() - 3 * 24 * 60 * 60 * 1000).toISOString(),
      ); // Older than 3 days

    if (conceptsError) {
      throw new Error(`Error fetching old concepts: ${conceptsError.message}`);
    }

    let deletedConceptsCount = 0;
    let deletedVariationsCount = 0;
    let deletedConceptFilesCount = 0;
    let deletedVariationFilesCount = 0;

    if (!oldConcepts || oldConcepts.length === 0) {
      console.log("No old concepts found to delete.");
    } else {
      deletedConceptsCount = oldConcepts.length;
      const conceptIds = oldConcepts.map((c) => c.id);
      const conceptPaths = oldConcepts
        .map((c) => c.image_path)
        .filter(Boolean) as string[];

      console.log(`Found ${conceptIds.length} old concepts to delete.`);

      // 3. Get variations for those concepts
      const variationsTable = getTableName("color_variations");
      console.log(
        `Fetching associated color variations from ${variationsTable}...`,
      );
      const { data: variations, error: variationsError } = await supabaseAdmin
        .from(variationsTable)
        .select("id, image_path")
        .in("concept_id", conceptIds);

      if (variationsError) {
        throw new Error(
          `Error fetching variations: ${variationsError.message}`,
        );
      }

      const variationPaths = variations
        ? (variations.map((v) => v.image_path).filter(Boolean) as string[])
        : [];
      deletedVariationsCount = variationPaths.length;
      console.log(
        `Found ${variationPaths.length} color variations associated with old concepts.`,
      );

      // 4. Delete variations from database (concepts ON DELETE CASCADE should handle this, but explicit can be safer)
      if (variations && variations.length > 0) {
        console.log("Deleting color variations from database...");
        const { error: deleteVariationsError } = await supabaseAdmin
          .from(variationsTable)
          .delete()
          .in("concept_id", conceptIds);
        if (deleteVariationsError) {
          throw new Error(
            `Error deleting variations: ${deleteVariationsError.message}`,
          );
        }
      }

      // 5. Delete concepts from database
      console.log("Deleting old concepts from database...");
      const { error: deleteConceptsError } = await supabaseAdmin
        .from(conceptsTable)
        .delete()
        .in("id", conceptIds);
      if (deleteConceptsError) {
        throw new Error(
          `Error deleting concepts: ${deleteConceptsError.message}`,
        );
      }

      // 6. Delete files from storage
      console.log("Deleting files from storage...");
      for (const path of conceptPaths) {
        if (await deleteFromStorage(STORAGE_BUCKET_CONCEPT, path)) {
          deletedConceptFilesCount++;
        }
      }
      for (const path of variationPaths) {
        if (await deleteFromStorage(STORAGE_BUCKET_PALETTE, path)) {
          deletedVariationFilesCount++;
        }
      }
      console.log(
        `Deleted ${deletedConceptFilesCount}/${conceptPaths.length} old concept files.`,
      );
      console.log(
        `Deleted ${deletedVariationFilesCount}/${variationPaths.length} old variation files.`,
      );
    }

    // Return success response
    return new Response(
      JSON.stringify({
        message: "Cleanup completed successfully",
        stuck_tasks_updated: stuckTasksCount,
        old_concepts_deleted: deletedConceptsCount,
        old_variations_deleted: deletedVariationsCount,
        old_concept_files_deleted: deletedConceptFilesCount,
        old_variation_files_deleted: deletedVariationFilesCount,
      }),
      {
        status: 200,
        headers: { "Content-Type": "application/json" },
      },
    );
  } catch (error) {
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

**Key Changes and Explanations:**

1.  **Environment Variable for Environment (`APP_ENVIRONMENT`):**

    - I've added `const appEnvironment = Deno.env.get("APP_ENVIRONMENT") ?? "dev";`.
    - You **MUST** set this environment variable in your Supabase Edge Function settings (via the Supabase Dashboard).
      - For your dev Supabase project, set `APP_ENVIRONMENT` to `dev`.
      - For your prod Supabase project, set `APP_ENVIRONMENT` to `prod`.
    - This is crucial for `getTableName` to work correctly.

2.  **`getTableName` Utility:**

    - This function now dynamically constructs table names like `tasks_dev`, `concepts_prod`, etc., based on `appEnvironment`.

3.  **`TASK_STATUS` Constants:**

    - Defined at the top to mirror your Python backend constants.

4.  **Supabase Admin Client:**

    - The existing `supabase` client is renamed to `supabaseAdmin` for clarity and is used by your `cleanupStuckTasks` function. It's already initialized with the service role key.

5.  **Timeout Values:**

    - `PROCESSING_TIMEOUT_MINUTES` and `PENDING_TIMEOUT_MINUTES` are now defined within the `serve` function. You might want to make these configurable via environment variables in the Supabase dashboard too if you need to adjust them without code changes.

6.  **Logging:**

    - The function includes `console.log` and `console.error` statements. Review these and adjust the verbosity as needed. Supabase Edge Function logs can be viewed in your project's dashboard.

7.  **Error Handling in `cleanupStuckTasks`:**

    - The snippet correctly logs errors from Supabase calls but continues processing other tasks/categories. This is generally good for a cleanup job.

8.  **Main `serve` Function Integration:**
    - The `cleanupStuckTasks` function is now called within the main `try...catch` block of the `serve` handler.
    - The count of updated stuck tasks is included in the final JSON response.
    - The existing logic for cleaning old concepts and variations now also uses `getTableName`.

**To Deploy This:**

1.  **Update Environment Variables in Supabase Dashboard:**

    - Go to your Supabase project > Edge Functions > Select your `cleanup-old-data` function.
    - Go to Settings (or similar tab for environment variables).
    - Ensure `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are correctly set (they usually are by default).
    - **Add a new environment variable `APP_ENVIRONMENT`**:
      - Set its value to `dev` for your development Supabase project.
      - Set its value to `prod` for your production Supabase project.
    - Optionally, add `STORAGE_BUCKET_CONCEPT` and `STORAGE_BUCKET_PALETTE` if they are not already set or if you want to override the defaults derived from `appEnvironment`.
    - Optionally, add `PROCESSING_TIMEOUT_MINUTES` and `PENDING_TIMEOUT_MINUTES` if you made them configurable.

2.  **Deploy the Edge Function:**
    - Use the Supabase CLI: `supabase functions deploy cleanup-old-data --project-ref <your-project-ref>`
    - Make sure you're deploying to the correct project (dev or prod).

**Additional Considerations:**

- **Idempotency:** The `update` operations are generally idempotent for setting a task to `failed`. If the function runs multiple times on the same stuck task, it won't cause issues.
- **Performance:** For a very large number of tasks, fetching and updating in loops might be slow. Supabase is generally efficient, but if you hit performance bottlenecks, you might explore batch updates or more complex SQL queries via RPC if needed (though the current approach is clear and should be fine for moderate loads).
- **Testing:** Thoroughly test this in your `dev` environment first by manually creating tasks that would be considered "stuck" (e.g., by setting their `created_at` or `updated_at` far in the past).
- **RPC vs. Direct Table Access:** Your existing function uses RPC calls (e.g., `get_old_concepts`). The new task cleanup logic uses direct table access (`.from(tableName)`). Both are fine. RPCs can encapsulate more complex SQL, while direct access is simpler for basic CRUD. They can coexist. The provided solution modifies your existing RPC calls to use `getTableName`.

This updated Edge Function should significantly improve the resiliency of your task processing system by automatically handling tasks that get stuck for various reasons. Remember to set the `APP_ENVIRONMENT` variable in your Supabase function settings!
