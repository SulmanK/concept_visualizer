# Design Doc: Production-Ready Rate Limit Enhancements

**1. Problem Statement:**

The current rate limit implementation works but can be enhanced for better accuracy, user experience, and robustness, aligning it more closely with production best practices seen in major web applications and APIs. Key areas for improvement include more direct use of standard rate limit headers, providing more immediate feedback to users, and centralizing state management logic.

**2. Goals:**

*   Increase the accuracy of rate limit tracking by using server-provided headers (`X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`).
*   Improve perceived application responsiveness through optimistic UI updates.
*   Provide clearer and more proactive feedback to users regarding their rate limit status and potential errors.
*   Centralize and simplify the caching strategy for rate limit data.
*   (Optional) Introduce client-side retry mechanisms for rate-limited requests where appropriate.

**3. Proposed Enhancements:**

**3.1. Direct Header Utilization & Centralized Caching**

*   **Problem:** Current system relies heavily on polling a status endpoint and an internal hook timer, potentially diverging from the *actual* limits communicated by the server via headers on every response. Caching logic is split between the hook and the service.
*   **Solution:**
    *   Modify `rateLimitService.ts` to be the sole owner of the rate limit cache.
    *   The `extractRateLimitHeaders` function (called by the global fetch interceptor) will update this central cache, storing `limit`, `remaining`, and `reset` timestamp *per rate limit category* (e.g., 'svg_conversion', 'generation').
    *   The cache validity for each category should be determined by comparing the current time with the stored `reset` timestamp from the `X-RateLimit-Reset` header.
    *   Refactor `useRateLimits` hook:
        *   Remove its internal `lastFetchTime` cache.
        *   `fetchData` should first consult the `rateLimitService` cache.
        *   Only call the dedicated status endpoint (`/api/health/rate-limits-status`) if the service's cache for a category is missing or expired (based on the `Reset` timestamp), or during a forced refresh.
*   **Impact:** More accurate rate limit tracking, reduced polling of the status endpoint, simplified caching logic.

**3.2. Optimistic UI Updates**

*   **Problem:** The UI reflects rate limit changes only *after* an API call completes and the state is refreshed, leading to a slight delay.
*   **Solution:**
    *   Add a function to `RateLimitContext` (e.g., `decrementLimit(category: string, amount: number = 1)`).
    *   This function will *immediately* update the locally cached/context state for the specified category.
    *   Components triggering rate-limited actions (e.g., Generate button, SVG Export) will call `decrementLimit('category_name')` *just before* initiating the API request.
    *   The subsequent state refresh (triggered by event or headers) will eventually fetch the authoritative state from the server, self-correcting if needed.
*   **Impact:** Improved perceived responsiveness of the UI.

**3.3. Enhanced User Feedback & Error Handling**

*   **Problem:** Rate limit feedback is minimal (loading/error state in panel). Hitting a limit results in a generic failure.
*   **Solution:**
    *   **Proactive Warnings:** In the `RateLimitsPanel` or near relevant action buttons, display warnings (e.g., text, color change) when a `remaining` count is low (e.g., < 5).
    *   **Specific Rate Limit Errors:** Modify the API client (`apiClient.ts`) or the global fetch interceptor to specifically detect 429 (Too Many Requests) status codes. When detected:
        *   Extract `Retry-After` or `X-RateLimit-Reset` headers if available.
        *   Display a user-friendly toast/error message stating *which* limit was hit and *when* it resets (e.g., "Generation limit reached. Please try again in 35 seconds.").
        *   Update the central cache with this information if possible.
    *   **Visual Indicators:** Enhance `RateLimitsPanel` with visual bars or gauges representing quota usage.
*   **Impact:** Better user understanding of limits, reduced frustration when limits are hit.

**3.4. Client-Side Retry Logic (Optional)**

*   **Problem:** Rate-limited requests currently fail immediately.
*   **Solution:**
    *   Identify API calls where an automatic retry might be acceptable (e.g., non-critical background tasks).
    *   Wrap these calls in the `apiClient` or specific service functions.
    *   If a call receives a 429 response, check for `Retry-After` (seconds) or `X-RateLimit-Reset` (timestamp) headers.
    *   Wait for the specified duration and retry the request automatically *once*.
*   **Impact:** Increased resilience for certain operations, potentially smoothing over brief rate limit bursts. Requires careful consideration of which endpoints are suitable.

**4. Implementation Plan:**

1.  **Refactor `rateLimitService.ts`:** Implement central caching based on headers and reset timestamps. Expose functions to get cached data.
2.  **Refactor `useRateLimits.ts`:** Remove internal cache, consume data from `rateLimitService`, trigger status endpoint calls only when necessary.
3.  **Update `RateLimitContext.tsx`:** Add `decrementLimit` function and integrate it with the service cache.
4.  **Update `apiClient.ts` / Fetch Interceptor:** Implement 429 error handling and specific error reporting. Extract relevant headers on 429s. Potentially add retry logic.
5.  **Update UI Components:**
    *   Call `decrementLimit` before relevant actions.
    *   Add proactive warnings and visual indicators in `RateLimitsPanel` and near action buttons.
    *   Ensure UI handles the specific rate limit error messages gracefully.

**5. Alternatives Considered:**

*   **No Optimistic Updates:** Simpler, but less responsive UI.
*   **Server-Driven Retries:** Relying purely on server suggestions (less common for client-side limits like these).
*   **More Complex Caching Libraries:** Overkill for this specific need. 