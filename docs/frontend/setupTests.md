# Test Setup

The `setupTests.ts` file configures the testing environment for the frontend application. This setup runs before each test file and establishes global test configurations, mocks, and utilities.

## Overview

This file is automatically loaded by Jest before running tests. It configures testing libraries like React Testing Library and sets up global mocks for browser APIs, third-party libraries, and application services.

## Key Configurations

### Jest Configuration

```tsx
// Import Jest's extended expect functionality
import '@testing-library/jest-dom';

// Set Jest timeout for all tests
jest.setTimeout(10000);
```

### Mock Setup

The file sets up mocks for various browser APIs and third-party services that might not be available in the test environment:

```tsx
// Mock browser APIs
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

// Mock Supabase
jest.mock('@supabase/supabase-js', () => {
  return {
    createClient: jest.fn(() => ({
      from: jest.fn(() => ({
        select: jest.fn(() => ({
          eq: jest.fn(() => ({
            single: jest.fn(() => ({ data: null, error: null })),
            order: jest.fn(() => ({ data: [], error: null })),
            data: [],
            error: null,
          })),
          order: jest.fn(() => ({ data: [], error: null })),
          data: [],
          error: null,
        })),
        insert: jest.fn(() => ({ data: { id: 'mock-id' }, error: null })),
        update: jest.fn(() => ({ data: { id: 'mock-id' }, error: null })),
        delete: jest.fn(() => ({ data: null, error: null })),
      })),
      storage: {
        from: jest.fn(() => ({
          upload: jest.fn(() => ({ data: { path: 'mock-path' }, error: null })),
          getPublicUrl: jest.fn(() => ({ data: { publicUrl: 'https://example.com/mock-url' } })),
        })),
      },
      auth: {
        onAuthStateChange: jest.fn(() => ({ data: null, error: null, unsubscribe: jest.fn() })),
        getSession: jest.fn(() => ({ data: { session: null }, error: null })),
        signOut: jest.fn(() => ({ error: null })),
      },
    })),
  };
});

// Mock intersection observer
global.IntersectionObserver = class IntersectionObserver {
  constructor(callback) {
    this.callback = callback;
  }
  observe() { return null; }
  unobserve() { return null; }
  disconnect() { return null; }
};
```

### Custom Render Function

The file often defines a custom render function that wraps the component under test with all the necessary providers:

```tsx
import { render, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { theme } from './theme';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import { RateLimitProvider } from './contexts/RateLimitContext';
import { TaskProvider } from './contexts/TaskContext';
import { ToastProvider } from './contexts/ToastProvider';

// Create a custom renderer that includes providers
const customRender = (
  ui: React.ReactElement,
  options?: Omit<RenderOptions, 'wrapper'> & { queryClient?: QueryClient }
) => {
  const queryClient = options?.queryClient || new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={theme}>
          <AuthProvider>
            <RateLimitProvider>
              <TaskProvider>
                <ToastProvider>
                  <BrowserRouter>
                    {children}
                  </BrowserRouter>
                </ToastProvider>
              </TaskProvider>
            </RateLimitProvider>
          </AuthProvider>
        </ThemeProvider>
      </QueryClientProvider>
    );
  };

  return render(ui, { wrapper: AllTheProviders, ...options });
};

// Re-export everything
export * from '@testing-library/react';
// Override render method
export { customRender as render };
```

## Extending Test Setup

To add new configurations to the test setup:

1. Import any required libraries or modules
2. Set up mocks for external dependencies
3. Configure global settings for test environment
4. Add or modify custom test utilities 

For example, to add a mock for the Fetch API:

```tsx
// Mock fetch API
global.fetch = jest.fn().mockImplementation(() => 
  Promise.resolve({
    ok: true,
    json: () => Promise.resolve({}),
    text: () => Promise.resolve(''),
    blob: () => Promise.resolve(new Blob()),
  })
);
```

## Usage

When writing tests, you can import the custom render function and other utilities from this setup:

```tsx
// Component test example
import { render, screen, fireEvent } from '../setupTests';
import { Button } from './Button';

describe('Button component', () => {
  test('renders correctly', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);
    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
``` 