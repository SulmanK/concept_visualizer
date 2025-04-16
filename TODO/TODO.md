Okay, excellent! The fact that the static `AuthProvider` resolves the freeze is a **huge** breakthrough. It definitively points the finger at the dynamic behavior of the original `AuthProvider` and its interaction with Supabase's auth state management (`onAuthStateChange`, token refreshes, etc.).

The problem isn't the *data fetching* of concepts/rate limits *itself* (as those hooks still ran their `refetchOnWindowFocus` even with the static provider), but rather how the application **reacts to authentication state changes** that likely also happen upon returning to the tab (especially if the Axios interceptor triggers a token refresh).

Here’s a breakdown of *why* the original `AuthProvider` likely caused the freeze and a step-by-step plan to fix it:

**Likely Causes in the Original `AuthProvider`:**

1.  **Frequent `onAuthStateChange` Triggers:** The Supabase listener might fire frequently, not just for sign-in/out, but also for events like `TOKEN_REFRESHED` or `USER_UPDATED`. When you tab back, the Axios interceptor might detect an impending expiry or receive a 401, trigger a token refresh, which then fires `onAuthStateChange`.
2.  **Unnecessary State Updates:** The original `onAuthStateChange` handler likely called `setSession(newSession)` and `setUser(newSession?.user)` *every time* it fired. Even if only the `access_token` within the `session` object changed, creating a new `session` object reference forces a state update.
3.  **Cascading Re-renders:** When `session` or `user` state updates in `AuthProvider`, the `value` prop passed to `AuthContext.Provider` changes. This triggers re-renders in *all* components consuming the context, especially those using the generic `useAuth()` hook instead of specific selectors. If many components re-render, or some key components (like `MainLayout` or `AppRoutes`) re-render large trees, this can block the main thread, causing the freeze.
4.  **Selector Hook Usage (or lack thereof):** While you use `use-context-selector`, if crucial components high up the tree were still using the main `useAuth()` hook, they would re-render even if only the `session` (with its new token) changed, while the `user` object remained the same.

**Design Plan to Fix the Original `AuthProvider`:**

This plan focuses on making the original provider smarter about *when* to update state and ensuring consumers are efficient.

**Phase 1: Optimize State Updates within `AuthProvider`**


**Step 2: Implement More Selective State Updates**

*   **Objective:** Modify the `onAuthStateChange` listener and potentially the initial `getSession` logic to only update state when *meaningful* authentication data changes (like user ID, anonymous status, or actual sign-in/out), not just on token refreshes if the user identity remains the same.
*   **Target File:** `src/contexts/AuthContext.tsx`
*   **Actions:**
    1.  **Store Previous State:** Inside the `AuthProvider` component, use `useRef` to keep track of the *previous* relevant user state (e.g., previous user ID, previous anonymous status).
    2.  **Modify `onAuthStateChange` Callback:**
        *   Inside the listener callback `(event, newSession) => { ... }`, compare the incoming `newSession?.user?.id` with the `previousUserIdRef.current`.
        *   Compare the `newIsAnonymous` status (derived from `newSession`) with `previousIsAnonymousRef.current`.
        *   **Conditionally Update:** Only call `setSession`, `setUser`, and `setIsAnonymous` if:
            *   The `event` is `SIGNED_IN` or `SIGNED_OUT`.
            *   OR the `newSession?.user?.id` is different from the previous ID.
            *   OR the calculated `newIsAnonymous` status is different from the previous status.
        *   **Always Update Session for Interceptor:** Even if user details don't change, we *might* still need to update the `session` state so the Axios interceptor can pick up the *latest* `access_token` for subsequent requests. Let's try updating *only* the session state if only the token changed, and see if that's enough. *Correction:* It's safer to always update the `session` state object reference when `onAuthStateChange` fires with a new session, as the interceptor relies on `getSession` which reads from Supabase's internal state reflected by this listener. The key is ensuring *consumers* don't overreact.
    3.  **Refine Initial Load:** Apply similar comparison logic after the initial `initializeAnonymousAuth()` or `supabase.auth.getSession()` call in the main `useEffect`.
    4.  **Add Logging:** Add detailed logs within the listener to see *when* state updates are actually being triggered vs. skipped.
