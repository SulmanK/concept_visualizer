# Supabase Integration for Backend

## Overview
This document outlines the integration of Supabase with the Concept Visualizer backend for data persistence and session management.

## Database Schema

The Supabase PostgreSQL database will have the following schema:

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
  base_image_url TEXT NOT NULL
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_url TEXT NOT NULL
);

-- Create indexes for performance
CREATE INDEX concepts_session_id_idx ON concepts(session_id);
CREATE INDEX color_variations_concept_id_idx ON color_variations(concept_id);
```

## Supabase Client

```python
# backend/app/core/supabase.py
from supabase import create_client, Client
from pydantic import BaseSettings
import logging

class Settings(BaseSettings):
    """Settings for Supabase configuration."""
    supabase_url: str
    supabase_key: str
    
    class Config:
        env_file = ".env"

class SupabaseClient:
    """Client for interacting with Supabase."""
    
    def __init__(self, settings: Settings):
        """Initialize Supabase client with configured settings.
        
        Args:
            settings: Application settings containing Supabase credentials
        """
        self.client = create_client(settings.supabase_url, settings.supabase_key)
        self.logger = logging.getLogger("supabase_client")
    
    def get_session(self, session_id: str):
        """Get a session by ID.
        
        Args:
            session_id: UUID of the session to retrieve
            
        Returns:
            Session data or None if not found
        """
        try:
            result = self.client.table("sessions").select("*").eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error retrieving session: {e}")
            return None
    
    def create_session(self):
        """Create a new session.
        
        Returns:
            New session data with ID
        """
        try:
            result = self.client.table("sessions").insert({}).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error creating session: {e}")
            return None
    
    def update_session_activity(self, session_id: str):
        """Update session's last_active_at timestamp.
        
        Args:
            session_id: UUID of the session to update
            
        Returns:
            Updated session data or None on error
        """
        try:
            result = self.client.table("sessions").update(
                {"last_active_at": "now()"}
            ).eq("id", session_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error updating session activity: {e}")
            return None
    
    def store_concept(self, concept_data):
        """Store a new concept.
        
        Args:
            concept_data: Dictionary with concept details
            
        Returns:
            Created concept data or None on error
        """
        try:
            result = self.client.table("concepts").insert(concept_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            self.logger.error(f"Error storing concept: {e}")
            return None
    
    def store_color_variations(self, variations):
        """Store color variations for a concept.
        
        Args:
            variations: List of color variation dictionaries
            
        Returns:
            Created color variation data or None on error
        """
        try:
            result = self.client.table("color_variations").insert(variations).execute()
            return result.data
        except Exception as e:
            self.logger.error(f"Error storing color variations: {e}")
            return None
    
    def get_recent_concepts(self, session_id: str, limit: int = 10):
        """Get recent concepts for a session.
        
        Args:
            session_id: UUID of the session
            limit: Maximum number of concepts to return
            
        Returns:
            List of concepts with their variations
        """
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

# Factory function for creating the client
def get_supabase_client(settings: Settings = None):
    """Factory function to get Supabase client.
    
    Args:
        settings: Optional settings object
        
    Returns:
        Configured SupabaseClient instance
    """
    if settings is None:
        settings = Settings()
    return SupabaseClient(settings)
```

## Session Management Service

```python
# backend/app/services/session_service.py
from fastapi import Depends, Cookie, Response
from typing import Optional, Tuple
from ..core.supabase import get_supabase_client, SupabaseClient

class SessionService:
    """Service for managing user sessions."""
    
    def __init__(self, supabase_client: SupabaseClient = Depends(get_supabase_client)):
        """Initialize session service with a Supabase client.
        
        Args:
            supabase_client: Client for interacting with Supabase
        """
        self.supabase_client = supabase_client
        
    async def get_or_create_session(
        self, 
        response: Response,
        session_id: Optional[str] = Cookie(None, alias="concept_session")
    ) -> Tuple[str, bool]:
        """Get existing session or create a new one.
        
        Args:
            response: FastAPI response object for setting cookies
            session_id: Optional existing session ID from cookies
            
        Returns:
            Tuple of (session_id, is_new_session)
        """
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
    """Factory function for SessionService.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        Configured SessionService instance
    """
    return SessionService(supabase_client)
```

## Concept Storage Service

```python
# backend/app/services/concept_storage_service.py
from fastapi import Depends
from typing import List, Dict, Optional
from ..core.supabase import get_supabase_client, SupabaseClient
from ..models.concept import ColorPalette, ConceptSummary, ConceptDetail

class ConceptStorageService:
    """Service for storing and retrieving concepts."""
    
    def __init__(self, supabase_client: SupabaseClient = Depends(get_supabase_client)):
        """Initialize concept storage service with a Supabase client.
        
        Args:
            supabase_client: Client for interacting with Supabase
        """
        self.supabase_client = supabase_client
    
    async def store_concept(
        self,
        session_id: str,
        logo_description: str,
        theme_description: str,
        base_image_url: str,
        color_palettes: List[Dict]
    ) -> Optional[Dict]:
        """Store a new concept and its color variations.
        
        Args:
            session_id: Session ID to associate with the concept
            logo_description: User's logo description
            theme_description: User's theme description
            base_image_url: URL of the generated base image
            color_palettes: List of color palette dictionaries
            
        Returns:
            Created concept data or None on error
        """
        # Insert concept
        concept_data = {
            "session_id": session_id,
            "logo_description": logo_description,
            "theme_description": theme_description,
            "base_image_url": base_image_url
        }
        
        concept = self.supabase_client.store_concept(concept_data)
        if not concept:
            return None
        
        # Insert color variations
        variations = []
        for palette in color_palettes:
            variation = {
                "concept_id": concept["id"],
                "palette_name": palette["name"],
                "colors": palette["colors"],
                "description": palette.get("description"),
                "image_url": palette["image_url"]  # URL to the palette-specific image
            }
            variations.append(variation)
        
        variations_result = self.supabase_client.store_color_variations(variations)
        
        # Return full concept with variations
        if variations_result:
            concept["color_variations"] = variations_result
            return concept
        return concept
    
    async def get_recent_concepts(self, session_id: str, limit: int = 10) -> List[ConceptSummary]:
        """Get recent concepts for a session.
        
        Args:
            session_id: Session ID to get concepts for
            limit: Maximum number of concepts to return
            
        Returns:
            List of concept summaries with their variations
        """
        concepts = self.supabase_client.get_recent_concepts(session_id, limit)
        
        # Convert to ConceptSummary model
        return [self._to_concept_summary(concept) for concept in concepts]
    
    async def get_concept_detail(self, concept_id: str) -> Optional[ConceptDetail]:
        """Get detailed information about a specific concept.
        
        Args:
            concept_id: ID of the concept to retrieve
            
        Returns:
            Concept detail object or None if not found
        """
        try:
            result = self.supabase_client.client.table("concepts").select(
                "*, color_variations(*)"
            ).eq("id", concept_id).execute()
            
            if result.data:
                return self._to_concept_detail(result.data[0])
            return None
        except Exception as e:
            self.supabase_client.logger.error(f"Error retrieving concept detail: {e}")
            return None
    
    def _to_concept_summary(self, concept_data: Dict) -> ConceptSummary:
        """Convert raw concept data to ConceptSummary model.
        
        Args:
            concept_data: Raw concept data from Supabase
            
        Returns:
            ConceptSummary object
        """
        # Implementation depends on ConceptSummary model
        pass
    
    def _to_concept_detail(self, concept_data: Dict) -> ConceptDetail:
        """Convert raw concept data to ConceptDetail model.
        
        Args:
            concept_data: Raw concept data from Supabase
            
        Returns:
            ConceptDetail object
        """
        # Implementation depends on ConceptDetail model
        pass

# Dependency function for FastAPI routes
async def get_concept_storage_service(
    supabase_client: SupabaseClient = Depends(get_supabase_client)
) -> ConceptStorageService:
    """Factory function for ConceptStorageService.
    
    Args:
        supabase_client: Supabase client dependency
        
    Returns:
        Configured ConceptStorageService instance
    """
    return ConceptStorageService(supabase_client)
```

## API Endpoints

```python
# backend/app/api/routes/concept.py
from fastapi import APIRouter, Depends, Response, Cookie
from typing import Optional, List
from ...models.request import PromptRequest, RefinementRequest
from ...models.response import GenerationResponse
from ...models.concept import ConceptSummary, ConceptDetail
from ...services.concept_service import ConceptService, get_concept_service
from ...services.session_service import SessionService, get_session_service
from ...services.concept_storage_service import ConceptStorageService, get_concept_storage_service

router = APIRouter()

@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    response: Response,
    concept_service: ConceptService = Depends(get_concept_service),
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service)
):
    """Generate a concept based on user prompt and store it.
    
    Args:
        request: User prompt request with logo and theme descriptions
        response: FastAPI response object for setting cookies
        concept_service: Service for generating concepts
        session_service: Service for managing sessions
        storage_service: Service for storing concepts
        
    Returns:
        Generated concept with image URL and color palettes
    """
    # Get or create session
    session_id, _ = await session_service.get_or_create_session(response)
    
    # Generate concept
    concept_data = await concept_service.generate_concept(
        request.logo_description,
        request.theme_description
    )
    
    # Store concept in Supabase
    stored_concept = await storage_service.store_concept(
        session_id=session_id,
        logo_description=request.logo_description,
        theme_description=request.theme_description,
        base_image_url=concept_data["image_url"],
        color_palettes=concept_data["color_palettes"]
    )
    
    # Return generation response
    return GenerationResponse(
        prompt_id=stored_concept["id"] if stored_concept else concept_data["prompt_id"],
        image_url=concept_data["image_url"],
        color_palettes=concept_data["color_palettes"]
    )

