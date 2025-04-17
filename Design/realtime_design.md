Okay, let's outline a design plan to switch your task status updates from HTTP polling to using Supabase Realtime subscriptions (which utilizes WebSockets under the hood).

Yes, using **WebSockets (or SSE) via Supabase Realtime is a much more common and efficient approach for this kind of real-time status update in production applications** compared to frequent polling. It reduces server load, minimizes latency, and provides a better user experience.

Here's a step-by-step plan:

---

## Design Plan: Implement Real-time Task Status with Supabase

**Objective:** Replace the current HTTP polling mechanism for task status updates with Supabase Realtime subscriptions to provide efficient, near real-time updates to the frontend.

**Phase 1: Backend & Supabase Configuration**

**Step 1: Enable Realtime for the `tasks` Table**

*   **Goal:** Ensure Supabase broadcasts changes made to the `tasks` table.
*   **Action:**
    1.  Go to your Supabase project dashboard.
    2.  Navigate to `Database` -> `Replication`.
    3.  Find your `tasks` table (usually under the `public` schema unless you specified otherwise).
    4.  Click the "Source" toggle or configure replication to enable broadcasting for `INSERT`, `UPDATE`, and `DELETE` events on the `tasks` table. Ensure the publication includes the `tasks` table. Supabase usually handles this automatically when you enable RLS and use the default `supabase_realtime` publication.
*   **Verification:** Confirm in the Supabase dashboard that replication/realtime is active for the `tasks` table.

**Step 2: Verify RLS Policies for `tasks` Table**

*   **Goal:** Ensure users can subscribe to *their own* task updates.
*   **File:** `backend/scripts/update_rls_policy.sql` (or verify in Supabase SQL Editor)
*   **Action:**
    1.  Review the `SELECT` policy for the `tasks` table. The existing policy should be sufficient:
        ```sql
        CREATE POLICY "Users (auth+anon) can view their own tasks"
        ON tasks FOR SELECT
        TO authenticated, anon
        USING (user_id = auth.uid());
        ```
    2.  This policy ensures that a user's Supabase client, when authenticated with their JWT, can only subscribe to changes for rows where `user_id` matches their `auth.uid()`.
*   **Verification:** Manually check the policies in the Supabase dashboard or by querying `pg_policies`.

**Step 3: Confirm Backend Task Updates**

*   **Goal:** Ensure the backend reliably updates the `tasks` table when status changes.
*   **File:** `backend/app/services/task/service.py`
*   **Action:**
    1.  Review the `update_task_status` method in `TaskService`.
    2.  Confirm it performs a standard SQL `UPDATE` operation on the `tasks` table, modifying the `status`, `result_id`, `error_message`, and `updated_at` columns as needed. These database updates are what trigger the Realtime broadcasts.
*   **Verification:** No code change likely needed, just confirmation of the update mechanism.

**Phase 2: Frontend Implementation**

**Step 4: Remove Old Polling Hook (`useTaskPolling`)**

*   **Goal:** Eliminate the HTTP polling logic.
*   **File:** `src/hooks/useTaskPolling.ts`
*   **Action:**
    1.  Delete the `useTaskPolling.ts` file.
    2.  Remove its export from `src/hooks/index.ts`.
    3.  Remove its usage from `src/contexts/TaskContext.tsx`.
*   **Verification:** Ensure the app compiles and runs without errors related to the removed hook. The task status will temporarily stop updating.

**Step 5: Create a New Hook for Realtime Subscription (`useTaskSubscription`)**

