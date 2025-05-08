# Supabase Anonymous Authentication Migration Plan

## Problem Statement

The application currently uses a custom session management system with manually implemented session ID generation, synchronization, and persistence. This approach has several issues:

1. Multiple redundant sync requests on page refresh
2. Complex backend caching mechanisms that require manual optimization
3. Distributed session management logic across frontend and backend
4. No built-in security mechanism for authentication claims
5. Maintenance burden of custom session management

## Solution: Migrate to Supabase Anonymous Authentication

We will replace our custom session management with Supabase's Anonymous Authentication, which provides:

1. Built-in JWT-based authentication
2. Seamless conversion from anonymous to permanent users
3. Built-in security with role-based permissions
4. Standard authentication flows and token management
5. Centralized session state management

## Current Architecture

### Backend (FastAPI)

- Custom session management in `app/services/session/manager.py`
- Session storage in `app/core/supabase/session_storage.py`
- Session API endpoints in `app/api/routes/session/session_routes.py`

### Frontend (React)

- Custom session management in `src/services/sessionManager.ts`
- Session synchronization logic in multiple components
- Multiple scattered session sync requests

## Target Architecture

### Backend

- Remove custom session endpoints
- Use Supabase Auth's JWT verification for authentication
- Add middleware to verify Supabase JWTs
- Use Row Level Security (RLS) with `is_anonymous` claim for data access

### Frontend

- Centralized session management with Supabase Auth
- Single point of initialization for anonymous sign-in
- React Context Provider for session state
- Custom hooks for accessing session information

## Implementation Plan

### Phase 1: Backend Changes

#### 1.1 Update Supabase Client Integration

```python
# app/core/supabase/client.py

import os
from supabase import create_client, Client
from fastapi import Request, HTTPException
import jwt
from typing import Optional, Dict, Any

class SupabaseAuthClient:
    """Client for Supabase authentication."""

    def __init__(self):
        """Initialize the Supabase authentication client."""
        self.url = os.environ.get("CONCEPT_SUPABASE_URL")
        self.key = os.environ.get("CONCEPT_SUPABASE_KEY")
        self.jwt_secret = os.environ.get("CONCEPT_SUPABASE_JWT_SECRET")

        if not self.url or not self.key:
            raise ValueError("Supabase URL and key must be provided")

        self.client = create_client(self.url, self.key)

    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and return the payload."""
        try:
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"],
                options={"verify_signature": True}
            )
            return payload
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    def get_user_from_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Extract user information from request authorization header."""
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None

        token = auth_header.replace("Bearer ", "")
        return self.verify_token(token)
```

#### 1.2 Create Auth Middleware

```python
# app/core/middleware/auth.py

from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.supabase.client import SupabaseAuthClient
import logging

logger = logging.getLogger("auth_middleware")

class AuthMiddleware(BaseHTTPMiddleware):
    """Middleware to handle authentication."""

    def __init__(self, app):
        """Initialize the middleware with Supabase client."""
        super().__init__(app)
        self.auth_client = SupabaseAuthClient()

    async def dispatch(self, request: Request, call_next):
        """Process the request to check authentication."""
        # Skip authentication for certain paths
        if self._should_skip_auth(request.url.path):
            return await call_next(request)

        # Verify the token
        try:
            user = self.auth_client.get_user_from_request(request)
            if not user:
                # Anonymous access is permitted for many routes
                # Continue processing with anonymous role
                request.state.user = None
                request.state.is_anonymous = True
            else:
                # Set user data in request state
                request.state.user = user
                request.state.is_anonymous = user.get("is_anonymous", False)

            # Continue processing
            return await call_next(request)

        except HTTPException as e:
            # Handle auth errors
            logger.warning(f"Auth error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Middleware error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"detail": "Internal server error during authentication"}
            )

    def _should_skip_auth(self, path: str) -> bool:
        """Determine if authentication should be skipped for this path."""
        public_paths = [
            "/api/health",
            "/api/docs",
            "/api/openapi.json",
        ]

        for public_path in public_paths:
            if path.startswith(public_path):
                return True

        return False
```

#### 1.3 Update API Dependencies

