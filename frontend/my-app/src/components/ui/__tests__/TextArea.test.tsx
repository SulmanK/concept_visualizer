import React from 'react';
import { render, screen, fireEvent } from '../../../test-utils';
import { TextArea } from '../TextArea';

describe('TextArea Component', () => {
  test('renders textarea element', () => {
    render(<TextArea placeholder="Test TextArea" />);
    expect(screen.getByPlaceholderText('Test TextArea')).toBeInTheDocument();
  });

  test('applies default classes', () => {
    const { container } = render(<TextArea />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement?.className).toContain('w-full');
    expect(textareaElement?.className).toContain('px-4');
    expect(textareaElement?.className).toContain('py-3');
    expect(textareaElement?.className).toContain('border');
    expect(textareaElement?.className).toContain('rounded-lg');
    expect(textareaElement?.className).toContain('focus:outline-none');
    expect(textareaElement?.className).toContain('resize-y');
  });

  test('accepts custom className', () => {
    const { container } = render(<TextArea className="custom-class" />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement?.className).toContain('custom-class');
  });

  test('forwards additional props to textarea element', () => {
    render(<TextArea data-testid="test-textarea" rows={5} />);
    
    const textareaElement = screen.getByTestId('test-textarea');
    expect(textareaElement).toHaveAttribute('rows', '5');
  });

  test('handles onChange events', () => {
    const handleChange = jest.fn();
    render(<TextArea onChange={handleChange} data-testid="test-textarea" />);
    
    const textareaElement = screen.getByTestId('test-textarea');
    fireEvent.change(textareaElement, { target: { value: 'test value' } });
    
    expect(handleChange).toHaveBeenCalled();
  });

  test('applies error styling when error prop is true', () => {
    const { container } = render(<TextArea error="There is an error" />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement?.className).toContain('border-red-300');
    expect(textareaElement?.className).toContain('focus:ring-red-200');
    expect(textareaElement?.className).toContain('focus:border-red-500');
  });

  test('renders error message when provided', () => {
    render(<TextArea error="This is an error" />);
    
    expect(screen.getByText('This is an error')).toBeInTheDocument();
    expect(screen.getByText('This is an error')).toHaveClass('text-red-600');
  });

  test('renders label when provided', () => {
    render(<TextArea label="TextArea Label" />);
    
    expect(screen.getByText('TextArea Label')).toBeInTheDocument();
  });

  test('applies disabled styling', () => {
    const { container } = render(<TextArea disabled className="bg-gray-100 cursor-not-allowed" />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement).toBeDisabled();
    expect(textareaElement?.className).toContain('bg-gray-100');
    expect(textareaElement?.className).toContain('cursor-not-allowed');
  });

  test('applies resize class when resize prop is true', () => {
    const { container } = render(<TextArea className="resize" />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement?.className).toContain('resize');
  });

  test('applies no-resize class when resize prop is false', () => {
    const { container } = render(<TextArea className="resize-none" />);
    const textareaElement = container.querySelector('textarea');
    
    expect(textareaElement?.className).toContain('resize-none');
  });
}); 