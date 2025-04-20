# Types

This directory contains TypeScript types, interfaces, and type declarations used throughout the Concept Visualizer application. Well-defined types ensure type safety, improve developer experience, and provide better documentation.

## Directory Structure

Types are organized by domain and functionality:

- **API Types**: Interfaces matching backend API request and response structures
- **Domain Types**: Core business domain types like Concept, Palette, etc.
- **Component Props**: Type definitions for component props
- **Utility Types**: Reusable utility types and type helpers

## Key Type Definitions

### Concept Types

```typescript
// Core concept type representing a generated concept
export interface Concept {
  id: string;
  userId: string;
  logoDescription: string;
  themeDescription: string;
  imagePath: string;
  imageUrl: string;
  createdAt: string;
  colorVariations?: ColorVariation[];
}

// Color variation/palette for a concept
export interface ColorVariation {
  id: string;
  conceptId: string;
  paletteName: string;
  colors: string[];
  description?: string;
  imagePath: string;
  imageUrl: string;
  createdAt: string;
}
```

### API Request/Response Types

```typescript
// Generate concept request
export interface GenerateConceptRequest {
  logoDescription: string;
  themeDescription: string;
}

// Generate concept response
export interface GenerateConceptResponse {
  id: string;
  imageUrl: string;
  colors: string[];
}

// Task status type for async operations
export type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';

// Task response from the backend
export interface TaskResponse {
  taskId: string;
  status: TaskStatus;
  result?: any;
  error?: string;
}
```

### Component Prop Types

```typescript
// Button component props
export interface ButtonProps {
  label: string;
  variant?: 'primary' | 'secondary' | 'text';
  size?: 'small' | 'medium' | 'large';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

// Form input props
export interface InputProps {
  name: string;
  label?: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  error?: string;
  disabled?: boolean;
  required?: boolean;
  maxLength?: number;
}
```

## Type Utilities

The application includes several type utilities for common patterns:

```typescript
// Make all properties in T optional
export type Partial<T> = {
  [P in keyof T]?: T[P];
};

// Make all properties in T required
export type Required<T> = {
  [P in keyof T]-?: T[P];
};

// Pick only some properties from T
export type Pick<T, K extends keyof T> = {
  [P in K]: T[P];
};

// Omit some properties from T
export type Omit<T, K extends keyof T> = Pick<T, Exclude<keyof T, K>>;
```

## Best Practices

1. **Prefer Interfaces** for public API contracts and object shapes
2. **Use Type Aliases** for unions, intersections, and utility types
3. **Be Explicit** with property types rather than using `any`
4. **Use Readonly** for immutable data structures
5. **Document Types** with JSDoc comments for better IntelliSense
6. **Consistent Naming** using PascalCase for interfaces and types
7. **Single Responsibility** - keep types focused on one domain or concept 