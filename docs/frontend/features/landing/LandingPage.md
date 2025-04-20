# LandingPage

The LandingPage component serves as the main entry point for users, showcasing the concept visualization capabilities and providing quick access to concept creation.

## Overview

This component is the primary landing page that introduces users to the application and provides immediate access to create new concepts. It combines explanatory content with functional components to enable users to start using the application right away.

## Component Structure

```tsx
const LandingPage: React.FC = () => {
  const { data: recentConcepts, isLoading } = useConceptQueries.useRecentConcepts({
    limit: 3,
    sortOrder: 'newest'
  });
  
  return (
    <MainLayout>
      <ConceptHeader />
      
      <section className="main-content">
        <ConceptFormSection />
        
        <HowItWorks />
        
        {!isLoading && recentConcepts?.items.length > 0 && (
          <RecentConceptsSection concepts={recentConcepts.items} />
        )}
      </section>
      
      <section className="results-section">
        <ResultsSection />
      </section>
    </MainLayout>
  );
};
```

## Features

- **Concept Creation**: Provides a form for creating new concepts directly from the landing page
- **How It Works**: Explains the concept visualization process to new users
- **Recent Concepts**: Shows the user's most recent concepts for quick access
- **Example Results**: Showcases example concept visualizations to demonstrate capabilities

## Dependencies

- `MainLayout`: Standard layout wrapper with header and footer
- `ConceptHeader`: Hero section with introductory content
- `ConceptFormSection`: Section containing the concept creation form
- `HowItWorks`: Explanatory section detailing the concept creation process
- `RecentConceptsSection`: Section displaying the user's recent concepts
- `ResultsSection`: Section showcasing example results

## Props

This component does not accept any props as it's a top-level page component.

## State Management

- Uses React Query via `useConceptQueries.useRecentConcepts` to fetch recent concepts
- Local component state for any UI interactions

## Related Components

- [ConceptFormSection](./components/ConceptFormSection.md)
- [ConceptHeader](./components/ConceptHeader.md)
- [HowItWorks](./components/HowItWorks.md)
- [RecentConceptsSection](./components/RecentConceptsSection.md)
- [ResultsSection](./components/ResultsSection.md)

## Usage

This page is typically the default route for unauthenticated users and is accessed via the root URL:

```tsx
<Route path="/" element={<LandingPage />} />
```

## Behavior

- When a user submits the concept form, they are redirected to the results view
- Recent concepts are shown only if the user has created concepts previously
- The page is responsive and adapts to different screen sizes
- Performance optimizations include:
  - Lazy loading of images
  - Conditional rendering of recent concepts
  - Optimized asset loading 