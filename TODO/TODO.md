Okay, let's create a step-by-step design plan to complete the refactoring and address the identified issues, focusing on simplifying the frontend state management around image URLs.

**Goal Recap:**

1.  Ensure frontend components *directly* use the pre-signed `image_url` provided by the refactored backend API and hooks.
2.  Remove legacy client-side URL processing logic.
3.  Clean up unused utility functions related to old URL handling.
4.  Verify this fixes state inconsistencies, particularly potential bugs related to tab switching and data refetching.

---

**Refactoring Action Plan**

**Phase 1: Component-Level Refactoring (Task 7 Continuation)**

**Step 1: Simplify `ConceptCard.tsx` URL Handling** [x]

*   **Objective:** Modify `ConceptCard` to trust and directly use the `image_url` fields provided in the `concept` prop (which comes from the API via `useRecentConcepts`). Remove internal URL processing.
*   **Target File:** `src/components/ui/ConceptCard.tsx`
*   **Actions:**
    1.  **Remove Imports:** Delete the import and usage of `formatImageUrl` from `../../services/supabaseClient`. [x]
    2.  **Remove Helper:** Delete the internal `processImageUrl` helper function. [x]
    3.  **Simplify `logoImageUrl`:** Modify the `useMemo` hook for `logoImageUrl`. [x]
        *   It should *directly* return the appropriate URL based on `selectedVariationIndex`:
            *   If `selectedVariationIndex` points to the original (index 0 if `includeOriginal` is true, or always index 0 if no variations), use `concept.image_url` (or `concept.base_image_url` as fallback).
            *   If `selectedVariationIndex` points to a specific variation, use `concept.color_variations[index].image_url`.
            *   Handle cases where URLs might be missing (return a placeholder or empty string).
        *   Remove any calls to `formatImageUrl` or `processImageUrl`.
    4.  **Verify `OptimizedImage` Props:** Ensure the simplified `logoImageUrl` is correctly passed to the `<OptimizedImage>` component's `src` prop. [x]
    5.  **Remove `sampleImageUrl` Logic (if feasible):** If sample concepts can also provide a direct `image_url`, simplify the logic further by removing the special handling for `sampleImageUrl`. If needed, ensure it's just passed directly. [x]
*   **Verification:**
    *   The `ConceptCard` component renders correctly using data from `useRecentConcepts`.
    *   Both the main "logo" image and the header background/initials display correctly.
    *   Selecting different color variation dots updates the main logo image correctly using the `image_url` from the selected variation.
    *   No console errors related to URL processing within `ConceptCard`.

**Step 2: Refactor `RecentConceptsSection.tsx`** [x]

*   **Objective:** Simplify the data adaptation logic now that `ConceptCard` handles URLs directly.
*   **Target File:** `src/features/landing/components/RecentConceptsSection.tsx`
*   **Actions:**
    1.  **Review `adaptConceptForUiCard`:** Analyze if this function is still necessary or can be significantly simplified. [x]
        *   Ideally, the `concept` object fetched by `useRecentConcepts` should be passable directly (or with minimal transformation like generating initials) to `ConceptCard`.
        *   Remove any logic within the adapter that processes or selects URLs (e.g., generating the `images` array if `ConceptCard` no longer needs it).
    2.  **Update Prop Passing:** Ensure the necessary props (like `concept`, `onEdit`, `onViewDetails`) are passed correctly to the simplified `ConceptCard`. [x]
*   **Verification:**
    *   The recent concepts section renders correctly.
    *   `ConceptCard` components within the section display the correct images and variations.
    *   `onEdit` and `onViewDetails` handlers still function correctly.

**Step 3: Review `ConceptResult.tsx` URL Handling** [x]

*   **Objective:** Ensure `ConceptResult` also trusts the API-provided `image_url` and doesn't perform unnecessary client-side processing.
*   **Target File:** `src/components/concept/ConceptResult.tsx`
*   **Actions:**
    1.  **Analyze `getFormattedUrl`:** Determine if this internal helper is still needed. If the `concept.image_url` (and variation URLs) from the API/hooks are always ready-to-use signed URLs, this function might just need to return the input URL or handle null/undefined cases. [x]
    2.  **Review `formatImageUrl` Prop:** Check where this prop is passed *from*. Ensure the calling component (likely `ResultsSection` or similar) provides a reliable URL or remove the prop dependency if the internal `concept.image_url` is sufficient. [x]
    3.  **Simplify `getCurrentImageUrl`:** Ensure this function correctly selects the `image_url` from the `concept` or the selected `variation` without extra processing. [x]
