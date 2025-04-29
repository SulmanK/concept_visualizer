# Schema Update: Adding Image URL Fields to Database and Components

## Overview

This document outlines the design plan for updating our database schema and application components to properly handle both image paths and image URLs for the Concept Visualizer application. The change addresses URL handling issues with Supabase storage signed URLs and implements a more resilient approach for image management.

## Current Issues

1. **Double-Signed URLs**: We're experiencing issues where image URLs are being double-signed, resulting in corrupted URLs.
2. **Schema Inconsistency**: The database currently has inconsistent schema with `base_image_path` in concepts and `image_path` in color variations, but sometimes storing full URLs.
3. **URL Regeneration**: There's no clear way to regenerate URLs when they expire.
4. **Frontend Double Handling**: Frontend components try to generate signed URLs even when receiving already signed URLs.

## Schema Changes

We're modifying the database schema to add image URL fields and make naming consistent:

```sql
-- Concepts table
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  session_id UUID REFERENCES sessions(id) NOT NULL,
  logo_description TEXT NOT NULL,
  theme_description TEXT NOT NULL,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage (renamed from base_image_path)
  image_url TEXT -- Full signed URL of the image (new field)
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  image_url TEXT -- Full signed URL of the image (new field)
);
```

Key changes:

- Renamed `base_image_path` to `image_path` in the concepts table
- Added `image_url` field to both tables to store signed URLs

## Backend Changes

### Data Models

1. Update Pydantic models in `backend/app/models/`:

```python
# Concept model updates
class ConceptBase(BaseModel):
    logo_description: str
    theme_description: str
    image_path: str
    image_url: Optional[str] = None  # New field

class ConceptInDB(ConceptBase):
    id: UUID
    created_at: datetime
    session_id: UUID

# Color variation model updates
class ColorVariationBase(BaseModel):
    palette_name: str
    colors: List[str]
    description: Optional[str] = None
    image_path: str
    image_url: Optional[str] = None  # New field

class ColorVariationInDB(ColorVariationBase):
    id: UUID
    concept_id: UUID
```

### Storage Services

1. Update `ImageStorageService` to store both path and URL:

```python
def store_image(self, image_data, session_id, concept_id=None, file_name=None, metadata=None, is_palette=False) -> Tuple[str, str]:
    """
    Store an image in the storage bucket and return both path and signed URL.

    Returns:
        Tuple[str, str]: (image_path, image_url)
    """
    # [Existing code for storing the image]

    # Get the storage path
    path = f"{session_id}/{file_name}" if not concept_id else f"{session_id}/{concept_id}/{file_name}"

    # [Existing upload code]

    # Generate signed URL with 3-day expiration
    image_url = self.get_signed_url(path, is_palette=is_palette)

    return path, image_url
```

2. Update `ConceptStorageService` to handle both fields:

```python
async def create_concept(self, session_id: str, logo_description: str, theme_description: str, image_path: str, image_url: str) -> Dict[str, Any]:
    """
    Create a new concept with both image_path and image_url.
    """
    query = """
    INSERT INTO concepts (session_id, logo_description, theme_description, image_path, image_url)
    VALUES ($1, $2, $3, $4, $5)
    RETURNING id, created_at, session_id, logo_description, theme_description, image_path, image_url
    """
    result = await self.database.fetch_one(
        query, session_id, logo_description, theme_description, image_path, image_url
    )
    return dict(result) if result else None

async def create_variation(self, concept_id: str, palette_name: str, colors: List[str], description: str, image_path: str, image_url: str) -> Dict[str, Any]:
    """
    Create a new color variation with both image_path and image_url.
    """
    query = """
    INSERT INTO color_variations (concept_id, palette_name, colors, description, image_path, image_url)
    VALUES ($1, $2, $3, $4, $5, $6)
    RETURNING id, concept_id, palette_name, colors, description, image_path, image_url
    """
    result = await self.database.fetch_one(
        query, concept_id, palette_name, colors, description, image_path, image_url
    )
    return dict(result) if result else None
```

