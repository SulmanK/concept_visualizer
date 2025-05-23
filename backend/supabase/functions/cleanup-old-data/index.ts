import { serve } from "https://deno.land/std@0.177.0/http/server.ts";
import {
  createClient,
  SupabaseClient,
} from "https://esm.sh/@supabase/supabase-js@2.39.8";

// --- Environment Variables & Configuration ---
const supabaseUrl = Deno.env.get("SUPABASE_URL") ?? "";
const supabaseServiceRoleKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "";
const appEnvironment = Deno.env.get("APP_ENVIRONMENT") ?? "dev"; // Custom: 'dev' or 'prod'

// Create Supabase admin client
const supabaseAdmin: SupabaseClient = createClient(
  supabaseUrl,
  supabaseServiceRoleKey,
);

// Storage bucket names
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

// --- Function to delete a file from storage ---
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

// --- Enhanced cleanupStuckTasks Function ---
async function cleanupStuckTasks(
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

// --- Main serve Function ---
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

    // 2. Get concepts older than 30 days
    console.log("Fetching concepts older than 30 days...");
    const conceptsTable = getTableName("concepts");
    const { data: oldConcepts, error: conceptsError } = await supabaseAdmin
      .from(conceptsTable)
      .select("id, image_path")
      .lt(
        "created_at",
        new Date(Date.now() - 30 * 24 * 60 * 60 * 1000).toISOString(),
      ); // Older than 30 days

    if (conceptsError) {
      throw new Error(`Error fetching old concepts: ${conceptsError.message}`);
    }

    let deletedConceptsCount = 0;
    let deletedVariationsCount = 0;
    let deletedConceptFilesCount = 0;
    let deletedVariationFilesCount = 0;
    let deletedTasksCount = 0;

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

      // 5.5 Delete associated tasks
      console.log("Deleting tasks associated with old concepts...");
      const tasksTable = getTableName("tasks");

      // First, retrieve the task IDs associated with these concepts
      const { data: associatedTasks, error: tasksQueryError } =
        await supabaseAdmin
          .from(tasksTable)
          .select("id")
          .in("result_id", conceptIds); // Using result_id instead of concept_id

      if (tasksQueryError) {
        console.error(
          `Error fetching tasks for old concepts: ${tasksQueryError.message}`,
        );
      } else if (associatedTasks && associatedTasks.length > 0) {
        const taskIds = associatedTasks.map((t) => t.id);
        console.log(`Found ${taskIds.length} tasks to delete for old concepts`);

        // Delete the tasks
        const { error: deleteTasksError } = await supabaseAdmin
          .from(tasksTable)
          .delete()
          .in("id", taskIds);

        if (deleteTasksError) {
          console.error(
            `Error deleting tasks for old concepts: ${deleteTasksError.message}`,
          );
        } else {
          deletedTasksCount = taskIds.length;
          console.log(
            `Successfully deleted ${deletedTasksCount} tasks for old concepts`,
          );
        }
      } else {
        console.log("No tasks found for old concepts");
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
        old_tasks_deleted: deletedTasksCount || 0,
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
