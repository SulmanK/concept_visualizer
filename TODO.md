# Concept Visualizer - Project TODO

## Design Documents

### Backend Component Design
- [x] Design document for JigsawStack client implementation
  - [x] Image generation client
  - [x] Text generation client
- [x] Design document for API endpoints
  - [x] Generate concept endpoint
  - [x] Refine concept endpoint
- [x] Design document for service layer
  - [x] Concept generation service
  - [x] Color palette generation function
- [x] Design document for data models
  - [x] Request/response models
  - [x] Internal data structures
- [x] Design document for Supabase integration
  - [x] Database schema
  - [x] Session management
  - [x] Concept storage service
  - [x] Image storage using Supabase Storage

### Frontend Component Design
- [x] Design document for shared components (Button, LoadingSpinner, ErrorMessage)
- [x] Design document for ConceptCreator feature
- [x] Design document for Refinement feature
- [x] Design document for frontend hooks and services (API client, error handling, etc.)
- [x] Design document for frontend state management with Supabase
  - [x] Context for recent concepts
  - [x] Integration with API client

## Frontend Structure Improvements (Clean Code)

### Directory Structure and Organization
- [x] Implement consistent feature folder structure
- [x] Create feature-based organization for all features
- [x] Ensure each feature follows the pattern:
  ```
  features/
  ├── feature-name/
  │   ├── components/          # Feature-specific components
  │   ├── hooks/               # Feature-specific hooks
  │   ├── types/               # Feature-specific types
  │   ├── __tests__/           # Tests co-located with feature
  │   ├── index.ts             # Exports the main component
  │   └── FeatureName.tsx      # Main feature component
  ```
- [x] Move `RecentConcepts` from components to features directory
- [ ] Ensure all shared components are in the appropriate directories

### Refactor Large Components
- [x] Refactor `ConceptGenerator.tsx` (currently 478 lines)
  - [x] Create `features/concept-generator/` directory
  - [x] Extract `HowItWorks` section to a separate component
  - [x] Extract `ConceptHeader` to a separate component
  - [x] Extract `ResultsSection` to a separate component
  - [x] Remove all inline styles and move to CSS modules or Tailwind classes
  - [x] Create proper index.ts export file
  - [x] Restructure main component to use the extracted components

- [x] Refactor `ConceptRefinement.tsx` into a proper feature directory
  - [x] Create `features/concept-refinement/` directory
  - [x] Extract components following same pattern as concept-generator
  - [x] Remove all inline styles and use consistent styling approach

### Styling Consistency
- [x] Establish consistent styling approach
  - [x] Either use CSS modules or Tailwind classes consistently
  - [x] Remove all inline styles from components
  - [x] Use design tokens from `styles/variables.css` for all styles
  - [x] Create utility classes for common style patterns
  - [x] Update components to use the consistent styling approach

### Type Organization
- [x] Reorganize types for better maintainability
  - [x] Split monolithic `types/index.ts` into domain-specific files
    - [x] Create `types/api.types.ts` for API-related types
    - [x] Create `types/concept.types.ts` for concept-related types
    - [x] Create `types/ui.types.ts` for UI component types
    - [x] Create `types/form.types.ts` for form-related types
  - [x] Move feature-specific types to their feature directories
  - [x] Update imports across the codebase to use the new type structure

### Test Organization 
- [x] Complete test co-location with components
  - [x] Move remaining tests from central `__tests__` directory to component directories
  - [x] Ensure consistent test naming patterns
  - [x] Create test utilities directory for shared test helpers
  - [x] Update test imports across the codebase

