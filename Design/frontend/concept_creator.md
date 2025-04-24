# ConceptCreator Feature Design Document

## Current Context

The Concept Visualizer application aims to help users generate visual concepts based on textual descriptions. The ConceptCreator feature is the core functionality of this application, allowing users to:

1. Input descriptive text for a logo and theme
2. Generate visual concepts through JigsawStack's AI capabilities
3. View the generated image and associated color palette
4. Refine or regenerate concepts as needed

This feature builds upon the already-designed backend components:

- JigsawStack client for image and text generation
- Concept generation service
- API endpoints for concept generation

And will utilize the shared UI components:

- Button component
- LoadingSpinner component
- ErrorMessage component

The Modern Gradient Violet theme has been selected as the visual design language for the application.

## Requirements

### Functional Requirements

1. **Text Input**

   - User can enter a logo description (required)
   - User can enter a theme description (required)
   - Input fields should have appropriate validation
   - Input fields should provide helpful placeholder text

2. **Generation Control**

   - User can submit the form to generate a concept
   - User can clear the form and start over
   - User can see the generation in progress

3. **Results Display**

   - User can view the generated image
   - User can view the generated color palette
   - User can copy color codes to clipboard
   - User can see the original prompts that generated the concept

4. **Error Handling**
   - User receives clear error messages for any failures
   - User can retry generation after an error
   - User can dismiss error messages

### Non-Functional Requirements

1. **Performance**

   - Form submission should feel responsive (< 300ms)
   - Loading state should be communicated clearly
   - UI should remain responsive during API calls

2. **Usability**

   - Interface should be intuitive and follow Modern Gradient Violet theme
   - All components should be fully accessible
   - Mobile responsiveness for all screen sizes

3. **Maintainability**
   - Clear separation of concerns between UI and business logic
   - Consistent naming conventions
   - Type safety throughout the implementation

## Design Decisions

### 1. Component Structure

Will implement a modular component structure because:

- Enables independent testing of each component
- Promotes reusability across the application
- Simplifies maintenance and future enhancements

The ConceptCreator feature will be composed of:

- `ConceptForm`: Manages input fields and form submission
- `ImageDisplay`: Renders the generated image with loading states
- `ColorPalettes`: Displays and manages interaction with the color palette
- `ConceptCreatorPage`: Orchestrates the above components

### 2. State Management

Will use React hooks for local state management because:

- The feature's state is contained within its own context
- No need for global state with limited feature scope
- Simpler implementation compared to a global state management solution

Custom hooks for business logic:

- `useConceptGeneration`: Manages API calls and processing responses
- `useFormValidation`: Handles input validation logic

### 3. API Interaction

Will implement a dedicated service for API calls because:

- Separates network logic from UI components
- Enables centralized error handling
- Makes testing more straightforward

The `conceptApi` service will be consumed by the `useConceptGeneration` hook.

### 4. Color Palette Presentation

Will implement a visually appealing color palette display because:

- Colors are a critical part of the concept visualization
- Helps users understand the color relationships
- Aligns with the application's focus on visual design

## Technical Design

### 1. ConceptForm Component

