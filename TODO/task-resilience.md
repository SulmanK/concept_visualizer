That's a very valid and common concern with distributed, asynchronous task processing! You're right, if your Cloud Function crashes unexpectedly (OOM, unhandled exception before your `finally` block, platform issues) or times out without updating the task status in your Postgres DB, that task can get stuck in "pending" or "processing". This would then block the user from submitting new tasks of the same type if your logic relies on there being no active tasks.

Here's a robust, multi-layered approach to handle this:

1.  **In-Function Robustness (First Line of Defense):**

    - **Immediate Status Update:** The very first thing your Cloud Function should do after parsing the Pub/Sub message is to update the task status in Postgres to "processing" and set an `updated_at` timestamp. This at least distinguishes tasks that were picked up from those that never even started.
    - **Aggressive `try...except...finally`:**
      ```python
      # Inside your Cloud Function's main handler
      task_id = message.get("task_id")
      task_service = services["task_service"] # Assuming you have this
      try:
          await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_PROCESSING)
          # ... your main image generation logic ...
          await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_COMPLETED, result_id=concept_id)
      except Exception as e:
          error_msg = f"Worker failed: {str(e)}"
          logger.error(f"Task {task_id} failed: {error_msg}", exc_info=True)
          try:
              await task_service.update_task_status(task_id=task_id, status=TASK_STATUS_FAILED, error_message=error_msg)
          except Exception as db_update_err:
              logger.error(f"CRITICAL: Failed to update task {task_id} to FAILED status: {db_update_err}")
          # Important: Re-raise the exception if you want Pub/Sub to retry (if configured)
          # or handle it so Pub/Sub acks the message if it's a non-retryable error.
          raise
      # No `finally` needed here for status update if the goal is to let Pub/Sub retry on error.
      # If you want to ACK the message even on failure (to send to DLQ or stop retries),
      # then a `finally` block that ensures the function exits cleanly (without re-raising) is needed.
      ```
    - **Idempotency:** Design your task processing to be idempotent if Pub/Sub retries. If a task marked "failed" gets retried, it shouldn't cause duplicate data or actions.

2.  **Stale Task Detection and Cleanup (Scheduled Job - Most Robust for Stuck Tasks):**

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

3.  **Pub/Sub Configuration:**

    - **Retry Policy:** Configure Pub/Sub topic subscriptions with a retry policy. If your Cloud Function explicitly errors out (e.g., you `raise` an exception), Pub/Sub will attempt to redeliver the message. This handles transient errors within the function.
    - **Dead-Letter Queue (DLQ):** Configure a DLQ for your Pub/Sub subscription. If a message fails delivery repeatedly (after configured retries), it will be sent to the DLQ. You can then inspect these messages to understand why they are failing. This is more for messages that _cannot_ be processed, rather than tasks that get stuck mid-process.

4.  **Cloud Function Configuration:**

    - **Timeout:** Set an appropriate timeout for your Cloud Function. It should be generous enough to complete most tasks but not so long that it masks actual issues. For Gen 2 functions, the max is 60 minutes for event-driven functions. If your image generation truly takes longer than that, you might need to rethink the architecture (e.g., break it into smaller steps or use a different compute service like Cloud Run jobs or GCE VMs).
    - **Memory:** Ensure your function has enough memory. OOM errors are silent killers that won't trigger your `except` blocks.
    - **Concurrency:** Configure concurrency appropriately. If it's too high, you might hit resource limits.

5.  **Client-Side UX:**
    - **Polling Timeout:** On the frontend, if a task remains "pending" or "processing" for an unusually long time (e.g., > 10-15 minutes for image generation), you can inform the user that something might be wrong and they could try again later or contact support.
    - **Allow Manual Cancellation (if feasible):** If a user sees a task stuck, allow them to request cancellation. This would set the task status to "cancelling" or "failed*cancelled" in the DB. Your worker logic would need to periodically check for this, but it's complex for serverless functions. More practically, the stale task detector could also check for tasks that users \_tried* to cancel.

**Recommended Combination:**

- **Primary:** Robust `try...except...finally` in the Cloud Function.
- **Secondary (Catch-all):** The scheduled "Stale Task Detection" job (integrated into your existing Supabase Edge Function) is crucial for tasks that die silently.
- **Tertiary:** Pub/Sub retry policies and DLQs for message-level issues.
- **Quaternary:** Proper Cloud Function configuration (timeout, memory).

By implementing the stale task detection within your existing `cleanup-old-data` Supabase function, you leverage an existing scheduled mechanism and keep related cleanup logic together. This is a very good and practical approach. Remember to adjust the timeout thresholds based on your expected maximum processing time for image generation tasks.
