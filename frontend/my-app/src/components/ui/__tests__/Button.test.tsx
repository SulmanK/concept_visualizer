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
    expect(button.className).toContain('bg-gradient-primary');
  });
  
  // Variant tests
  test.each([
    ['primary', 'bg-gradient-primary'],
    ['secondary', 'bg-gradient-secondary'],
    ['outline', 'border border-indigo-300'],
    ['ghost', 'text-indigo-600'],
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
  
  // Pill shape test
  test('renders pill shape when pill is true', () => {
    render(<Button pill>Pill Button</Button>);
    
    const button = screen.getByRole('button');
    expect(button.className).toContain('rounded-full');
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
  
  // Snapshot tests
  describe('Snapshots', () => {
    test('default button snapshot', () => {
      const { container } = render(<Button>Default Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('primary variant button snapshot', () => {
      const { container } = render(<Button variant="primary">Primary Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('secondary variant button snapshot', () => {
      const { container } = render(<Button variant="secondary">Secondary Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('outline variant button snapshot', () => {
      const { container } = render(<Button variant="outline">Outline Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('ghost variant button snapshot', () => {
      const { container } = render(<Button variant="ghost">Ghost Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('disabled button snapshot', () => {
      const { container } = render(<Button disabled>Disabled Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('pill button snapshot', () => {
      const { container } = render(<Button pill>Pill Button</Button>);
      expect(container.firstChild).toMatchSnapshot();
    });
  });
}); 