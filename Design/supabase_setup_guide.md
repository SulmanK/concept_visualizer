# Supabase Setup Guide for Concept Visualizer

This guide provides step-by-step instructions for setting up Supabase as the database and session management solution for the Concept Visualizer application.

## Overview

Supabase will serve as our PostgreSQL database with:

- Anonymous session tracking via cookies
- Storage of user-generated concepts and their metadata
- Storage of color palette variations
- Image storage using Supabase Storage
- RESTful API access to stored data

## Step 1: Create a Supabase Account and Project

1. Visit [supabase.com](https://supabase.com/) and sign up for an account

   - You can use GitHub, GitLab, or email for authentication
   - If using GitHub, authorize the Supabase application when prompted

2. Once logged in, click "New Project" in the dashboard

3. Enter project details:

   - **Organization:** Select or create an organization
   - **Name:** `concept-visualizer` (or your preferred name)
   - **Database Password:** Create a secure password (save this somewhere safe!)
   - **Region:** Choose a region closest to your users (lower latency)
   - **Pricing Plan:** Free tier is sufficient for development
     - Includes 500MB database, 1GB file storage, 2GB bandwidth
     - 50,000 monthly active users
     - 7-day log retention

4. Click "Create new project" and wait for initialization (approximately 2-3 minutes)

5. Note your project's URL in the dashboard (format: `https://[project-id].supabase.co`)

## Step 2: Create Storage Buckets

First, let's create the storage buckets for our images:

1. In the Supabase dashboard, navigate to the "Storage" section in the left sidebar

2. Click "Create a new bucket"

3. Create the following buckets:

   - **Name:** `concept-images` (for base images)

     - **Public/Private:** Private (we'll set up access policies later)
     - **File size limit:** 5MB (adequate for most generated images)
     - Click "Create bucket"

   - **Name:** `palette-images` (for color palette variations)
     - **Public/Private:** Private
     - **File size limit:** 5MB
     - Click "Create bucket"

4. For now, set up only basic read access:

   - Click on the bucket name
   - Go to the "Policies" tab
   - Click "Create a new policy"

   For anonymous read access:

   - Policy name: `Anonymous read access`
   - Policy definition: `true` (allows anyone to read images)
   - Operations: SELECT
   - Click "Save policy"

   > **Note:** We'll set up the write policies after creating the database schema.

## Step 3: Set Up Database Schema

Now, create the necessary database tables:

1. In the Supabase dashboard, navigate to the "SQL Editor" section in the left sidebar

2. Click "New Query" to create a new SQL script

3. Name it "Initial Schema Setup"

4. Paste the following SQL to create the tables and indexes:

```sql
-- Sessions table to track anonymous users
CREATE TABLE sessions (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Concepts table
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  session_id UUID REFERENCES sessions(id) NOT NULL,
  logo_description TEXT NOT NULL,
  theme_description TEXT NOT NULL,
  base_image_path TEXT NOT NULL -- Path to image in Supabase Storage
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL -- Path to image in Supabase Storage
);



-- Create indexes for performance
CREATE INDEX concepts_session_id_idx ON concepts(session_id);
CREATE INDEX color_variations_concept_id_idx ON color_variations(concept_id);

```

5. Click "Run" to execute the script

6. Verify the tables were created by checking the "Table Editor" section in the left sidebar
   - You should see the four new tables: `sessions`, `concepts`, `color_variations`, and `rate_limits`
   - Note that we're now using `base_image_path` and `image_path` instead of URLs, as these will store the Supabase Storage paths

## Step 4: Configure Production-Ready Access Policies

Now that your database schema is set up, configure access policies for all resources. For production environments, we'll use simplified policies that work reliably with Supabase while ensuring proper security through our application logic.

### Database Access Policies

1. Navigate to "Authentication" → "Policies" in the sidebar

2. For each table, enable Row Level Security:

   - Click on the table name
   - Toggle "Enable RLS" to ON

3. For the `sessions` table:

   - Click "New Policy"
   - Choose "Create a policy from scratch"
   - Policy name: `Basic access`
   - For the definition (using section), use:
     ```sql
     true
     ```
   - For the check expression, use the same expression
   - Operations: SELECT all operations (SELECT, INSERT, UPDATE, DELETE)
   - Click "Save Policy"

4. For the `concepts` table:

   - Create a policy named `Basic access`
   - For the definition (using section), use:
     ```sql
     true
     ```
   - For the check expression, use the same expression
   - Operations: SELECT, INSERT, UPDATE
   - Click "Save Policy"

5. For the `color_variations` table:
   - Create a policy named `Basic access`
   - For the definition (using section), use:
     ```sql
     true
     ```
   - For the check expression, use the same expression
   - Operations: SELECT, INSERT, UPDATE, DELETE
   - Click "Save Policy"

> **Note on Security:** While these policies grant broad access at the database level, our application will enforce security by:
>
> 1. Organizing data into session-specific structures
> 2. Only querying data belonging to the current session in our backend code
> 3. Validating session cookies in all API requests
> 4. Using the session ID to create a folder structure in storage

### Storage Access Policies

For storage buckets, configure policies that allow public access but rely on our application logic for security:

1. Navigate to "Storage" in the left sidebar

2. For each bucket (`concept-images` and `palette-images`):

   - Click on the bucket name
   - Go to the "Policies" tab
   - Remove any existing policies and add the following:

   For public read access:

   - Policy name: `Public read access`
   - Using expression:
     ```sql
     true
     ```
   - Operations: SELECT
   - This allows public read access to all images

   For write access:

   - Policy name: `Public write access`
   - Using expression:
     ```sql
     true
     ```
   - Operations: INSERT
   - This allows uploads to the bucket
   - Click "Save Policy"

## Step 5: Implementing Secure Session Management

To ensure proper security despite the simplified database policies, we'll implement robust session management in our application:

### Folder-Based Security for Storage

1. When storing images, always create a path with the session ID as the first folder segment:

   ```
   {session_id}/{unique_filename}.png
   ```

2. This ensures each user's data is organized in a separate folder, preventing accidental access to other users' data.

### Session-Based Filtering in Queries

When retrieving data from the database, always filter by the current session ID:

```python
def get_recent_concepts(self, session_id: str, limit: int = 10):
    """Get recent concepts for a session."""
    try:
        # Always filter by session_id to ensure users only see their own data
        result = self.client.table("concepts").select(
            "*, color_variations(*)"
        ).eq("session_id", session_id).order(
            "created_at", desc=True
        ).limit(limit).execute()

        return result.data
    except Exception as e:
        self.logger.error(f"Error retrieving recent concepts: {e}")
        return []
```

### Session Validation in API Endpoints

In your FastAPI routes, always validate the session before returning data:

```python
@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """Get recent concepts for the current session."""
    # Get or create session - validates the session cookie
    session_id, is_new_session = await session_service.get_or_create_session(response, session_id)

    # Return empty list for new sessions
    if is_new_session:
        return []

    # The storage service will filter by session_id, ensuring data isolation
    return await storage_service.get_recent_concepts(session_id)
```

## Step 6: Implementing Session-Based Rate Limiting

To ensure fair usage of your API and prevent abuse, we'll implement session-based rate limiting with Supabase:

### 1. Implementing a Supabase Storage Backend for Rate Limiting

Create a custom storage backend that will store rate limits in the Supabase `rate_limits` table:

```python
# backend/app/core/limiter.py
import datetime
import logging
from typing import Optional

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from backend.app.core.config import settings
from backend.app.core.supabase import get_supabase_client

logger = logging.getLogger(__name__)

def get_session_or_ip(request: Request) -> str:
    """Get the session ID from cookies or fall back to IP address."""
    # Try to get the session ID from cookies
    session_id = request.cookies.get("concept_session")

    if session_id:
        logger.debug(f"Rate limiting using session ID: {session_id}")
        return f"session:{session_id}"

    # Fall back to IP address
    ip = get_remote_address(request)
    logger.debug(f"Rate limiting using IP address: {ip}")
    return f"ip:{ip}"

class SupabaseStorage:
    """Storage implementation for rate limits using Supabase."""

    def __init__(self):
        """Initialize the storage with Supabase client."""
        self.client = get_supabase_client()
        self.table = "rate_limits"

    async def get(self, key: str) -> Optional[int]:
        """Get the current value for a rate limit key."""
        try:
            # Remove expired keys first
            self._cleanup_expired()

            # Get current value
            result = self.client.client.table(self.table).select("*").eq("key", key).execute()
            if result.data and len(result.data) > 0:
                item = result.data[0]
                # Check if expired
                if datetime.datetime.fromisoformat(item["expires_at"].replace("Z", "+00:00")) < datetime.datetime.now(datetime.timezone.utc):
                    return None
                return item["value"]
            return None
        except Exception as e:
            logger.error(f"Error getting rate limit key {key}: {e}")
            return None

    async def set(self, key: str, value: int, expiry: int) -> None:
        """Set a new value for a rate limit key."""
        try:
            expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(seconds=expiry)

            # Upsert the key
            self.client.client.table(self.table).upsert({
                "key": key,
                "value": value,
                "expires_at": expires_at.isoformat(),
                "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat()
            }).execute()
        except Exception as e:
            logger.error(f"Error setting rate limit key {key}: {e}")

    async def increment(self, key: str, amount: int, expiry: int) -> int:
        """Increment the value for a rate limit key."""
        try:
            current = await self.get(key) or 0
            new_value = current + amount
            await self.set(key, new_value, expiry)
            return new_value
        except Exception as e:
            logger.error(f"Error incrementing rate limit key {key}: {e}")
            return amount  # Default to just the increment amount

    def _cleanup_expired(self) -> None:
        """Delete expired rate limit keys."""
        try:
            self.client.client.table(self.table).delete().lt(
                "expires_at",
                datetime.datetime.now(datetime.timezone.utc).isoformat()
            ).execute()
        except Exception as e:
            logger.error(f"Error cleaning up expired rate limits: {e}")

# Define rate limit tiers
GENERAL_API_LIMITS = ["30/minute"]
GENERATION_LIMITS = ["5/minute", "20/hour"]
REFINEMENT_LIMITS = ["10/minute", "30/hour"]
MONTHLY_GENERATION_LIMIT = ["10/month"]

# Create limiter with Supabase storage
limiter = Limiter(
    key_func=get_session_or_ip,
    default_limits=["100/minute"]
)

def get_limiter() -> Limiter:
    """Get the configured rate limiter."""
    return limiter

## Step 7: Get API Keys

To connect your application to Supabase:

1. Go to "Project Settings" → "API" in the sidebar

2. Note down two important values:
   - **Project URL:** Your Supabase project URL (e.g., `https://[project-id].supabase.co`)
   - **anon key:** The public API key for anonymous access

3. These values will be used in your application's environment variables

4. Important: Never expose the `service_role` key in client-side code; it bypasses RLS policies

## Step 8: Set Up Backend Environment

1. Create or update your `.env` file in the backend directory:

```

SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
JIGSAWSTACK_API_KEY=your-jigsawstack-api-key

````

2. Install the Supabase client in your backend:

```bash
uv add supabase
uv add python-multipart  # Required for file handling
uv add pillow  # For image processing
````

3. If needed, create a requirements file that includes the Supabase dependency:

```
# requirements.txt
supabase>=1.0.0
python-multipart>=0.0.5
pillow>=8.0.0
```

## Step 9: Implement Backend Integration

Create the necessary files for Supabase integration:

### 1. Supabase Client

Create `backend/app/core/supabase.py` with enhanced storage support:

```python
from supabase import create_client, Client
from pydantic import BaseSettings
import logging
import uuid
import io
import requests
from PIL import Image
from typing import Optional

class Settings(BaseSettings):
    """Settings for Supabase configuration."""
    supabase_url: str
    supabase_key: str

    class Config:
        env_file = ".env"

class SupabaseClient:
    """Client for interacting with Supabase."""

    def __init__(self, settings: Settings):
        """Initialize Supabase client with configured settings."""
        self.client = create_client(settings.supabase_url, settings.supabase_key)
        self.logger = logging.getLogger("supabase_client")

    def get_session(self, session_id: str):
        """Get a session by ID."""
        try:
            result = self.client.table("sessions").select("*").eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving session: {e}")
            return None

    def create_session(self):
        """Create a new session."""
        try:
            result = self.client.table("sessions").insert({}).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None

    def update_session_activity(self, session_id: str):
        """Update session's last_active_at timestamp."""
        try:
            result = self.client.table("sessions").update(
                {"last_active_at": "now()"}
            ).eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error updating session activity: {e}")
            return None

    def store_concept(self, concept_data):
        """Store a new concept."""
        try:
            result = self.client.table("concepts").insert(concept_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error storing concept: {e}")
            return None

    def store_color_variations(self, variations):
        """Store color variations for a concept."""
        try:
            result = self.client.table("color_variations").insert(variations).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Error storing color variations: {e}")
            return None

    def get_recent_concepts(self, session_id: str, limit: int = 10):
        """Get recent concepts for a session."""
        try:
            # Security: Always filter by session_id to ensure users only see their own data
            result = self.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("session_id", session_id).order(
                "created_at", desc=True
            ).limit(limit).execute()

            return result.data
        except Exception as e:
            self.logger.error(f"Error retrieving recent concepts: {e}")
            return []

    async def upload_image_from_url(self, image_url: str, bucket: str, session_id: str):
        """Download an image from URL and upload to Supabase Storage.

        Args:
            image_url: URL of the image to download
            bucket: Storage bucket name ('concept-images' or 'palette-images')
            session_id: Session ID for organizing files

        Returns:
            Storage path of the uploaded image or None on error
        """
        try:
            # Download image from URL
            response = requests.get(image_url, timeout=10)
            response.raise_for_status()

            # Generate a unique filename
            file_ext = "png"  # Default extension
            content_type = response.headers.get("Content-Type", "")
            if "jpeg" in content_type or "jpg" in content_type:
                file_ext = "jpg"
            elif "png" in content_type:
                file_ext = "png"

            # Security: Create path with session_id as the first folder
            # This ensures each user's files are in separate folders
            unique_filename = f"{session_id}/{uuid.uuid4()}.{file_ext}"

            # Upload to Supabase Storage
            result = self.client.storage.from_(bucket).upload(
                path=unique_filename,
                file=response.content,
                file_options={
                    "content-type": content_type or "image/png"
                }
            )

            # Get public URL for the image
            file_path = unique_filename
            return file_path

        except Exception as e:
            self.logger.error(f"Error uploading image from URL: {e}")
            return None

    def get_image_url(self, path: str, bucket: str):
        """Get the public URL for an image in Supabase Storage.

        Args:
            path: Path of the image in storage
            bucket: Storage bucket name

        Returns:
            Public URL for the image
        """
        try:
            return self.client.storage.from_(bucket).get_public_url(path)
        except Exception as e:
            self.logger.error(f"Error getting image URL: {e}")
            return None

    async def apply_color_palette(self, image_path: str, palette: list, session_id: str):
        """Apply a color palette to an image and store the result.

        This is a basic implementation that would need enhancement for production.
        For MVP, it simply transfers the original image.

        Args:
            image_path: Path of the base image in storage
            palette: List of hex color codes
            session_id: Session ID for organizing files

        Returns:
            Path of the new image with applied palette
        """
        try:
            # For MVP, we'll just copy the original image
            # In a full implementation, we would apply the palette
            original_url = self.get_image_url(image_path, "concept-images")
            if not original_url:
                return None

            # Upload (for now, just the same image) to palette-images bucket
            return await self.upload_image_from_url(
                original_url,
                "palette-images",
                session_id
            )
        except Exception as e:
            self.logger.error(f"Error applying color palette: {e}")
            return None

# Factory function for creating the client
def get_supabase_client(settings: Settings = None):
    """Factory function to get Supabase client."""
    if settings is None:
        settings = Settings()
    return SupabaseClient(settings)
```

### 2. Session Management Service

Create `backend/app/services/session_service.py`:

```python
from fastapi import Depends, Cookie, Response
from typing import Optional, Tuple
from ..core.supabase import get_supabase_client, SupabaseClient

class SessionService:
    """Service for managing user sessions."""

    def __init__(self, supabase_client: SupabaseClient = Depends(get_supabase_client)):
        """Initialize session service with a Supabase client."""
        self.supabase_client = supabase_client

    async def get_or_create_session(
        self,
        response: Response,
        session_id: Optional[str] = Cookie(None, alias="concept_session")
    ) -> Tuple[str, bool]:
        """Get existing session or create a new one."""
        is_new_session = False

        if not session_id:
            # Create new session
            session = self.supabase_client.create_session()
            if session:
                session_id = session["id"]
                is_new_session = True
            else:
                # Fallback to a local UUID if Supabase is unavailable
                import uuid
                session_id = str(uuid.uuid4())
                is_new_session = True
        else:
            # Validate session exists and update last_active_at
            session = self.supabase_client.get_session(session_id)
            if not session:
                # Session ID in cookie doesn't exist in database
                # Create a new session instead
                session = self.supabase_client.create_session()
                if session:
                    session_id = session["id"]
                    is_new_session = True
                else:
                    import uuid
                    session_id = str(uuid.uuid4())
                    is_new_session = True
            else:
                # Update last_active_at for existing session
                self.supabase_client.update_session_activity(session_id)

        # Set session cookie
        response.set_cookie(
            key="concept_session",
            value=session_id,
            httponly=True,
            max_age=60*60*24*30,  # 30 days
            samesite="lax",
            secure=True  # Set to False in development if needed
        )

        return session_id, is_new_session

# Dependency function for FastAPI routes
async def get_session_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client)
) -> SessionService:
    """Factory function for SessionService."""
    return SessionService(supabase_client)
```

## Step 10: Set Up Frontend Environment

1. Create or update your `.env` file in the frontend directory:

```
VITE_API_BASE_URL=http://localhost:8000
```

2. Ensure your API client is configured to send cookies with requests using Axios:

```typescript
// api.ts
import axios from "axios";

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true, // Important: This allows cookies to be sent
});

export default apiClient;
```

## Step 11: Testing the Integration

Once everything is set up, test the integration:

1. Test image generation and storage:

   - Generate a concept and verify that:
     - The base image is stored in the `concept-images` bucket
     - The palette variations are stored in the `palette-images` bucket
     - The database records contain the correct storage paths

2. Test image retrieval:

   - View a concept detail page
   - Verify that all images are loading correctly
   - Check the browser's network tab to confirm images are loaded from Supabase Storage

3. Test session persistence:
   - Close and reopen the browser
   - Verify that your recent concepts are still available
   - Check that images still load correctly

## Step 12: Troubleshooting Common Issues

### CORS Issues

If you encounter CORS errors when loading images:

1. In the Supabase dashboard, navigate to "Storage" → Select the bucket → "Policies"
2. Verify the policies allow reading files
3. Check CORS settings in "Project Settings" → "API" → "CORS"

### Storage Permissions

If you get permission errors when uploading images:

1. Check the bucket's RLS policies
2. Ensure the session cookie is being correctly sent with headers
3. Try using the "Add policy" shortcut for a simple "Allow public uploads" rule temporarily

### Image Processing Issues

If images aren't processing correctly:

1. Check the logs for errors
2. Verify Pillow is installed correctly
3. Test with small, simple images first

## Step 13: Implementing Nightly Data Purge

For development environments or implementations with privacy requirements, you may want to purge all data nightly. This section outlines how to implement this functionality.

### 1. Add Deletion Methods to the Supabase Client

Add the following methods to your `backend/app/core/supabase.py` file:

```python
# Add these methods to the SupabaseClient class
async def purge_all_data(self):
    """Purge all data from database and storage.

    This method deletes all data from all tables and storage buckets.
    Use with caution - this is a destructive operation.

    Returns:
        bool: True if purge was successful, False otherwise
    """
    try:
        # Delete all from database tables (in correct order to preserve foreign keys)
        await self.delete_all_color_variations()
        await self.delete_all_concepts()
        await self.delete_all_sessions()
        await self.delete_all_rate_limits()

        # Delete all from storage buckets
        await self.delete_all_storage_objects("palette-images")
        await self.delete_all_storage_objects("concept-images")

        self.logger.info("Successfully purged all data")
        return True
    except Exception as e:
        self.logger.error(f"Error purging all data: {e}")
        return False

async def delete_all_color_variations(self):
    """Delete all records from color_variations table."""
    try:
        result = await self.client.table("color_variations").delete().neq("id", "impossible-value").execute()
        self.logger.info(f"Deleted {len(result.data) if result.data else 0} color variations")
        return True
    except Exception as e:
        self.logger.error(f"Error deleting color variations: {e}")
        return False

async def delete_all_concepts(self):
    """Delete all records from concepts table."""
    try:
        result = await self.client.table("concepts").delete().neq("id", "impossible-value").execute()
        self.logger.info(f"Deleted {len(result.data) if result.data else 0} concepts")
        return True
    except Exception as e:
        self.logger.error(f"Error deleting concepts: {e}")
        return False

async def delete_all_sessions(self):
    """Delete all records from sessions table."""
    try:
        result = await self.client.table("sessions").delete().neq("id", "impossible-value").execute()
        self.logger.info(f"Deleted {len(result.data) if result.data else 0} sessions")
        return True
    except Exception as e:
        self.logger.error(f"Error deleting sessions: {e}")
        return False

async def delete_all_rate_limits(self):
    """Delete all records from rate_limits table."""
    try:
        result = await self.client.table("rate_limits").delete().neq("id", "impossible-value").execute()
        self.logger.info(f"Deleted {len(result.data) if result.data else 0} rate limits")
        return True
    except Exception as e:
        self.logger.error(f"Error deleting rate limits: {e}")
        return False

async def delete_all_storage_objects(self, bucket: str):
    """Delete all objects from a storage bucket.

    Args:
        bucket: Name of the storage bucket to purge

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # List all objects in the bucket
        result = self.client.storage.from_(bucket).list()

        # Delete each folder/file
        for item in result:
            if item.get("name"):
                if item.get("id"):  # It's a file
                    self.client.storage.from_(bucket).remove([item["name"]])
                else:  # It's a folder - recursively list and delete
                    sub_items = self.client.storage.from_(bucket).list(item["name"])
                    for sub_item in sub_items:
                        if sub_item.get("name"):
                            self.client.storage.from_(bucket).remove([sub_item["name"]])

        self.logger.info(f"Deleted all objects from {bucket} bucket")
        return True
    except Exception as e:
        self.logger.error(f"Error deleting objects from {bucket} bucket: {e}")
        return False
```

### 2. Create an API Endpoint for Purging Data

Create a new API endpoint in `backend/app/api/routes/admin.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from ...core.supabase import get_supabase_client, SupabaseClient
from ...core.config import settings

router = APIRouter()

API_KEY_HEADER = APIKeyHeader(name="X-Admin-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)):
    """Verify admin API key for secure operations."""
    if not api_key or api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return api_key

@router.post("/purge-all-data", status_code=200)
async def purge_all_data(
    supabase_client: SupabaseClient = Depends(get_supabase_client),
    api_key: str = Depends(verify_api_key)
):
    """Purge all data from database and storage.

    This is a destructive operation and requires an admin API key.
    """
    success = await supabase_client.purge_all_data()
    if not success:
        raise HTTPException(status_code=500, detail="Failed to purge data")
    return {"message": "All data purged successfully"}
```

### 3. Update Configuration for Admin API Key

Add the admin API key to your settings in `backend/app/core/config.py`:

```python
class Settings(BaseSettings):
    # Other settings...
    ADMIN_API_KEY: str

    class Config:
        env_file = ".env"
```

Then add the key to your `.env` file:

```
ADMIN_API_KEY=your-secure-admin-key-here
```

### 4. Register the Admin Router

Update `backend/app/api/api.py` to include the admin routes:

```python
from fastapi import APIRouter
from .routes import concept, admin

api_router = APIRouter()
api_router.include_router(concept.router, prefix="/concept", tags=["concept"])
api_router.include_router(admin.router, prefix="/admin", tags=["admin"])
```

### 5. Create a Nightly Purge Script

Create a script that can be run via a cron job or scheduled task:

```python
# backend/scripts/purge_data.py
import asyncio
import requests
import os
import sys
import logging
from datetime import datetime

# Add the parent directory to the path so we can import from the app
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"purge_log_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("data_purge")

async def purge_data():
    """Send request to the API to purge all data."""
    try:
        api_url = os.environ.get("API_BASE_URL", "http://localhost:8000")
        admin_key = os.environ.get("ADMIN_API_KEY")

        if not admin_key:
            logger.error("ADMIN_API_KEY environment variable is not set")
            return False

        response = requests.post(
            f"{api_url}/api/admin/purge-all-data",
            headers={"X-Admin-API-Key": admin_key}
        )

        if response.status_code == 200:
            logger.info("Data purge completed successfully")
            return True
        else:
            logger.error(f"Failed to purge data: {response.status_code} - {response.text}")
            return False

    except Exception as e:
        logger.error(f"Error during data purge: {e}")
        return False

if __name__ == "__main__":
    logger.info("Starting data purge process")
    success = asyncio.run(purge_data())
    exit(0 if success else 1)
```

### 6. Set Up a Cron Job for Nightly Execution

Set up a cron job to run the script nightly:

1. On your server, edit the crontab:

   ```bash
   crontab -e
   ```

2. Add an entry to run the script at midnight:

   ```
   0 0 * * * cd /path/to/your/app && /usr/bin/python /path/to/your/app/backend/scripts/purge_data.py
   ```

3. Make sure environment variables are available to the cron job:
   ```
   0 0 * * * cd /path/to/your/app && export $(cat .env | xargs) && /usr/bin/python /path/to/your/app/backend/scripts/purge_data.py
   ```

### 7. Alternative: Use Supabase Edge Functions

For a more integrated approach with Supabase, you can use Edge Functions:

1. Create a new Edge Function in your Supabase project dashboard:

   ```javascript
   // supabase/functions/purge-data/index.ts
   import { createClient } from "https://esm.sh/@supabase/supabase-js@2.7.1";

   Deno.serve(async (req) => {
     try {
       // Create a Supabase client with the Admin key
       const supabaseAdmin = createClient(
         Deno.env.get("SUPABASE_URL") ?? "",
         Deno.env.get("SUPABASE_SERVICE_ROLE_KEY") ?? "",
         { auth: { persistSession: false } },
       );

       // Delete all data from tables (in correct order)
       await supabaseAdmin
         .from("color_variations")
         .delete()
         .not("id", "is", null);
       await supabaseAdmin.from("concepts").delete().not("id", "is", null);
       await supabaseAdmin.from("sessions").delete().not("id", "is", null);

       // Delete all storage objects
       // Note: This is simplified. For production, implement recursive folder deletion
       const buckets = ["concept-images", "palette-images"];
       for (const bucket of buckets) {
         const { data: files } = await supabaseAdmin.storage
           .from(bucket)
           .list();
         if (files && files.length > 0) {
           const filePaths = files.map((file) => file.name);
           await supabaseAdmin.storage.from(bucket).remove(filePaths);
         }
       }

       return new Response(
         JSON.stringify({ message: "All data purged successfully" }),
         {
           headers: { "Content-Type": "application/json" },
           status: 200,
         },
       );
     } catch (error) {
       return new Response(JSON.stringify({ error: error.message }), {
         headers: { "Content-Type": "application/json" },
         status: 500,
       });
     }
   });
   ```

2. Deploy the function:

   ```bash
   supabase functions deploy purge-data
   ```

3. Create a scheduled cron trigger in the Supabase dashboard or using external scheduling services like GitHub Actions or cloud schedulers.

### 8. Testing the Purge Functionality

Before relying on scheduled purging, test the functionality manually:

1. Generate some test data through your application
2. Verify data exists in tables and storage buckets
3. Run the purge script manually:
   ```bash
   python backend/scripts/purge_data.py
   ```
4. Verify all data has been deleted from tables and storage buckets

### 9. Important Considerations

1. **Data Backup**: Consider backing up important data before purging if needed
2. **Service Disruption**: Be aware that purging while the application is in use may cause disruptions
3. **Rate Limits**: Large data purges might hit API rate limits; consider implementing batching
4. **Security**: Keep your admin API key secure and restrict access to the purge endpoint
5. **Logging**: Maintain logs of purge operations for troubleshooting and verification

By implementing this data purge process, you ensure that your application maintains data privacy and keeps storage usage manageable by removing all data on a nightly basis.

## Conclusion

With Supabase properly set up, your Concept Visualizer application now has:

- Persistent storage for concepts and color palettes in PostgreSQL
- Efficient image storage using Supabase Storage
- Session management without requiring user authentication
- Secure access controls through Row Level Security
- High-performance data access through indexes

This infrastructure provides a solid foundation for future enhancements like user accounts, sharing features, and more sophisticated image processing for color palette applications.
