# ESLint Issues - TODO List

The following ESLint issues have been identified in the frontend codebase and need to be fixed.

- Make sure to run npx eslint to check if the issue still exists

## Completed Issues (117/133)

We've fixed the following categories of issues:

- 44/44 Component issues
- 25/30 Context issues (pending React refresh fixes)
- 17/17 Feature issues
- 36/36 Hook issues
- 22/47 Service issues

## Pending Issues (16/133)

### React Refresh Issues (15 issues)

These should be fixed by moving the inlined functions to separate files:

#### AuthContext (4 issues)

- [ ] Line 260
- [ ] Line 268
- [ ] Line 276
- [ ] Line 284

#### RateLimitContext (6 issues)

- [ ] Line 102
- [ ] Line 109
- [ ] Line 116
- [ ] Line 123
- [ ] Line 130
- [ ] Line 151

#### TaskContext (5 issues)

- [ ] Line 373
- [ ] Line 375
- [ ] Line 377
- [ ] Line 379
- [ ] Line 381
- [ ] Line 383
- [ ] Line 385
- [ ] Line 387
- [ ] Line 389

### Type Issues in apiInterceptors.test.ts (5 issues)

These are related to type issues in the test mocks:

- [ ] Fix generic type parameters in lines 11, 12
- [ ] Fix any type on line 43:35
- [ ] Fix any type on line 87:25

## Fixed Issues

- [x] Fixed `showErrorNotification` mock for tests
- [x] Fixed unused parameters in hook functions
- [x] Fixed missing dependencies in useEffect calls
- [x] Fixed many any types across the codebase
- [x] Fixed unused imports throughout the codebase

## Components (44 issues)

### Components/Concept Tests (5 issues)

- [x] Fix unused `waitFor` import in `ConceptForm.test.tsx:2:37`
- [x] Fix unused `FormStatus` import in `ConceptForm.test.tsx:5:10`
- [x] Fix unused `size` variable in `ConceptForm.test.tsx:123:24`
- [x] Fix unused `FormStatus` import in `ConceptRefinementForm.test.tsx:4:10`
- [x] Replace `any` type in `ConceptResult.test.tsx:42:26`

### Components/UI (9 issues)

- [x] Fix unused `Link` import in `ConceptCard.tsx:4:10`
- [x] Fix unused `gradient` variable in `ConceptCard.tsx:156:3`
- [x] Fix unused `variations` variable in `ConceptCard.tsx:162:3`
- [x] Fix unused `selectedColor` variable in `ConceptCard.tsx:328:9`
- [x] Fix unused `imageUrl` variable in `ConceptCard.tsx:356:9`
- [x] Add missing `handleDismiss` dependency to useEffect in `Toast.tsx:164:6`
- [x] Replace `any` type in `Button.test.tsx:29:40`
- [x] Replace `any` type in `Button.test.tsx:41:34`
- [x] Replace `any` type in `ColorPalette.test.tsx:103:64`

## Contexts (30 issues)

### AuthContext (7 issues)

- [x] Fix unused `useContext` import in `AuthContext.tsx:2:3`
- [x] Fix unused `isAnonymousUser` in `AuthContext.tsx:14:3`
- [x] Add missing `handleSignOut` dependency to useEffect in `AuthContext.tsx:71:6`
- [ ] Fix React refresh issues by moving constants/functions to separate files: [fix later]
  - [ ] Line 260
  - [ ] Line 268
  - [ ] Line 276
  - [ ] Line 284

### RateLimitContext (8 issues)

- [x] Fix `refetch` function dependency issue in `RateLimitContext.tsx:67:9`
- [ ] Fix React refresh issues by moving constants/functions to separate files:[fix later]
  - [ ] Line 102
  - [ ] Line 109
  - [ ] Line 116
  - [ ] Line 123
  - [ ] Line 130
  - [ ] Line 151

### TaskContext (15 issues)