```tsx
import React from "react";
import { Button } from "../../components/Button/Button";
import { ErrorMessage } from "../../components/ErrorMessage/ErrorMessage";
import type { PromptFormData } from "../../types";

interface ConceptFormProps {
  onSubmit: (data: PromptFormData) => void;
  isLoading: boolean;
  error: string | null;
  onDismissError: () => void;
}

export const ConceptForm: React.FC<ConceptFormProps> = ({
  onSubmit,
  isLoading,
  error,
  onDismissError,
}) => {
  // Component implementation details

  return (
    <div className="p-8 rounded-2xl shadow-modern border border-purple-100 bg-white">
      <h2 className="text-2xl font-bold mb-6 text-violet-900">
        Generate New Concept
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        <div>
          <label
            htmlFor="logoDescription"
            className="block text-sm font-semibold text-violet-800 mb-2"
          >
            Logo Description
          </label>
          <input
            id="logoDescription"
            type="text"
            value={formData.logoDescription}
            onChange={handleInputChange}
            name="logoDescription"
            className="w-full px-5 py-3 bg-violet-50/70 border border-violet-200 rounded-lg focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all duration-200"
            placeholder="A modern tech startup logo with abstract geometric shapes"
            required
          />
        </div>

        <div>
          <label
            htmlFor="themeDescription"
            className="block text-sm font-semibold text-violet-800 mb-2"
          >
            Theme Description
          </label>
          <input
            id="themeDescription"
            type="text"
            value={formData.themeDescription}
            onChange={handleInputChange}
            name="themeDescription"
            className="w-full px-5 py-3 bg-violet-50/70 border border-violet-200 rounded-lg focus:ring-2 focus:ring-primary/30 focus:border-primary focus:outline-none transition-all duration-200"
            placeholder="Professional corporate theme with a touch of creativity"
            required
          />
        </div>

        {error && (
          <ErrorMessage
            message={error}
            onDismiss={onDismissError}
            onRetry={handleSubmit}
          />
        )}

        <div className="flex justify-end pt-4">
          <Button
            type="submit"
            isLoading={isLoading}
            variant="primary"
            size="medium"
          >
            Generate Concept
          </Button>
        </div>
      </form>
    </div>
  );
};
```

### 2. ImageDisplay Component

```tsx
import React from "react";
import { LoadingSpinner } from "../../components/LoadingSpinner/LoadingSpinner";

interface ImageDisplayProps {
  imageUrl: string | null;
  isLoading: boolean;
  alt: string;
}

export const ImageDisplay: React.FC<ImageDisplayProps> = ({
  imageUrl,
  isLoading,
  alt,
}) => {
  return (
    <div className="rounded-2xl overflow-hidden border border-purple-100 bg-white shadow-modern">
      <div className="aspect-square w-full flex items-center justify-center bg-violet-50/50 p-4">
        {isLoading ? (
          <div className="flex flex-col items-center justify-center">
            <LoadingSpinner size="large" />
            <p className="mt-4 text-violet-800 text-sm">
              Generating your concept...
            </p>
          </div>
        ) : imageUrl ? (
          <img
            src={imageUrl}
            alt={alt || "Generated concept"}
            className="max-h-full object-contain rounded-lg"
          />
        ) : (
          <div className="text-center text-violet-400">
            <svg
              className="mx-auto h-12 w-12 opacity-50"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={1.5}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="mt-2 text-sm">
              Your generated image will appear here
            </p>
          </div>
        )}
      </div>

      {imageUrl && !isLoading && (
        <div className="p-4 border-t border-purple-100 bg-white">
          <h3 className="font-medium text-violet-900">Generated Concept</h3>
          <p className="text-sm text-violet-700 mt-1">Based on your prompt</p>
        </div>
      )}
    </div>
  );
};
```

### 3. ColorPalettes Component

