import React from 'react';
import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import { Spinner } from '../Spinner';

// Mock the LoadingIndicator component
vi.mock('../LoadingIndicator', () => {
  return {
    LoadingIndicator: vi.fn(props => <div data-testid="mocked-loading-indicator" {...props} />)
  };
});

// Import LoadingIndicator after mocking
import { LoadingIndicator } from '../LoadingIndicator';

describe('Spinner', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  
  it('renders the LoadingIndicator component', () => {
    render(<Spinner />);
    
    expect(screen.getByTestId('mocked-loading-indicator')).toBeInTheDocument();
    expect(LoadingIndicator).toHaveBeenCalled();
  });
  
  it('passes size="medium" to LoadingIndicator by default', () => {
    render(<Spinner />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'medium',
        className: '',
        variant: 'primary'
      }),
      expect.anything()
    );
  });
  
  it('converts sm size to small for LoadingIndicator', () => {
    render(<Spinner size="sm" />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'small',
        className: '',
        variant: 'primary'
      }),
      expect.anything()
    );
  });
  
  it('converts md size to medium for LoadingIndicator', () => {
    render(<Spinner size="md" />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'medium',
        className: '',
        variant: 'primary'
      }),
      expect.anything()
    );
  });
  
  it('converts lg size to large for LoadingIndicator', () => {
    render(<Spinner size="lg" />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'large',
        className: '',
        variant: 'primary'
      }),
      expect.anything()
    );
  });
  
  it('passes className prop to LoadingIndicator', () => {
    const customClass = 'custom-spinner-class';
    render(<Spinner className={customClass} />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'medium',
        className: customClass,
        variant: 'primary'
      }),
      expect.anything()
    );
  });
  
  it('sets primary variant on LoadingIndicator', () => {
    render(<Spinner />);
    
    expect(LoadingIndicator).toHaveBeenCalledWith(
      expect.objectContaining({
        size: 'medium',
        className: '',
        variant: 'primary'
      }),
      expect.anything()
    );
  });
}); 