- [x] Fix unused `useContext` import in `TaskContext.tsx:2:3`
- [x] Fix unused `pollingInterval` variable in `TaskContext.tsx:112:3`
- [x] Fix unused `taskContextData` variable in `TaskContext.tsx:179:9`
- [ ] Fix React refresh issues by moving constants/functions to separate files:[fix later]
  - [ ] Line 363
  - [ ] Line 373
  - [ ] Line 375
  - [ ] Line 377
  - [ ] Line 379
  - [ ] Line 381
  - [ ] Line 383
  - [ ] Line 385
  - [ ] Line 387
  - [ ] Line 389

### Context Tests (8 issues)

- [x] Fix unused `waitFor` import in `RateLimitContext.test.tsx:5:3`
- [x] Fix unused `useRateLimitsQueryModule` in `RateLimitContext.test.tsx:75:13`
- [x] Fix unused `renderHook` import in `TaskContext.test.tsx:7:3`
- [x] Fix unused `mockErrorCallback` in `TaskContext.test.tsx:44:5`
- [x] Fix unused `mockStatusCallback` in `TaskContext.test.tsx:45:5`
- [x] Fix unused hooks in `TaskContext.test.tsx`:
  - [x] `useActiveTaskId` (line 100:3)
  - [x] `useTaskInitiating` (line 101:3)
  - [x] `useOnTaskCleared` (line 102:3)

## Features (17 issues)

### ConceptDetailPage (8 issues)

- [x] Fix unused `useMemo` import in `ConceptDetailPage.tsx:8:3`
- [x] Fix unused `Suspense` import in `ConceptDetailPage.tsx:10:3`
- [x] Fix unused `useQueryClient` import in `ConceptDetailPage.tsx:20:10`
- [x] Fix unused `eventService` import in `ConceptDetailPage.tsx:21:10`
- [x] Fix unused `AppEvent` import in `ConceptDetailPage.tsx:21:24`
- [x] Fix unused `EnhancedImagePreview` variable in `ConceptDetailPage.tsx:24:7`
- [x] Fix unused `refetch` variable in `ConceptDetailPage.tsx:70:5`
- [x] Fix unused `conceptId` variable in `ConceptDetailPage.tsx:658:9`

### ExportOptions (2 issues)

- [x] Fix ref value in effect cleanup in `ExportOptions.tsx:197:39`
- [x] Add missing `storagePath` dependency to useCallback in `ExportOptions.tsx:242:6`

### RefinementPage (7 issues)

- [x] Fix unused `useSearchParams` import in `RefinementPage.tsx:6:3`
- [x] Fix unused `useAuth` import in `RefinementPage.tsx:15:3`
- [x] Fix unused `TaskResponse` import in `RefinementPage.tsx:20:10`
- [x] Fix unused `isAuthLoading` variable in `RefinementPage.tsx:35:9`
- [x] Fix unused `handleAsyncError` in `RefinementPage.tsx:37:9`
- [x] Replace `any` type in `RefinementPage.tsx:42:58`
- [x] Fix unused variables in `RefinementPage.tsx`:
  - [x] `refineConceptMutation` (line 94:13)
  - [x] `isSuccess` (line 97:5)
  - [x] `refinementPrompt` (line 135:5)
  - [x] `logoDescription` (line 136:5)
  - [x] `themeDescription` (line 137:5)
  - [x] `preserveAspects` (line 138:5)

### RefinementSelectionPage Tests (2 issues)

- [x] Fix unused `queryClient` in `RefinementSelectionPage.test.tsx:60:9`
- [x] Fix unused `Wrapper` variable in `RefinementSelectionPage.test.tsx:69:9`

### RefinementActions (2 issues)

- [x] Fix unused `refinedConceptId` in `RefinementActions.tsx:17:3`
- [x] Fix unused `selectedColor` in `RefinementActions.tsx:18:3`

## Hooks (36 issues)

### Hook Tests (15 issues)

- [x] Fix unused imports in `useErrorHandling.test.tsx`:
  - [x] `React` (line 1:8)
  - [x] `ReactNode` (line 1:17)
  - [x] `ErrorCategory` (line 4:28)
  - [x] Fix unused `ValidationError` in line 38:7
  - [x] Fix unused `ApiError` in line 48:7
