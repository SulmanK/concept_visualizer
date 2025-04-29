# Concept Visualizer Design Document

## Current Context

- Currently there is no existing system - this is a new application
- The application will be a simple web-based tool for generating visual concepts and color palettes
- Need to address the gap between textual descriptions and visual representations in creative workflows

## Requirements

### Functional Requirements

- Allow users to input descriptions for a logo and theme
- Generate a base image based on user's logo description
- Generate multiple hex color palette variations based on the theme
- Provide ability to refine results by adding more details to the original prompt
- Display results visually in an intuitive interface
- Store recent concepts for users to review later

### Non-Functional Requirements

- Responsive web interface that works on both desktop and mobile
- Fast response times (ideally under 5 seconds for generation)
- Secure handling of user inputs and API integrations
- Scalable architecture to handle multiple concurrent users
- Accessible design following WCAG guidelines

## Design Decisions

### 1. Tech Stack

Will implement using Python (backend) and React (frontend) because:

- Python offers excellent support for AI/ML integrations and image processing
- React provides a component-based architecture ideal for this interactive UI
- This combination allows for separation of concerns between UI and processing logic
- Deployment on Vercel simplifies CI/CD and offers good performance
- UV will be used for Python package management for better dependency resolution and performance

### 2. API Integration

Will use JigsawStack API for image generation because:

- Provides high-quality image generation capabilities
- Offers customizable parameters for fine-tuning outputs
- Has reliable documentation and support
- Can be integrated with other JigsawStack APIs for enhanced functionality

### 3. Color Palette Generation

Will primarily use JigsawStack's Text Generation API for color palette generation because:

- Provides semantic understanding of themes (e.g., "corporate," "playful")
- Generates color palettes that are conceptually aligned with themes
- Offers flexibility in requesting specific palette types and formats
- Can provide explanations for color choices to enhance user understanding
- More consistent quality compared to image-based extraction methods

Secondary approaches that may complement the primary method:

- Optional fallback to algorithmic generation for complementary colors
- User customization of AI-generated palettes

### 4. Database and State Management

Will use Supabase (PostgreSQL as a service) for storage and state management because:

- Provides PostgreSQL database with robust relational data capabilities
- Offers seamless integration with Vercel deployments
- Provides RESTful and real-time APIs out of the box
- Includes authentication services for future expansion
- Has a generous free tier for development and small applications

Key components for database design:

- Anonymous session tracking via cookies
- Storage of concepts linked to sessions
- Storage of color palette variations for each concept
- Storage of generated images in Supabase Storage buckets, with references in the database
- Organized storage with separate buckets for base concepts and palette variations

### 5. Image Storage with Supabase Storage

Will use Supabase Storage for storing generated images because:

- Provides secure, scalable, and performant object storage
- Integrates seamlessly with Supabase database
- Offers granular access control through Row Level Security (RLS)
- Supports organized file structures with buckets and folders
- Enables image permanence beyond JigsawStack URL expiration
- Allows for future image processing capabilities

Storage architecture:

- Two separate buckets: `concept-images` for base images and `palette-images` for color variations
- Organized folders by session ID for easy management
- Security policies to ensure users can only access their own images
- Database records store image paths rather than full URLs
- Paths follow the pattern: `sessionId/uniqueId.ext` for easy organization

## Technical Design

### 1. Core Components

