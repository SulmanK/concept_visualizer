Okay, let's break down the implementation of the centralized authentication system using Axios interceptors into a set of actionable tasks.

**Goal:** Refactor the frontend API handling to use Axios interceptors for reliable authentication token management, eliminating potential race conditions and stale token issues.

---

### Phase 1: Setup and Axios Integration

**Objective:** Replace the current `fetch`-based API utility with an Axios instance.

1.  **Install Axios:**
    *   Task: Add Axios and its types to the frontend project.
    *   Command: `npm install axios @types/axios` or `yarn add axios @types/axios`
    *   File: `frontend/my-app/package.json`

2.  **Refactor `apiClient.ts`:**
    *   Task: Modify `src/services/apiClient.ts`.
    *   Action: Remove the existing `fetch`-based `request`, `get`, `post` functions.
    *   Action: Create a configured Axios instance (`axiosInstance`) using `axios.create()`, setting the `baseURL`.
    *   Action: Re-implement the exported `apiClient.get`, `apiClient.post`, and `apiClient.exportImage` methods using the `axiosInstance`. Ensure `exportImage` correctly sets `responseType: 'blob'`.
    *   Note: Keep the function signatures the same for now to minimize changes in consuming hooks/components.

---

### Phase 2: Implement Axios Interceptors

**Objective:** Add interceptors to automatically handle token injection and refresh attempts.

3.  **Implement Request Interceptor:**
    *   Task: Add a request interceptor to the `axiosInstance` in `src/services/apiClient.ts`.
    *   Action: Inside the interceptor (`axiosInstance.interceptors.request.use(async (config) => { ... })`):
        *   Fetch the current session using `supabase.auth.getSession()`.
        *   If a valid `session.access_token` exists, add the `Authorization: Bearer <token>` header to `config.headers`.
        *   If no token exists, ensure the `Authorization` header is *removed* (`delete config.headers.Authorization;`).
        *   Add `console.log` statements to track token presence/absence for debugging.
        *   Return the modified `config`.
    *   Action: Add basic error handling within the interceptor's error callback.

4.  **Implement Response Error Interceptor (401 Handling & Refresh):**
    *   Task: Add a response error interceptor (`axiosInstance.interceptors.response.use(null, async (error) => { ... })`) in `src/services/apiClient.ts`.
    *   Action: Check if the error response status is 401 (`error.response?.status === 401`).
    *   Action: Check if the original request hasn't already been retried (add a custom flag like `config._retry = true`).
    *   Action: If it's a 401 and not a retry:
        *   Attempt to refresh the token using `supabase.auth.refreshSession()`.
        *   If refresh succeeds:
            *   Get the new token from the refreshed session.
            *   Update the original request's `Authorization` header.
            *   Retry the original request using `axiosInstance(originalRequest)`.
        *   If refresh fails:
            *   Log the failure.
            *   Dispatch a custom DOM event (e.g., `auth-error-needs-logout`) to signal a global logout requirement.
            *   Reject the promise with the original error.
    *   Action: If it's not a 401 or it's already a retry, reject the promise with the error (or a processed version).

5.  **Implement Response Interceptor (Rate Limit & Header Handling):**
    *   Task: Extend the response interceptor (or use the success callback `axiosInstance.interceptors.response.use((response) => { ... })`) in `src/services/apiClient.ts`.
    *   Action: In the *success* part of the interceptor, extract rate limit headers using the existing `extractRateLimitHeaders` function (adapt it if necessary to work with Axios response objects).
    *   Action: In the *error* part of the interceptor:
        *   Check if the error status is 429.
        *   If 429, parse rate limit details from headers/body.
        *   Create and throw the custom `RateLimitError`.
        *   Dispatch the `show-rate-limits` and `show-api-toast` custom events.

---

### Phase 3: Refactor Authentication Context

**Objective:** Simplify `AuthProvider` to rely more on Supabase's state management and the interceptors.

6.  **Simplify `AuthProvider.tsx`:**
    *   Task: Review and potentially remove the proactive refresh timer (`useEffect` based on `session.expires_at`). Assess if Supabase's built-in refresh + the interceptor's retry logic is sufficient. *Recommendation: Remove it first, test thoroughly, and add back only if necessary.*
    *   Task: Ensure the `onAuthStateChange` listener correctly updates the context's `session`, `user`, and `isAnonymous` state. This should be the primary driver of state updates.
    *   Task: Add an effect to listen for the `auth-error-needs-logout` DOM event dispatched by the interceptor. When caught, call the `handleSignOut` function.
    *   Task: Remove any direct token fetching logic within the provider that might conflict with interceptors. `initializeAnonymousAuth` is still needed for the initial anonymous sign-in.

---

### Phase 4: Cleanup and Deprecation

**Objective:** Remove old, redundant token management code.

7.  **Remove `tokenService.ts`:**
    *   Task: Delete the file `src/services/tokenService.ts`.
    *   Task: Search the codebase for any remaining imports of `tokenService` and remove/refactor them.

8.  **Remove Old `apiClient` Logic:**
    *   Task: Delete the `getAuthHeaders` function from `src/services/apiClient.ts`.

9.  **Deprecate `useApi.ts`:**
    *   Task: Add a prominent `@deprecated` JSDoc comment to `src/hooks/useApi.ts`.
    *   Task: Add a `console.warn` inside the hook advising developers to switch to `apiClient` methods or React Query.
    *   Task: (Optional but recommended) Gradually refactor components/hooks currently using `useApi` to use the new `apiClient` methods or integrate directly with React Query's `useQuery`/`useMutation` using `apiClient` methods as the `queryFn`/`mutationFn`.

---

### Phase 5: Testing and Verification

**Objective:** Ensure the new authentication flow is robust and fixes the original issue.

10. **Update/Write Tests:**
    *   Task: Write unit tests for the Axios request and response interceptors in `apiClient.ts`, mocking `supabase.auth` methods.
    *   Task: Update existing integration tests (or create new ones) that involve API calls to ensure they pass with the new Axios client and interceptor logic.
    *   Task: Specifically test scenarios involving token expiry and refresh (this might require mocking timers or Supabase responses).

11. **Manual Testing:**
    *   Task: Clear all application storage (localStorage, cookies).
    *   Task: Load the application and perform actions requiring API calls. Verify success.
    *   Task: Leave the application idle for ~5 minutes (longer than the refresh buffer) and perform actions. Verify success.
    *   Task: Leave the application idle for ~1 hour (longer than token expiry) and perform actions. Verify success (refresh should occur).
    *   Task: Monitor the browser's Network tab and Console for 401 errors, retries, and successful calls. Check for any auth-related errors.
    *   Task: Test the logout functionality.
    *   Task: Test rate limit scenarios if possible to ensure `RateLimitError` is handled correctly.

---

This structured approach should help you systematically implement the centralized authentication handling and resolve the intermittent functionality loss. Remember to commit frequently and test each phase.