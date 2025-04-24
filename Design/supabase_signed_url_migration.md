# Design Document: Migrating from Public URLs to Signed URLs for Supabase Storage

## Problem Statement

Our application currently uses methods named `get_public_url` for accessing Supabase storage resources, but our Supabase storage buckets are configured as private, requiring proper signed URLs for secure access. We need to update our codebase to explicitly use signed URLs and remove any remaining public URL access patterns to ensure proper security.

## Background

Supabase provides two main ways to access files in storage:

1. **Public URLs** - For public buckets, accessible by anyone without authentication
2. **Signed URLs** - For private buckets, temporary access with built-in expiration, requiring authentication

Our project has evolved to use private buckets for security, but parts of our codebase still reference "public URL" functions that may create confusion and security issues.

## Current Implementation Analysis

### Backend Implementation

#### ImageStorageService in `backend/app/services/image/storage.py`

- `get_public_url(path, is_palette)` method (lines ~319-415) actually already generates signed URLs despite its name
- The method implements several approaches to generate URLs:
  1. Special handling for palette images with direct URL + JWT token
  2. Standard signed URL generation using `/storage/v1/object/sign/` endpoint
  3. Fallback to direct URL with JWT token if signing fails
  4. Last resort fallback to public URL in error cases (potential security issue)

#### Other Backend Components Using URL Generation

- `authenticate_url` method in `ImageStorageService` - Calls `get_public_url`
- `store_image` method - Uses `get_public_url` to return image URL after storage
- `list_images` method - Uses `get_public_url` for each image in the list
- `ImageService.get_image_url` method - Wraps `storage.get_public_url` call
- `ImageService.apply_color_palette` - Uses `storage.get_public_url` for verification

#### Legacy Components

- `ImageStorage` class in `backend/app/core/supabase/image_storage.py` still uses `.get_public_url()` directly from the Supabase client

### Frontend Implementation

#### Supabase Client in `frontend/my-app/src/services/supabaseClient.ts`

- Has both `getPublicImageUrl` and `getImageUrl` functions:
  - `getImageUrl` - Tries signed URL first, falls back to public URL
  - `getPublicImageUrl` - Uses only public URLs (potential security issue)
  - `getAuthenticatedImageUrl` - Adds token to public URL (not using proper signed URLs)

#### Components Using URLs

- `ConceptResult` component - Has custom URL formatting logic with fallback to `getPublicImageUrl`
- Various components using these client functions to display images

## Proposed Changes

### Backend Changes

1. **Create New Method**

   - Implement `get_signed_url(path, is_palette, expiry_seconds=259200)` in `ImageStorageService` with 3-day default expiration
   - Copy and improve functionality from existing `get_public_url` with configurable expiry
   - Set default expiration to 3 days (259200 seconds) to match our file retention policy

2. **Remove Old Method and Update Callers**

   - Remove the `get_public_url` method completely
   - Update all calling code to use `get_signed_url` directly
   - No backward compatibility layer will be maintained

3. **Update Internal Method Calls**

   - Update all internal service calls to use `get_signed_url` directly without fallbacks
   - Remove any code that falls back to public URLs

4. **JWT Token Generation**

   - Update JWT token creation with 3-day expiration (259200 seconds) to match file retention policy
   - Ensure path-based tokens use consistent approach

5. **Validation and Security**
   - Add validation to ensure storage buckets are configured as private
   - Improve error handling for URL signing failures
   - Remove any direct calls to Supabase's `.get_public_url()` method

### Frontend Changes

1. **Update Client Methods**

   - Remove `getPublicImageUrl` function entirely
   - Update `getImageUrl` to use signed URLs exclusively without fallbacks
   - Create new `getSignedImageUrl` function with 3-day expiration to replace all URL generation

2. **Update URL Caching Strategy**

   - Implement proper caching for signed URLs with expiration awareness
   - URL cache can be more aggressive since URLs will remain valid for the entire 3-day file lifecycle

3. **Refactor Components**

   - Update all components to use signed URLs exclusively
   - Remove `getPublicImageUrl` usage from `ConceptResult`
   - Handle token expiration gracefully in UI components

4. **Error Handling**
   - Add consistent error handling for URL signing failures
   - Implement retry logic for failed URL signing attempts

## Implementation Plan

### Phase 1: Backend Implementation

1. Create `get_signed_url` method in `ImageStorageService` with 3-day expiration
2. Remove `get_public_url` method entirely
3. Update all backend code to use `get_signed_url` directly
4. Remove all public URL generation code and fallbacks

### Phase 2: Frontend Implementation

1. Implement `getSignedImageUrl` in frontend client with 3-day expiration
2. Remove `getPublicImageUrl` function entirely
3. Update all components to use signed URLs exclusively
4. Implement proper signed URL caching

### Phase A: Security Validation

1. Validate all storage buckets are properly configured as private
2. Implement audit logging for URL access
3. Verify RLS policies correctly limit access to authorized users

## Security Considerations

1. **URL Expiration**

   - Configure 3-day expiration time (259200 seconds) to match file retention policy
   - This ensures files are accessible for their entire lifetime but not beyond
   - The automatic file deletion process will remove files after 3 days, so expired URLs will return 404 errors

2. **RLS Policies**

   - Ensure Row Level Security policies are correctly configured for bucket access
   - Verify session ID validation in RLS policies

3. **Access Logging**

   - Implement audit logging for URL access patterns
   - Monitor for unauthorized access attempts

4. **Error Handling**
   - Avoid exposing sensitive information in error messages
   - Provide user-friendly alternatives when URL signing fails

## Completion Criteria

1. All URL generation in the backend uses `get_signed_url`
2. All URL generation in the frontend uses signed URLs
3. No public URL access patterns remain in the codebase
4. Documentation reflects the secure URL access pattern

## Future Work

1. Consider automatic cleanup for URLs that reference deleted files
2. Add support for different access levels with varying expiration times
3. Implement comprehensive testing for URL signing functionality
4. Consider implementing URL revocation mechanism for security incidents
