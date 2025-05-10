That's a very valid and common concern with distributed, asynchronous task processing! You're right, if your Cloud Function crashes unexpectedly (OOM, unhandled exception before your `finally` block, platform issues) or times out without updating the task status in your Postgres DB, that task can get stuck in "pending" or "processing". This would then block the user from submitting new tasks of the same type if your logic relies on there being no active tasks.

Here's a robust, multi-layered approach to handle this:

1.  **Stale Task Detection and Cleanup (Scheduled Job - Most Robust for Stuck Tasks):**

    - This is the most reliable way to catch tasks that got truly stuck.
    - You already have a Supabase Edge Function (`cleanup-old-data/index.ts`) scheduled to run daily. This is the _perfect_ place to add logic for detecting and handling stuck tasks.
    - **Define "Stuck":**
      - A task in `pending` status for too long (e.g., > 15-30 minutes) means it was likely never picked up or crashed immediately.
      - A task in `processing` status whose `updated_at` timestamp hasn't changed for a duration longer than your function's maximum timeout + a buffer (e.g., if your function timeout is 9 minutes, consider anything > 15-20 minutes stuck).
    - **Action for Stuck Tasks:**

      - Update their status to `failed`.
      - Set an `error_message` like "Task processing timed out or worker crashed."
      - Log this action for monitoring.

    - **Implementation in your Supabase Edge Function:**

      ```typescript
      // Inside your cleanup-old-data/index.ts

      async function cleanupStuckTasks(
        supabaseAdminClient: SupabaseClient,
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

        // Find tasks stuck in "processing"
        const { data: stuckProcessingTasks, error: processingError } =
          await supabaseAdminClient
            .from(getTableName("tasks")) // Use your getTableName utility
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
            const { error: updateError } = await supabaseAdminClient
              .from(getTableName("tasks"))
              .update({
                status: TASK_STATUS.FAILED,
                error_message: `Task timed out after being in processing for over ${processingTimeoutMinutes} minutes.`,
                updated_at: new Date().toISOString(),
              })
              .eq("id", task.id);
            if (updateError)
              console.error(
                `Error failing stuck processing task ${task.id}:`,
                updateError.message,
              );
            else stuckTasksUpdated++;
          }
        }

        // Find tasks stuck in "pending"
        const { data: stuckPendingTasks, error: pendingError } =
          await supabaseAdminClient
            .from(getTableName("tasks"))
            .select("id")
            .eq("status", TASK_STATUS.PENDING)
            .lt("created_at", pendingCutoff); // Use created_at for pending tasks

        if (pendingError) {
          console.error(
            "Error fetching stuck pending tasks:",
            pendingError.message,
          );
        } else if (stuckPendingTasks && stuckPendingTasks.length > 0) {
          console.log(
            `Found ${stuckPendingTasks.length} tasks stuck in pending.`,
          );
          for (const task of stuckPendingTasks) {
            const { error: updateError } = await supabaseAdminClient
              .from(getTableName("tasks"))
              .update({
                status: TASK_STATUS.FAILED,
                error_message: `Task remained pending for over ${pendingTimeoutMinutes} minutes and was not picked up.`,
                updated_at: new Date().toISOString(),
              })
              .eq("id", task.id);
            if (updateError)
              console.error(
                `Error failing stuck pending task ${task.id}:`,
                updateError.message,
              );
            else stuckTasksUpdated++;
          }
        }
        if (stuckTasksUpdated > 0) {
          console.log(`Marked ${stuckTasksUpdated} stuck tasks as failed.`);
        }
        return stuckTasksUpdated;
      }

      // In your main serve function:
      // ...
      const PROCESSING_TIMEOUT_MINUTES = 20; // Example: if function timeout is 9 min, allow 20 min.
      const PENDING_TIMEOUT_MINUTES = 30; // Example: if a task is pending for 30 min, something is wrong.
      const stuckTasksCount = await cleanupStuckTasks(
        supabase,
        PROCESSING_TIMEOUT_MINUTES,
        PENDING_TIMEOUT_MINUTES,
      );
      // ... include stuckTasksCount in response
      ```

      - You'll need to pass your Supabase admin client (created with service role key) to this function.
      - Ensure your `getTableName` utility is available or replicate its logic for `tasks_dev` / `tasks_prod`.
      - Add the `TASK_STATUS` constants to this Edge Function as well.

2.  Monitoring and Alerting

    Problem: You need to know when functions are failing or performing poorly.

    Solution:

        Utilize Google Cloud Monitoring and Logging.

        Set up alerts for:

            High error rates in your Cloud Function.



            Failed tasks in Task table?

    Benefit: Proactive issue detection and faster response to problems.

3.  Enhanced Error Handling & Idempotency

    Problem: Broad exception handling; potential re-execution of completed steps on retry.

    Solution:

        Idempotency Check: Before starting any significant work, check if the task is already in a terminal state (COMPLETED or FAILED). If so, log and exit.

        Specific Exception Handling: Catch specific exceptions (e.g., JigsawStackError, DatabaseError, httpx.TimeoutException) to log more detailed information or implement different retry/failure logic.

        Checkpointing (Advanced): For very long tasks, you could save progress checkpoints (e.g., "base_image_generated") in the task's metadata. On retry, resume from the last successful checkpoint. This is more complex to implement.

    Code Example (Conceptual for process_generation_task):

    # At the beginning of process_generation_task

    task_service = services["task_service"]
    initial_task_data = await task_service.get_task(task_id=task_id, user_id=user_id) # Assuming user_id is implicitly trusted here or handled by RLS
    if initial_task_data.get("status") in [TASK_STATUS_COMPLETED, TASK_STATUS_FAILED]:
    logger.info(f"Task {task_id} already in terminal state '{initial_task_data.get('status')}' Skipping processing.")
    return

    await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_PROCESSING)

    try: # ... your generation logic ... # Example of more specific error handling within the logic:
    try:
    concept_response = await concept_service.generate_concept(...)
    except JigsawStackConnectionError as jce: # Assuming you have such custom exceptions
    logger.error(f"Task {task_id}: JigsawStack connection error: {jce}") # Potentially retry this specific step if appropriate, or fail the task
    raise # Re-raise to be caught by the outer try-except
    except JigsawStackGenerationError as jge:
    logger.error(f"Task {task_id}: JigsawStack generation error: {jge}")
    raise # Re-raise # ...
    except Exception as e: # ... existing failure logic ...
