# Frontend Documentation

This directory contains documentation for the Concept Visualizer frontend, which is built with React and follows a feature-based organization.

## Architecture Overview

The frontend is built with:

- **React**: For component-based UI
- **TypeScript**: For type safety
- **React Router**: For routing
- **Axios**: For API calls
- **CSS Modules**: For component styling

## Key Directories

```
frontend/
├── src/
│   ├── features/       # Feature-based organization
│   │   ├── landing/    # Main landing page
│   │   ├── concepts/   # Concept-related features
│   │   └── refinement/ # Refinement features
│   ├── components/     # Shared components
│   ├── hooks/          # Shared hooks
│   ├── contexts/       # React contexts
│   ├── services/       # API service layer
│   ├── utils/          # Utility functions
│   ├── types/          # Shared TypeScript types
│   └── styles/         # Global styles
```

## Key Concepts

### Feature-Based Organization

The frontend is organized by features, with each feature containing its own components, hooks, and logic.

### Component Hierarchy

- **Page Components**: Top-level components rendered by routes
- **Feature Components**: Components specific to a feature
- **Shared Components**: Reusable components used across features

### State Management

- **React Context**: For global state (e.g., concept data)
- **React Hooks**: For local state and logic
- **URL Parameters**: For sharing state via URLs

### API Integration

- **Services**: Abstraction over API calls
- **Hooks**: Custom hooks for API interaction
- **Error Handling**: Consistent error handling for API calls

## Documentation Organization

- **Components**: Documentation for UI components
- **Hooks**: Documentation for custom hooks
- **Services**: Documentation for API services
- **State Management**: Documentation for state management
- **Routing**: Documentation for routing structure 