@router.get("/recent", response_model=List[ConceptSummary])
async def get_recent_concepts(
    response: Response,
    session_service: SessionService = Depends(get_session_service),
    storage_service: ConceptStorageService = Depends(get_concept_storage_service),
    session_id: Optional[str] = Cookie(None, alias="concept_session")
):
    """Get recent concepts for the current session.
    
    Args:
        response: FastAPI response object for setting cookies
        session_service: Service for managing sessions
        storage_service: Service for storing concepts
        session_id: Optional session ID from cookies
        
    Returns:
        List of recent concept summaries
    """
    # Get or create session
    session_id, is_new_session = await session_service.get_or_create_session(response, session_id)
    
    # Return empty list for new sessions
    if is_new_session:
        return []
    
    # Get recent concepts
    return await storage_service.get_recent_concepts(session_id)

@router.get("/concept/{concept_id}", response_model=ConceptDetail)
async def get_concept_detail(
    concept_id: str,
    storage_service: ConceptStorageService = Depends(get_concept_storage_service)
):
    """Get detailed information about a specific concept.
    
    Args:
        concept_id: ID of the concept to retrieve
        storage_service: Service for storing concepts
        
    Returns:
        Concept detail object
    """
    return await storage_service.get_concept_detail(concept_id)
```

## Environment Configuration

The backend will need the following environment variables:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-service-role-key or anon key
JIGSAWSTACK_API_KEY=your-jigsawstack-api-key
```