```python
# app/api/dependencies.py

from fastapi import Depends, Request, HTTPException
from typing import Dict, Any, Optional

def get_current_user(request: Request) -> Optional[Dict[str, Any]]:
    """Get the current user from request state."""
    return request.state.user

def get_verified_user(
    user: Optional[Dict[str, Any]] = Depends(get_current_user)
) -> Dict[str, Any]:
    """Get the current user, ensuring they are authenticated."""
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )
    return user
```

#### 1.4 Remove Legacy Session Routes

Delete or deprecate the following files:

- `app/api/routes/session/session_routes.py`
- `app/services/session/manager.py`

#### 1.5 Update Concept Storage to Use Anonymous Authentication

```python
# app/core/supabase/concept_storage.py

# Update methods to use user_id instead of session_id
def get_concepts_by_user(
    self,
    user_id: str,
    limit: int = 20,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """Get concepts by user ID."""
    # Implementation...

# Update create_concept to use user_id
def create_concept(
    self,
    user_id: str,
    logo_description: str,
    theme_description: str,
    image_path: str,
    # ...other parameters
) -> Dict[str, Any]:
    """Create a new concept."""
    # Implementation...
```

### Phase 2: Frontend Changes

#### 2.1 Update Supabase Client with Anonymous Auth

```typescript
// src/services/supabaseClient.ts

import { createClient } from "@supabase/supabase-js";

// Environment variables for Supabase
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || "";
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || "";

// Create default client
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
});

/**
 * Initialize anonymous authentication
 * @returns Promise with session data
 */
export const initializeAnonymousAuth = async () => {
  // Check if we have an existing session
  let {
    data: { session },
  } = await supabase.auth.getSession();

  // If no session exists, sign in anonymously
  if (!session) {
    console.log("No session found, signing in anonymously");
    const { data, error } = await supabase.auth.signInAnonymously();

    if (error) {
      console.error("Error signing in anonymously:", error);
      throw error;
    }

    session = data.session;
    console.log("Anonymous sign-in successful");
  } else {
    console.log("Using existing session");
  }

  return session;
};

/**
 * Get the current user ID
 * @returns User ID string or null if not authenticated
 */
export const getUserId = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  return session?.user?.id || null;
};

/**
 * Check if the current user is anonymous
 * @returns Boolean indicating if user is anonymous
 */
export const isAnonymousUser = async () => {
  const {
    data: { session },
  } = await supabase.auth.getSession();
  if (!session) return false;

  // Check is_anonymous claim in JWT
  const claims = session.user.app_metadata;
  return claims.is_anonymous === true;
};

/**
 * Convert anonymous user to permanent by linking email
 * @param email User's email address
 * @returns Promise with result
 */
export const linkEmailToAnonymousUser = async (email: string) => {
  return await supabase.auth.updateUser({ email });
};

/**
 * Sign out the current user
 * @returns Promise with sign out result
 */
export const signOut = async () => {
  return await supabase.auth.signOut();
};
```

#### 2.2 Create Session Context

```typescript
// src/contexts/AuthContext.tsx

import React, { createContext, useContext, useEffect, useState } from "react";
import { Session, User } from "@supabase/supabase-js";
import { supabase, initializeAnonymousAuth } from "../services/supabaseClient";

interface AuthContextType {
  session: Session | null;
  user: User | null;
  isAnonymous: boolean;
  isLoading: boolean;
  error: Error | null;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isAnonymous, setIsAnonymous] = useState<boolean>(false);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  useEffect(() => {
    // Initialize auth once on mount
    const initAuth = async () => {
      try {
        setIsLoading(true);

        // Initialize anonymous authentication
        const session = await initializeAnonymousAuth();
        setSession(session);
        setUser(session?.user || null);
        setIsAnonymous(session?.user?.app_metadata?.is_anonymous || false);

        // Set up auth state listener
        const {
          data: { subscription },
        } = supabase.auth.onAuthStateChange((event, session) => {
          setSession(session);
          setUser(session?.user || null);
          setIsAnonymous(session?.user?.app_metadata?.is_anonymous || false);
        });

        // Return cleanup function
        return () => {
          subscription.unsubscribe();
        };
      } catch (error) {
        console.error("Error initializing auth:", error);
        setError(error as Error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const signOut = async () => {
    try {
      await supabase.auth.signOut();
      // After sign out, initialize a new anonymous session
      await initializeAnonymousAuth();
    } catch (error) {
      console.error("Error signing out:", error);
      setError(error as Error);
    }
  };

  const value = {
    session,
    user,
    isAnonymous,
    isLoading,
    error,
    signOut,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
```