## Theme selection and UI design
- [x] Create theme variations
- [x] Select Modern Gradient Violet theme as the project theme
- [x] **URGENT: Implement Modern Gradient Indigo theme**
  - [x] Update color palette in tailwind.config.js to use indigo color scheme
  - [x] Update base styles to match the Modern Gradient Indigo aesthetic
  - [x] Apply new background gradients to page sections
  - [x] Update component styling to match Modern Gradient Indigo design
  - [x] **Refine component styling to match mockup design**
    - [x] Card component enhancement
      - [x] Add backdrop-blur-sm effect to cards
      - [x] Update background to white/90 opacity
      - [x] Refine card border and shadow styles to match mockup
    - [x] Header & Navigation
      - [x] Make header more compact (reduced height)
      - [x] Update nav buttons to pill-shaped design
      - [x] Adjust logo size and spacing
      - [x] Remove bottom border for cleaner look
    - [x] Recent Concepts section
      - [x] Implement gradient header backgrounds for concept cards
      - [x] Add centered initials in a white circle for each concept
      - [x] Fix grid layout to 3 columns with proper spacing
      - [x] Style color palette display with consistent sizing
    - [x] Form elements
      - [x] Refine input and textarea styling with proper padding (px-4 py-3)
      - [x] Update focus states to use ring-2 ring-primary/30
      - [x] Add helper text styling below inputs
      - [x] Ensure consistent label styling (font-medium text-indigo-700)
    - [x] How It Works section
      - [x] Implement numbered circles with indigo-100 background
      - [x] Create 3-column grid layout for features
      - [x] Add proper spacing between features
      - [x] Style action buttons with proper spacing
    - [x] Navigation
      - [x] Update active/inactive states for nav items
      - [x] Add proper hover effects for nav items
      - [x] Refine spacing between nav items
    - [x] Visual polish
      - [x] Ensure consistent spacing between all sections
      - [x] Add subtle animation effects for interactive elements
      - [x] Update button styles to fully match the mockup design
      - [x] Verify typography hierarchy matches the mockup

## Frontend component design
- [x] Design document for ConceptCreator feature
- [x] Design document for Refinement feature
- [x] Design document for frontend hooks and services (API client, error handling, etc.)

## Phase 1: Basic Implementation
- [x] Initialize project structure (backend and frontend)
- [x] Set up backend (FastAPI) with Python 3.11
- [x] Configure basic API routing structure
- [x] Create API models for request/response types
- [x] Set up the JigsawStack integration service for the API
- [x] Implement the concept generation and refinement endpoints
- [x] Implement the Modern Gradient Violet theme in the frontend setup
- [x] Create core UI components (Button, Input, TextArea, Card, etc.)
- [x] Implement the API hooks for frontend-backend communication
- [x] Build ConceptGenerator feature
- [x] Build ConceptRefinement feature
- [x] Set up routing structure with React Router

## Phase 1.5: Component Verification
### Frontend Verification
- [x] Set up the frontend testing infrastructure
  - [x] Install and configure Vitest for React testing
  - [x] Set up JSDOM for browser environment testing
  - [x] Configure test utilities and helper functions
  - [x] Create test scripts in package.json
- [x] Create baseline utility function tests
  - [x] Implement string utilities test suite
  - [x] Implement format utilities test suite
  - [x] Implement validation utilities test suite
- [x] Verify UI components functionality
  - [x] Test Button component with different variants and states
  - [x] Test Input and TextArea components with validation
  - [x] Test Card component with different content structures
  - [x] Test ColorPalette component with sample data
  - [x] Test Header component with different routes and states
  - [x] Test Footer component with year prop and link rendering
  - [x] Fix failing component tests to match implementation (Header/Footer fixed)
  - [x] Add snapshot tests for critical UI components
  - [x] Test ConceptForm component with form submission and validation
  - [x] Test ConceptRefinementForm component with form submission and aspect selection
  - [x] Test ConceptResult component with rendering and button interactions
- [ ] Verify API hooks
  - [ ] Create mock service for API testing
  - [ ] Update mock implementation in test setup file
  - [x] Test useApi hook with different request types
  - [x] Test useConceptGeneration hook with success and error scenarios
  - [x] Test useConceptRefinement hook with various inputs
  - [x] **Fix failing hook tests**
    - [x] Fix useApi.test.ts - simplified tests to focus on public API
    - [x] Fix useConceptGeneration.test.ts - simplified to test validation and state transitions
    - [x] Fix useConceptRefinement.test.ts - simplified to test validation and state transitions
- [x] Verify feature components
  - [x] Test ConceptGenerator component workflow
  - [x] Test ConceptRefinement component with mock data
  - [x] Test Home component rendering
  - [x] Test TestHeader component
  - [x] Verify navigation between components
  - [x] Test state management in feature components
- [x] Implement end-to-end testing
  - [x] Set up Playwright for E2E testing
  - [x] Create end-to-end test for concept generation flow
  - [x] Create end-to-end test for concept refinement flow
  - [x] Add visual regression tests for key pages
- [x] Verify responsive design across different viewport sizes
  - [x] Create viewport size testing utility
  - [x] Test components at mobile, tablet, and desktop sizes
  - [x] Verify layout shifts and responsive behaviors
- [x] Implement accessibility testing
  - [x] Set up axe-core with Playwright
  - [x] Create accessibility test suite for all pages
  - [x] Check WCAG 2.0 A and AA compliance
  - [x] Verify form elements have proper labels and ARIA attributes

