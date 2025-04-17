Okay, I've reviewed the codebase structure and the plan, and identified the specific files most likely needing modification for each task.

Here is the updated design plan with the relevant files listed for each task:

---

**Design Plan: Frontend Error Handling Enhancement (with Files)**

**Goal:**

1.  Correctly display specific "Rate Limit Exceeded" errors from the backend (HTTP 429) instead of generic "Network Error".
2.  Establish a robust, consistent, and user-friendly error handling pattern across the frontend application suitable for production.

**Core Strategy:** (Remains the same as previous plan)

**Key Components Involved:** (Remains the same as previous plan)

---

**Task Breakdown (with Files):**

**Phase 1: Fix Rate Limit Error Display**

1.  **Task:** Modify `apiClient.ts` Response Error Interceptor for 429.
    *   **Description:** Detect 429 errors, parse details, throw custom `RateLimitError`.
    *   **Files to Modify:**
        *   `frontend/my-app/src/services/apiClient.ts` (Modify interceptor logic, ensure `RateLimitError` class is correctly defined and used).

2.  **Task:** Update `useErrorHandling` to Recognize `RateLimitError`.
    *   **Description:** Enhance the hook to identify `RateLimitError` and store its specific details.
    *   **Files to Modify:**
        *   `frontend/my-app/src/hooks/useErrorHandling.tsx` (Update `categorizeError`/`handleError`, potentially update `ErrorWithCategory` interface).

3.  **Task:** Create/Enhance UI Component for Rate Limit Errors.
    *   **Description:** Update `ErrorMessage` to display rate limit details or create a specialized component.
    *   **Files to Modify:**
        *   `frontend/my-app/src/components/ui/ErrorMessage.tsx` (Add conditional rendering for `type === 'rateLimit'`).
        *   `frontend/my-app/src/services/rateLimitService.ts` (Import `formatTimeRemaining` helper).

4.  **Task:** Integrate Enhanced Error Display into Relevant Components.
    *   **Description:** Ensure components using API mutations/queries correctly display the categorized error, specifically the rate limit details.
    *   **Files to Modify:**
        *   `frontend/my-app/src/components/concept/ConceptForm.tsx` (Ensure it can render the enhanced `ErrorMessage` or `RateLimitErrorMessage` based on props).
        *   `frontend/my-app/src/hooks/useConceptMutations.ts` (Ensure it correctly catches `RateLimitError` and passes appropriate state/props).
        *   *(Review)* Other components that directly handle API errors might need similar updates.

**Phase 2: Production-Ready Error Handling Improvements**

5.  **Task:** Enhance `apiClient.ts` for Other HTTP Errors.
    *   **Description:** Add interceptor logic for 401, 403, 404, 5xx, network errors, throwing specific custom error types.
    *   **Files to Modify:**
        *   `frontend/my-app/src/services/apiClient.ts` (Add more `if/else if` blocks in the error interceptor, potentially define new error classes like `AuthError`, `NotFoundError`, `ServerError`, etc.).

6.  **Task:** Update `useErrorHandling` Categories.
    *   **Description:** Update the hook's types and logic to recognize and categorize the new error types from Task 5.
    *   **Files to Modify:**
        *   `frontend/my-app/src/hooks/useErrorHandling.tsx` (Update `ErrorCategory` type, update `categorizeError`/`handleError` logic).

7.  **Task:** Enhance `ErrorMessage` Component for All Categories.
    *   **Description:** Add distinct icons, colors, and potentially default action suggestions based on the expanded error categories. Handle display of field-specific validation errors.
    *   **Files to Modify:**
        *   `frontend/my-app/src/components/ui/ErrorMessage.tsx` (Add more conditional rendering based on `type`, icons, styling).

8.  **Task:** Implement Global Error Display.
    *   **Description:** Use `useErrorHandling` at a high level (e.g., `App.tsx`) to show a global error banner for unhandled or critical errors.
    *   **Files to Modify:**
        *   `frontend/my-app/src/App.tsx` (Import and use `useErrorHandling`, add conditional rendering for a global `ErrorMessage`).
        *   `frontend/my-app/src/components/ui/ErrorMessage.tsx` (Ensure it's suitable for global display).

9.  **Task:** Review and Refactor Mutation/Query Hooks.
    *   **Description:** Ensure all React Query hooks consistently use the centralized error handling (`createQueryErrorHandler` or similar) for their `onError` callbacks.
    *   **Files to Modify:**
        *   `frontend/my-app/src/hooks/useConceptMutations.ts`
        *   `frontend/my-app/src/hooks/useConceptQueries.ts`
        *   `frontend/my-app/src/hooks/useExportImageMutation.ts`
        *   `frontend/my-app/src/hooks/useRateLimitsQuery.ts`
        *   `frontend/my-app/src/hooks/useTaskQueries.ts`
        *   `frontend/my-app/src/hooks/useSessionQuery.ts`
        *   `frontend/my-app/src/hooks/useConfigQuery.ts`
        *   `frontend/my-app/src/utils/errorUtils.ts` (Verify `createQueryErrorHandler` integrates well).

