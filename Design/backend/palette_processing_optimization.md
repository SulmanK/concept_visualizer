# Palette Processing Optimisation Design Document

## Current Context

- The _ImageService_ orchestrates palette variation creation through `create_palette_variations`.
- For each palette the flow is:
  1. Apply palette to the base image (CPU-bound, <1 s).
  2. Upload the new image to Supabase Storage via HTTP (I/O-bound, ≈65-70 s).
- Cloud Run worker is limited to **540 s** per request when triggered by Pub/Sub.
- Sequential processing of 7 palettes now finishes in **≈509 s**, leaving just 31 s head-room.
- Any increase in palette count or latency will break the SLA; we need sustainable margin and faster throughput.

## Requirements

### Functional Requirements

- Generate _N_ palette variations for a concept image and store them in Supabase.
- Preserve existing API contracts and database schema.
- Behaviour must be toggled via configuration (`settings.py`).

### Non-Functional Requirements

- End-to-end processing of 7 palettes should complete in **≤300 s**.
- Solution must stay within single Cloud Run instance (no always-on resources).
- Zero loss of image quality noticeable to end-users.
- Observability: log timings per palette and overall run; expose Cloud Monitoring metrics.

## Design Decisions

### 1. Precise Instrumentation First

_Approach_: Add high-resolution timing around **palette processing** and **Supabase upload** steps.

- Rationale: We need empirical data to decide if the upload layer or the CPU image manipulation is dominant.
- Implementation: wrap `processing.process_image` and `persistence.store_image` calls with `time.perf_counter()` and emit structured logs: `STEP=process_palette START/END`, `STEP=upload_palette START/END`.
- Trade-off: Slight log noise increase (can be filtered by label).

### 2. Controlled Concurrency for Uploads (PNG retained)

_Approach_: Keep **parallel palette generation** but **cap concurrent uploads** with an async semaphore (e.g. `max_parallel_uploads = 2`).

- Rationale: Utilise I/O wait time; overlapping 2 uploads cuts wall-time nearly in half without memory explosion.
- Alternatives: Full concurrency (N uploads) – risks memory and 429s; Sequential – already at limit.

### 3. Streaming Upload API

_Approach_: Switch to Supabase `PUT /object/{bucket}/{path}` with chunked streaming instead of `POST` with full payload in memory.

- Rationale: Start transfer earlier, overlap encoding + network.
- Trade-off: More complex retry/error handling.

## Technical Design

### 1. Core Components

```python
class PaletteUploader:
    """Uploads PNG image bytes via async stream with timing instrumentation."""

    async def upload(self, img: bytes, *, user_id: str, filename: str) -> tuple[str, str]:
        start = perf_counter()
        path, url = await self._supabase_put(img, user_id, filename)
        logger.info("UPLOAD_COMPLETE", extra={"duration": perf_counter() - start})
        return path, url
```

- Integrated into `ImagePersistenceServiceInterface` implementation.
- `ImageService.create_palette_variations` will:
  1. Encode WEBP in memory.
  2. Await `uploader.upload` inside a bounded semaphore.

### 2. Data Models

No DB-schema changes; add `format` field to palette metadata for traceability.

### 3. Integration Points

- Supabase Storage REST endpoint (`/storage/v1/object/{bucket}`)
- Existing persistence service remains the single source of truth; new uploader is an internal helper.

## Implementation Plan

1. **Phase 1 – Instrumentation (0.5 day)**

   - Add timing wrappers and structured logs.
   - Deploy to **dev**, trigger sample run, collect metrics.

2. **Phase 2 – Bounded Concurrency (1 day)**

   - Introduce `max_parallel_uploads` setting.
   - Replace current `semaphore` limit (used for full processing) with separate semaphore just around `store_image`.
   - Target: 2 parallel uploads.

3. **Phase 3 – Streaming Uploads (optional, 2–3 days)**
   - Implement chunked uploader using `httpx.AsyncClient.stream("PUT", …)`.
   - Retry with exponential back-off on transient errors.

## Testing Strategy

- **Unit tests** for instrumentation helpers (ensure durations logged) and for upload concurrency logic.
- **Integration tests** in staging Supabase bucket measuring upload time; assert <15 s per file.
- Mock Supabase in CI to keep tests fast.

## Observability

- Add structured log lines:
  - `UPLOAD_START`, `UPLOAD_COMPLETE`, duration.
- Expose custom Cloud Run metric `palette_upload_seconds` via structured logs + Cloud Monitoring filter.

## Future Considerations

- Use Cloud Storage signed URLs (faster regional edge) if Supabase remains slow.
- Background "fan-out" model: publish palette tasks and let second worker upload – removes 540 s limit entirely.

## Dependencies

- No new runtime deps; may add `orjson` for structured log performance (optional).

## Security Considerations

- Preserve current signed-URL generation & expiry.
- WEBP conversion runs in-memory only; no temp files written to `/tmp`.

## Rollout Strategy

1. Deploy Phase 1 to **dev**, confirm logs.
2. If metrics good, promote to **prod**.
3. Repeat for phases 2 & 3.

## References

- Supabase Storage REST docs
- Google Cloud Run request-timeout limits
- Previous sequential run analysis (Design/task-design/log-sequential.md)