## Modern Gradient Indigo Theme Implementation (URGENT)
- [x] Update color scheme and typography
  - [x] Change primary colors from violet to indigo (`#4F46E5`/`#4338CA`) in tailwind.config.js
  - [x] Update secondary colors to lighter indigo (`#818CF8`/`#6366F1`)
  - [x] Adjust accent color to `#EEF2FF`
  - [x] Ensure Montserrat font is consistently applied
- [x] Update component styles
  - [x] Modify button gradients to use indigo color palette
  - [x] Update card styling with new shadow and border colors
  - [x] Adjust form inputs to use indigo focus states
  - [x] Update loading spinners with indigo colors
- [x] Implement layout improvements
  - [x] Add backdrop blur effect to header and cards
  - [x] Update page background to indigo gradient
  - [x] Improve spacing and padding in form layouts
  - [x] Add better card styling for concept display
- [x] Update visual elements
  - [x] Implement gradient text for headings
  - [x] Update error messages with indigo styling
  - [x] Add consistent border-radius across components
  - [x] Ensure proper hover and focus states on all interactive elements
- [ ] Responsive design improvements
  - [ ] Ensure mobile layout is optimized
  - [ ] Fix any responsive issues with cards grid
  - [ ] Test all breakpoints for consistent experience

### Backend Verification
- [ ] Verify API endpoints
  - [x] Test health endpoint
  - [ ] Test concept generation endpoint with various inputs
  - [ ] Test concept refinement endpoint with different parameters
- [ ] Verify JigsawStack integration
  - [ ] Create mock JigsawStack API responses
  - [ ] Test with minimal valid inputs
  - [ ] Test with edge case inputs
- [ ] Verify error handling
  - [ ] Test error responses for invalid inputs
  - [ ] Test error handling for JigsawStack API failures
  - [ ] Test validation error messages
- [ ] Run load testing on key endpoints
- [ ] Create API documentation with Swagger UI

## Phase 2: Supabase Integration and Recent Concepts Feature

- [x] Set up Supabase project
  - [x] Create Supabase project for development
  - [x] Configure database access policies
  - [x] Create database schema (sessions, concepts, color_variations)
  - [x] Set up indexes for query optimization
  - [x] Configure storage buckets for images
    - [x] Create `concept-images` bucket for base images
    - [x] Create `palette-images` bucket for color variations
    - [x] Set up access policies for buckets
- [x] Backend Supabase integration preparation
  - [x] Install Supabase Python client
  - [x] Install Pillow for image processing
  - [x] Add dependencies to pyproject.toml
  - [x] Implement SupabaseClient class
  - [x] Create environment configuration for Supabase credentials
  - [x] Implement SessionService for cookie-based session management
  - [x] Implement ImageService for image storage and retrieval
    - [x] Implement function to download images from JigsawStack
    - [x] Implement function to upload images to Supabase Storage
    - [x] Implement function to apply color palettes to images
  - [x] Implement ConceptStorageService for storing/retrieving concepts
  - [x] Update API endpoints to use Supabase services
    - [x] Update existing concept generation and refinement endpoints
    - [x] Add new endpoints for retrieving recent concepts
    - [x] Add endpoint for retrieving concept details
- [x] Frontend Supabase integration
  - [x] Configure API client to support cookie-based authentication
  - [x] Implement ConceptContext for global state management
  - [x] Create RecentConcepts component for displaying stored concepts
  - [x] Update useConceptGeneration hook to refresh recent concepts
  - [x] Create ConceptDetail page for viewing stored concepts
  - [x] Add route for concept detail page
- [ ] Cross-browser testing for cookie handling
  - [ ] Test session persistence in Chrome, Firefox, Safari
  - [ ] Verify cookie secure flags work correctly
  - [ ] Test session expiration handling
<!-- - [ ] Implement image processing service (not doing this for now)
  - [ ] Research approaches for applying color palettes to images
  - [ ] Implement basic solution for MVP (using same image for all palettes)
  - [ ] Plan for future enhancements with proper colorization -->

## Phase 3: Enhanced Features and Polish
- [ ] Add user authentication for saving concepts
- [ ] Create a concept gallery to browse saved concepts
- [ ] Add concept comparison functionality
- [ ] Implement a favorites feature for marking preferred concepts
- [ ] Create export functionality for concepts in different formats
- [ ] Add concept sharing capabilities
- [ ] Implement loading states and error displays
- [ ] Add animations and transitions
- [ ] Create responsive designs for mobile