```python
# Backend Core Components
from typing import List, Dict, Optional
import requests
import logging
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

class PromptRequest(BaseModel):
    """Model for user prompt requests"""
    logo_description: str = Field(..., min_length=3, max_length=500)
    theme_description: str = Field(..., min_length=3, max_length=500)

class RefinementRequest(BaseModel):
    """Model for refinement requests"""
    original_prompt_id: str
    additional_details: str = Field(..., min_length=3, max_length=500)

class ColorPalette(BaseModel):
    """Model for a color palette"""
    name: str
    colors: List[str]  # Hex codes
    description: Optional[str] = None

class GenerationResponse(BaseModel):
    """Model for generation response"""
    prompt_id: str
    image_url: str
    color_palettes: List[ColorPalette]

class JigsawStackClient:
    """Client for interacting with JigsawStack APIs"""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.jigsawstack.com"
        self.logger = logging.getLogger("jigsawstack_client")

    async def generate_image(self, prompt: str, params: Dict = None) -> Dict:
        """Generate image using JigsawStack Image Generation API"""
        # Implementation details
        pass

    async def generate_text(self, prompt: str, params: Dict = None) -> Dict:
        """Generate text using JigsawStack Text Generation API"""
        # Implementation details
        pass

async def generate_color_palette(theme_description: str) -> List[ColorPalette]:
    """Generate multiple color palettes based on theme description.

    Uses JigsawStack Text Generation API to create semantically relevant
    color palettes based on the provided theme.
    """
    prompt = f"""Generate 3 different color palettes in hex code format for: {theme_description}
    For each palette provide:
    1. A descriptive name (2-3 words)
    2. 5 hex color codes
    3. A one-sentence explanation of how it relates to the theme
    Format as JSON: [{{name: string, colors: string[], description: string}}]"""

    response = await jigsawstack_client.generate_text(prompt=prompt, params={"format": "json"})
    return parse_color_palette_response(response)
```

### 2. Data Models

```python
# Frontend Data Models (TypeScript)
interface PromptInput {
  logoDescription: string;
  themeDescription: string;
}

interface ColorPalette {
  name: string;
  colors: string[];  // Hex codes
  description?: string;
  imagePath?: string; // Path to stored image in Supabase
  imageUrl?: string;  // Public URL for the image
}

interface GenerationResult {
  promptId: string;
  imageUrl: string;
  colorPalettes: ColorPalette[];
}

// Error handling
interface ApiError {
  statusCode: number;
  message: string;
  details?: string;
}
```

### 3. Integration Points

- Frontend to Backend API:

  - POST /api/generate - Send prompt and receive generated content
  - POST /api/refine - Send refinement request for existing prompt
  - GET /api/recent - Get recent concepts for the current session

- Backend to JigsawStack APIs:

  - Image generation endpoint for logo creation
  - Text generation endpoint for color palette generation

- Backend to Supabase:

  - Tables for sessions, concepts, and color variations
  - Storage buckets for storing generated images
  - APIs for storing and retrieving concept data and images

- Data flow:
  1. User submits prompt via React UI
  2. Backend receives request and calls JigsawStack Image API for logo
  3. Backend downloads the generated image and uploads it to Supabase Storage
  4. Backend calls JigsawStack Text API for color palette generation
  5. Backend applies color palettes to create variations of the base image and stores them in Supabase Storage
  6. All image paths and metadata are stored in Supabase database tables
  7. Results with public image URLs are returned to frontend for display
  8. User can refine results via additional prompts
  9. User can view recent concepts from their session, loading images directly from Supabase Storage

### 4. Supabase Schema

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
  base_image_path TEXT NOT NULL  -- Path to image in Supabase Storage
);

-- Color variations table
CREATE TABLE color_variations (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  concept_id UUID REFERENCES concepts(id) NOT NULL,
  palette_name TEXT NOT NULL,
  colors JSONB NOT NULL, -- Array of hex codes
  description TEXT,
  image_path TEXT NOT NULL  -- Path to image in Supabase Storage
);
```

### 5. Supabase Storage Configuration

```sql
-- Create storage buckets
-- 1. concept-images: For base concept images
-- 2. palette-images: For color palette variations

-- Storage access policies for concept-images bucket
-- Allow anyone to read images (for display)
CREATE POLICY "Public Read Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'concept-images');

-- Allow session owners to upload images
CREATE POLICY "Session Owner Upload Access"
ON storage.objects FOR INSERT
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = request.headers->>'concept_session'
);

-- Similar policies for palette-images bucket
CREATE POLICY "Public Read Access"
ON storage.objects FOR SELECT
USING (bucket_id = 'palette-images');

