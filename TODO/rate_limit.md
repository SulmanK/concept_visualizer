
**Task 1: Update `extractRateLimitHeaders` Function in `rateLimitService.ts`**

*   **File:** `frontend/my-app/src/services/rateLimitService.ts`
*   **Action:** Modify the `extractRateLimitHeaders` function signature.
    *   Change the `response` parameter type from `Response` to `AxiosResponse` (import `AxiosResponse` from 'axios').
*   **Action:** Update header access logic within `extractRateLimitHeaders`.
    *   Remove the `response.headers.forEach` loop.
    *   Access headers directly using lowercase keys from `response.headers` (e.g., `response.headers['x-ratelimit-limit']`).
    *   Ensure parsing handles potential `undefined` values for headers (e.g., use `as string | undefined` and check for existence).
*   **Action:** Enhance logging within `extractRateLimitHeaders`.
    *   Add a `console.warn` if expected rate limit headers (`x-ratelimit-limit`, `x-ratelimit-remaining`, `x-ratelimit-reset`) are missing, especially for critical endpoints like `/export/` or `/concepts/`. Include the endpoint URL in the log.
    *   Add a `console.debug` statement logging all received headers for debugging purposes when expected headers are missing.
*   **Action:** Refine the logic for updating the main `rateLimitCache`.
    *   Add checks to ensure `rateLimitCache.main`, `rateLimitCache.main.limits`, and the specific `category` (e.g., `rateLimitCache.main.limits[category]`) exist before attempting to update the cache to prevent runtime errors. Log a message if the category is not found in the cache.

**Task 2: Update Success Response Interceptor in `apiClient.ts`**

*   **File:** `frontend/my-app/src/services/apiClient.ts`
*   **Action:** Modify the success part of the `axiosInstance.interceptors.response.use` function.
    *   Ensure the `response` parameter is explicitly typed as `AxiosResponse`.
    *   Remove the creation of `fetchCompatResponse`.
    *   Call the updated `extractRateLimitHeaders` function, passing the `response` (the `AxiosResponse` object) and `response.config.url` directly.
    *   Wrap the call to `extractRateLimitHeaders` in a `try...catch` block and log any errors that occur during header processing.

**Task 3: Enhance 429 Error Handling in `apiClient.ts`**

*   **File:** `frontend/my-app/src/services/apiClient.ts`
*   **Action:** Refine the error handling logic within the `axiosInstance.interceptors.response.use` error callback, specifically for `error.response?.status === 429`.
    *   Improve parsing of `x-ratelimit-reset` and `retry-after` headers. Handle cases where they might be Unix timestamps or seconds. Calculate `resetAfterSeconds` (seconds from now until reset) reliably.
    *   Derive `limit` and `current` values from the headers (`x-ratelimit-limit`, `x-ratelimit-remaining`) if available.
    *   Ensure the `errorData` object passed to the `RateLimitError` constructor contains the best available values for `limit`, `current`, and `reset_after_seconds`.
    *   Update the instantiation of `RateLimitError` to use these potentially derived values.

**Task 4: Deprecate `getAuthHeaders` Function in `apiClient.ts`**

*   **File:** `frontend/my-app/src/services/apiClient.ts`
*   **Action:** Locate the `getAuthHeaders` function.
*   **Action:** Add a JSDoc comment `@deprecated This function is deprecated. Authentication headers are now handled by the Axios request interceptor.` above the function definition.
*   **Action (Optional but Recommended):** Search the codebase for any remaining calls to `getAuthHeaders` and remove them, as the interceptor now handles this automatically.