```tsx
import React from "react";
import { Button } from "../../components/Button/Button";
import type { HexColor } from "../../types";

interface ColorPalettesProps {
  colors: HexColor[] | null;
  isLoading: boolean;
}

export const ColorPalettes: React.FC<ColorPalettesProps> = ({
  colors,
  isLoading,
}) => {
  const copyToClipboard = (color: string) => {
    navigator.clipboard.writeText(color);
    // Show feedback (could use a toast notification)
  };

  if (isLoading) {
    return (
      <div className="rounded-2xl border border-purple-100 bg-white shadow-modern p-6">
        <h3 className="text-lg font-semibold text-violet-900 mb-3">
          Color Palette
        </h3>
        <div className="animate-pulse space-y-3">
          <div className="h-8 bg-violet-100 rounded-md"></div>
          <div className="grid grid-cols-5 gap-2">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-violet-100 rounded-md"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!colors || colors.length === 0) {
    return (
      <div className="rounded-2xl border border-purple-100 bg-white shadow-modern p-6">
        <h3 className="text-lg font-semibold text-violet-900 mb-3">
          Color Palette
        </h3>
        <p className="text-violet-700 text-sm">
          Color palette will be generated with your concept
        </p>
      </div>
    );
  }

  return (
    <div className="rounded-2xl border border-purple-100 bg-white shadow-modern p-6">
      <h3 className="text-lg font-semibold text-violet-900 mb-3">
        Color Palette
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mt-4">
        {colors.map((color, index) => (
          <div key={index} className="flex flex-col">
            <div
              className="h-20 rounded-md"
              style={{ backgroundColor: color }}
            />
            <div className="flex items-center justify-between mt-2">
              <code className="text-xs text-violet-900">{color}</code>
              <button
                onClick={() => copyToClipboard(color)}
                className="text-violet-600 hover:text-violet-800 text-sm"
                aria-label={`Copy color ${color}`}
              >
                <svg
                  className="h-4 w-4"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M8 5H6a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2v-1M8 5a2 2 0 002 2h2a2 2 0 002-2M8 5a2 2 0 012-2h2a2 2 0 012 2m0 0h2a2 2 0 012 2v3m2 4H10m0 0l3-3m-3 3l3 3"
                  />
                </svg>
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### 4. ConceptCreatorPage Component

```tsx
import React, { useState } from "react";
import { ConceptForm } from "./ConceptForm";
import { ImageDisplay } from "./ImageDisplay";
import { ColorPalettes } from "./ColorPalettes";
import { useConceptGeneration } from "../hooks/useConceptGeneration";
import type { PromptFormData } from "../../types";

export const ConceptCreatorPage: React.FC = () => {
  const { generateConcept, result, isLoading, error, clearError } =
    useConceptGeneration();

  const handleSubmit = async (data: PromptFormData) => {
    await generateConcept(data);
  };

  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <h1 className="text-4xl font-bold mb-2 bg-gradient-to-r from-violet-600 to-fuchsia-500 bg-clip-text text-transparent">
        Concept Visualizer
      </h1>
      <p className="text-violet-700 mb-8">
        Generate unique visual concepts with AI
      </p>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div>
          <ConceptForm
            onSubmit={handleSubmit}
            isLoading={isLoading}
            error={error}
            onDismissError={clearError}
          />
        </div>

        <div className="space-y-8">
          <ImageDisplay
            imageUrl={result?.imageUrl || null}
            isLoading={isLoading}
            alt={`Generated concept for ${result?.prompt || "concept"}`}
          />

          <ColorPalettes
            colors={result?.colors || null}
            isLoading={isLoading}
          />
        </div>
      </div>
    </div>
  );
};
```

### 5. TypeScript Interfaces

```typescript
// types/index.ts

export type HexColor = string; // Hex color code (e.g., "#RRGGBB")

export interface PromptFormData {
  logoDescription: string;
  themeDescription: string;
}

export interface GenerationResult {
  imageUrl: string;
  colors: HexColor[];
  prompt: string; // Original prompt that generated the concept
  timestamp: Date;
}

export interface ConceptApiResponse {
  success: boolean;
  data?: {
    imageUrl: string;
    colors: HexColor[];
  };
  error?: string;
}
```

### 6. Custom Hooks

```typescript
// hooks/useConceptGeneration.ts

import { useState } from "react";
import { conceptApi } from "../services/conceptApi";
import type { PromptFormData, GenerationResult } from "../types";

