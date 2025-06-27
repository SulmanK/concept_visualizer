# How to Implement JWT-Based Security for Supabase Storage

This guide provides step-by-step instructions for implementing Supabase storage security using JSON Web Tokens (JWTs) for the Concept Visualizer application. This approach secures storage buckets while maintaining the session-based, no-registration model.

## Overview

There are two main approaches to securing Supabase storage:

1. **Authentication JWTs with RLS Policies**: Using session-based authentication tokens with Row Level Security
2. **Signed URLs with Resource-Specific Tokens**: Using properly formatted resource-specific tokens with Supabase's signed URL endpoints

This guide recommends a **hybrid approach** that combines signed URLs for consistent access with RLS policies for defense-in-depth security.

### Authentication JWT Approach (Original)

In this approach:

- Your backend generates Supabase-compatible JWTs containing the session ID
- These tokens are used for authenticating storage requests
- Supabase RLS policies check the JWT claims against object file paths
- Works only when proper RLS policies and JWT extraction functions are configured

### Signed URL Approach (Recommended)

In this approach:

- Your backend generates URL-specific tokens with the proper format Supabase expects
- These tokens are bound to specific file paths for limited time access
- The signed URLs work consistently across platforms and browsers
- Can be combined with RLS policies for added security

### Benefits of the Hybrid Approach

- **Consistent access**: Works reliably across all browsers and platforms
- **Multiple security layers**: RLS policies act as a defense-in-depth measure
- **Path-based security**: Maintains session ID in file paths for RLS validation
- **No cookies required**: Works well with CORS and mobile applications

## Implementation Steps

### 1. Get Supabase JWT Secret

First, obtain your Supabase JWT secret:

1. **Navigate to Supabase Dashboard**

   - Go to your project → Settings → API
   - Scroll down to "JWT Settings"
   - Copy your JWT Secret (treat this as sensitive information!)

2. **Add Secret to Environment Variables**
   - Add to your `.env` file (never commit this to version control):
   ```
   SUPABASE_JWT_SECRET="your_jwt_secret_here"
   SUPABASE_URL="https://your-project-ref.supabase.co"
   SUPABASE_ANON_KEY="your_anon_key_here"
   ```

### 2. Create JWT Utility Functions for Both Token Types

Add both standard authentication tokens and resource-specific signed URL tokens:

```python
# backend/app/utils/jwt_utils.py
import time
import os
from typing import Dict, Any
from jose import jwt

# Get JWT secret from environment
SUPABASE_JWT_SECRET = os.environ.get("SUPABASE_JWT_SECRET")
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_PROJECT_REF = SUPABASE_URL.replace("https://", "").split(".")[0] if SUPABASE_URL else ""

def create_supabase_jwt(session_id: str, expires_in_seconds: int = 3600) -> str:
    """
    Create a Supabase-compatible JWT with session ID in claims.

    Args:
        session_id: User's session ID
        expires_in_seconds: Token validity period in seconds

    Returns:
        JWT token string
    """
    now = int(time.time())

    # Create payload with standard and custom claims
    # This structure follows Supabase's expected JWT format
    payload = {
        # Standard claims
        "iss": SUPABASE_URL,  # Issuer
        "iat": now,  # Issued at
        "exp": now + expires_in_seconds,  # Expiration
        "aud": SUPABASE_URL,  # Audience - must match your Supabase URL
        "role": "anon",  # Role (anonymous)

        # Custom claim for session ID in the format Supabase expects
        "sub": "",  # No authenticated user
        "session_id": session_id,  # Custom claim for our app

        # App metadata is where Supabase looks for custom claims
        "app_metadata": {
            "session_id": session_id
        }
    }

    # Generate and sign the token
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    return token

def create_supabase_jwt_for_storage(path: str, expiry_timestamp: int) -> str:
    """
    Create a Supabase-compatible JWT specifically for storage signed URLs.

    This function creates a token in the same format that Supabase uses for
    signed URLs, which is different from the authentication JWT format.

    Args:
        path: The storage path for which to create the signed URL
        expiry_timestamp: Expiration timestamp (unix time)

    Returns:
        JWT token string suitable for signed URLs
    """
    # Create payload matching Supabase's signed URL token format
    payload = {
        "url": path,  # Storage path
        "iat": int(time.time()),  # Issued at
        "exp": expiry_timestamp  # Expiration timestamp
    }

    # Generate and sign the token
    token = jwt.encode(payload, SUPABASE_JWT_SECRET, algorithm="HS256")
    return token
```

### 3. Update Image Storage Service for Signed URLs

Implement the hybrid approach in your storage service:

