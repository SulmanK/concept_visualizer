# Design Doc: Refactor Rate Limit State Management

**1. Problem Statement:**

The `RateLimitsPanel` component exhibits a bug where it gets stuck in a loading state if an API operation that affects rate limits occurs *before* the panel is opened for the first time. This happens because the `useRateLimits` hook, responsible for fetching and managing rate limit state, is only initialized when the `RateLimitsPanel` mounts. If events triggering rate limit updates occur before the hook is active, the state management becomes inconsistent upon panel opening.

**2. Goals:**

- Fix the loading loop/stuck loading state bug.
- Ensure rate limit data is fetched and updated reliably, regardless of whether the `RateLimitsPanel` is currently visible.
- Decouple rate limit state management from the `RateLimitsPanel` component lifecycle.

**3. Proposed Solution:**

Introduce a `RateLimitContext` to manage the rate limit state globally within the authenticated part of the application.

- **`RateLimitContext.tsx`:**
    - Define the context type (`RateLimitContextType`).
    - Create the React context.
    - Implement `RateLimitProvider`:
        - A new context provider component.
        - Internally uses the existing `useRateLimits` hook logic.
        - Wraps the authenticated application routes or main layout.
        - Provides the `rateLimits`, `isLoading`, `error`, and `refetch` values via context.
    - Implement `useRateLimitContext` hook for easy consumption.
- **`useRateLimits` Hook (`hooks/useRateLimits.ts`):**
    - Retain the existing hook logic. It will be used internally by the `RateLimitProvider`. No significant changes needed here initially.
- **`RateLimitsPanel` (`components/RateLimitsPanel/RateLimitsPanel.tsx`):**
    - Refactor to consume the state from `useRateLimitContext` instead of calling `useRateLimits` directly.
- **`App.tsx` (or similar root component):**
    - Integrate the `RateLimitProvider` to wrap the main application content that requires rate limit awareness (e.g., wrap the `MainLayout` or the routes rendered within it).

**4. Implementation Plan:**

1.  **Create `frontend/my-app/src/contexts/RateLimitContext.tsx`:**
    - Define `RateLimitContextType` interface (matching the return type of `useRateLimits`).
    - Create `RateLimitContext = React.createContext<RateLimitContextType | undefined>(undefined)`.
    - Implement `RateLimitProvider`:
        - Takes `children` as props.
        - Calls `const rateLimitState = useRateLimits();` internally.
        - Returns `<RateLimitContext.Provider value={rateLimitState}>{children}</RateLimitContext.Provider>`.
    - Implement `useRateLimitContext`:
        - Gets context using `useContext(RateLimitContext)`.
        - Throws an error if context is undefined (meaning it's used outside the provider).
        - Returns the context value.
2.  **Integrate `RateLimitProvider`:**
    - Identify the appropriate component to wrap (likely in `App.tsx` around the authenticated routes or `MainLayout`).
    - Import and wrap the chosen component/section with `<RateLimitProvider>`.
3.  **Refactor `RateLimitsPanel.tsx`:**
    - Remove the import and direct call to `useRateLimits()`.
    - Import `useRateLimitContext` from `../../contexts/RateLimitContext`.
    - Replace the hook call with `const { rateLimits, isLoading, error, refetch } = useRateLimitContext();`.
4.  **Testing:**
    - Verify the original bug scenario: Load page, perform rate-limited action (e.g., generate), *then* open the panel. Panel should show correct, up-to-date info without getting stuck.
    - Verify the standard working scenario: Load page, open panel, perform action. Panel should update.
    - Verify periodic refresh still works within the panel.
    - Verify the manual refresh button in the panel still works.
    - Ensure no regressions in rate limit handling elsewhere.

**5. Alternatives Considered:**

- **Lifting State to Parent (`MainLayout.tsx`):** Moving `useRateLimits` directly into `MainLayout`. Less flexible, couples state tightly to layout, harder if other components need the data.
- **Global State Library (Zustand/Redux):** Overkill for this specific, localized state need. Context is more idiomatic for this scope.

