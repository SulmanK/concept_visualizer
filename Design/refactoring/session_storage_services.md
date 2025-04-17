# Session and Storage Services Refactoring Design Document

## Problem Statement

The current Session and Storage services have grown in complexity and would benefit from better separation of concerns:

- `session/manager.py` (364 lines): Manages user sessions with several responsibilities
- `storage/concept_storage.py` (371 lines): Handles concept storage with intertwined responsibilities

While these files aren't as large as the image services, they still handle multiple distinct responsibilities that should be separated for better maintainability and testability.

## Goals

1. Improve separation of concerns in session management
2. Split storage services by entity type and functionality
3. Create clear interfaces for each service component
4. Maintain backward compatibility with existing service users
5. Enhance testability with smaller, focused components
6. Reduce code duplication
7. Improve error handling and logging consistency

## Design

### 1. Session Services Architecture

The refactored session services will be organized as follows:

```
app/services/session/
├── __init__.py                # Export factory functions and interfaces
├── interfaces.py              # Session service interfaces
├── auth.py                    # Session authentication service
├── persistence.py             # Session persistence service
├── lifecycle.py               # Session lifecycle management
├── manager.py                 # Main session service (uses composition)
└── factory.py                 # Factory functions
```

### 2. Storage Services Architecture

The refactored storage services will be organized as follows:

```
app/services/storage/
├── __init__.py                # Export factory functions and interfaces
├── interfaces.py              # Storage service interfaces
├── concept/                   # Concept storage services
│   ├── __init__.py
│   ├── persistence.py         # Basic concept persistence
│   ├── query.py               # Concept querying operations
│   └── factory.py             # Factory functions
├── palette/                   # Palette storage services
│   ├── __init__.py
│   ├── persistence.py         # Palette persistence
│   └── factory.py             # Factory functions
├── utils.py                   # Shared storage utilities
└── factory.py                 # Main factory functions
```

### 3. Session Services Components

#### 3.1 Session Authentication Service (`auth.py`)

```python
class SessionAuthService:
    """Service for session authentication operations."""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize with a Supabase client."""
        self.supabase_client = supabase_client
        self.logger = logging.getLogger(__name__)
    
    async def validate_session(self, session_id: str) -> bool:
        """Validate that a session exists and is active."""
        # Implementation...
    
    def get_session_client(self, session_id: str) -> SupabaseClient:
        """Get a Supabase client configured with the session ID in headers."""
        # Implementation...
```

#### 3.2 Session Persistence Service (`persistence.py`)

```python
class SessionPersistenceService:
    """Service for session storage operations."""
    
    def __init__(self, session_storage: SessionStorage):
        """Initialize with a SessionStorage instance."""
        self.session_storage = session_storage
        self.logger = logging.getLogger(__name__)
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get a session by ID."""
        # Implementation...
    
    async def create_session(self) -> Dict[str, Any]:
        """Create a new session."""
        # Implementation...
    
    async def create_session_with_id(self, session_id: str) -> Dict[str, Any]:
        """Create a new session with a specific ID."""
        # Implementation...
    
    async def update_session_activity(self, session_id: str) -> bool:
        """Update the last activity timestamp of a session."""
        # Implementation...
```

#### 3.3 Session Lifecycle Service (`lifecycle.py`)

```python
class SessionLifecycleService:
    """Service for session lifecycle management."""
    
    def __init__(self, session_storage: SessionStorage):
        """Initialize with a SessionStorage instance."""
        self.session_storage = session_storage
        self.logger = logging.getLogger(__name__)
    
    async def expire_session(self, session_id: str) -> bool:
        """Mark a session as expired."""
        # Implementation...
    
    async def clean_expired_sessions(self, max_age_days: int = 30) -> int:
        """Clean up expired sessions older than specified days."""
        # Implementation...
    
    def _set_session_cookie(self, response: Response, session_id: str, max_age: int = 2592000) -> None:
        """Set a session cookie in the response."""
        # Implementation (2592000 = 30 days)...
```

#### 3.4 Main Session Service (`manager.py`)

```python
class SessionService:
    """Main service for session management using composition."""
    
    def __init__(
        self,
        auth_service: SessionAuthService,
        persistence_service: SessionPersistenceService,
        lifecycle_service: SessionLifecycleService
    ):
        """Initialize with specialized services."""
        self.auth = auth_service
        self.persistence = persistence_service
        self.lifecycle = lifecycle_service
        self.logger = logging.getLogger(__name__)
    
    async def get_or_create_session(
        self, 
        response: Response,
        session_id: Optional[str] = Cookie(None, alias="concept_session"),
        client_session_id: Optional[str] = None
    ) -> Tuple[str, bool]:
        """Get existing session or create a new one."""
        # Implementation using composition...
    
    # Other methods delegating to specialized services...
```

### 4. Storage Services Components

#### 4.1 Concept Persistence Service (`concept/persistence.py`)

```python
class ConceptPersistenceService:
    """Service for basic concept persistence operations."""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize with a Supabase client."""
        self.supabase_client = supabase_client
        self.logger = logging.getLogger(__name__)
    
    async def store_concept(self, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Store a new concept."""
        # Implementation...
    
    async def update_concept(self, concept_id: str, concept_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update an existing concept."""
        # Implementation...
    
    async def delete_concept(self, concept_id: str, session_id: str) -> bool:
        """Delete a concept."""
        # Implementation...
```

