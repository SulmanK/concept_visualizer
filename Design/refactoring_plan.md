# Frontend Refactoring Plan

This document outlines the step-by-step process to refactor the frontend codebase to match our new directory structure.

## Goals

1. Make the directory structure match the routing structure
2. Rename components to be more descriptive of their purpose
3. Ensure consistent naming conventions
4. Maintain all existing functionality

## Step 1: Create New Directory Structure

```bash
# Create new directories
mkdir -p frontend/my-app/src/features/landing/components
mkdir -p frontend/my-app/src/features/landing/hooks
mkdir -p frontend/my-app/src/features/landing/types
mkdir -p frontend/my-app/src/features/concepts/detail/components
mkdir -p frontend/my-app/src/features/concepts/recent/components
mkdir -p frontend/my-app/src/features/concepts/create
mkdir -p frontend/my-app/src/features/refinement/components
```

## Step 2: Move and Rename Files (Landing Page)

```bash
# Move concept-generator files to landing
cp frontend/my-app/src/features/concept-generator/ConceptGeneratorPage.tsx frontend/my-app/src/features/landing/LandingPage.tsx
cp -r frontend/my-app/src/features/concept-generator/components/* frontend/my-app/src/features/landing/components/
cp -r frontend/my-app/src/features/concept-generator/hooks/* frontend/my-app/src/features/landing/hooks/
cp -r frontend/my-app/src/features/concept-generator/types/* frontend/my-app/src/features/landing/types/

# Create index.ts
echo "export { LandingPage } from './LandingPage';" > frontend/my-app/src/features/landing/index.ts
```

## Step 3: Update Concept Detail Page

```bash
# Move ConceptDetail to concepts/detail
cp frontend/my-app/src/features/ConceptDetail/ConceptDetail.tsx frontend/my-app/src/features/concepts/detail/ConceptDetailPage.tsx
cp -r frontend/my-app/src/features/ConceptDetail/components/* frontend/my-app/src/features/concepts/detail/components/

# Create index.ts
echo "export { ConceptDetailPage } from './ConceptDetailPage';" > frontend/my-app/src/features/concepts/detail/index.ts
```

## Step 4: Update Recent Concepts Page

```bash
# Move RecentConceptsPage to concepts/recent
cp frontend/my-app/src/features/recent-concepts/RecentConceptsPage.tsx frontend/my-app/src/features/concepts/recent/RecentConceptsPage.tsx
cp -r frontend/my-app/src/features/recent-concepts/components/* frontend/my-app/src/features/concepts/recent/components/

# Create index.ts
echo "export { RecentConceptsPage } from './RecentConceptsPage';" > frontend/my-app/src/features/concepts/recent/index.ts
```

## Step 5: Create Concepts Create Page (redirect to landing)

```bash
# Create index.ts that re-exports LandingPage
echo "export { LandingPage as CreateConceptPage } from '../../landing';" > frontend/my-app/src/features/concepts/create/index.ts
```

## Step 6: Update Refinement Page

```bash
# Move concept-refinement to refinement
cp frontend/my-app/src/features/concept-refinement/ConceptRefinementPage.tsx frontend/my-app/src/features/refinement/RefinementPage.tsx
cp -r frontend/my-app/src/features/concept-refinement/components/* frontend/my-app/src/features/refinement/components/

# Create index.ts
echo "export { RefinementPage } from './RefinementPage';" > frontend/my-app/src/features/refinement/index.ts
```

## Step 7: Update Imports in Each Moved File

For each moved file, update the import paths to reflect the new structure. This is manual work that requires careful examination of each file's dependencies.

Example:
```typescript
// Before
import { ConceptForm } from '../../../components/concept/ConceptForm';

// After (if the import path needs to change)
import { ConceptForm } from '../../../components/concept/ConceptForm';
```

## Step 8: Update App.tsx Routes

```typescript
// Update App.tsx to use the new components and routes
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { MainLayout } from './components/layout/MainLayout';
import { LandingPage } from './features/landing';
import { ConceptDetailPage } from './features/concepts/detail';
import { RecentConceptsPage } from './features/concepts/recent';
import { CreateConceptPage } from './features/concepts/create';
import { RefinementPage } from './features/refinement';

// Inside the render method:
<Router>
  <Routes>
    <Route path="/" element={<MainLayout />}>
      {/* Main landing page */}
      <Route index element={<LandingPage />} />
      
      {/* Create page */}
      <Route path="create" element={<CreateConceptPage />} />
      
      {/* Concept detail page */}
      <Route path="concepts/:conceptId" element={<ConceptDetailPage />} />
      
      {/* Recent concepts page */}
      <Route path="recent" element={<RecentConceptsPage />} />
      
      {/* Refinement page */}
      <Route path="refine/:conceptId" element={<RefinementPage />} />
    </Route>
  </Routes>
</Router>
```

## Step 9: Update Navigation Links

Ensure all navigation links throughout the application use the correct paths:

- `/` for the landing page
- `/concepts/:conceptId` for concept details (not `/concept/:conceptId`)
- `/refine/:conceptId` for refinement
- `/recent` for recent concepts

## Step 10: Fix Any Route-Related Issues

Pay special attention to any routes that might still be using `/concept/` instead of `/concepts/`. Update them to use the correct paths to ensure consistent routing throughout the application.

## Step 11: Testing

1. Test all routes to ensure they render the correct components
2. Test all links to ensure they navigate to the correct routes
3. Test all functionality to ensure it works as expected after the refactoring

## Step 12: Cleanup

Once everything is working correctly, you can safely remove the old directories:

```bash
rm -rf frontend/my-app/src/features/concept-generator
rm -rf frontend/my-app/src/features/ConceptDetail
rm -rf frontend/my-app/src/features/recent-concepts
rm -rf frontend/my-app/src/features/concept-refinement
rm -rf frontend/my-app/src/features/home
```

## Implementation Notes

1. **Do This Gradually**: Refactor one section at a time and test between changes
2. **Use Git Branches**: Create a separate branch for this refactoring
3. **Frequent Commits**: Make small, focused commits with clear messages
4. **Visual Regression Tests**: If possible, take screenshots before and after to compare
5. **Keep a Backup**: Ensure you have a backup of the original code

## Rollback Plan

If anything goes wrong during the refactoring:

1. Revert to the previous commit
2. Document what went wrong
3. Develop a more targeted approach to fix the specific issue 