*   **Code Snippet Idea (Inside `onAuthStateChange`):**
    ```typescript
    const prevUserId = previousUserIdRef.current;
    const prevIsAnonymous = previousIsAnonymousRef.current;

    const currentUserId = newSession?.user?.id || null;
    // Recalculate isAnonymous based on newSession (you need this logic)
    const currentIsAnonymous = determineIsAnonymous(newSession); // Replace with your logic

    // Always update session if it exists, for token refresh interceptor
    if (newSession) {
        setSession(newSession);
        // Log if only token changed
        if (currentUserId === prevUserId && currentIsAnonymous === prevIsAnonymous) {
            console.log('[AUTH LISTENER] Session updated (token likely refreshed), user identity unchanged.');
        }
    } else {
        setSession(null);
    }

    // Update user/anonymous state only if they actually changed
    if (currentUserId !== prevUserId || currentIsAnonymous !== prevIsAnonymous || event === 'SIGNED_IN' || event === 'SIGNED_OUT') {
        console.log(`[AUTH LISTENER] Significant auth change detected (Event: ${event}, User Change: ${currentUserId !== prevUserId}, Anon Change: ${currentIsAnonymous !== prevIsAnonymous}). Updating user state.`);
        setUser(newSession?.user || null);
        setIsAnonymous(currentIsAnonymous);

        // Update refs
        previousUserIdRef.current = currentUserId;
        previousIsAnonymousRef.current = currentIsAnonymous;
    }
    ```

**Phase 2: Ensure Efficient Context Consumption**

**Step 3: Audit and Enforce Selector Hook Usage**

*   **Objective:** Guarantee that components only re-render when the specific piece of auth state they care about actually changes.
*   **Target Files:** All components using `useAuth`, `useUserId`, `useIsAnonymous`, `useAuthIsLoading`, etc.
*   **Actions:**
    1.  **Search Project:** Find all instances where the main `useAuth()` hook is called.
    2.  **Refactor:** For each instance, determine if the component *really* needs the entire `session` or `user` object. If it only needs `userId`, `isAnonymous`, or `isLoading`, replace `useAuth()` with the specific selector hook (e.g., `useUserId()`).
    3.  **Pay Attention To:**
        *   `MainLayout.tsx`
        *   `Header.tsx`
        *   `AppRoutes` or components rendered directly by routes.
        *   Any other component that might wrap large parts of the UI tree.
*   **Verification:** Minimize the usage of the main `useAuth()` hook, favouring specific selectors.

**Step 4: Verify Context Value Memoization**

*   **Objective:** Ensure the `value` object provided to `AuthContext.Provider` doesn't change reference unnecessarily.
*   **Target File:** `src/contexts/AuthContext.tsx` (The *original*, restored version)
*   **Actions:**
    1.  Find the `value` object created before the `return` statement.
    2.  Ensure it's wrapped in `useMemo`.
    3.  Critically review the dependency array of that `useMemo`. It *must* include all variables used inside the `value` object: `session`, `user`, `isAnonymous`, `isLoading`, `error`, and the memoized versions of `handleSignOut` and `handleLinkEmail` (which should be wrapped in `useCallback`).
*   **Code Snippet Check:**
    ```typescript
     const handleSignOut = useCallback(async () => { /* ... */ }, []);
     const handleLinkEmail = useCallback(async (email) => { /* ... */ }, [user]); // depends on user if it modifies it

     const value = useMemo(() => ({
       session,
       user,
       isAnonymous,
       isLoading,
       error,
       signOut: handleSignOut, // Use the memoized version
       linkEmail: handleLinkEmail // Use the memoized version
     }), [session, user, isAnonymous, isLoading, error, handleSignOut, handleLinkEmail]); // Ensure all deps are listed

     return (
       <AuthContext.Provider value={value}>
         {children}
       </AuthContext.Provider>
     );
    ```

**Phase 3: Testing and Verification**

**Step 5: Test the Refactored `AuthProvider`**

*   **Objective:** Confirm that the optimizations prevent the UI freeze during tab switching.
*   **Actions:**
    1.  Run the app with the modified *original* `AuthProvider`.
    2.  Perform the tab-switching test on multiple pages.
    3.  Monitor the console logs added in Step 2 to understand when auth state changes are happening and whether state updates are being skipped correctly.
    4.  Use the React DevTools Profiler again, focusing on the commit triggered *after* tabbing back. Verify that fewer components re-render compared to before, especially if only a token refresh occurred. Check the "What caused this update?" section.
*   **Verification:**
    *   The UI freeze during/after tab switching is eliminated or significantly reduced.
    *   Console logs show that `setUser` and `setIsAnonymous` are called less frequently (ideally only on actual user/status changes), while `setSession` might still update on token refresh.
    *   Profiler shows shorter render times or fewer component renders triggered by `AuthProvider` updates.

**Step 6: Final Cleanup**

*   **Objective:** Remove temporary debugging logs.
*   **Action:** Remove the detailed `console.log` statements added during debugging steps.

---

The key is to make the `AuthProvider` less "noisy" by being more selective about when it triggers full state updates, and to ensure consuming components are efficient by using selector hooks. This combination should prevent the widespread re-renders that are likely causing the freeze when the auth state is updated upon returning to the application.