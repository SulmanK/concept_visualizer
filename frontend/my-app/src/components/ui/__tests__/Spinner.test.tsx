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
    
    expect(LoadingIndicator).toHaveBeenCalled();
  });
  
  it('passes size="medium" to LoadingIndicator by default', () => {
    render(<Spinner />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('medium');
    expect(callArgs.className).toBe('');
    expect(callArgs.variant).toBe('primary');
  });
  
  it('converts sm size to small for LoadingIndicator', () => {
    render(<Spinner size="sm" />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('small');
    expect(callArgs.className).toBe('');
    expect(callArgs.variant).toBe('primary');
  });
  
  it('converts md size to medium for LoadingIndicator', () => {
    render(<Spinner size="md" />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('medium');
    expect(callArgs.className).toBe('');
    expect(callArgs.variant).toBe('primary');
  });
  
  it('converts lg size to large for LoadingIndicator', () => {
    render(<Spinner size="lg" />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('large');
    expect(callArgs.className).toBe('');
    expect(callArgs.variant).toBe('primary');
  });
  
  it('passes className prop to LoadingIndicator', () => {
    const customClass = 'custom-spinner-class';
    render(<Spinner className={customClass} />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('medium');
    expect(callArgs.className).toBe(customClass);
    expect(callArgs.variant).toBe('primary');
  });
  
  it('sets primary variant on LoadingIndicator', () => {
    render(<Spinner />);
    
    const callArgs = vi.mocked(LoadingIndicator).mock.calls[0][0];
    expect(callArgs.size).toBe('medium');
    expect(callArgs.className).toBe('');
    expect(callArgs.variant).toBe('primary');
  });
}); 