#### 2.3 Update App Component

```typescript
// src/App.tsx

import React from "react";
import { BrowserRouter as Router } from "react-router-dom";
import { AuthProvider } from "./contexts/AuthContext";
import Routes from "./Routes";

const App: React.FC = () => {
  return (
    <Router>
      <AuthProvider>
        <Routes />
      </AuthProvider>
    </Router>
  );
};

export default App;
```

#### 2.4 Create API Client with Auth

```typescript
// src/services/apiClient.ts

import { supabase } from "./supabaseClient";

// Base URL for API
const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

/**
 * Make an authenticated API request
 * @param endpoint API endpoint path
 * @param options Fetch options
 * @returns Promise with response data
 */
export const apiRequest = async (
  endpoint: string,
  options: RequestInit = {},
) => {
  try {
    // Get the current session
    const {
      data: { session },
    } = await supabase.auth.getSession();
    const token = session?.access_token;

    // Prepare headers with auth token
    const headers = {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...options.headers,
    };

    // Make the request
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    // Handle non-OK responses
    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API error (${response.status}): ${errorText}`);
    }

    // Parse JSON response
    const data = await response.json();
    return data;
  } catch (error) {
    console.error(`API request error for ${endpoint}:`, error);
    throw error;
  }
};

/**
 * Convenience methods for common HTTP methods
 */
export const api = {
  get: (endpoint: string, options?: RequestInit) =>
    apiRequest(endpoint, { method: "GET", ...options }),

  post: (endpoint: string, body: any, options?: RequestInit) =>
    apiRequest(endpoint, {
      method: "POST",
      body: JSON.stringify(body),
      ...options,
    }),

  put: (endpoint: string, body: any, options?: RequestInit) =>
    apiRequest(endpoint, {
      method: "PUT",
      body: JSON.stringify(body),
      ...options,
    }),

  delete: (endpoint: string, options?: RequestInit) =>
    apiRequest(endpoint, { method: "DELETE", ...options }),
};
```

#### 2.5 Remove Legacy Session Manager

Delete or refactor:

- `src/services/sessionManager.ts`

#### 2.6 Update Concept Fetching Logic

```typescript
// src/services/conceptService.ts

import { api } from "./apiClient";
import { getUserId } from "./supabaseClient";

/**
 * Fetch recent concepts for the current user
 * @param limit Number of concepts to fetch
 * @returns Array of concept data
 */