*   **Verification:**
    *   The `ConceptResult` component displays the correct image (original or selected variation).
    *   The download button (`handleDownload`) uses the correct, final image URL.

**Step 4: Verify `OptimizedImage.tsx`** [x]

*   **Objective:** Confirm the `OptimizedImage` component functions correctly with potentially long, signed URLs containing tokens.
*   **Target File:** `src/components/ui/OptimizedImage.tsx`
*   **Actions:**
    1.  **Test Rendering:** Manually test or add a specific story/test case where `OptimizedImage` is given a long, complex URL similar to a Supabase signed URL. [x]
    2.  **Review Error Handling:** Ensure the `onError` handler provides useful feedback if a signed URL fails to load (e.g., expired token, invalid path). [x]
*   **Verification:**
    *   `OptimizedImage` renders images correctly when passed valid signed URLs.
    *   Error states are handled gracefully.

---

**Phase 2: Code Cleanup (Task 8 Continuation)**

**Step 5: Remove Legacy URL Utilities** [x]

*   **Objective:** Eliminate unused and potentially confusing URL helper functions from the Supabase client service.
*   **Target File:** `src/services/supabaseClient.ts`
*   **Actions:**
    1.  **Delete Functions:** Remove the implementations of `formatImageUrl`, `getImageUrl`, and `getSignedImageUrl`. [x]
    2.  **Update Imports:** Search the codebase for any remaining imports of these functions and remove them or refactor the calling code to no longer need them (should have been done in Phase 1). [x]
*   **Verification:**
    *   The application builds and runs without errors after removal.
    *   All image displays and related functionality still work correctly, relying solely on the `image_url` provided by the API/hooks.

---

**Phase 3: Verification and Testing**

**Step 6: Focused Testing** [x]

*   **Objective:** Verify the refactoring fixed the original state/tab-switching bug and didn't introduce regressions.
*   **Actions:**
    1.  **Tab Switching Test:**
        *   Navigate to pages displaying concepts (`/`, `/recent`, `/concepts/:id`).
        *   Switch to another browser tab and wait (e.g., 30-60 seconds to potentially allow query cache to go stale or trigger background refetch).
        *   Switch back to the application tab.
        *   Observe: Does the UI remain responsive? Are images displayed correctly? Does the state update consistently after the `refetchOnWindowFocus` trigger?
    2.  **Navigation Test:** Navigate between the landing page, recent concepts, concept detail, and refinement pages. Ensure images load correctly and consistently on each page.
    3.  **Interaction Test:** Interact with `ConceptCard` components (clicking variations) and verify the main image updates reliably.
    4.  **Refetch Test:** Use React Query DevTools to manually trigger refetches for `useRecentConcepts` and `useConceptDetail` and ensure the UI updates correctly without breaking.
*   **Verification:**
    *   The UI remains responsive and functional after switching tabs and triggering data refetches.
    *   Images load consistently across different views and interactions.
    *   No console errors related to state updates or URL handling.

**Step 7: Review DevTools and Logs** [x]

*   **Objective:** Use debugging tools to confirm the intended data flow.
*   **Actions:**
    1.  **React Query DevTools:** Inspect the data cached for `concepts/recent` and `concepts/detail` queries. Confirm that the `image_url` fields contain complete, signed URLs. Observe query states during tab switching and refetches.
    2.  **Console Logs:** Temporarily add specific logs (using `devLog`) in hooks and components to trace the `image_url` from the API response through the hooks and into the component props (`ConceptCard`, `OptimizedImage`). Remove before finalizing.
*   **Verification:**
    *   Data flow is as expected: API -> Hook -> Component -> `<img>` src attribute.
    *   No unnecessary URL processing is happening in the frontend components.



---

This plan provides a structured approach to completing the refactoring, focusing on the component layer where the issues likely reside, followed by cleanup and thorough verification. Remember to commit changes incrementally after each logical step.