export const useConceptGeneration = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<GenerationResult | null>(null);

  const generateConcept = async (data: PromptFormData) => {
    setIsLoading(true);
    setError(null);

    try {
      const response = await conceptApi.generateConcept(data);

      if (response.success && response.data) {
        setResult({
          imageUrl: response.data.imageUrl,
          colors: response.data.colors,
          prompt: `${data.logoDescription} + ${data.themeDescription}`,
          timestamp: new Date(),
        });
      } else {
        setError(response.error || "Failed to generate concept");
      }
    } catch (err) {
      setError("An unexpected error occurred. Please try again.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => setError(null);

  return {
    generateConcept,
    result,
    isLoading,
    error,
    clearError,
  };
};
```

## Data Flow

```
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│               │     │               │     │               │
│  ConceptForm  │────▶│ useConception │────▶│  conceptApi   │
│               │     │  Generation   │     │               │
└───────┬───────┘     └───────┬───────┘     └───────┬───────┘
        │                     │                     │
        │                     │                     │
        │                     │                     │
┌───────▼───────┐     ┌───────▼───────┐     ┌───────────────┐
│               │     │               │     │               │
│ ImageDisplay  │◀────┤ConceptCreator │◀────┤  JigsawStack  │
│               │     │     Page      │     │     API       │
└───────────────┘     └───────┬───────┘     └───────────────┘
                              │
                              │
                      ┌───────▼───────┐
                      │               │
                      │ ColorPalettes │
                      │               │
                      └───────────────┘
```

## Testing Strategy

### Unit Tests

For each component, test the following aspects:

#### ConceptForm

- Form renders correctly with empty inputs
- Validation works correctly for required fields
- Form submission triggers the onSubmit callback with correct data
- Loading state disables form submission
- Error state shows the ErrorMessage component

```tsx
// ConceptForm.test.tsx (example)
import { render, screen, fireEvent } from "@testing-library/react";
import { ConceptForm } from "./ConceptForm";

describe("ConceptForm", () => {
  const mockSubmit = jest.fn();
  const mockDismissError = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders empty form initially", () => {
    render(
      <ConceptForm
        onSubmit={mockSubmit}
        isLoading={false}
        error={null}
        onDismissError={mockDismissError}
      />,
    );

    expect(screen.getByLabelText(/logo description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/theme description/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /generate concept/i }),
    ).toBeInTheDocument();
  });

  test("submits form with valid data", () => {
    render(
      <ConceptForm
        onSubmit={mockSubmit}
        isLoading={false}
        error={null}
        onDismissError={mockDismissError}
      />,
    );

    const logoInput = screen.getByLabelText(/logo description/i);
    const themeInput = screen.getByLabelText(/theme description/i);

    fireEvent.change(logoInput, { target: { value: "Test Logo" } });
    fireEvent.change(themeInput, { target: { value: "Test Theme" } });
    fireEvent.click(screen.getByRole("button", { name: /generate concept/i }));

    expect(mockSubmit).toHaveBeenCalledWith({
      logoDescription: "Test Logo",
      themeDescription: "Test Theme",
    });
  });

  // Additional tests...
});
```

#### ImageDisplay

- Renders loading state correctly
- Renders empty state correctly
- Renders image correctly when provided
- Alt text is correctly set

#### ColorPalettes

- Renders loading state correctly
- Renders empty state correctly
- Renders colors correctly
- Copy button functionality works

#### ConceptCreatorPage

- Integration of all subcomponents
- Data flow between components
- API interactions through the useConceptGeneration hook

### Integration Tests

- Test the full feature flow from form submission to result display
- Test error handling scenarios
- Test responsive design at different screen sizes

## Future Considerations

### Potential Enhancements

- Add support for advanced generation options (style, aspect ratio, etc.)
- Implement concept history to save and revisit previous generations
- Add social sharing capabilities
- Support for multiple color palette variations

### Known Limitations

- Initial version only supports generating one concept at a time
- No persistent storage of generated concepts
- Limited customization options for the generated concepts
- Simple color palette display without color theory information

## Dependencies

### Runtime Dependencies

- React 18+
- TypeScript 5+
- Tailwind CSS
- Axios for API requests
- React Router for navigation (if implementing multiple pages)

### Development Dependencies

- React Testing Library
- Jest
- MSW (Mock Service Worker) for API mocking
- eslint with TypeScript and React plugins
- prettier for code formatting

## Security Considerations

- Validate all user inputs before sending to the API
- Implement API rate limiting to prevent abuse
- Ensure proper error handling to avoid exposing sensitive information
- Use HTTPS for all API communications

## Integration Points

- JigsawStack API for image and text generation
- Backend API endpoints for concept generation
- Frontend router for navigation between features
- Browser clipboard API for copying color codes

This design document provides a comprehensive blueprint for implementing the ConceptCreator feature, ensuring consistent design, maintainable code structure, and a delightful user experience that aligns with the Modern Gradient Violet theme.
