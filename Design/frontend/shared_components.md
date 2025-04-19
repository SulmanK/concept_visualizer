# Frontend Shared Components Design Document

## Current Context
- The Concept Visualizer requires reusable UI components to maintain consistency
- These components will be used across different features (concept creation and refinement)
- Components should follow modern React practices with TypeScript and proper styling
- Tailwind CSS will be used for styling components

## Requirements

### Functional Requirements
- Create reusable Button component with different variants (primary, secondary, disabled)
- Implement LoadingSpinner component for asynchronous operations
- Design ErrorMessage component for displaying user-friendly error messages
- Ensure all components are accessible and responsive
- Support light and dark mode where applicable

### Non-Functional Requirements
- Maintain consistent styling across all shared components
- Ensure components are fully typed with TypeScript
- Optimize for performance (minimize re-renders)
- Support screen readers and keyboard navigation
- Implement responsive design principles 

## Design Decisions

### 1. Component Library Strategy
Will implement a custom component library rather than using a third-party UI library because:
- We need complete control over styling and behavior
- The project scope is limited to a few essential components
- This approach avoids adding unnecessary dependencies
- Custom components can be tailored to our specific needs

### 2. Component API Design
Will design component APIs to be:
- Consistent across all components (similar prop patterns)
- Flexible enough to handle various use cases
- Well-typed with TypeScript to improve developer experience
- Compatible with React's composition model

### 3. Styling Approach
Will use Tailwind CSS for styling because:
- It provides utility classes that streamline development
- It works well with component-based architecture
- It promotes consistency through design constraints
- It enables responsive design with minimal effort

## Technical Design

### 1. Button Component

```tsx
// frontend/src/components/Button/Button.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const buttonVariants = cva(
  // Base styles applied to all buttons
  "inline-flex items-center justify-center rounded-md font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-primary text-white hover:bg-primary-dark",
        secondary: "bg-secondary text-white hover:bg-secondary-dark",
        outline: "border border-input bg-transparent hover:bg-accent hover:text-accent-foreground",
        ghost: "hover:bg-accent hover:text-accent-foreground",
      },
      size: {
        sm: "h-9 px-3 text-sm",
        md: "h-10 px-4 py-2",
        lg: "h-11 px-8 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export interface ButtonProps 
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  /**
   * Whether the button is in a loading state
   */
  isLoading?: boolean;
}

/**
 * Primary UI component for user interaction
 */
export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, isLoading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={buttonVariants({ variant, size, className })}
        ref={ref}
        disabled={disabled || isLoading}
        {...props}
      >
        {isLoading ? (
          <span className="mr-2">
            <LoadingSpinner size="sm" />
          </span>
        ) : null}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';
```

### 2. LoadingSpinner Component

```tsx
// frontend/src/components/LoadingSpinner/LoadingSpinner.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const spinnerVariants = cva("animate-spin", {
  variants: {
    size: {
      sm: "h-4 w-4",
      md: "h-8 w-8",
      lg: "h-12 w-12",
    },
    color: {
      primary: "text-primary",
      white: "text-white",
      gray: "text-gray-400",
    },
  },
  defaultVariants: {
    size: "md",
    color: "primary",
  },
});

export interface LoadingSpinnerProps extends VariantProps<typeof spinnerVariants> {
  /**
   * Additional CSS class name
   */
  className?: string;
  
  /**
   * Accessible label for screen readers
   */
  label?: string;
}

/**
 * Loading spinner component for indicating loading states
 */
export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({ 
  size, 
  color, 
  className, 
  label = "Loading..." 
}) => {
  return (
    <div role="status" className="inline-block">
      <svg
        className={spinnerVariants({ size, color, className })}
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
        aria-label={label}
      >
        <circle
          className="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          strokeWidth="4"
        ></circle>
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        ></path>
      </svg>
      <span className="sr-only">{label}</span>
    </div>
  );
};
```

### 3. ErrorMessage Component

