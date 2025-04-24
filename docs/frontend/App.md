# App Component

The `App` component is the root component of the application, responsible for setting up the application structure, routing, and global providers.

## Component Structure

```tsx
function App() {
  // Component implementation
}
```

## Responsibilities

The App component is responsible for:

1. Setting up the router and defining application routes
2. Configuring global providers (Auth, Theme, Query, Toast, etc.)
3. Setting up error boundaries
4. Configuring lazy loading for performance optimization
5. Establishing the base layout structure

## Key Features

### Routing

The App component uses React Router to define the application's routes, including:

- Landing page (`/`)
- Recent concepts page (`/concepts`)
- Concept detail page (`/concepts/:id`)
- Refinement page (`/concepts/:id/refine`)
- Error pages (404, 500)

### Global Providers

The App component sets up the following providers:

- `ThemeProvider`: Provides MUI theming
- `QueryClientProvider`: Sets up React Query for data fetching
- `AuthProvider`: Handles authentication state
- `RateLimitProvider`: Manages API rate limit information
- `TaskProvider`: Manages background task state
- `ToastProvider`: Manages toast notifications

### Error Handling

The App component includes global error boundaries to catch and handle unhandled exceptions at different levels of the component tree.

### Lazy Loading

Performance-critical routes and components are lazy-loaded using React's `lazy` and `Suspense` to improve initial load time and reduce bundle size.

## Example

```tsx
import React, { Suspense, lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ThemeProvider } from "@mui/material/styles";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { ErrorBoundary } from "components/ui/ErrorBoundary";
import { LoadingIndicator } from "components/ui/LoadingIndicator";
import { theme } from "./theme";
import { AuthProvider } from "contexts/AuthContext";
import { RateLimitProvider } from "contexts/RateLimitContext";
import { TaskProvider } from "contexts/TaskContext";
import { ToastProvider } from "contexts/ToastProvider";
import MainLayout from "components/layout/MainLayout";

// Lazy-loaded components
const LandingPage = lazy(() => import("features/landing/LandingPage"));
const RecentConceptsPage = lazy(
  () => import("features/concepts/recent/RecentConceptsPage"),
);
const ConceptDetailPage = lazy(
  () => import("features/concepts/detail/ConceptDetailPage"),
);
const RefinementPage = lazy(() => import("features/refinement/RefinementPage"));
const NotFoundPage = lazy(() => import("components/NotFoundPage"));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <AuthProvider>
            <RateLimitProvider>
              <TaskProvider>
                <ToastProvider>
                  <BrowserRouter>
                    <MainLayout>
                      <Suspense fallback={<LoadingIndicator />}>
                        <Routes>
                          <Route path="/" element={<LandingPage />} />
                          <Route
                            path="/concepts"
                            element={<RecentConceptsPage />}
                          />
                          <Route
                            path="/concepts/:id"
                            element={<ConceptDetailPage />}
                          />
                          <Route
                            path="/concepts/:id/refine"
                            element={<RefinementPage />}
                          />
                          <Route path="*" element={<NotFoundPage />} />
                        </Routes>
                      </Suspense>
                    </MainLayout>
                  </BrowserRouter>
                </ToastProvider>
              </TaskProvider>
            </RateLimitProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}

export default App;
```