CREATE POLICY "Session Owner Upload Access"
ON storage.objects FOR INSERT
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = request.headers->>'concept_session'
);
```

## Implementation Plan

1. Phase 1: Basic Implementation

   - Setup project structure with UV for Python dependency management
   - Implement backend API with FastAPI
   - Create React frontend with basic UI components
   - Integrate with JigsawStack Image API for logo generation
   - Implement color palette generation using JigsawStack Text API
   - Expected timeline: 2 weeks

2. Phase 2: Enhancement

   - Add Supabase integration for data persistence
     - Set up database tables for sessions, concepts, and color variations
     - Configure Supabase Storage buckets for image storage
     - Implement image download and upload service
   - Add anonymous session management with cookies
   - Implement "Recent Concepts" feature using stored data
   - Add refinement functionality
   - Implement error handling and fallback mechanisms
   - Enhance UI with better visualization of results
   - Expected timeline: 1 week

3. Phase 3: Production Readiness
   - Optimize performance
   - Add comprehensive error handling
   - Implement analytics and monitoring
   - Deploy to Vercel
   - Expected timeline: 1 week

## Testing Strategy

### Unit Tests

- Test backend API endpoints using pytest
- Test color palette generation functions
- Test image processing and storage functions
- Test frontend components using React Testing Library
- Mock external API calls for reliable testing
- Test error handling scenarios

### Integration Tests

- Test end-to-end flow from user input to displayed results
- Test error handling and edge cases
- Test refinement workflow
- Verify storage and retrieval of images from Supabase Storage
- Vercel preview deployments for integration testing

## Observability

### Logging

- Use Python's logging module with structured JSON format
- Log API calls, generation times, and error conditions
- Log image storage operations and performance metrics
- Use different log levels based on severity (INFO, ERROR, etc.)
- Include request IDs for traceability across services

### Metrics

- Track API response times
- Monitor generation success rates
- Track image storage operation success rates and times
- Count refinement iterations
- Track user engagement metrics
- Monitor external API and storage usage for cost optimization

## User Experience Considerations

- Provide clear feedback during generation (loading indicators)
- Show meaningful error messages when generation fails
- Allow easy copying/exporting of color codes
- Ensure responsive design works on mobile devices
- Implement keyboard accessibility
- Enable color palette comparison and selection
- Display recent concepts for easy reference
- Ensure images load quickly and efficiently from Supabase Storage

## Future Considerations

### Potential Enhancements

- User accounts for saving generated concepts
- Gallery of public concepts for inspiration
- Export functionality (PNG, PDF, design system specs)
- Custom parameters for advanced users
- Additional image styles and generation options
- More sophisticated image colorization algorithms
- A/B testing different generation prompts

### Known Limitations

- Limited to JigsawStack API capabilities
- Anonymous sessions will eventually expire
- Basic image colorization in initial implementation
- Limited refinement options in first iteration
- Potential for rate limits or cost constraints with external APIs

## Dependencies

### Runtime Dependencies

#### Backend

- Python 3.11
- FastAPI
- Uvicorn
- Requests
- Pydantic
- Python-dotenv
- Pillow (for image processing)
- Supabase Python client

#### Frontend

- React 19+
- TypeScript
- Axios
- React Color (for color visualization)
- Tailwind CSS

### Development Dependencies

- UV (Python package management)
- Pytest
- Black (code formatting)
- ESLint
- Prettier
- React Testing Library

## Security Considerations

- Input validation and sanitization for all user inputs
- Environment variables for API keys and sensitive configurations
- Rate limiting to prevent abuse
- CORS configuration to restrict unauthorized access
- Content moderation for user-generated prompts
- Secure cookie handling for session management
- Storage access policies to restrict image access to legitimate users
- HTTPS for all data transmission
- Proper error handling to prevent information leakage

## Rollout Strategy

1. Development phase - local development and testing
2. Alpha testing - internal testing with sample prompts
3. Beta deployment - limited user testing on Vercel preview
4. Production deployment - public release on Vercel
5. Monitoring period - watch for issues and gather user feedback
6. Iterative improvements based on user feedback

## References

- JigsawStack API documentation
- React documentation
- FastAPI documentation
- Vercel deployment guides
- UV documentation (https://github.com/astral-sh/uv)
- Supabase documentation (https://supabase.com/docs)
- Supabase Storage documentation (https://supabase.com/docs/guides/storage)
- Pillow documentation (https://pillow.readthedocs.io/)