```tsx
// frontend/src/components/ErrorMessage/ErrorMessage.tsx
import React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';

const errorVariants = cva(
  "flex items-center p-4 rounded-md text-sm",
  {
    variants: {
      variant: {
        default: "bg-red-50 text-red-800 border border-red-200",
        toast: "bg-red-600 text-white shadow-md",
      },
      size: {
        sm: "text-xs p-2",
        md: "text-sm p-4",
        lg: "text-base p-6",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "md",
    },
  }
);

export interface ErrorMessageProps extends VariantProps<typeof errorVariants> {
  /**
   * Error message content
   */
  message: string;
  
  /**
   * Optional error details (may be technical)
   */
  details?: string;
  
  /**
   * Additional CSS class name
   */
  className?: string;
  
  /**
   * Optional retry callback
   */
  onRetry?: () => void;
  
  /**
   * Optional dismiss callback
   */
  onDismiss?: () => void;
}

/**
 * Component for displaying error messages to users
 */
export const ErrorMessage: React.FC<ErrorMessageProps> = ({
  message,
  details,
  className,
  variant,
  size,
  onRetry,
  onDismiss,
}) => {
  return (
    <div className={errorVariants({ variant, size, className })} role="alert">
      <div className="flex-1">
        <div className="font-medium">{message}</div>
        {details && <div className="text-xs mt-1 opacity-80">{details}</div>}
      </div>
      
      <div className="flex gap-2 ml-4">
        {onRetry && (
          <button
            onClick={onRetry}
            className="text-xs font-medium underline focus:outline-none"
            aria-label="Retry"
          >
            Retry
          </button>
        )}
        
        {onDismiss && (
          <button
            onClick={onDismiss}
            className="text-xs font-medium focus:outline-none"
            aria-label="Dismiss"
          >
            ✕
          </button>
        )}
      </div>
    </div>
  );
};
```

### 4. Integration Example

```tsx
// Sample usage of shared components
import React, { useState } from 'react';
import { Button } from '../components/Button/Button';
import { LoadingSpinner } from '../components/LoadingSpinner/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage/ErrorMessage';

export const ConceptForm: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const handleSubmit = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Submit form logic
      await new Promise(resolve => setTimeout(resolve, 2000));
    } catch (err) {
      setError('Failed to generate concept. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <div className="space-y-4">
      {/* Form fields */}
      
      {error && (
        <ErrorMessage 
          message={error} 
          onDismiss={() => setError(null)}
          onRetry={handleSubmit}
        />
      )}
      
      <div className="flex justify-end">
        <Button 
          variant="primary" 
          isLoading={isLoading} 
          onClick={handleSubmit}
        >
          Generate Concept
        </Button>
      </div>
      
      {isLoading && (
        <div className="flex justify-center py-8">
          <LoadingSpinner size="lg" label="Generating your concept..." />
        </div>
      )}
    </div>
  );
};
```

## Component API Reference

### Button API
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `variant` | `'primary' \| 'secondary' \| 'outline' \| 'ghost'` | `'primary'` | Visual style of the button |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Size variant of the button |
| `isLoading` | `boolean` | `false` | Whether the button is in a loading state |
| `disabled` | `boolean` | `false` | Whether the button is disabled |
| `children` | `ReactNode` | - | Button content |
| All HTML button props | `ButtonHTMLAttributes<HTMLButtonElement>` | - | All native button attributes |

### LoadingSpinner API
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Size of the spinner |
| `color` | `'primary' \| 'white' \| 'gray'` | `'primary'` | Color of the spinner |
| `label` | `string` | `'Loading...'` | Accessible label for screen readers |
| `className` | `string` | - | Additional CSS class name |

### ErrorMessage API
| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `message` | `string` | - | Main error message |
| `details` | `string` | - | Optional technical details |
| `variant` | `'default' \| 'toast'` | `'default'` | Visual style of the error message |
| `size` | `'sm' \| 'md' \| 'lg'` | `'md'` | Size of the error message |
| `onRetry` | `() => void` | - | Optional retry handler |
| `onDismiss` | `() => void` | - | Optional dismiss handler |
| `className` | `string` | - | Additional CSS class name |