#### 4.2 Concept Query Service (`concept/query.py`)

```python
class ConceptQueryService:
    """Service for concept retrieval operations."""
    
    def __init__(self, supabase_client: SupabaseClient, image_storage: ImageStorage):
        """Initialize with a Supabase client and image storage."""
        self.supabase_client = supabase_client
        self.image_storage = image_storage
        self.logger = logging.getLogger(__name__)
    
    async def get_recent_concepts(self, session_id: str, limit: int = 10) -> List[ConceptSummary]:
        """Get recent concepts for a session."""
        # Implementation...
    
    async def get_concept_detail(self, concept_id: str, session_id: str) -> Optional[ConceptDetail]:
        """Get detailed information about a specific concept."""
        # Implementation...
    
    async def search_concepts(
        self, 
        session_id: str, 
        query: str, 
        limit: int = 10, 
        offset: int = 0
    ) -> Tuple[List[ConceptSummary], int]:
        """Search concepts by text query."""
        # Implementation...
```

#### 4.3 Palette Persistence Service (`palette/persistence.py`)

```python
class PalettePersistenceService:
    """Service for palette persistence operations."""
    
    def __init__(self, supabase_client: SupabaseClient):
        """Initialize with a Supabase client."""
        self.supabase_client = supabase_client
        self.logger = logging.getLogger(__name__)
    
    async def store_color_variations(
        self, 
        concept_id: str,
        variations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Store color variations for a concept."""
        # Implementation...
    
    async def get_color_variations(self, concept_id: str) -> List[Dict[str, Any]]:
        """Get color variations for a concept."""
        # Implementation...
    
    async def update_color_variation(
        self, 
        variation_id: str,
        variation_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update a color variation."""
        # Implementation...
```

#### 4.4 Main Storage Factory (`factory.py`)

```python
def get_concept_persistence_service(
    supabase_client: Optional[SupabaseClient] = None
) -> ConceptPersistenceService:
    """Get a concept persistence service instance."""
    if supabase_client is None:
        supabase_client = get_supabase_client()
    
    return ConceptPersistenceService(supabase_client)

def get_concept_query_service(
    supabase_client: Optional[SupabaseClient] = None,
    image_storage: Optional[ImageStorage] = None
) -> ConceptQueryService:
    """Get a concept query service instance."""
    if supabase_client is None:
        supabase_client = get_supabase_client()
    if image_storage is None:
        image_storage = get_image_storage(supabase_client)
    
    return ConceptQueryService(supabase_client, image_storage)

# Legacy support
def get_concept_storage_service(
    supabase_client: Optional[SupabaseClient] = None
) -> ConceptStorageService:
    """Get the main concept storage service (for backward compatibility)."""
    if supabase_client is None:
        supabase_client = get_supabase_client()
    
    persistence = get_concept_persistence_service(supabase_client)
    query = get_concept_query_service(supabase_client)
    palette = get_palette_persistence_service(supabase_client)
    
    return ConceptStorageService(persistence, query, palette)
```

### 5. Interfaces and Protocols

Define clear interfaces for each service:

```python
class SessionAuthInterface(Protocol):
    """Interface for session authentication services."""
    
    async def validate_session(self, session_id: str) -> bool: ...
    
    def get_session_client(self, session_id: str) -> SupabaseClient: ...

class SessionPersistenceInterface(Protocol):
    """Interface for session persistence services."""
    
    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]: ...
    
    async def create_session(self) -> Dict[str, Any]: ...
    
    async def create_session_with_id(self, session_id: str) -> Dict[str, Any]: ...
    
    async def update_session_activity(self, session_id: str) -> bool: ...

# Other interfaces...
```

### 6. Backward Compatibility

To maintain backward compatibility:

1. Keep the original service class names and factory functions
2. Refactor the implementation to use composition with the new specialized services
3. Update documentation to encourage using the new specialized services
4. Add deprecation warnings to original methods (optional)

## Implementation Plan

### Phase 1: Session Services Refactoring

1. Create session interfaces
2. Implement session component services
3. Refactor SessionService to use composition
4. Create factory functions
5. Update tests

### Phase 2: Storage Services Refactoring

1. Create storage interfaces
2. Implement concept storage components
3. Implement palette storage components
4. Refactor ConceptStorageService to use composition
5. Create factory functions
6. Update tests

### Phase 3: Integration

1. Update service dependencies
2. Ensure backward compatibility
3. Verify all functionality
4. Update documentation

## Testing Strategy

1. Create unit tests for each service component
2. Mock dependencies for isolated testing
3. Create integration tests to verify correct interactions
4. Test backwards compatibility with existing code
5. Test error handling and edge cases

## Risks and Mitigations

1. **Risk**: Breaking changes in session handling affecting user experience
   **Mitigation**: Thorough testing of session creation/retrieval flows

2. **Risk**: Data access patterns change affecting performance
   **Mitigation**: Profile and benchmark query performance before and after changes

3. **Risk**: Complex dependencies between services
   **Mitigation**: Clear interface definitions and factory functions

## Timeline

- Phase 1 (Session Services): 2 days
- Phase 2 (Storage Services): 3 days
- Phase 3 (Integration): 1 day
- Testing: 2 days

Total: 8 days 