## Integration with Image Generation

The concept service will need to be updated to apply color palettes to images:

```python
# backend/app/services/image_service.py
from fastapi import Depends
from typing import List, Dict, Optional
import requests
from PIL import Image
import io
import os
from ..core.jigsawstack_client import JigsawStackClient, get_jigsawstack_client

class ImageService:
    """Service for image generation and color palette application."""
    
    def __init__(self, jigsawstack_client: JigsawStackClient = Depends(get_jigsawstack_client)):
        """Initialize with a JigsawStack client.
        
        Args:
            jigsawstack_client: Client for JigsawStack API
        """
        self.jigsawstack_client = jigsawstack_client
    
    async def generate_base_image(self, prompt: str) -> Optional[str]:
        """Generate base image using JigsawStack.
        
        Args:
            prompt: Image generation prompt
            
        Returns:
            URL of generated image or None on error
        """
        response = await self.jigsawstack_client.generate_image(prompt=prompt)
        if response and "url" in response:
            return response["url"]
        return None
    
    async def apply_color_palette(self, base_image_url: str, palette: List[str]) -> Optional[str]:
        """Apply a color palette to the base image.
        
        This is a placeholder for actual implementation. In a real implementation,
        this would either:
        1. Use a specialized API to recolor the image
        2. Use local image processing to apply the palette
        
        For MVP, we might simply associate different palettes with the same image.
        
        Args:
            base_image_url: URL of the base image
            palette: List of hex color codes
            
        Returns:
            URL of the recolored image or None on error
        """
        # For MVP, we'll return the same image for all palettes
        # In a production implementation, this would create variations
        return base_image_url
``` 