export const fetchRecentConcepts = async (limit = 10) => {
  // Get the current user ID
  const userId = await getUserId();

  // If no user ID, return empty array
  if (!userId) {
    return [];
  }

  // Fetch concepts using the API client
  return await api.get(`/concepts?user_id=${userId}&limit=${limit}`);
};
```

### Phase 3: Database and RLS Changes

#### 3.1 Update Database Schema

```sql
-- Concepts table with user_id instead of session_id
CREATE TABLE concepts (
  id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
  user_id UUID REFERENCES auth.users(id) NOT NULL,
  logo_description TEXT NOT NULL,
  theme_description TEXT NOT NULL,
  base_image_path TEXT NOT NULL, -- Path to image in Supabase Storage
  is_anonymous BOOLEAN DEFAULT TRUE -- Flag to identify concepts from anonymous users
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
CREATE INDEX concepts_user_id_idx ON concepts(user_id);
CREATE INDEX color_variations_concept_id_idx ON color_variations(concept_id);
```

#### 3.2 Add Row Level Security Policies

##### Database Table Policies

```sql
-- Enable RLS on tables
ALTER TABLE concepts ENABLE ROW LEVEL SECURITY;
ALTER TABLE color_variations ENABLE ROW LEVEL SECURITY;

-- Concepts table policies
CREATE POLICY "Users can view their own concepts"
ON concepts FOR SELECT
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can create their own concepts"
ON concepts FOR INSERT
TO authenticated
WITH CHECK (user_id = auth.uid());

CREATE POLICY "Users can update their own concepts"
ON concepts FOR UPDATE
TO authenticated
USING (user_id = auth.uid());

CREATE POLICY "Users can delete their own concepts"
ON concepts FOR DELETE
TO authenticated
USING (user_id = auth.uid());

-- Color variations policies
-- These policies use the concept's user_id through a join
CREATE POLICY "Users can view their own color variations"
ON color_variations FOR SELECT
TO authenticated
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can create their own color variations"
ON color_variations FOR INSERT
TO authenticated
WITH CHECK (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can update their own color variations"
ON color_variations FOR UPDATE
TO authenticated
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);

CREATE POLICY "Users can delete their own color variations"
ON color_variations FOR DELETE
TO authenticated
USING (
  concept_id IN (
    SELECT id FROM concepts WHERE user_id = auth.uid()
  )
);
```

##### Storage Bucket Policies

```sql
-- Concept images bucket policies
CREATE POLICY "Users can view their own concept images"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can upload their own concept images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own concept images"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own concept images"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'concept-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

-- Color variation images bucket policies
CREATE POLICY "Users can view their own palette images"
ON storage.objects FOR SELECT
TO authenticated
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can upload their own palette images"
ON storage.objects FOR INSERT
TO authenticated
WITH CHECK (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can update their own palette images"
ON storage.objects FOR UPDATE
TO authenticated
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);

CREATE POLICY "Users can delete their own palette images"
ON storage.objects FOR DELETE
TO authenticated
USING (
  bucket_id = 'palette-images' AND
  (storage.foldername(name))[1] = auth.uid()::text
);
```

Note: For storage buckets, we're organizing files by user ID as the first folder level:

- `concept-images/[user-id]/image1.png`
- `palette-images/[user-id]/palette1.png`

This ensures proper segmentation of files by user through RLS.

### Phase 4: Testing and Rollout

#### 4.1 Test Plan

1. **Unit Tests**

   - Test JWT verification in backend
   - Test anonymous authentication flow in frontend
   - Test API client with auth tokens

2. **Integration Tests**

   - Test end-to-end authentication flow
   - Test concept creation and retrieval with anonymous users
   - Test session persistence across page reloads

3. **User Acceptance Tests**
   - Verify user experience remains intact
   - Verify data migration was successful
   - Verify no data loss occurred

#### 4.2 Rollout Plan

1. **Development Phase**

   - Implement all changes in development environment
   - Run database migration in development
   - Complete all tests in development

2. **Staging Phase**

   - Deploy to staging environment
   - Run database migration in staging
   - Conduct UAT in staging

3. **Production Phase**
   - Deploy backend changes first
   - Run database migration script during off-peak hours
   - Deploy frontend changes
   - Monitor closely for any issues

#### 4.3 Rollback Plan

1. **Frontend Rollback**

   - Keep the old sessionManager.ts code in place during initial deployment
   - If issues occur, revert to using the original session implementation

2. **Backend Rollback**
   - Maintain compatibility with both auth systems during transition
   - If issues occur, disable middleware and revert to session endpoints

## Benefits of Migration

1. **Improved Security**

   - JWT-based authentication with proper claims
   - Built-in session management with expiration
   - Row-level security based on authenticated users

2. **Reduced Code Complexity**

   - Less custom code to maintain
   - Standard authentication patterns
   - Simplified API client logic

3. **Enhanced User Experience**

   - Seamless authentication across page reloads
   - Less network traffic for session management
   - Potential for easier user account creation

4. **Future Extensibility**
   - Easy path to add more authentication methods
   - Support for permanent accounts when needed
   - Built-in account linking capabilities

## Risks and Mitigations

| Risk                      | Mitigation                                           |
| ------------------------- | ---------------------------------------------------- |
| Data migration issues     | Run test migrations in development and staging first |
| User session disruption   | Implement gradual rollout with fallback mechanisms   |
| Performance issues        | Monitor response times and optimize as needed        |
| JWT verification overhead | Use appropriate caching strategies                   |
| Security vulnerabilities  | Follow Supabase security best practices              |

## Timeline

| Phase              | Estimated Duration |
| ------------------ | ------------------ |
| Backend Changes    | 3 days             |
| Frontend Changes   | 3 days             |
| Database Migration | 1 day              |
| Testing            | 2 days             |
| Rollout            | 1 day              |
| **Total**          | **10 days**        |
