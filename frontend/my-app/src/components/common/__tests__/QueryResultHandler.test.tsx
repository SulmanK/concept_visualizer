import React from 'react';
import { render, screen } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { QueryResultHandler } from '../QueryResultHandler';
import { LoadingIndicator } from '../../ui/LoadingIndicator';
import { ErrorMessage } from '../../ui/ErrorMessage';

// Mock the UI components
vi.mock('../../ui/LoadingIndicator', () => ({
  LoadingIndicator: () => <div data-testid="loading-indicator">Loading...</div>
}));

vi.mock('../../ui/ErrorMessage', () => ({
  ErrorMessage: ({ message }: { message: string }) => (
    <div data-testid="error-message">{message}</div>
  )
}));

describe('QueryResultHandler', () => {
  // Test data
  const mockData = { name: 'Test Data', id: 123 };
  
  // Reset mocks before each test
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('should render loading indicator when isLoading is true', () => {
    render(
      <QueryResultHandler
        isLoading={true}
        error={null}
        data={null}
        children={() => <div>Content</div>}
      />
    );
    
    // Default loading indicator should be shown
    expect(screen.getByTestId('loading-indicator')).toBeInTheDocument();
  });
  
  it('should render custom loading component when provided', () => {
    const customLoadingComponent = <div data-testid="custom-loading">Custom Loading...</div>;
    
    render(
      <QueryResultHandler
        isLoading={true}
        error={null}
        data={null}
        loadingComponent={customLoadingComponent}
        children={() => <div>Content</div>}
      />
    );
    
    // Custom loading component should be shown
    expect(screen.getByTestId('custom-loading')).toBeInTheDocument();
    
    // Default loading indicator should not be shown
    expect(screen.queryByTestId('loading-indicator')).not.toBeInTheDocument();
  });
  
  it('should render error message when error is present', () => {
    const testError = new Error('Test error message');
    
    render(
      <QueryResultHandler
        isLoading={false}
        error={testError}
        data={null}
        children={() => <div>Content</div>}
      />
    );
    
    // Error message should be shown with the correct message
    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByTestId('error-message')).toHaveTextContent('Test error message');
  });
  
  it('should render fallback error message when error is not an Error object', () => {
    // Using a string as an error
    const testError = 'Something went wrong';
    
    render(
      <QueryResultHandler
        isLoading={false}
        error={testError}
        data={null}
        fallbackErrorMessage="Custom fallback error message"
        children={() => <div>Content</div>}
      />
    );
    
    // Error message should be shown with the fallback message
    expect(screen.getByTestId('error-message')).toBeInTheDocument();
    expect(screen.getByTestId('error-message')).toHaveTextContent('Custom fallback error message');
  });
  
  it('should render custom error component when provided', () => {
    const testError = new Error('Test error message');
    const customErrorComponent = <div data-testid="custom-error">Custom Error Component</div>;
    
    render(
      <QueryResultHandler
        isLoading={false}
        error={testError}
        data={null}
        errorComponent={customErrorComponent}
        children={() => <div>Content</div>}
      />
    );
    
    // Custom error component should be shown
    expect(screen.getByTestId('custom-error')).toBeInTheDocument();
    
    // Default error message should not be shown
    expect(screen.queryByTestId('error-message')).not.toBeInTheDocument();
  });
  
  it('should render empty message when data is null', () => {
    render(
      <QueryResultHandler
        isLoading={false}
        error={null}
        data={null}
        emptyMessage="No results found"
        children={() => <div>Content</div>}
      />
    );
    
    // Custom empty message should be shown
    expect(screen.getByText('No results found')).toBeInTheDocument();
  });
  
  it('should render empty message when data is an empty array', () => {
    render(
      <QueryResultHandler
        isLoading={false}
        error={null}
        data={[]}
        emptyMessage="No items in the array"
        children={() => <div>Content</div>}
      />
    );
    
    // Custom empty message should be shown
    expect(screen.getByText('No items in the array')).toBeInTheDocument();
  });
  
  it('should render custom empty component when provided', () => {
    const customEmptyComponent = <div data-testid="custom-empty">Custom Empty State</div>;
    
    render(
      <QueryResultHandler
        isLoading={false}
        error={null}
        data={null}
        emptyComponent={customEmptyComponent}
        children={() => <div>Content</div>}
      />
    );
    
    // Custom empty component should be shown
    expect(screen.getByTestId('custom-empty')).toBeInTheDocument();
  });
  
  it('should render children function with data when data is available', () => {
    const childrenFn = vi.fn().mockImplementation((data) => (
      <div data-testid="children-content">
        Name: {data.name}, ID: {data.id}
      </div>
    ));
    
    const { debug } = render(
      <QueryResultHandler
        isLoading={false}
        error={null}
        data={mockData}
      >
        {childrenFn}
      </QueryResultHandler>
    );
    
    // Children function should be called with the data
    expect(childrenFn).toHaveBeenCalledWith(mockData);
    expect(screen.getByTestId('children-content')).toBeInTheDocument();
    expect(screen.getByText(`Name: ${mockData.name}, ID: ${mockData.id}`)).toBeInTheDocument();
  });
}); 