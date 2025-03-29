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

## Step 2: Set Up Storage Buckets for Images

Before creating the database schema, we need to set up storage buckets for our images:

1. In the Supabase dashboard, navigate to the "Storage" section in the left sidebar

2. Click "Create a new bucket"

3. Create the following buckets:
   - **Name:** `concept-images` (for base images)
     - **Public/Private:** Private (we'll set up access policies)
     - **File size limit:** 5MB (adequate for most generated images)
     - Click "Create bucket"

   - **Name:** `palette-images` (for color palette variations)
     - **Public/Private:** Private
     - **File size limit:** 5MB
     - Click "Create bucket"

4. Set up access policies for each bucket:
   - Click on the bucket name
   - Go to the "Policies" tab
   - Click "Create a new policy"
   
   For anonymous read access:
   - Policy name: `Anonymous read access`
   - Policy definition: `true` (allows anyone to read images)
   - Operations: SELECT
   - Click "Save policy"
   
   For session-based write access (add to both buckets):
   - Policy name: `Session-based write access`
   - Policy definition: 
     ```sql
     request.headers->>'concept_session' IN (
       SELECT id::text FROM sessions
     )
     ```
   - Operations: INSERT, UPDATE
   - Click "Save policy"

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
   - You should see the three new tables: `sessions`, `concepts`, and `color_variations`
   - Note that we're now using `base_image_path` and `image_path` instead of URLs, as these will store the Supabase Storage paths

## Step 4: Configure Database Access Policies

For security, we'll set up Row Level Security (RLS) policies:

1. Navigate to "Authentication" → "Policies" in the sidebar

2. For each table, enable Row Level Security:
   - Click on the table name
   - Toggle "Enable RLS" to ON
   - This ensures only authorized users can access specific rows

3. Set up policies for the `sessions` table:
   - Click "New Policy"
   - Choose "Create a policy from scratch"
   - Policy name: `Allow session owner access`
   - For the definition, use:
     ```sql
     (auth.uid() = session_id) OR
     (auth.uid() IS NULL AND request.headers->>'concept_session' = id::text)
     ```
   - Operations: Select all (SELECT, INSERT, UPDATE, DELETE)
   - This policy allows access if:
     - The authenticated user ID matches the session ID, OR
     - For anonymous users, the cookie header matches the session ID
   - Click "Save Policy"

4. For anonymous session creation:
   - Click "New Policy" again
   - Policy name: `Allow anonymous session creation`
   - Definition: `auth.uid() IS NULL`
   - Operations: INSERT
   - This allows anonymous users to create sessions
   - Click "Save Policy"

5. For the `concepts` table:
   - Create a policy named `Session owner access`
   - Definition: 
     ```sql
     session_id IN (
       SELECT id FROM sessions
       WHERE auth.uid() = session_id OR
         (auth.uid() IS NULL AND request.headers->>'concept_session' = id::text)
     )
     ```
   - Operations: SELECT, INSERT, UPDATE
   - This allows users to access only concepts associated with their session
   - Click "Save Policy"

6. For the `color_variations` table:
   - Create a policy named `Concept owner access`
   - Definition:
     ```sql
     concept_id IN (
       SELECT id FROM concepts
       WHERE session_id IN (
         SELECT id FROM sessions
         WHERE auth.uid() = session_id OR
           (auth.uid() IS NULL AND request.headers->>'concept_session' = id::text)
       )
     )
     ```
   - Operations: SELECT, INSERT, UPDATE
   - This allows users to access only color variations associated with their concepts
   - Click "Save Policy"

## Step 5: Get API Keys

To connect your application to Supabase:

1. Go to "Project Settings" → "API" in the sidebar

2. Note down two important values:
   - **Project URL:** Your Supabase project URL (e.g., `https://[project-id].supabase.co`)
   - **anon key:** The public API key for anonymous access

3. These values will be used in your application's environment variables

4. Important: Never expose the `service_role` key in client-side code; it bypasses RLS policies

## Step 6: Set Up Backend Environment

1. Create or update your `.env` file in the backend directory:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key
JIGSAWSTACK_API_KEY=your-jigsawstack-api-key
```

2. Install the Supabase client in your backend:

```bash
uv add supabase
uv add python-multipart  # Required for file handling
uv add pillow  # For image processing
```

3. If needed, create a requirements file that includes the Supabase dependency:

```
# requirements.txt
supabase>=1.0.0
python-multipart>=0.0.5
pillow>=8.0.0
```

## Step 7: Implement Backend Integration

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

### 3. Image Service

Create a dedicated service for image handling:

```python
# backend/app/services/image_service.py
from fastapi import Depends
from typing import List, Dict, Optional, Tuple
from ..core.supabase import get_supabase_client, SupabaseClient
from ..core.jigsawstack_client import JigsawStackClient, get_jigsawstack_client

class ImageService:
    """Service for image generation and storage."""
    
    def __init__(
        self, 
        supabase_client: SupabaseClient = Depends(get_supabase_client),
        jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client)
    ):
        """Initialize image service with required clients."""
        self.supabase_client = supabase_client
        self.jigsawstack_client = jigsawstack_client
    
    async def generate_and_store_image(self, prompt: str, session_id: str) -> Tuple[str, str]:
        """Generate an image and store it in Supabase.
        
        Args:
            prompt: Image generation prompt
            session_id: Current session ID
            
        Returns:
            Tuple of (storage_path, public_url) or (None, None) on error
        """
        try:
            # Generate image using JigsawStack
            result = await self.jigsawstack_client.generate_image(prompt=prompt)
            if not result or "url" not in result:
                return None, None
                
            # Download and upload to Supabase Storage
            storage_path = await self.supabase_client.upload_image_from_url(
                result["url"], 
                "concept-images", 
                session_id
            )
            
            if not storage_path:
                return None, None
                
            # Get public URL
            public_url = self.supabase_client.get_image_url(storage_path, "concept-images")
            
            return storage_path, public_url
        except Exception as e:
            return None, None
    
    async def create_palette_variations(
        self, 
        base_image_path: str, 
        palettes: List[Dict], 
        session_id: str
    ) -> List[Dict]:
        """Create variations of an image with different color palettes.
        
        Args:
            base_image_path: Storage path of the base image
            palettes: List of color palette dictionaries
            session_id: Current session ID
            
        Returns:
            List of palettes with added image_path and image_url fields
        """
        result_palettes = []
        
        for palette in palettes:
            # Apply palette to image
            palette_image_path = await self.supabase_client.apply_color_palette(
                base_image_path,
                palette["colors"],
                session_id
            )
            
            if palette_image_path:
                # Get public URL
                palette_image_url = self.supabase_client.get_image_url(
                    palette_image_path, 
                    "palette-images"
                )
                
                # Add paths to palette dict
                palette_copy = palette.copy()
                palette_copy["image_path"] = palette_image_path
                palette_copy["image_url"] = palette_image_url
                result_palettes.append(palette_copy)
                
        return result_palettes
