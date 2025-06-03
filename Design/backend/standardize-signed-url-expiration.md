# Design Document: Standardize Signed URL Expiration to 31 Days

## Overview

This document outlines the plan to standardize all signed URL expiration times from their current varying durations (1 hour to 4 days) to a consistent 31-day period that aligns with the application's 30-day file retention policy.

## Problem Statement

Currently, the codebase has inconsistent signed URL expiration times:

- `ImagePersistenceService.get_signed_url()`: 4 days (345,600 seconds)
- `ImageStorage.get_image_url()`: 4 days (345,600 seconds)
- `ImagePersistenceService.get_image_url()`: 1 hour (3,600 seconds)
- `ImageStorage.get_signed_url()`: 1 hour (3,600 seconds)
- Frontend `createSignedUrl`: 3 days (259,200 seconds)

These short expiration times cause URLs to expire while files are still stored (30-day retention), forcing unnecessary URL regeneration and potentially breaking user workflows.

## Solution

Standardize ALL signed URLs to expire after 31 days (2,678,400 seconds), providing:

- Alignment with 30-day file retention policy
- One extra day as safety buffer
- Consistent behavior across the entire application
- Reduced need for URL regeneration

## Technical Changes

### Backend Changes

#### 1. ImagePersistenceService

**File**: `backend/app/services/persistence/image_persistence_service.py`

Update default expiration times:

- `get_signed_url()`: Change default from 345,600 to 2,678,400 seconds
- `get_image_url()`: Change default from 3,600 to 2,678,400 seconds

#### 2. ImageStorage

**File**: `backend/app/core/supabase/image_storage.py`

Update default expiration times:

- `get_signed_url()`: Change default from 3,600 to 2,678,400 seconds
- `get_image_url()`: Change default from 345,600 to 2,678,400 seconds (already uses get_signed_url)

### Frontend Changes

#### 3. Supabase Client

**File**: `frontend/my-app/src/services/supabaseClient.ts`

Update the `createSignedUrl` call from 259,200 to 2,678,400 seconds.

### Constants Definition

Create a shared constant to ensure consistency:

#### 4. Backend Constants

**File**: `backend/app/core/config.py` (or new constants file)

```python
# Signed URL expiration time: 31 days in seconds
SIGNED_URL_EXPIRY_SECONDS = 31 * 24 * 60 * 60  # 2,678,400 seconds
```

#### 5. Frontend Constants

**File**: `frontend/my-app/src/constants/storage.ts` (new file)

```typescript
// Signed URL expiration time: 31 days in seconds
export const SIGNED_URL_EXPIRY_SECONDS = 31 * 24 * 60 * 60; // 2,678,400 seconds
```

### Documentation Updates

#### 6. Update Documentation

Update all relevant documentation files to reflect the new 31-day standard:

- `docs/backend/services/persistence/image_persistence_service.md`
- `docs/backend/core/supabase/image_storage.md`
- `docs/frontend/services/supabaseClient.md`

### Test Updates

#### 7. Update Tests

**File**: `backend/tests/app/services/persistence/test_image_persistence_service.py`

Update test expectations to use the new 31-day default values.

## Implementation Plan

### Phase 1: Backend Implementation

1. Define the constant in `backend/app/core/config.py`
2. Update `ImagePersistenceService` methods to use the new default
3. Update `ImageStorage` methods to use the new default
4. Update tests to reflect new expectations

### Phase 2: Frontend Implementation

1. Define the constant in frontend
2. Update `supabaseClient.ts` to use new expiration time
3. Verify all URL generation uses the new duration

### Phase 3: Documentation & Validation

1. Update all documentation to reflect 31-day standard
2. Run full test suite to ensure no regressions
3. Test URL generation and expiration behavior
4. Validate that URLs remain valid for 31 days

## Security Considerations

**Longer URL Lifespan**: 31-day URLs will remain valid longer than before. This is acceptable because:

- Files are stored for 30 days anyway
- URLs still require proper session authentication
- RLS policies still control access based on user ownership
- The application already expects URLs to be shared within user sessions

**Storage Cost**: No additional storage costs as this only affects URL expiration, not file retention.
