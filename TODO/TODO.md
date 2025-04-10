# Concept Visualizer - Project TODO

## Export Options Refactoring

### Phase 1: Backend Implementation (New Endpoint & Logic)

- [x] Define new API endpoint
  - [x] Create `backend/app/api/routes/export/export_routes.py` and `backend/app/api/routes/export/__init__.py`
  - [x] Define `POST /api/export/process` route
  - [x] Create Pydantic request model in `backend/app/models/export/request.py`
  - [x] Implement response handling (Direct File Response)
  - [x] Add authentication protection

- [x] Implement backend service logic
  - [x] Create or modify service in `backend/app/services/export/service.py`
  - [x] Implement secure image fetching based on image identifier
  - [x] Implement processing logic for different formats (PNG/JPG/SVG)
  - [x] Move and refactor vtracer logic from old SVG endpoint
  - [x] Implement direct file response handling

- [x] Register new route in `backend/app/api/router.py`

- [x] Add rate limiting to export endpoint

### Phase 2: Frontend Refactoring (Adopt New Endpoint)

- [x] Update API client
  - [x] Add `exportImage` function to `frontend/my-app/src/services/apiClient.ts`
  - [x] Handle appropriate response types (Blob)

- [x] Create new React Query mutation hook
  - [x] Create `frontend/my-app/src/hooks/useExportImageMutation.ts`
  - [x] Implement download functionality in `onSuccess` handler
  - [x] Add error handling with `createQueryErrorHandler`

- [x] Refactor `ExportOptions.tsx` component
  - [x] Remove old client-side Canvas processing logic
  - [x] Remove usage of old `useSvgConversionMutation` hook
  - [x] Integrate new `useExportImageMutation` hook
  - [x] Update download and preview buttons to use new mutation
  - [x] Update error handling

- [x] Clean up old SVG hook
  - [x] Remove `frontend/my-app/src/hooks/useSvgConversionMutation.ts`
  - [x] Remove related imports

### Phase 3: Backend Cleanup

- [x] Remove old SVG endpoint
  - [x] Delete `backend/app/api/routes/svg/converter.py`
  - [x] Update `backend/app/api/routes/svg/__init__.py` or remove directory
  - [x] Update `backend/app/api/router.py` to remove old SVG router

- [x] Remove old SVG models
  - [x] Delete `backend/app/models/svg/conversion.py` if unused
  - [x] Update related import files

- [x] Final code review and testing
  - [x] Search codebase for remaining dependencies on old SVG endpoint/models
  - [x] Update SVG exceptions to more generic Export exceptions
  - [x] Test all export formats and sizes
  - [x] Verify rate limiting functionality

## Image Processing and Rate Limit Improvements

### Part 1: Fix Image Palette Application

- [x] Rework image processing in LAB color space
  - [x] Modify `apply_palette_with_masking_optimized` function in `backend/app/services/image/processing.py`
  - [x] Convert image to LAB color space for better color handling
  - [x] Implement lightness-based color mapping for palette application
  - [x] Remove or simplify K-means logic for dominant color extraction
  - [x] Add helper functions for LAB conversion and lightness sorting if needed
  - [x] Optimize processing using vectorized operations
  - [x] Implement robust error handling

### Part 2: Refactor Export Rate Limiting

- [x] Consolidate export rate limits
  - [x] Define unified export limit category (e.g., `export_action`)
  - [x] Set appropriate rate limit string (e.g., "50/hour")

- [x] Backend rate limit changes
  - [x] Modify export route in `backend/app/api/routes/export/export_routes.py`
  - [x] Replace format-specific rate limits with single unified rate limit
  - [x] Update rate limit configuration in relevant files if needed
  - Great!

- [x] Frontend rate limit changes  
  - [x] Update rate limit types in `frontend/my-app/src/services/rateLimitService.ts`
  - [x] Modify `RateLimitCategory` type and related interfaces
  - [x] Update mapping functions for endpoints and categories
  - [x] Update export mutation hook in `frontend/my-app/src/hooks/useExportImageMutation.ts`
  - [x] Modify rate limit UI components in `frontend/my-app/src/components/RateLimitsPanel/RateLimitsPanel.tsx`

