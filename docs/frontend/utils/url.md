# URL Utilities

The `url.ts` module provides utility functions for URL manipulation and processing, specifically focused on handling storage URLs from Supabase and extracting relevant path information.

## Core Features

- Extract storage paths from Supabase URLs
- Handle different URL formats (public, authenticated, signed)
- Robust error handling for malformed URLs
- Detailed logging for debugging URL processing

## Available Functions

### extractStoragePathFromUrl

```typescript
extractStoragePathFromUrl(url: string | undefined): string | null
```

Extracts the storage path from a Supabase URL. This is particularly useful for working with image storage paths.

| Parameter | Type | Description |
|-----------|------|-------------|
| `url` | string \| undefined | The URL to extract the storage path from |

**Returns:** The storage path (e.g., "user-id/image-id.png") or null if not found or in case of an error

## Supported URL Formats

The function supports multiple Supabase storage URL formats:

1. **Public URLs**:
   ```
   https://[project-id].supabase.co/storage/v1/object/public/concept-images/[user-id]/[image-id].png
   ```

2. **Authenticated URLs**:
   ```
   https://[project-id].supabase.co/storage/v1/object/authenticated/concept-images/[user-id]/[image-id].png
   ```

3. **Signed URLs**:
   ```
   https://[project-id].supabase.co/storage/v1/object/sign/palette-images/[user-id]/[image-id].png?token=...
   ```

4. **Direct Storage Path References**:
   ```
   [user-id]/[image-id].png
   ```

## Usage Examples

### Extracting Path from Storage URL

```typescript
import { extractStoragePathFromUrl } from '../utils/url';

// Example with public URL
const publicUrl = 'https://example.supabase.co/storage/v1/object/public/concept-images/user123/image456.png';
const path1 = extractStoragePathFromUrl(publicUrl);
console.log(path1); // Output: "user123/image456.png"

// Example with signed URL
const signedUrl = 'https://example.supabase.co/storage/v1/object/sign/concept-images?token=abc&url=concept-images/user123/image789.png';
const path2 = extractStoragePathFromUrl(signedUrl);
console.log(path2); // Output: "user123/image789.png"

// With error handling
function getImagePath(imageUrl: string | undefined): string {
  const path = extractStoragePathFromUrl(imageUrl);
  if (!path) {
    return 'default-image.png';
  }
  return path;
}
```

## Implementation Details

The function works by:

1. Parsing the URL using the browser's `URL` constructor
2. Checking for known Supabase storage path patterns
3. Trying multiple extraction methods in sequence:
   - Split URL by bucket name (concept-images/ or palette-images/)
   - Check for URL parameters in signed URLs
   - Use regex pattern matching for direct paths
4. Logging detailed information about the extraction process
5. Returning null for invalid URLs or if no pattern matches

### Error Handling

The function is designed to be defensive and will:
- Return null for undefined/empty inputs
- Catch and log any exceptions during URL parsing
- Return null if path extraction fails
- Log detailed information to aid debugging 