```python
# backend/app/services/image/storage.py
import time
from datetime import datetime
import uuid
from typing import Union, Optional, Dict, Any, BinaryIO
from io import BytesIO
from fastapi import UploadFile
from PIL import Image
import logging
import requests

from ..utils.supabase import get_supabase_client
from ..errors import ImageStorageError, ImageNotFoundError
from app.utils.jwt_utils import create_supabase_jwt, create_supabase_jwt_for_storage
from app.core.config import settings

class ImageStorageService:
    def __init__(self, supabase_client=None):
        self.supabase = supabase_client or get_supabase_client()
        self.concept_bucket = "concept-images"
        self.palette_bucket = "palette-images"
        self.logger = logging.getLogger(__name__)

    def store_image(
        self,
        image_data: Union[bytes, BytesIO, UploadFile],
        session_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False
    ) -> str:
        """
        Store an image in the storage bucket with session ID metadata.

        Args:
            image_data: Image data as bytes, BytesIO or UploadFile
            session_id: Session ID for access control
            concept_id: Optional concept ID to associate with the image
            file_name: Optional file name (generated if not provided)
            metadata: Optional metadata to store with the image
            is_palette: Whether the image is a palette (uses palette-images bucket)

        Returns:
            Signed URL of the stored image

        Raises:
            ImageStorageError: If image storage fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket

            # Process image data to get bytes
            if isinstance(image_data, UploadFile):
                content = image_data.file.read()
            elif isinstance(image_data, BytesIO):
                content = image_data.getvalue()
            else:
                content = image_data

            # Default extension
            ext = "png"

            # Generate a unique file name if not provided
            if not file_name:
                timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                random_id = str(uuid.uuid4())[:8]

                # Try to determine file format
                try:
                    img = Image.open(BytesIO(content))
                    if img.format:
                        ext = img.format.lower()
                except Exception as e:
                    self.logger.warning(f"Could not determine image format: {str(e)}, using default: {ext}")

                file_name = f"{timestamp}_{random_id}.{ext}"

            # Create path with session_id as the first folder segment
            # This is CRITICAL for our RLS policy to work
            if concept_id:
                path = f"{session_id}/{concept_id}/{file_name}"
            else:
                path = f"{session_id}/{file_name}"

            # Prepare file metadata including session ID
            file_metadata = {"owner_session_id": session_id}
            if metadata:
                file_metadata.update(metadata)

            # Set content type based on extension
            content_type = "image/png"  # Default
            if ext == "jpg" or ext == "jpeg":
                content_type = "image/jpeg"
            elif ext == "gif":
                content_type = "image/gif"
            elif ext == "webp":
                content_type = "image/webp"

            # Set file options with metadata and content type
            file_options = {
                "contentType": content_type,
                "metadata": file_metadata
            }

            # Create a JWT token for authentication
            token = create_supabase_jwt(session_id)

            # Upload with metadata
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                self.supabase.client.storage.from_(bucket_name).upload(
                    path=path,
                    file=content,
                    file_options=file_options,
                    headers={"Authorization": f"Bearer {token}"}
                )
            else:
                self.supabase.storage.from_(bucket_name).upload(
                    path=path,
                    file=content,
                    file_options=file_options,
                    headers={"Authorization": f"Bearer {token}"}
                )

            # Generate signed URL for the image
            return self.get_signed_url(path, is_palette=is_palette)

        except Exception as e:
            error_msg = f"Failed to store image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)

    def get_signed_url(self, path: str, is_palette: bool = False, expiry_seconds: int = 259200) -> str:
        """
        Get a signed URL for an image with 3-day expiration by default.

        Args:
            path: Path to the image in storage
            is_palette: Whether the image is a palette (uses palette-images bucket)
            expiry_seconds: Expiration time in seconds (default: 3 days / 259200 seconds)

        Returns:
            Signed URL of the image with temporary access
        """
        # Select the appropriate bucket
        bucket_name = self.palette_bucket if is_palette else self.concept_bucket

        try:
            # Try to use the SDK method first
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).create_signed_url(
                    path=path,
                    expires_in=expiry_seconds
                )
            else:
                response = self.supabase.storage.from_(bucket_name).create_signed_url(
                    path=path,
                    expires_in=expiry_seconds
                )

            # Extract the signed URL from the response
            if response and isinstance(response, dict):
                # Get data field (newer SDK versions)
                data = response.get('data', response)

                if data and isinstance(data, dict):
                    # Try both key formats
                    signed_url = data.get('signedUrl') or data.get('signedURL')

                    if signed_url:
                        # Make URL absolute if it's relative
                        if signed_url.startswith('/'):
                            signed_url = f"{settings.SUPABASE_URL}{signed_url}"
                        return signed_url

            # If SDK method fails, create signed URL manually
            expiry = int(time.time()) + expiry_seconds
            token = create_supabase_jwt_for_storage(f"{bucket_name}/{path}", expiry)
            return f"{settings.SUPABASE_URL}/storage/v1/object/sign/{bucket_name}/{path}?token={token}"

        except Exception as e:
            self.logger.error(f"Error generating signed URL: {str(e)}")

            # Try fallback method
            try:
                expiry = int(time.time()) + expiry_seconds
                token = create_supabase_jwt_for_storage(f"{bucket_name}/{path}", expiry)
                return f"{settings.SUPABASE_URL}/storage/v1/object/sign/{bucket_name}/{path}?token={token}"
            except Exception as inner_e:
                self.logger.error(f"Fallback method also failed: {str(inner_e)}")
                # Last resort - public URL
                return f"{settings.SUPABASE_URL}/storage/v1/object/public/{bucket_name}/{path}"
```

