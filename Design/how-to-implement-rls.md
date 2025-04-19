# How to Implement Row Level Security (RLS) with Session IDs

This guide provides step-by-step instructions for implementing Supabase Row Level Security (RLS) for the Concept Visualizer application using session IDs. This approach secures storage buckets without requiring user registration.

## Overview

Row Level Security (RLS) in Supabase allows for fine-grained access control to data and files based on the requesting user or session. With this approach, we can:

- Make storage buckets private
- Allow users to access only their own files
- Prevent unauthorized access to images
- Maintain the session-based, no-registration model

## Implementation Steps

### 1. Update Supabase Storage Buckets

First, modify your Supabase storage buckets to be private:

1. **Navigate to Supabase Dashboard**
   - Go to your project → Storage → Buckets

2. **Update Bucket Settings**
   - For each bucket (`concept-images` and `palette-images`):
     - Click on the bucket name
     - Go to "Settings"
     - Set "Public Bucket" to OFF
     - Click "Save"

3. **Remove Existing Policies**
   - For each bucket, go to "Policies" tab
   - Delete any existing policies (we'll add new, more secure ones)

### 2. Create RLS Policies for Session-Based Access

Next, create policies that allow access based on session ID passed in a custom header:

1. **Create Policy for the `concept-images` Bucket**:
   - Go to "Policies" tab for the bucket
   - Click "Add Policy"
   - Choose "Create a policy from scratch"
   - Fill in the following:
     - **Policy Name**: `Access own session images`
     - **Target Roles**: `authenticated` and `anon` (select both)
     - **Using Policy Definition** (for read access):
     ```sql
     -- Check if the first segment of the path (session ID) matches the session ID in header
     bucket_id = 'concept-images' 
     AND 
     REGEXP_SUBSTR(name, '^[^/]+') = coalesce(
       current_setting('request.headers', true)::json->>'x-concept-session',
       ''
     )
     ```
     - **Operations**: `SELECT` (for read access)
     - Click "Save Policy"

   - Add another policy for write access:
     - **Policy Name**: `Upload to own session folder`
     - **Target Roles**: `authenticated` and `anon` (select both)
     - **Using Policy Definition**:
     ```sql
     -- Check if the first segment of the path (session ID) matches the session ID in header
     bucket_id = 'concept-images' 
     AND 
     REGEXP_SUBSTR(name, '^[^/]+') = coalesce(
       current_setting('request.headers', true)::json->>'x-concept-session',
       ''
     )
     ```
     - **Operations**: `INSERT`
     - Click "Save Policy"

   - Add a policy for delete access:
     - **Policy Name**: `Delete own session images`
     - **Target Roles**: `authenticated` and `anon` (select both)
     - **Using Policy Definition**:
     ```sql
     -- Check if the first segment of the path (session ID) matches the session ID in header
     bucket_id = 'concept-images' 
     AND 
     REGEXP_SUBSTR(name, '^[^/]+') = coalesce(
       current_setting('request.headers', true)::json->>'x-concept-session',
       ''
     )
     ```
     - **Operations**: `DELETE`
     - Click "Save Policy"

2. **Repeat for the `palette-images` Bucket**
   - Create identical policies for the palette-images bucket, just change the bucket_id to 'palette-images'

### 3. Update Backend Image Storage Service

Modify your storage service to include the session ID header with requests:

```python
# backend/app/services/image/storage.py

class ImageStorageService:
    # ... existing code ...
    
    def get_image(self, image_path: str, session_id: str, is_palette: bool = False) -> bytes:
        """
        Retrieve an image from storage.
        
        Args:
            image_path: Path of the image in storage
            session_id: Session ID for access control
            is_palette: Whether the image is a palette (uses palette-images bucket)
            
        Returns:
            Image data as bytes
            
        Raises:
            ImageNotFoundError: If image is not found
            ImageStorageError: If image retrieval fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Add session ID header for RLS
            headers = {"x-concept-session": session_id}
            
            # Download the image
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                response = self.supabase.client.storage.from_(bucket_name).download(
                    path=image_path,
                    headers=headers
                )
            else:
                response = self.supabase.storage.from_(bucket_name).download(
                    path=image_path,
                    headers=headers
                )
                
            return response
            
        except Exception as e:
            error_msg = f"Failed to get image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            
            if "404" in str(e) or "not found" in str(e).lower():
                raise ImageNotFoundError(f"Image not found: {image_path}")
                
            # Access denied errors
            if "403" in str(e) or "forbidden" in str(e).lower() or "access denied" in str(e).lower():
                self.logger.warning(f"Access denied to image {image_path}, possibly due to RLS policy")
                raise ImageStorageError(f"Access denied to image: {image_path}")
                
            raise ImageStorageError(error_msg)
    
    def get_public_url(self, image_path: str, session_id: str, is_palette: bool = False) -> str:
        """
        Get the access URL for an image in storage.
        
        With RLS, these are not truly "public" URLs anymore - they require
        the session ID header to be present when accessing them.
        
        Args:
            image_path: Path to the image in storage
            session_id: Session ID for access control
            is_palette: Whether this is a palette image (uses palette-images bucket)
            
        Returns:
            Access URL for the image
            
        Raises:
            ImageStorageError: If URL generation fails
        """
        try:
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Get the base URL
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                url = self.supabase.client.storage.from_(bucket_name).get_public_url(image_path)
            else:
                url = self.supabase.storage.from_(bucket_name).get_public_url(image_path)
            
            # For frontend direct access, we need to append a custom query parameter
            # that will be processed by our frontend interceptor to add the header
            url = f"{url}?session_id={session_id}"
                
            return url
                
        except Exception as e:
            error_msg = f"Failed to get access URL for image {image_path}: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
    
    def store_image(
        self, 
        image_data: Union[bytes, BytesIO, UploadFile], 
        session_id: str,
        concept_id: Optional[str] = None,
        file_name: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_palette: bool = False,
    ) -> str:
        """
        Store an image in the appropriate bucket.
        
        Args:
            image_data: Image data to store
            session_id: User session ID for RLS
            concept_id: Optional concept ID associated with the image
            file_name: Optional file name to use
            metadata: Optional metadata to store with the image
            is_palette: Whether this is a palette image
            
        Returns:
            Public URL of stored image
        """
        try:
            # ... existing image processing code ...
            
            # Make sure path starts with session_id
            # This is critical for RLS path-based policies
            path = f"{session_id}/{file_name}"
            if concept_id:
                path = f"{session_id}/{concept_id}/{file_name}"
                
            # Add session ID header for RLS
            headers = {"x-concept-session": session_id}
            
            # Select the appropriate bucket
            bucket_name = self.palette_bucket if is_palette else self.concept_bucket
            
            # Upload with session header
            if hasattr(self.supabase, 'client') and hasattr(self.supabase.client, 'storage'):
                self.supabase.client.storage.from_(bucket_name).upload(
                    path=path,
                    file=image_data,
                    file_options={"contentType": content_type},
                    headers=headers
                )
                
                # Get public URL with session parameter for frontend
                url = self.supabase.client.storage.from_(bucket_name).get_public_url(path)
                url = f"{url}?session_id={session_id}"
            else:
                self.supabase.storage.from_(bucket_name).upload(
                    path=path,
                    file=image_data,
                    file_options={"contentType": content_type},
                    headers=headers
                )
                
                # Get public URL with session parameter for frontend
                url = self.supabase.storage.from_(bucket_name).get_public_url(path)
                url = f"{url}?session_id={session_id}"
                
            return url
            
        except Exception as e:
            error_msg = f"Failed to store image: {str(e)}"
            self.logger.error(error_msg)
            raise ImageStorageError(error_msg)
```

### 4. Update API Request Handlers

Ensure your API endpoints extract the session ID and pass it to the image service:

```python
# backend/app/api/routes/concept/generation.py

@router.post("/generate", response_model=ConceptGenerationResponse)
async def generate_concept(
    request: ConceptPromptRequest,
    session_id: str = Cookie(None, alias="concept_session"),
    concept_service: ConceptService = Depends(get_concept_service)
):
    """Generate a concept based on the provided prompt."""
    
    try:
        # Generate the concept
        concept = await concept_service.generate_concept(request.prompt, session_id)
        
        # Get the public URL with session ID for frontend 
        image_url = await concept_service.get_concept_image_url(concept["id"], session_id)
        
        return {
            "concept_id": concept["id"],
            "image_url": image_url
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### 5. Update Frontend Supabase Client

Configure your frontend Supabase client to include the session ID header with requests:

```typescript
// frontend/src/services/supabaseClient.ts
import { createClient } from '@supabase/supabase-js';
import Cookies from 'js-cookie';

// Function to create a Supabase client with session headers
const createSupabaseClient = () => {
  // Get session from cookie
  const sessionId = Cookies.get('concept_session');
  
  // Create client with custom headers
  return createClient(
    import.meta.env.VITE_SUPABASE_URL,
    import.meta.env.VITE_SUPABASE_ANON_KEY,
    {
      global: {
        headers: {
          'x-concept-session': sessionId || '',
        },
      },
    }
  );
};

// Create the client
const supabaseClient = createSupabaseClient();

// Export a function to refresh client when session changes
export const refreshSupabaseClient = () => {
  // Get current session ID
  const sessionId = Cookies.get('concept_session');
  
  // Update headers on the global fetch
  supabaseClient.storage.setAuth(sessionId || '');
};

export default supabaseClient;
```

### 6. Update Frontend Image Components

Add a request interceptor to your frontend to handle image URLs with session parameters:

```typescript
// frontend/src/utils/imageInterceptor.ts
import Cookies from 'js-cookie';

// Create an interceptor function to modify image URLs before they're fetched
export function createImageUrlInterceptor() {
  // Original fetch function
  const originalFetch = window.fetch;
  
  // Override fetch to add headers for storage URLs
  window.fetch = function (input, init) {
    // Only intercept string URLs (not Request objects)
    if (typeof input === 'string') {
      const url = new URL(input);
      
      // Check if this is a Supabase storage URL and has a session_id parameter
      if (
        url.host.includes('supabase') && 
        url.pathname.includes('storage/v1/object') && 
        url.searchParams.has('session_id')
      ) {
        // Extract the session ID from the URL
        const sessionId = url.searchParams.get('session_id');
        // Remove it from URL to avoid exposing it
        url.searchParams.delete('session_id');
        
        // Create headers if they don't exist
        const headers = init?.headers || {};
        const newHeaders = new Headers(headers);
        
        // Add the session ID header
        newHeaders.set('x-concept-session', sessionId);
        
        // Update the init object with our new headers
        init = {
          ...init,
          headers: newHeaders,
        };
        
        // Update input to use the cleaned URL
        input = url.toString();
      }
    }
    
    // Call the original fetch with possibly modified parameters
    return originalFetch.call(window, input, init);
  };
}

// Apply this interceptor when the app starts
export function setupImageInterceptor() {
  createImageUrlInterceptor();
}
```

Initialize this interceptor in your app's entry point:

```typescript
// frontend/src/main.tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import { setupImageInterceptor } from './utils/imageInterceptor';

// Set up image interceptor
setupImageInterceptor();

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
```

Update your image components to handle the session parameter:

```tsx
// frontend/src/components/concept/ConceptImage.tsx
import React from 'react';
import supabaseClient from '../../services/supabaseClient';

interface ConceptImageProps {
  path: string;
  sessionId: string;
  isPalette?: boolean;
  alt: string;
  className?: string;
}

const ConceptImage: React.FC<ConceptImageProps> = ({ 
  path, 
  sessionId,
  isPalette = false, 
  alt, 
  className 
}) => {
  // The URL already contains the session_id parameter from the backend
  // The interceptor will handle adding the header when the image is fetched
  const bucketName = isPalette ? 'palette-images' : 'concept-images';
  let imageUrl = supabaseClient.storage.from(bucketName).getPublicUrl(path).data.publicUrl;
  
  // Add session_id parameter if not already present (e.g., for directly constructed URLs)
  if (!imageUrl.includes('session_id=')) {
    imageUrl = `${imageUrl}?session_id=${sessionId}`;
  }
  
  return (
    <img 
      src={imageUrl} 
      alt={alt} 
      className={className}
      // Handle access errors
      onError={(e) => {
        console.error('Error loading image:', path);
        // Optionally replace with fallback image
        e.currentTarget.src = '/path/to/fallback-image.png';
      }}
    />
  );
};

export default ConceptImage;
```

### 7. Update Session Management

Ensure your session management code sets the session cookie and makes it available to components:

```tsx
// frontend/src/context/SessionContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import Cookies from 'js-cookie';
import { refreshSupabaseClient } from '../services/supabaseClient';

interface SessionContextProps {
  sessionId: string | null;
  isLoading: boolean;
  refreshSession: () => Promise<void>;
}

const SessionContext = createContext<SessionContextProps>({
  sessionId: null,
  isLoading: true,
  refreshSession: async () => {},
});

export const SessionProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const loadSession = async () => {
    try {
      // Try to get session from cookie
      const cookieSession = Cookies.get('concept_session');
      
      if (cookieSession) {
        setSessionId(cookieSession);
      } else {
        // If no session, fetch one from the server
        const response = await fetch('/api/session', {
          method: 'POST',
          credentials: 'include',
        });
        
        if (response.ok) {
          const data = await response.json();
          setSessionId(data.session_id);
        }
      }
    } catch (error) {
      console.error('Error loading session:', error);
    } finally {
      setIsLoading(false);
    }
  };
  
  const refreshSession = async () => {
    try {
      const response = await fetch('/api/session/refresh', {
        method: 'POST',
        credentials: 'include',
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        
        // Refresh the Supabase client with the new session
        refreshSupabaseClient();
      }
    } catch (error) {
      console.error('Error refreshing session:', error);
    }
  };
  
  useEffect(() => {
    loadSession();
  }, []);
  
  return (
    <SessionContext.Provider
      value={{
        sessionId,
        isLoading,
        refreshSession,
      }}
    >
      {children}
    </SessionContext.Provider>
  );
};

export const useSession = () => useContext(SessionContext);
```

Use the session context in your components:

```tsx
// frontend/src/components/concept/ConceptDisplay.tsx
import React from 'react';
import ConceptImage from './ConceptImage';
import { useSession } from '../../context/SessionContext';

interface ConceptDisplayProps {
  conceptId: string;
  imagePath: string;
}

const ConceptDisplay: React.FC<ConceptDisplayProps> = ({ conceptId, imagePath }) => {
  const { sessionId, isLoading } = useSession();
  
  if (isLoading || !sessionId) {
    return <div>Loading...</div>;
  }
  
  return (
    <div className="concept-container">
      <h3>Concept: {conceptId}</h3>
      <ConceptImage 
        path={imagePath}
        sessionId={sessionId}
        alt={`Concept ${conceptId}`}
        className="concept-image"
      />
    </div>
  );
};

export default ConceptDisplay;
```

## Testing the Implementation

After implementing RLS with custom headers, test your application thoroughly:

1. **Session Creation Test**
   - Start a fresh browser session
   - Generate a concept
   - Verify an image is created and visible
   - Check browser network tab to verify the x-concept-session header is sent with image requests

2. **Session Persistence Test**
   - Close and reopen the browser
   - Verify you can still see your previously generated concepts

3. **Cross-Session Security Test**
   - Extract an image URL from one browser session
   - Open an incognito window (with a different session)
   - Try to access the image URL directly without the header
   - Verify access is denied

4. **Policy Test in SQL Editor**
   - In Supabase Dashboard, go to SQL Editor
   - Test your policy logic with example values:
   ```sql
   -- Simulate a request with a specific header
   SELECT
     bucket_id = 'concept-images' AND
     REGEXP_SUBSTR('session123/image.png', '^[^/]+') = 'session123'
   ```

## Troubleshooting Common Issues

### Images Not Loading

If images fail to load after implementing RLS:

1. **Check Browser Console and Network Tab**
   - Look for 403 (Forbidden) errors
   - Verify the x-concept-session header is being sent with image requests
   - Check that the header value matches the session ID in the path

2. **Test Policy Logic**
   - Use Supabase SQL Editor to test policy logic with example values
   - Temporarily simplify policies for debugging

3. **Check Path Format**
   - Ensure your image paths always start with the session ID
   - Example: `{session_id}/{timestamp}_{random}.png`

### Permission Errors on Upload

If you can't upload images:

1. **Verify Headers in Upload Requests**
   - Check that the x-concept-session header is being sent with upload requests

2. **Simplify Policy Temporarily**
   - Try setting a very permissive policy to isolate the issue
   - Add complexity back gradually

## Conclusion

By implementing Row Level Security with session IDs in custom headers, you've created a secure and reliable storage system for your Concept Visualizer application. This approach:

- Restricts access to images based on session ownership
- Prevents unauthorized access and enumeration
- Maintains a smooth user experience
- Works reliably across browsers and environments
- Leverages Supabase's built-in security features

The implementation is secure and operates efficiently as the security checks happen at the database level rather than in your application code. Using custom headers provides better reliability than cookies for Supabase RLS policies while maintaining the same level of security. 