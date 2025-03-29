import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConceptForm } from '../ConceptForm';
import { FormStatus } from '../../../types';

describe('ConceptForm Component', () => {
  // Mock handlers
  const mockSubmit = jest.fn();
  const mockReset = jest.fn();
  
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  // Basic rendering test
  test('renders form fields and submit button', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="idle" 
        onReset={mockReset}
      />
    );
    
    // Check for page title
    const title = screen.getByText('Create New Concept');
    expect(title).toBeInTheDocument();
    
    // Check for form inputs
    const logoLabel = screen.getByText('Logo Description');
    const themeLabel = screen.getByText('Theme/Color Scheme Description');
    expect(logoLabel).toBeInTheDocument();
    expect(themeLabel).toBeInTheDocument();
    
    // Check for the submit button
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    expect(submitButton).toBeInTheDocument();
  });
  
  // Form validation test - empty fields
  test('validates form and prevents submission with empty fields', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="idle" 
        onReset={mockReset}
      />
    );
    
    // Find and click the submit button without filling out the form
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    fireEvent.click(submitButton);
    
    // Check for validation error messages
    const logoError = screen.getByText('Please enter a logo description');
    const themeError = screen.getByText('Please enter a theme description');
    expect(logoError).toBeInTheDocument();
    expect(themeError).toBeInTheDocument();
    
    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });
  
  // Form validation test - too short inputs
  test('validates form and prevents submission with inputs that are too short', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="idle" 
        onReset={mockReset}
      />
    );
    
    // Find the textareas by their labels
    const logoLabel = screen.getByText('Logo Description');
    const themeLabel = screen.getByText('Theme/Color Scheme Description');
    
    // Find the textareas that are siblings of the labels
    const logoTextarea = logoLabel.parentElement?.querySelector('textarea');
    const themeTextarea = themeLabel.parentElement?.querySelector('textarea');
    
    // Fill out the form with values that are too short
    if (logoTextarea && themeTextarea) {
      fireEvent.change(logoTextarea, { target: { value: 'Logo' } });
      fireEvent.change(themeTextarea, { target: { value: 'Blue' } });
    }
    
    // Find and click the submit button
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    fireEvent.click(submitButton);
    
    // Check for validation error messages
    const logoError = screen.getByText('Logo description must be at least 5 characters');
    const themeError = screen.getByText('Theme description must be at least 5 characters');
    expect(logoError).toBeInTheDocument();
    expect(themeError).toBeInTheDocument();
    
    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });
  
  // Successful form submission test
  test('submits form with valid inputs', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="idle" 
        onReset={mockReset}
      />
    );
    
    // Find the textareas by their labels
    const logoLabel = screen.getByText('Logo Description');
    const themeLabel = screen.getByText('Theme/Color Scheme Description');
    
    // Find the textareas that are siblings of the labels
    const logoTextarea = logoLabel.parentElement?.querySelector('textarea');
    const themeTextarea = themeLabel.parentElement?.querySelector('textarea');
    
    // Fill out the form with valid values
    if (logoTextarea && themeTextarea) {
      fireEvent.change(logoTextarea, { target: { value: 'A modern logo with abstract shapes' } });
      fireEvent.change(themeTextarea, { target: { value: 'Blue and purple gradient theme' } });
    }
    
    // Find and click the submit button
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    fireEvent.click(submitButton);
    
    // Verify that the submission handler was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith(
      'A modern logo with abstract shapes', 
      'Blue and purple gradient theme'
    );
  });
  
  // Loading state test
  test('displays loading state when status is submitting', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="submitting" 
        onReset={mockReset}
      />
    );
    
    // Check for the loading button text
    const loadingButton = screen.getByText('Generating...');
    expect(loadingButton).toBeInTheDocument();
    
    // Verify that the button is disabled
    const button = loadingButton.closest('button');
    expect(button).toBeDisabled();
    
    // Verify that the textareas are disabled
    const textareas = screen.getAllByRole('textbox');
    textareas.forEach(textarea => {
      expect(textarea).toBeDisabled();
    });
  });
  
  // Error state test
  test('displays error message when provided', () => {
    const errorMessage = 'Failed to generate concept';
    
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="error" 
        error={errorMessage}
        onReset={mockReset}
      />
    );
    
    // Check for the error message
    const errorElement = screen.getByText(errorMessage);
    expect(errorElement).toBeInTheDocument();
  });
  
  // Success state test - form inputs should be disabled
  test('disables form inputs when status is success', () => {
    render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="success" 
        onReset={mockReset}
      />
    );
    
    // Check that the form inputs are disabled
    const textareas = screen.getAllByRole('textbox');
    textareas.forEach(textarea => {
      expect(textarea).toBeDisabled();
    });
    
    // Check that the submit button is disabled
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    expect(submitButton).toBeDisabled();
  });
  
  // Snapshot test
  test('matches snapshot', () => {
    const { container } = render(
      <ConceptForm 
        onSubmit={mockSubmit} 
        status="idle" 
        onReset={mockReset}
      />
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });
}); 