### API Endpoints

1. Update the concept generation endpoint to use both fields:

```python
@router.post("/generate", response_model=GenerationResponse)
async def generate_concept(
    request: PromptRequest,
    background_tasks: BackgroundTasks,
    concept_service: ConceptService = Depends(get_concept_service),
    session_id: str = Depends(get_session_id),
):
    """Generate a new concept based on the provided prompt."""
    # [Existing code]

    # Store generated image
    image_path, image_url = await concept_service.store_generated_image(
        image_data, session_id, concept_id
    )

    # Create concept in database with both path and URL
    concept = await concept_service.create_concept(
        session_id=session_id,
        logo_description=request.logo_description,
        theme_description=request.theme_description,
        image_path=image_path,
        image_url=image_url
    )

    # [Remaining code]
```

## Frontend Changes

### Types and Interfaces

1. Update TypeScript interfaces for concept data:

```typescript
// frontend/src/types/index.ts
export interface ConceptData {
  id: string;
  created_at: string;
  session_id: string;
  logo_description: string;
  theme_description: string;
  image_path: string; // Storage path
  image_url: string; // Signed URL
  // Other fields...
}

export interface ColorVariation {
  id: string;
  concept_id: string;
  palette_name: string;
  colors: string[];
  description?: string;
  image_path: string; // Storage path
  image_url: string; // Signed URL
}
```

### Image Display Components

1. Update `ConceptResult.tsx` to use `image_url` when available:

```typescript
const getFormattedUrl = (url: string | undefined, bucketType = "concept") => {
  if (!url) return "";

  // If we have an image_url from the API, use it directly
  if (url.startsWith("http")) {
    // Handle double-signed URLs by using our URL processing logic
    // [Existing URL detection and processing logic]
    return url;
  }

  // If we only have a path, generate a signed URL
  return getSignedImageUrl(url, bucketType as "concept" | "palette");
};

// When using in component:
const imageUrl =
  concept.image_url || getFormattedUrl(concept.image_path, "concept");
```

2. Update image fetching logic in `ConceptCard` to use `image_url`:

```typescript
// In ConceptCard component
const [imageUrl, setImageUrl] = useState<string>("");

useEffect(() => {
  // If we have an image_url, use it directly
  if (concept.image_url) {
    setImageUrl(concept.image_url);
    return;
  }

  // Otherwise generate from path
  const fetchImageUrl = async () => {
    try {
      const signedUrl = await getImageUrl(concept.image_path, "concept");
      setImageUrl(signedUrl);
    } catch (error) {
      console.error("Error getting image URL:", error);
    }
  };

  fetchImageUrl();
}, [concept]);
```

## Implementation Plan

### Phase 1: Database and Models

1. Update database schema (already done)
2. Update Pydantic models in backend
3. Update TypeScript interfaces in frontend

### Phase 2: Backend Services

1. Modify ImageStorageService to generate and return both path and URL
2. Update ConceptStorageService to store and retrieve both fields
3. Update API endpoints to pass both fields through the system

### Phase 3: Frontend Components

1. Update image URL handling in utility functions
2. Modify components to prefer image_url over generating URLs from paths
3. Update image display components with proper fallbacks

## URL Handling Strategy

The new strategy for URL handling will follow these principles:

1. **Source of Truth**: The database stores both the raw path and the signed URL
2. **Preference Order**:
   - Use `image_url` from the database when available
   - Fall back to generating a new signed URL from `image_path` when needed
3. **Regeneration**: When URLs expire, the system will generate new ones from the paths
4. **Detection**: The frontend will detect already-signed URLs and avoid double-signing

## Conclusion

This schema update provides a more robust approach to handling image URLs in our application. By storing both the path and URL, we gain flexibility in how we access images while preventing issues like double-signing. The implementation plan ensures a smooth transition to the new schema across both backend and frontend components.

The approach aligns with our broader security goals by continuing to use signed URLs for all image access while improving reliability and performance by reducing the need for URL generation on every access.
