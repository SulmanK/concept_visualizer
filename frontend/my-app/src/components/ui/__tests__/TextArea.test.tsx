import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TextArea } from '../TextArea';

describe('TextArea Component', () => {
  // Basic rendering tests
  test('renders textarea with label', () => {
    render(<TextArea label="Description" name="description" />);
    
    const label = screen.getByText('Description');
    expect(label).toBeInTheDocument();
    
    const textarea = screen.getByLabelText('Description');
    expect(textarea).toBeInTheDocument();
  });
  
  test('renders textarea with placeholder', () => {
    render(<TextArea label="Description" name="description" placeholder="Enter description here" />);
    
    const textarea = screen.getByPlaceholderText('Enter description here');
    expect(textarea).toBeInTheDocument();
  });
  
  // Row tests
  test('applies the rows attribute correctly', () => {
    render(<TextArea label="Description" name="description" rows={6} />);
    
    const textarea = screen.getByLabelText('Description');
    expect(textarea).toHaveAttribute('rows', '6');
  });
  
  // Error state tests
  test('displays error message when provided', () => {
    render(
      <TextArea 
        label="Description" 
        name="description" 
        error="Description must be at least 10 characters" 
      />
    );
    
    const errorMessage = screen.getByText('Description must be at least 10 characters');
    expect(errorMessage).toBeInTheDocument();
    
    const textarea = screen.getByLabelText('Description');
    expect(textarea.className).toContain('border-red-500');
  });
  
  // Required state test
  test('adds required attribute when isRequired is true', () => {
    render(<TextArea label="Description" name="description" isRequired />);
    
    const textarea = screen.getByLabelText(/Description/);
    expect(textarea).toHaveAttribute('required');
    
    const requiredIndicator = screen.getByText('*');
    expect(requiredIndicator).toBeInTheDocument();
  });
  
  // Disabled state test
  test('disables textarea when isDisabled is true', () => {
    render(<TextArea label="Description" name="description" isDisabled />);
    
    const textarea = screen.getByLabelText('Description');
    expect(textarea).toBeDisabled();
  });
  
  // FullWidth test
  test('renders full width textarea when fullWidth is true', () => {
    render(<TextArea label="Description" name="description" fullWidth />);
    
    const textareaContainer = screen.getByLabelText('Description').parentElement;
    expect(textareaContainer?.className).toContain('w-full');
  });
  
  // Event handling tests
  test('calls onChange when textarea value changes', () => {
    const handleChange = jest.fn();
    render(<TextArea label="Description" name="description" onChange={handleChange} />);
    
    const textarea = screen.getByLabelText('Description');
    fireEvent.change(textarea, { target: { value: 'New description content' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
  
  test('calls onFocus when textarea is focused', () => {
    const handleFocus = jest.fn();
    render(<TextArea label="Description" name="description" onFocus={handleFocus} />);
    
    const textarea = screen.getByLabelText('Description');
    fireEvent.focus(textarea);
    
    expect(handleFocus).toHaveBeenCalledTimes(1);
  });
  
  test('calls onBlur when textarea loses focus', () => {
    const handleBlur = jest.fn();
    render(<TextArea label="Description" name="description" onBlur={handleBlur} />);
    
    const textarea = screen.getByLabelText('Description');
    fireEvent.blur(textarea);
    
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });
  
  // Controlled textarea test
  test('works as a controlled component', () => {
    const handleChange = jest.fn();
    const { rerender } = render(
      <TextArea 
        label="Controlled TextArea" 
        name="controlled" 
        value="initial text" 
        onChange={handleChange} 
      />
    );
    
    const textarea = screen.getByLabelText('Controlled TextArea');
    expect(textarea).toHaveValue('initial text');
    
    // Simulate user typing
    fireEvent.change(textarea, { target: { value: 'new text content' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
    
    // Update the component with new value
    rerender(
      <TextArea 
        label="Controlled TextArea" 
        name="controlled" 
        value="new text content" 
        onChange={handleChange} 
      />
    );
    
    expect(textarea).toHaveValue('new text content');
  });
}); 