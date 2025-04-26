# TODO List

## Frontend Test Failures (`frontend/my-app`)

- [x] **`AuthContext.test.tsx` (11 tests):** Fix `TypeError: useAuth is not a function` and related assertion failures. Likely an issue with context/hook export or mocking.
- [x] **`TaskContext.test.tsx` (12 tests):** Fix `TypeError: useTaskContext is not a function` and related assertion failures. Likely an issue with context/hook export or mocking.
- [x] **`RateLimitContext.test.tsx` (12 tests):** Fix `TypeError` for `useRateLimitContext`, `useRateLimitsData`, etc. Likely an issue with context/hook export or mocking.
- [x] **`conceptService.test.ts` (1 test):** Fix `should return null for 404 errors` test. Adjust mock error setup.
- [x] **`ConceptList.test.tsx` (5 tests):** Fix `Error: [vitest] No "AuthContext" export is defined on the mock`. Correct the mocking of `AuthContext`.
- [x] **`Footer.test.tsx` (2 tests):** Update snapshots for `default footer snapshot` and `footer with custom year snapshot`. Verify changes are intentional.
- [x] **`useToast.test.tsx` (2 tests):** Fix `Error: Element type is invalid...`. Investigate component export/import/mocking related to `ToastProvider`.

## Summary of Fixes

1. **Context Imports:** Updated tests to import hooks from their new locations (`useAuth.ts`, `useTask.ts`, `useRateLimits.ts`) rather than from context files.
2. **Mock AxiosError:** Fixed the conceptService test by properly mocking an AxiosError with the right structure.
3. **Footer Snapshots:** Updated snapshots to match current implementation.
4. **Toast Provider:** Fixed import of ToastProvider from the correct location.