## Testing Strategy

### Unit Tests

```tsx
// frontend/src/components/Button/Button.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button component', () => {
  test('renders correctly with default props', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
    expect(button).toHaveClass('bg-primary');
  });
  
  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    
    fireEvent.click(screen.getByRole('button', { name: /click me/i }));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('displays loading state correctly', () => {
    render(<Button isLoading>Submit</Button>);
    
    expect(screen.getByText('Submit')).toBeInTheDocument();
    expect(screen.getByLabelText(/loading/i)).toBeInTheDocument();
    expect(screen.getByRole('button')).toBeDisabled();
  });
  
  test('applies variant styles correctly', () => {
    const { rerender } = render(<Button variant="secondary">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('bg-secondary');
    
    rerender(<Button variant="outline">Button</Button>);
    expect(screen.getByRole('button')).toHaveClass('border-input');
  });
});
```

### Testing LoadingSpinner Component
```tsx
// frontend/src/components/LoadingSpinner/LoadingSpinner.test.tsx
import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from './LoadingSpinner';

describe('LoadingSpinner component', () => {
  test('renders correctly with default props', () => {
    render(<LoadingSpinner />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByLabelText(/loading/i)).toBeInTheDocument();
  });
  
  test('respects custom label', () => {
    render(<LoadingSpinner label="Processing data" />);
    
    expect(screen.getByText('Processing data')).toBeInTheDocument();
  });
  
  test('applies size classes correctly', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />);
    
    expect(screen.getByLabelText(/loading/i)).toHaveClass('h-4 w-4');
    
    rerender(<LoadingSpinner size="lg" />);
    expect(screen.getByLabelText(/loading/i)).toHaveClass('h-12 w-12');
  });
});
```

### Testing ErrorMessage Component
```tsx
// frontend/src/components/ErrorMessage/ErrorMessage.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ErrorMessage } from './ErrorMessage';

describe('ErrorMessage component', () => {
  test('renders correctly with required props', () => {
    render(<ErrorMessage message="Something went wrong" />);
    
    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });
  
  test('displays details when provided', () => {
    render(
      <ErrorMessage 
        message="Failed to load data" 
        details="Network error: Connection refused" 
      />
    );
    
    expect(screen.getByText('Failed to load data')).toBeInTheDocument();
    expect(screen.getByText('Network error: Connection refused')).toBeInTheDocument();
  });
  
  test('handles retry callback', () => {
    const handleRetry = jest.fn();
    render(
      <ErrorMessage 
        message="Error occurred" 
        onRetry={handleRetry} 
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /retry/i }));
    expect(handleRetry).toHaveBeenCalledTimes(1);
  });
  
  test('handles dismiss callback', () => {
    const handleDismiss = jest.fn();
    render(
      <ErrorMessage 
        message="Error occurred" 
        onDismiss={handleDismiss} 
      />
    );
    
    fireEvent.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(handleDismiss).toHaveBeenCalledTimes(1);
  });
});
```

## Future Considerations

### Potential Enhancements
- Add animation variants to components
- Implement a theme context for easier dark/light mode switching
- Create additional component variants as needed
- Add form-specific components (Input, Textarea, Select)
- Enhance accessibility with ARIA attributes and keyboard navigation
- Add internationalization support for error messages

### Known Limitations
- Limited set of component variants
- No form validation integration
- No animation framework integration
- Limited theme customization

## Dependencies

### Runtime Dependencies
- React (core library)
- class-variance-authority (for component variants)
- tailwindcss (for styling)
- clsx (for conditional class names)

### Development Dependencies
- TypeScript (for type checking)
- @testing-library/react (for component testing)
- jest (for test running)
- eslint (for code quality)
- prettier (for code formatting)

## References
- [React Documentation](https://react.dev/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Testing Library Documentation](https://testing-library.com/docs/react-testing-library/intro/)
- [Accessible Components Patterns](https://www.w3.org/WAI/ARIA/apg/patterns/) 