- [x] Fix unused `React` import in `useNetworkStatus.test.tsx:1:8`
- [x] Replace `any` type in `useRateLimitsQuery.test.ts:200:86`
- [x] Fix unused `mockCompletedTaskResponse` in `useTaskQueries.test.ts:39:7`
- [x] Fix unused imports in `useTaskSubscription.test.ts`:
  - [x] `renderHook` (line 1:10)
  - [x] `act` (line 1:22)
  - [x] `waitFor` (line 1:27)
  - [x] `TASK_STATUS` (line 6:10)
- [x] Fix unused variables in `useTaskSubscription.test.ts`:
  - [x] `mockProcessingTask` (line 40:7)
  - [x] `mockCompletedTask` (line 45:7)
  - [x] `mockFailedTask` (line 51:7)
  - [x] `mockSubscribeCallback` (line 61:5)
  - [x] `useTaskSubscription` (line 73:10)
  - [x] `createWrapper` (line 79:9)
- [x] Fix require-style import in `useTaskSubscription.test.ts:101:26`
- [x] Fix unused `vi` import in `useToast.test.tsx:4:10`

### Animation Hooks (1 issue)

- [x] Add missing `value` dependency to useEffect in `useAnimatedValue.tsx:160:6`

### useConceptMutations (6 issues)

- [x] Fix unused `useToast` import in `useConceptMutations.ts:8:10`
- [x] Fix unused `ConceptData` import in `useConceptMutations.ts:18:10`
- [x] Replace `any` type in `useConceptMutations.ts:23:45`
- [x] Fix unused `user` variable in `useConceptMutations.ts:81:11`
- [x] Fix unused variables in `useConceptMutations.ts`:
  - [x] `isRateLimited` (line 91:10)
  - [x] `rateLimitDetails` (line 92:10)
  - [x] `user` (second instance, line 334:11)
  - [x] `isRateLimited` (second instance, line 344:10)
  - [x] `rateLimitDetails` (second instance, line 345:10)

### useErrorHandling (6 issues)

- [x] Fix unused `formatTimeRemaining` import in `useErrorHandling.tsx:3:10`
- [x] Replace `any` types in:
  - [x] Line 195:28
  - [x] Line 264:28
  - [x] Line 305:30
  - [x] Line 371:32
- [x] Fix unused `e` variable in:
  - [x] Line 290:16
  - [x] Line 315:20

### Other Hooks (8 issues)

- [x] Fix unused `RateLimitError` in `useExportImageMutation.ts:10:3`
- [x] Replace `any` type in `useExportImageMutation.ts:35:30`
- [x] Fix unused `error` in `useNetworkStatus.tsx:98:14`
- [x] Add missing `updateOnlineStatus` dependency in `useNetworkStatus.tsx:114:6`
- [x] Replace `any` type in `useNetworkStatus.tsx:171:40`
- [x] Replace `any` type in `useSessionQuery.ts:9:18`
- [x] Replace `any` type in `useTaskSubscription.ts:28:29`
- [x] Add missing `createAndSubscribeToChannel` dependency in `useTaskSubscription.ts:178:6`
- [x] Fix React refresh issues in `useToast.tsx`:
  - [x] Line 176:14
  - [x] Line 186:16

## Services (47 issues)

### Service Tests (36 issues)

- [x] Fix unused imports in `apiClient.test.ts`:
  - [x] `afterEach` (not present)
  - [x] `AxiosInstance` (not present)
  - [x] `AxiosRequestConfig` (not present)
  - [x] `AxiosResponse` (not present)
- [x] Replace `any` type in `apiClient.test.ts:56:35` (already fixed with ErrorWithIsAxiosErrorFlag)
- [x] Fix unused variables in `apiClient.test.ts`:
  - [x] `setAuthToken` (not present)
  - [x] `clearAuthToken` (not present)
  - [x] `axios` (not present)
- [x] Fix unused `axios` import in `apiInterceptors.test.ts:7:8`
- [ ] Replace `any` types in `apiInterceptors.test.ts`:
  - [x] Line 13:48 with Promise<AxiosResponse | never>
  - [ ] Line 11:43 and 11:59
  - [ ] Line 12:46 and 12:54
  - [ ] Line 43:35
  - [ ] Line 87:25
- [x] Add missing mock for `showErrorNotification` in `apiInterceptors.test.ts` that's used in lines 277, 298, and 317
