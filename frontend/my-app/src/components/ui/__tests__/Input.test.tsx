import React from 'react';
import { render, screen, fireEvent } from '../../../test-utils';
import { Input } from '../Input';

describe('Input Component', () => {
  test('renders input element', () => {
    render(<Input placeholder="Test Input" />);
    expect(screen.getByPlaceholderText('Test Input')).toBeInTheDocument();
  });

  test('applies default classes', () => {
    const { container } = render(<Input />);
    const inputElement = container.querySelector('input');
    
    expect(inputElement?.className).toContain('w-full');
    expect(inputElement?.className).toContain('px-4');
    expect(inputElement?.className).toContain('py-3');
    expect(inputElement?.className).toContain('border');
    expect(inputElement?.className).toContain('rounded-lg');
    expect(inputElement?.className).toContain('focus:outline-none');
  });

  test('accepts custom className', () => {
    const { container } = render(<Input className="custom-class" />);
    const inputElement = container.querySelector('input');
    
    expect(inputElement?.className).toContain('custom-class');
  });

  test('forwards additional props to input element', () => {
    render(<Input data-testid="test-input" type="password" />);
    
    const inputElement = screen.getByTestId('test-input');
    expect(inputElement).toHaveAttribute('type', 'password');
  });

  test('handles onChange events', () => {
    const handleChange = jest.fn();
    render(<Input onChange={handleChange} data-testid="test-input" />);
    
    const inputElement = screen.getByTestId('test-input');
    fireEvent.change(inputElement, { target: { value: 'test value' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  test('applies error styling when error prop is true', () => {
    const { container } = render(<Input error="There is an error" />);
    const inputElement = container.querySelector('input');
    
    expect(inputElement?.className).toContain('border-red-300');
    expect(inputElement?.className).toContain('focus:ring-red-200');
    expect(inputElement?.className).toContain('focus:border-red-500');
  });

  test('renders error message when provided', () => {
    render(<Input error="This is an error" />);
    
    expect(screen.getByText('This is an error')).toBeInTheDocument();
    expect(screen.getByText('This is an error')).toHaveClass('text-red-600');
  });

  test('renders label when provided', () => {
    render(<Input label="Input Label" />);
    
    expect(screen.getByText('Input Label')).toBeInTheDocument();
  });

  test('applies disabled styling', () => {
    const { container } = render(<Input disabled className="bg-gray-100 cursor-not-allowed" />);
    const inputElement = container.querySelector('input');
    
    expect(inputElement).toBeDisabled();
    expect(inputElement?.className).toContain('bg-gray-100');
    expect(inputElement?.className).toContain('cursor-not-allowed');
  });
}); 