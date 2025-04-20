# Supabase Client Service

The Supabase Client Service provides a configured Supabase client for the Concept Visualizer application. It handles authentication, session management, storage access, and provides interfaces for interacting with Supabase data.

## Core Features

- Configured Supabase client with automatic token refresh
- Anonymous authentication management
- Session validation and refresh
- Storage access with authenticated URLs
- Concept data retrieval and management

## Key Interfaces

```typescript
export interface ConceptData {
  id: string;
  user_id: string;
  logo_description: string;
  theme_description: string;
  image_path: string;
  image_url: string;
  created_at: string;
  color_variations?: ColorVariationData[];
  storage_path?: string;
}

export interface ColorVariationData {
  id: string;
  concept_id: string;
  palette_name: string;
  colors: string[];
  description?: string;
  image_path: string;
  image_url: string;
  created_at: string;
  storage_path?: string;
}
```

## Authentication Functions

| Function | Description |
|----------|-------------|
| `validateAndRefreshToken()` | Validates the current session token and refreshes if needed |
| `initializeAnonymousAuth()` | Initializes anonymous authentication if no session exists |
| `getUserId()` | Returns the current user ID |
| `isAnonymousUser()` | Checks if the current user is authenticated anonymously |
| `linkEmailToAnonymousUser(email)` | Converts an anonymous user to a permanent account by linking an email |
| `signOut()` | Signs out the current user and creates a new anonymous session |
| `getAuthenticatedClient()` | Returns a Supabase client with valid authentication |

## Storage Functions

| Function | Description |
|----------|-------------|
| `getAuthenticatedImageUrl(bucket, path)` | Generates a signed URL for a storage item |

## Data Access Functions

| Function | Description |
|----------|-------------|
| `fetchRecentConcepts(userId, limit)` | Fetches recent concepts for a user |
| `fetchConceptDetail(conceptId, userId)` | Fetches detailed information about a specific concept |
| `fetchConceptById(conceptId)` | Fetches a concept by ID |
| `getConceptDetails(conceptId)` | Gets detailed information about a concept including variations |

## Usage Examples

### Authentication Management

```typescript
import { initializeAnonymousAuth, isAnonymousUser } from '../services/supabaseClient';

// Initialize anonymous auth on app start
useEffect(() => {
  const init = async () => {
    await initializeAnonymousAuth();
    const anonymous = await isAnonymousUser();
    console.log('User is anonymous:', anonymous);
  };
  
  init();
}, []);
```

### Fetching Concept Data

```typescript
import { fetchRecentConcepts, getUserId } from '../services/supabaseClient';

const RecentConceptsList = () => {
  const [concepts, setConcepts] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    const loadConcepts = async () => {
      setLoading(true);
      try {
        const userId = await getUserId();
        if (userId) {
          const recentConcepts = await fetchRecentConcepts(userId, 5);
          setConcepts(recentConcepts);
        }
      } catch (error) {
        console.error('Failed to load concepts:', error);
      } finally {
        setLoading(false);
      }
    };
    
    loadConcepts();
  }, []);
  
  // Render component with concepts...
};
```

## Implementation Notes

- The service creates a singleton Supabase client instance
- Anonymous authentication is used by default
- Token refresh is handled automatically with a 5-minute pre-expiry threshold
- Rate limits are refreshed after authentication state changes
- Authenticated URLs use signed URLs with a 3-day expiration
- Fallback mechanisms exist for error cases 