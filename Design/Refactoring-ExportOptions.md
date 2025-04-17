
---

## Refactoring Plan: Centralized Export Endpoint

### Phase 1: Backend Implementation (New Endpoint & Logic)

1.  **Define New API Endpoint:**
    *   **File:** Create `backend/app/api/routes/export/export_routes.py` and `backend/app/api/routes/export/__init__.py`.
    *   **Route:** Define `POST /api/export/process`.
    *   **Request Body Model:** Create a Pydantic model (e.g., in `backend/app/models/export/request.py`) accepting:
        *   `image_identifier`: `str` (Storage path like `user_id/.../image.png`). **Backend MUST validate ownership.**
        *   `target_format`: `Literal['png', 'jpg', 'svg']`
        *   `target_size`: `Literal['small', 'medium', 'large', 'original']`
        *   *(Optional)* `svg_params`: `dict` (For fine-tuning SVG conversion if needed).
    *   **Response:** Choose a strategy:
        *   **(A) Direct File Response (Recommended):** Use FastAPI's `StreamingResponse` or `FileResponse`. Set `Content-Type` and `Content-Disposition` headers.
        *   **(B) Signed URL Response:** Upload processed file to temporary storage, return `{ "downloadUrl": "..." }`. (More complex).
    *   **Authentication:** Protect the endpoint using FastAPI `Depends` for authenticated users.

2.  **Implement Backend Service Logic:**
    *   **File:** Modify/add functions in `backend/app/services/image/service.py` or create `backend/app/services/export/service.py`.
    *   **Fetch Original:** Implement secure fetching using `image_identifier` and the authenticated user's ID. **Do not trust client URLs.** Use storage client methods.
    *   **Processing:**
        *   Use Pillow/OpenCV for resizing and PNG/JPG conversion.
        *   **Reuse SVG Logic:** If `target_format == 'svg'`, **move** the `vtracer` logic from the old SVG endpoint (`backend/app/api/routes/svg/converter.py`) into this service. Pass `svg_params` if needed.
    *   **Response Handling:** Implement the chosen response strategy (Direct File or Signed URL).

3.  **Register New Route:**
    *   **File:** `backend/app/api/router.py`
    *   Import and include the new export router in the main `api_router`.

4.  **Add Rate Limiting:**
    *   **File:** `backend/app/api/routes/export/export_routes.py`
    *   Apply rate limits using `Depends(RateLimiter(...))` or utilities. Consider separate limits for SVG.

### Phase 2: Frontend Refactoring (Adopt New Endpoint)

1.  **Update API Client:**
    *   **File:** `frontend/my-app/src/services/apiClient.ts`
    *   Add `exportImage(params: ExportRequestParams): Promise<Blob | { downloadUrl: string }>`.
    *   This function calls `POST /api/export/process`.
    *   Handle the response type correctly (Blob or JSON). Use `responseType: 'blob'` if expecting direct file data.

2.  **Create New React Query Mutation Hook:**
    *   **File:** Create `frontend/my-app/src/hooks/useExportImageMutation.ts`.
    *   Use `useMutation` from `@tanstack/react-query`.
    *   **`mutationFn`:** Calls `apiClient.exportImage`.
    *   **`onSuccess`:** Triggers the browser download:
        *   Blob: Create object URL -> trigger link click -> revoke object URL.
        *   JSON `{ downloadUrl }`: Use `window.location.href` or trigger link click with the URL.
    *   **`onError`:** Use `createQueryErrorHandler` for standard error handling/toasts.
    *   Include optimistic updates for the appropriate rate limit category.

3.  **Refactor `ExportOptions.tsx` Component:**
    *   **File:** `frontend/my-app/src/features/concepts/detail/components/ExportOptions.tsx` (or similar).
    *   **Remove Old Logic:** Delete client-side Canvas processing, `useSvgConversionMutation` usage, and related state (`processedImageUrl`, `isAutoProcessing`).
    *   **Integrate New Hook:** Import and use `useExportImageMutation`.
    *   **Update Download Button (`handleDownloadClick`):**
        *   Call `mutate` from `useExportImageMutation`, passing `imageUrl`/`imagePath`, `selectedFormat`, `selectedSize`.
        *   Use the hook's `isPending` for loading state.
    *   **Update Preview Button (`handlePreview`):**
        *   **(A) Backend Preview:** Call `mutate`, handle `onSuccess` by opening the Blob URL/Signed URL in a new tab.
        *   **(B) Client Preview (PNG/JPG Only - Optional):** Keep *minimal* Canvas logic for quick PNG/JPG previews if desired. SVG preview still uses the backend. (Recommendation: Use backend).
    *   **Error Display:** Use `error` from the mutation hook with `ErrorMessage`.

4.  **Cleanup Old SVG Hook:**
    *   **File:** Delete `frontend/my-app/src/hooks/useSvgConversionMutation.ts`.
    *   Remove imports referencing it.

### Phase 3: Backend Cleanup

1.  **Remove Old SVG Endpoint:**
    *   **File:** Delete `backend/app/api/routes/svg/converter.py`.
    *   **File:** Update `backend/app/api/routes/svg/__init__.py` (or remove directory if empty).
    *   **File:** Update `backend/app/api/router.py` to remove the old SVG router inclusion.

2.  **Remove Old SVG Models:**
    *   **File:** Delete `backend/app/models/svg/conversion.py` if `SVGConversionRequest`/`Response` are unused.
    *   Update `backend/app/models/svg/__init__.py` and `backend/app/models/__init__.py`.

3.  **Code Review:** Search codebase for any remaining dependencies on the old SVG endpoint/models.



---
This consolidated approach will result in a cleaner, more efficient, and easier-to-maintain export feature.