import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { Input } from '../Input';

describe('Input Component', () => {
  // Basic rendering tests
  test('renders input with label', () => {
    render(<Input label="Username" name="username" />);
    
    const label = screen.getByText('Username');
    expect(label).toBeInTheDocument();
    
    const input = screen.getByLabelText('Username');
    expect(input).toBeInTheDocument();
  });
  
  test('renders input with placeholder', () => {
    render(<Input label="Username" name="username" placeholder="Enter your username" />);
    
    const input = screen.getByPlaceholderText('Enter your username');
    expect(input).toBeInTheDocument();
  });
  
  // Type tests
  test.each([
    ['text', 'text'],
    ['email', 'email'],
    ['password', 'password'],
    ['number', 'number'],
  ])('renders input with type %s', (type, expectedType) => {
    render(<Input label="Test" name="test" type={type as any} />);
    
    const input = screen.getByLabelText('Test');
    expect(input).toHaveAttribute('type', expectedType);
  });
  
  // Error state tests
  test('displays error message when provided', () => {
    render(
      <Input 
        label="Password" 
        name="password" 
        error="Password must be at least 8 characters" 
      />
    );
    
    const errorMessage = screen.getByText('Password must be at least 8 characters');
    expect(errorMessage).toBeInTheDocument();
    
    const input = screen.getByLabelText('Password');
    expect(input.className).toContain('border-accent-500');
  });
  
  // Required state test
  test('adds required attribute when required prop is true', () => {
    render(<Input label="Email" name="email" required />);
    
    const input = screen.getByLabelText(/Email/);
    expect(input).toHaveAttribute('required');
  });
  
  // Disabled state test
  test('disables input when disabled prop is true', () => {
    render(<Input label="Username" name="username" disabled />);
    
    const input = screen.getByLabelText('Username');
    expect(input).toBeDisabled();
  });
  
  // FullWidth test
  test('renders full width input when fullWidth is true', () => {
    render(<Input label="Username" name="username" fullWidth />);
    
    const container = screen.getByLabelText('Username').closest('div')?.parentElement;
    expect(container?.className).toContain('w-full');
  });
  
  // Event handling tests
  test('calls onChange when input value changes', () => {
    const handleChange = jest.fn();
    render(<Input label="Search" name="search" onChange={handleChange} />);
    
    const input = screen.getByLabelText('Search');
    fireEvent.change(input, { target: { value: 'test query' } });
    
    expect(handleChange).toHaveBeenCalledTimes(1);
  });
  
  test('calls onFocus when input is focused', () => {
    const handleFocus = jest.fn();
    render(<Input label="Email" name="email" onFocus={handleFocus} />);
    
    const input = screen.getByLabelText('Email');
    fireEvent.focus(input);
    
    expect(handleFocus).toHaveBeenCalledTimes(1);
  });
  
  test('calls onBlur when input loses focus', () => {
    const handleBlur = jest.fn();
    render(<Input label="Password" name="password" onBlur={handleBlur} />);
    
    const input = screen.getByLabelText('Password');
    fireEvent.blur(input);
    
    expect(handleBlur).toHaveBeenCalledTimes(1);
  });
  
  // Helper text test
  test('displays helper text when provided', () => {
    render(
      <Input 
        label="Username" 
        name="username" 
        helperText="Enter your username" 
      />
    );
    
    const helperText = screen.getByText('Enter your username');
    expect(helperText).toBeInTheDocument();
    expect(helperText.className).toContain('helper-text');
  });
  
  // Controlled input test
  test('works as a controlled component', () => {
    const handleChange = jest.fn();
    const { rerender } = render(
      <Input 
        label="Controlled Input" 
        name="controlled" 
        value="initial value" 
        onChange={handleChange} 
      />
    );
    
    const input = screen.getByLabelText('Controlled Input');
    expect(input).toHaveValue('initial value');
    
    // Simulate user typing
    fireEvent.change(input, { target: { value: 'new value' } });
    expect(handleChange).toHaveBeenCalledTimes(1);
    
    // Update the component with new value
    rerender(
      <Input 
        label="Controlled Input" 
        name="controlled" 
        value="new value" 
        onChange={handleChange} 
      />
    );
    
    expect(input).toHaveValue('new value');
  });
}); 