## Phase 4: Advanced Features
- [ ] Implement concept categories and tagging
- [ ] Add advanced refinement options (style transfer, color manipulation)
- [ ] Integrate AI-assisted concept suggestions
- [ ] Add user preferences for default theme and style settings
- [ ] Create concept versioning to track changes
- [ ] Implement batch generation for multiple concepts at once
- [ ] Add analytics for concept performance (user ratings, shares, etc.)
- [ ] Create enterprise features (team sharing, permissions, etc.)

## Project Management
- [ ] Set up GitHub repository
- [ ] Configure GitHub Actions for CI/CD
  - [ ] Set up continuous integration for frontend tests
  - [ ] Create workflow for backend tests
  - [ ] Configure deployment pipeline
- [ ] Create issue templates
- [ ] Define release process

## Concept Visualizer - Current Status

### Testing Progress
- [x] UI Component Tests: Fixed and passing
  - [x] Button, Card, Input, TextArea components
  - [x] Header, Footer components
  - [x] ColorPalette component
- [x] Concept Component Tests: Fixed and passing
  - [x] ConceptForm component
  - [x] ConceptRefinementForm component
  - [x] ConceptResult component
- [x] Feature Component Tests: Fixed and passing
  - [x] ConceptGenerator component
  - [x] ConceptRefinement component
  - [x] Home component
  - [x] ~~TestHeader component~~ (Removed: TestHeader component and tests were removed to clean up the codebase)
- [x] Hook Tests: Fixed and passing
  - [x] useApi hook
  - [x] useConceptGeneration hook
  - [x] useConceptRefinement hook

### Code Refactoring Progress
- [x] CSS Refactoring
  - [x] Combined header-fix.css and header.module.css into a single file
  - [x] Converted Header component from inline styles to CSS modules
  - [x] Improved organization and documentation in CSS files
- [x] Structure Refactoring - Initial Improvements
  - [x] Moved App.tsx out of App/ directory to root level
  - [x] Created a proper styles directory with variables.css and global.css
  - [x] Converted Home.tsx to a feature-based structure with dedicated components
  - [x] Implemented co-location of tests with components (examples in Button and HomePage)
  - [x] Removed redundant CSS files and consolidated styles

### Next Steps
- [x] Implement API mock service for better integration tests
- [x] Set up end-to-end testing with Playwright
- [x] Add responsive design tests
- [x] Add visual regression tests
- [x] Add accessibility testing
- [ ] Implement Supabase integration for data persistence
- [ ] Set up Supabase Storage for image storage
- [ ] Add "Recent Concepts" feature to the UI 
- [ ] **Implement the Frontend Structure Improvements (Clean Code)**
  - [ ] Refactor large components (ConceptGenerator, ConceptRefinement)
  - [ ] Establish consistent feature-based organization
  - [ ] Consolidate styling approach (either CSS modules or Tailwind)
  - [ ] Reorganize types for better maintainability
  - [ ] Complete test co-location with components

## Supabase Storage Integration Checklist

- [x] Create Supabase project and configure API keys
- [x] Install Supabase client libraries for Python backend
- [x] Create storage buckets in Supabase:
  - [x] `concept-images` bucket for base concept images
  - [x] `palette-images` bucket for color variations
- [x] Configure storage access policies:
  - [x] Public read access for both buckets
  - [x] Public write access with application-level security
- [x] Implement `upload_image_from_url` method in `SupabaseClient`
  - [x] Handle downloading images from JigsawStack
  - [x] Generate unique filenames with session-based folders
  - [x] Upload to appropriate bucket
- [x] Implement `get_image_url` method to generate public URLs
- [x] Implement `apply_color_palette` method for palette variations
- [x] Update `ImageService` methods to use Supabase storage:
  - [x] `generate_and_store_image` for base concept images
  - [x] `create_palette_variations` for palette-specific images
  - [x] `refine_and_store_image` for refined concepts
- [x] Update response models to include image URLs
- [x] Test the complete flow from API to storage and back

## Integration Testing Recommendations

The following tests should be performed to ensure proper storage integration:

1. Generate a concept and verify images are stored in correct Supabase buckets
2. Check that image paths follow the `{session_id}/{uuid}.{extension}` pattern
3. Confirm that public URLs are accessible in a web browser
4. Verify different sessions have files in separate folders
5. Test the palette variations by checking both storage and retrieval
6. Ensure refined images are properly stored and retrievable 