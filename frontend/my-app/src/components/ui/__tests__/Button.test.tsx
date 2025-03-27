import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from '../Button';

describe('Button Component', () => {
  // Basic rendering tests
  test('renders button with children', () => {
    render(<Button>Click me</Button>);
    
    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toBeInTheDocument();
  });
  
  test('renders button with primary variant by default', () => {
    render(<Button>Default Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain('btn-primary');
  });
  
  // Variant tests
  test.each([
    ['primary', 'btn-primary'],
    ['secondary', 'btn-secondary'],
    ['accent', 'btn-accent'],
    ['outline', 'btn-outline'],
  ])('renders %s variant correctly', (variant, expectedClass) => {
    render(<Button variant={variant as any}>Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain(expectedClass);
  });
  
  // Size tests
  test.each([
    ['sm', 'text-xs'],
    ['md', 'text-sm'],
    ['lg', 'text-base'],
  ])('renders %s size correctly', (size, expectedClass) => {
    render(<Button size={size as any}>Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain(expectedClass);
  });
  
  // Loading state tests
  test('renders loading spinner when isLoading is true', () => {
    render(<Button isLoading>Loading Button</Button>);
    
    const svg = document.querySelector('svg.animate-spin');
    expect(svg).toBeInTheDocument();
  });
  
  test('button is disabled when isLoading is true', () => {
    render(<Button isLoading>Loading Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button).toBeDisabled();
  });
  
  // Full width test
  test('renders full width button when fullWidth is true', () => {
    render(<Button fullWidth>Full Width Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain('w-full');
  });
  
  // Icon tests
  test('renders with left icon', () => {
    const icon = <span data-testid="left-icon">🔍</span>;
    render(<Button iconLeft={icon}>Button with Left Icon</Button>);
    
    expect(screen.getByTestId('left-icon')).toBeInTheDocument();
  });
  
  test('renders with right icon', () => {
    const icon = <span data-testid="right-icon">→</span>;
    render(<Button iconRight={icon}>Button with Right Icon</Button>);
    
    expect(screen.getByTestId('right-icon')).toBeInTheDocument();
  });
  
  // Event tests
  test('calls onClick when button is clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Clickable Button</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
  
  test('does not call onClick when button is disabled', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} disabled>Disabled Button</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
  
  test('does not call onClick when button is loading', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick} isLoading>Loading Button</Button>);
    
    fireEvent.click(screen.getByRole('button'));
    expect(handleClick).not.toHaveBeenCalled();
  });
}); 