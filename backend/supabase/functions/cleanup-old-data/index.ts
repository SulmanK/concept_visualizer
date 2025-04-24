import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

// Get environment variables
const supabaseUrl = Deno.env.get("MY_SUPABASE_URL") || "";
const supabaseKey = Deno.env.get("MY_SERVICE_ROLE_KEY") || "";

// Create Supabase client
const supabase = createClient(supabaseUrl, supabaseKey);

// Storage bucket names from environment variables
const STORAGE_BUCKET_CONCEPT = Deno.env.get("STORAGE_BUCKET_CONCEPT") || "";
const STORAGE_BUCKET_PALETTE = Deno.env.get("STORAGE_BUCKET_PALETTE") || "";

// Function to delete a file from storage
async function deleteFromStorage(
  bucketName: string,
  path: string,
): Promise<boolean> {
  try {
    const { error } = await supabase.storage.from(bucketName).remove([path]);

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

// Function to clean up stuck tasks
async function cleanupStuckTasks(minutesThreshold: number): Promise<number> {
  try {
    console.log(
      `Looking for stuck tasks older than ${minutesThreshold} minutes...`,
    );

    // Calculate the cutoff timestamp (current time minus threshold)
    const now = new Date();
    const cutoffTime = new Date(
      now.getTime() - minutesThreshold * 60 * 1000,
    ).toISOString();

    // Get stuck tasks (those in 'pending' or 'processing' state that haven't been updated recently)
    const { data: stuckTasks, error } = await supabase
      .from("tasks")
      .select("id, status, type, updated_at")
      .or("status.eq.pending,status.eq.processing")
      .lt("updated_at", cutoffTime);

    if (error) {
      console.error("Error fetching stuck tasks:", error.message);
      return 0;
    }

    if (!stuckTasks || stuckTasks.length === 0) {
      console.log("No stuck tasks found");
      return 0;
    }

    console.log(`Found ${stuckTasks.length} stuck tasks to mark as failed`);

    // Mark each task as failed
    let updatedCount = 0;
    for (const task of stuckTasks) {
      const { error: updateError } = await supabase
        .from("tasks")
        .update({
          status: "failed",
          error_message: `Task was stuck in '${task.status}' state for more than ${minutesThreshold} minutes`,
          updated_at: new Date().toISOString(),
        })
        .eq("id", task.id);

      if (updateError) {
        console.error(`Error updating task ${task.id}:`, updateError.message);
      } else {
        updatedCount++;
        console.log(
          `Marked task ${task.id} as failed (was in '${task.status}' state since ${task.updated_at})`,
        );
      }
    }

    return updatedCount;
  } catch (err) {
    console.error("Error cleaning up stuck tasks:", err);
    return 0;
  }
}

serve(async (req) => {
  try {
    console.log("Starting data cleanup process");

    // 1. Clean up stuck tasks (those in pending/processing for more than 30 minutes)
    const stuckTasksUpdated = await cleanupStuckTasks(30);

    // 2. Get concepts older than 3 days
    console.log("Fetching concepts older than 3 days...");
    const { data: oldConcepts, error: conceptsError } = await supabase.rpc(
      "get_old_concepts",
      { days_threshold: 3 },
    );

    if (conceptsError) {
      throw new Error(`Error fetching old concepts: ${conceptsError.message}`);
    }

    if (!oldConcepts || oldConcepts.length === 0) {
      console.log("No old concepts found");
      return new Response(
        JSON.stringify({
          message: "Cleanup completed",
          stuck_tasks_updated: stuckTasksUpdated,
          old_concepts_deleted: 0,
        }),
        {
          status: 200,
          headers: { "Content-Type": "application/json" },
        },
      );
    }

    const conceptIds = oldConcepts.map((c) => c.id);
    const conceptPaths = oldConcepts.map((c) => c.image_path).filter(Boolean);

    console.log(`Found ${conceptIds.length} concepts to delete`);

    // 3. Get variations for those concepts
    console.log("Fetching associated color variations...");
    const { data: variations, error: variationsError } = await supabase.rpc(
      "get_variations_for_concepts",
      { concept_ids: conceptIds },
    );

    if (variationsError) {
      throw new Error(`Error fetching variations: ${variationsError.message}`);
    }

    const variationPaths = variations
      ? variations.map((v) => v.image_path).filter(Boolean)
      : [];
    console.log(`Found ${variationPaths.length} color variations to delete`);

    // 4. Delete variations from database
    console.log("Deleting color variations from database...");
    const { error: deleteVariationsError } = await supabase.rpc(
      "delete_variations_for_concepts",
      { concept_ids: conceptIds },
    );

    if (deleteVariationsError) {
      throw new Error(
        `Error deleting variations: ${deleteVariationsError.message}`,
      );
    }

    // 5. Delete concepts from database
    console.log("Deleting concepts from database...");
    const { error: deleteConceptsError } = await supabase.rpc(
      "delete_concepts",
      { concept_ids: conceptIds },
    );

    if (deleteConceptsError) {
      throw new Error(
        `Error deleting concepts: ${deleteConceptsError.message}`,
      );
    }

    // 6. Delete files from storage
    console.log("Deleting files from storage...");

    // Delete concept images
    let deletedConceptFiles = 0;
    for (const path of conceptPaths) {
      if (path && (await deleteFromStorage(STORAGE_BUCKET_CONCEPT, path))) {
        deletedConceptFiles++;
      }
    }

    // Delete variation images
    let deletedVariationFiles = 0;
    for (const path of variationPaths) {
      if (path && (await deleteFromStorage(STORAGE_BUCKET_PALETTE, path))) {
        deletedVariationFiles++;
      }
    }

    console.log(
      `Deleted ${deletedConceptFiles}/${conceptPaths.length} concept files`,
    );
    console.log(
      `Deleted ${deletedVariationFiles}/${variationPaths.length} variation files`,
    );

    // Return success response
    return new Response(
      JSON.stringify({
        message: "Cleanup completed successfully",
        stuck_tasks_updated: stuckTasksUpdated,
        deleted_concepts: conceptIds.length,
        deleted_variations: variationPaths.length,
        deleted_concept_files: deletedConceptFiles,
        deleted_variation_files: deletedVariationFiles,
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
      {
        status: 500,
        headers: { "Content-Type": "application/json" },
      },
    );
  }
});