*   **Goal:** Encapsulate the logic for subscribing to Supabase Realtime updates for a specific task.
*   **File:** `src/hooks/useTaskSubscription.ts` (New file)
*   **Action:**
    1.  Create the new hook file.
    2.  Implement the `useTaskSubscription` hook:
        *   Accept `taskId` as an argument.
        *   Use `useState` to store the latest `TaskResponse` received from the subscription.
        *   Use `useEffect` to manage the Supabase Realtime subscription:
            *   Check if `taskId` is valid.
            *   Import the `supabase` client instance.
            *   Create a channel specific to the task (e.g., `realtime:public:tasks:id=eq.${taskId}`).
            *   Define a callback function (`handleTaskUpdate`) to process incoming `UPDATE` events. This function will update the local state and potentially the React Query cache (`queryClient.setQueryData`).
            *   Subscribe to `postgres_changes` events for the specific task row (`table: 'tasks', event: 'UPDATE', schema: 'public', filter: `id=eq.${taskId}`).
            *   Handle subscription state changes (e.g., `SUBSCRIBED`, `CHANNEL_ERROR`, `TIMED_OUT`). Log these events.
            *   Implement cleanup: `supabase.removeChannel(channel)` when the hook unmounts or `taskId` changes.
        *   Return the latest `taskData` and potentially the subscription status/error.
*   **Verification:** Unit test the hook logic (mocking `supabase.channel` and its methods).

**Step 6: Integrate `useTaskSubscription` into `TaskContext`**

*   **Goal:** Use the new subscription hook to drive the task state within the context.
*   **File:** `src/contexts/TaskContext.tsx`
*   **Action:**
    1.  Import `useTaskSubscription`.
    2.  Inside `TaskProvider`, call `useTaskSubscription` with the current `activeTaskId`.
        ```tsx
        const { taskData: subscribedTaskData, error: subscriptionError } = useTaskSubscription(activeTaskId);
        ```
    3.  Modify the context state updates:
        *   Use `subscribedTaskData` to update `activeTaskData` within the context.
        *   The boolean flags (`isPending`, `isProcessing`, etc.) should be derived directly from `subscribedTaskData?.status`.
    4.  Implement an **Initial Fetch**: When `activeTaskId` is first set (and non-null), *also* trigger a one-time fetch using `useTaskStatusQuery` (or a direct `queryClient.fetchQuery`) to get the *immediate* current status. This prevents a delay before the first subscription update arrives. Store this initial fetch result in the context's `activeTaskData` until the subscription provides an update.
    5.  Handle `subscriptionError`. Decide how to surface this to the user (e.g., set an error state in the context, show a toast).
    6.  Update the derived boolean states (`isTaskPending`, etc.) based on the `subscribedTaskData`.
*   **Verification:**
    *   When a task is started, the context should first reflect the initial fetched state, then update in near real-time as the backend updates the database.
    *   Check console logs for subscription events and updates.

**Step 7: Update Components Consuming Task State**

*   **Goal:** Ensure components react correctly to the real-time updates provided by the context.
*   **Files:** `src/components/TaskStatusBar.tsx`, `src/features/landing/LandingPage.tsx`, potentially others.
*   **Action:**
    1.  Review `TaskStatusBar.tsx`: Its logic should already work as it reads derived states (`isPending`, `isProcessing`, etc.) from `TaskContext`. Verify its visibility logic is still appropriate (Step 2 from the previous plan might still be relevant).
    2.  Review `LandingPage.tsx`: Ensure `getFormStatus` and `getProcessingMessage` derive state correctly from the updated `TaskContext`.
    3.  Ensure any components relying on `useTaskPolling` are updated to use `useTaskContext` or its selector hooks.
*   **Verification:** Components should update dynamically as the task progresses without page reloads or manual refreshes.

**Phase 3: Testing & Refinement**

**Step 8: Testing**

*   **Goal:** Verify the real-time updates work correctly and handle various scenarios.
*   **Actions:**
    1.  **Manual Testing:**
        *   Submit tasks and observe the `TaskStatusBar` for immediate status changes (pending -> processing -> completed/failed).
        *   Test consecutive submissions.
        *   Test network interruptions: disconnect Wi-Fi while a task is processing, then reconnect. Does the status update correctly? (Supabase client handles reconnection attempts).
        *   Test browser tab visibility changes: Start a task, switch tabs, come back. Is the status up-to-date?
    2.  **Automated Testing (Vitest):**
        *   Unit test `useTaskSubscription` by mocking Supabase channel methods (`on`, `subscribe`, `unsubscribe`). Simulate receiving different payload types.
        *   Update `TaskContext` tests to mock `useTaskSubscription`.
    3.  **Automated Testing (Playwright):**
        *   Difficult to test *true* real-time updates reliably in E2E without complex backend mocking.
        *   Focus E2E tests on verifying the *final* state (e.g., task completion leads to results rendering) and the *initial* state changes (e.g., status bar appears).
        *   Consider adding short `waitFor` delays after actions and checking if the status bar *eventually* reflects the expected state.

**Step 9: Optimize and Refine**

*   **Goal:** Fine-tune performance and user experience.
*   **Actions:**
    1.  **Subscription Management:** Ensure subscriptions are properly cleaned up when `activeTaskId` becomes null or the component unmounts.
    2.  **Error Handling:** Implement robust handling for subscription errors (e.g., display a persistent error, attempt resubscription).
    3.  **UI Feedback:** Ensure smooth UI transitions between states.
    4.  **Cache Updates:** Confirm that React Query cache invalidation/updates triggered by the subscription work as expected (e.g., `setQueryData` in the subscription callback).

---

This plan provides a clear path to transition from polling to a more efficient real-time system using Supabase. Remember to handle potential errors gracefully, especially around network connectivity and subscription management.