### 4. Configure RLS Policies

Set up Row Level Security policies for your storage buckets:

1. **Navigate to Supabase Dashboard SQL Editor**:

   - Create a new SQL query

2. **Add RLS Policies**:

   ```sql
   -- For the concept-images bucket
   CREATE POLICY "Users can select their own images"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'concept-images' AND ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can insert their own images"
   ON storage.objects FOR INSERT
   WITH CHECK (bucket_id = 'concept-images' AND
              ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can update their own images"
   ON storage.objects FOR UPDATE
   USING (bucket_id = 'concept-images' AND
         ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can delete their own images"
   ON storage.objects FOR DELETE
   USING (bucket_id = 'concept-images' AND
         ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   -- Similar policies for palette-images bucket
   CREATE POLICY "Users can select their own palette images"
   ON storage.objects FOR SELECT
   USING (bucket_id = 'palette-images' AND ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can insert their own palette images"
   ON storage.objects FOR INSERT
   WITH CHECK (bucket_id = 'palette-images' AND
              ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can update their own palette images"
   ON storage.objects FOR UPDATE
   USING (bucket_id = 'palette-images' AND
         ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));

   CREATE POLICY "Users can delete their own palette images"
   ON storage.objects FOR DELETE
   USING (bucket_id = 'palette-images' AND
         ((auth.jwt() ->> 'session_id')::text = (storage.foldername(name))[1]));
   ```

### 5. Configure JWT Function in Supabase (Optional but Recommended)

To make authentication JWTs work with RLS, you need to add a custom JWT extraction function:

```sql
-- Function to extract JWT from URL query parameter
-- NOTE: Updated to use public schema due to Supabase deprecating custom objects in internal schemas
CREATE OR REPLACE FUNCTION public.get_jwt_from_url()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  _token text;
BEGIN
  -- Extract the token from query string
  _token := split_part(split_part(current_setting('request.url.query', true), 'token=', 2), '&', 1);

  -- Return the token if found, otherwise return NULL
  RETURN NULLIF(_token, '');
END;
$$;

-- Function to get JWT from header or URL
-- NOTE: Updated to use public schema due to Supabase deprecating custom objects in internal schemas
CREATE OR REPLACE FUNCTION public.get_jwt()
RETURNS text
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
  _token text;
BEGIN
  -- Try to get token from Authorization header first
  _token := coalesce(
    current_setting('request.headers', true)::json->>'authorization',
    current_setting('request.headers', true)::json->>'Authorization'
  );

  -- Extract Bearer token if present
  IF _token IS NOT NULL AND _token LIKE 'Bearer %' THEN
    _token := replace(_token, 'Bearer ', '');
  ELSE
    -- Try to get token from URL query parameter
    _token := public.get_jwt_from_url();
  END IF;

  -- Return the token if found, otherwise return NULL
  RETURN _token;
END;
$$;
```

### 6. Update Frontend Client

Update your frontend to handle the signed URLs:

```typescript
// frontend/src/services/supabaseClient.ts
import { createClient } from "@supabase/supabase-js";
import { tokenService } from "./tokenService";

const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
const supabaseAnonKey = import.meta.env.VITE_SUPABASE_ANON_KEY;

// Create client
const supabaseClient = createClient(supabaseUrl, supabaseAnonKey);

/**
 * Get a signed URL for an image in Supabase Storage
 * Works for both public and private buckets
 *
 * @param path Path to the image in storage
 * @param bucketType Type of bucket ('concept' or 'palette')
 * @returns Signed URL for the image with 3-day expiration
 */
export const getImageUrl = async (
  path: string,
  bucketType: "concept" | "palette",
): Promise<string> => {
  // Get actual bucket name from config
  const bucket = bucketType === "concept" ? "concept-images" : "palette-images";

  // If path is empty or null, return empty string
  if (!path) {
    console.error("No path provided to getImageUrl");
    return "";
  }

  // If path already contains a signed URL token, it's already a complete URL - return it directly
  if (path.includes("/object/sign/") && path.includes("token=")) {
    console.log(`Path is already a complete signed URL`);

    // Ensure the URL is absolute by adding the Supabase URL if it's relative
    if (path.startsWith("/")) {
      return `${supabaseUrl}${path}`;
    }

    return path;
  }

  // If path already looks like a complete URL with http, return it directly
  if (path.startsWith("http")) {
    return path;
  }

  try {
    // Use createSignedUrl with 3-day expiration
    const { data } = await supabaseClient.storage
      .from(bucket)
      .createSignedUrl(path, 259200); // 3 days in seconds

    if (data && data.signedUrl) {
      return data.signedUrl;
    }

    console.error("Failed to create signed URL");

    // Create a fallback URL with the path
    return `${supabaseUrl}/storage/v1/object/public/${bucket}/${path}`;
  } catch (error) {
    console.error(`Error getting signed URL for ${path}:`, error);
    return `${supabaseUrl}/storage/v1/object/public/${bucket}/${path}`;
  }
};

export default supabaseClient;
```

## Understanding the Security Model

### How This Hybrid Approach Works

1. **Storage Structure**: File paths are prefixed with the session ID: `{session_id}/{file_name}`

2. **First Security Layer - Signed URLs**:

   - Resource-specific tokens bound to exact file paths
   - Limited time access control (typically 3 days)
   - Prevents unauthorized direct access to files

3. **Second Security Layer - RLS Policies**:

   - Verifies session ID in JWT matches the session ID in file path
   - Protects against unauthorized uploads, updates, deletes
   - Works for both API access and URL access with auth.get_jwt_from_url()

4. **Why Two Layers?**:
   - Signed URLs provide reliable access for users across platforms
   - RLS provides database-level security for all operations
   - Defense-in-depth approach protects against various attack vectors

### Key Differences Between Token Types

1. **Authentication JWT**:

   ```json
   {
     "iss": "https://your-project.supabase.co",
     "iat": 1617302400,
     "exp": 1617388800,
     "aud": "https://your-project.supabase.co",
     "role": "anon",
     "sub": "",
     "session_id": "123e4567-e89b-12d3-a456-426614174000",
     "app_metadata": {
       "session_id": "123e4567-e89b-12d3-a456-426614174000"
     }
   }
   ```

2. **Signed URL JWT**:
   ```json
   {
     "url": "bucket-name/123e4567-e89b-12d3-a456-426614174000/image.png",
     "iat": 1617302400,
     "exp": 1617388800
   }
   ```

The first type identifies a session, while the second authorizes access to a specific resource.

## Troubleshooting Common Issues

### Signed URL Issues

If signed URLs aren't working:

1. **Check Token Format**:

   - Use [jwt.io](https://jwt.io/) to decode the token
   - Verify it has the `url` claim with correct path

2. **Check JWT Secret**:

   - Ensure the secret matches what's in Supabase settings
   - Check environment variables are loaded correctly

3. **Check URL Format**:
   - URLs should be in format: `/storage/v1/object/sign/{bucket}/{path}?token={token}`
   - Ensure token is properly appended

### RLS Policy Issues

If RLS policies aren't working:

1. **Check Path Structure**:

   - Ensure all file paths start with session ID
   - Check that `storage.foldername(name)[1]` correctly extracts the session ID

2. **Test JWT Extraction**:

   - Run SQL query to verify JWT claims are accessible:

   ```sql
   SELECT auth.jwt() -> 'app_metadata' ->> 'session_id' as session_id;
   ```

3. **Check Policy Syntax**:
   - Verify the policy conditions match your JWT structure
   - Ensure bucket IDs are correct

## Conclusion

The hybrid approach using signed URLs with RLS policies provides:

1. **Reliable file access** using properly formatted signed URL tokens
2. **Enhanced security** through defense-in-depth with RLS policies
3. **Consistent behavior** across all buckets and browsers
4. **Separation of concerns** between file access and session management

This approach ensures your application is both secure and robust, with multiple safeguards to protect user data while maintaining a seamless user experience.

## Additional Resources

- [Supabase Storage Documentation](https://supabase.com/docs/guides/storage)
- [Supabase Auth & JWT Documentation](https://supabase.com/docs/guides/auth/jwts)
- [Row Level Security in Postgres](https://www.postgresql.org/docs/current/ddl-rowsecurity.html)
- [JWT.io Debugger](https://jwt.io/)