```

### 4. Update API Endpoints

Modify the API endpoints in `backend/app/api/routes/concept.py` to use the new storage approach:

```python
from fastapi import APIRouter, Depends, Response, Cookie
from typing import Optional, List
from ...models.request import PromptRequest, RefinementRequest
from ...models.response import GenerationResponse
from ...models.concept import ConceptSummary, ConceptDetail
from ...services.concept_service import ConceptService, get_concept_service
from ...services.session_service import SessionService, get_session_service
from ...services.image_service import ImageService, get_image_service
from ...services.concept_storage_service import ConceptStorageService, get_concept_storage_service

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    image_service: ImageService = Depends(get_image_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service)
):
    """Generate a concept based on user prompt and store it."""
    # Get or create session
    session_id, _ = await session_service.get_or_create_session(response)
    
    # Generate base image and store it
    base_image_path, base_image_url = await image_service.generate_and_store_image(
        request.logo_description,
        session_id
    )
    
    # Generate color palettes
    palettes = await concept_service.generate_color_palettes(request.theme_description)
    
    # Apply color palettes to create variations
    palette_variations = await image_service.create_palette_variations(
        base_image_path,
        palettes,
        session_id
    )
    
    # Store concept in database
    concept = await storage_service.store_concept(
        session_id=session_id,
        logo_description=request.logo_description,
        theme_description=request.theme_description,
        base_image_path=base_image_path,
        color_palettes=palette_variations
    )
    
    # Return response
    return GenerationResponse(
        prompt_id=concept["id"],
        image_url=base_image_url,
        color_palettes=[
            {
                "name": p["name"],
                "colors": p["colors"],
                "description": p.get("description"),
                "image_url": p["image_url"]
            } 
            for p in palette_variations
        ]
    )

@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """Get recent concepts for the current session."""
    # Get or create session
    session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
    
    # Return empty list for new sessions
    if is_new_session:
        return []
    
    # Get recent concepts
    return await storage_service.get_recent_concepts(session_id)
```

## Step 8: Set Up Frontend Environment

1. Create or update your `.env` file in the frontend directory:

```
VITE_API_BASE_URL=http://localhost:8000
```

2. Ensure your API client is configured to send cookies with requests using Axios:

```typescript
// api.ts
import axios from 'axios';

const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important: This allows cookies to be sent
});

export default apiClient;
```

## Step 9: Testing the Integration

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

## Step 10: Troubleshooting Common Issues

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

## Conclusion

With Supabase properly set up, your Concept Visualizer application now has:

- Persistent storage for concepts and color palettes in PostgreSQL
- Efficient image storage using Supabase Storage
- Session management without requiring user authentication
- Secure access controls through Row Level Security
- High-performance data access through indexes

This infrastructure provides a solid foundation for future enhancements like user accounts, sharing features, and more sophisticated image processing for color palette applications. 