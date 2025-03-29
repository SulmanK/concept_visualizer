import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConceptRefinementForm } from '../ConceptRefinementForm';
import { FormStatus } from '../../../types';

describe('ConceptRefinementForm Component', () => {
  // Mock handlers and props
  const mockSubmit = jest.fn();
  const mockCancel = jest.fn();
  const originalImageUrl = 'https://example.com/original-concept.png';
  const initialLogoDescription = 'Initial logo description';
  const initialThemeDescription = 'Initial theme description';
  
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  // Basic rendering test
  test('renders form fields and buttons', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
        initialLogoDescription={initialLogoDescription}
        initialThemeDescription={initialThemeDescription}
      />
    );
    
    // Check for card title - be more specific to get the heading, not the button
    const titleHeading = screen.getByRole('heading', { name: 'Refine Concept' });
    expect(titleHeading).toBeInTheDocument();
    
    // Check for form inputs
    const refinementLabel = screen.getByText('Refinement Instructions');
    const logoLabel = screen.getByText('Updated Logo Description (Optional)');
    const themeLabel = screen.getByText('Updated Theme Description (Optional)');
    expect(refinementLabel).toBeInTheDocument();
    expect(logoLabel).toBeInTheDocument();
    expect(themeLabel).toBeInTheDocument();
    
    // Check for the original image
    const originalImage = screen.getByAltText('Original concept');
    expect(originalImage).toBeInTheDocument();
    expect(originalImage).toHaveAttribute('src', originalImageUrl);
    
    // Check for preserve aspects section
    const preserveAspectsText = screen.getByText('Preserve Aspects (Optional)');
    expect(preserveAspectsText).toBeInTheDocument();
    
    // Check for aspect options
    const layoutOption = screen.getByText('Layout');
    const colorsOption = screen.getByText('Colors');
    const styleOption = screen.getByText('Style');
    const symbolsOption = screen.getByText('Symbols/Icons');
    const proportionsOption = screen.getByText('Proportions');
    expect(layoutOption).toBeInTheDocument();
    expect(colorsOption).toBeInTheDocument();
    expect(styleOption).toBeInTheDocument();
    expect(symbolsOption).toBeInTheDocument();
    expect(proportionsOption).toBeInTheDocument();
    
    // Check for buttons
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    expect(cancelButton).toBeInTheDocument();
    expect(submitButton).toBeInTheDocument();
  });
  
  // Initial values test
  test('renders with initial values', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
        initialLogoDescription={initialLogoDescription}
        initialThemeDescription={initialThemeDescription}
      />
    );
    
    // Find the textareas by their labels
    const logoLabel = screen.getByText('Updated Logo Description (Optional)');
    const themeLabel = screen.getByText('Updated Theme Description (Optional)');
    
    // Find the textareas via their parent elements
    const logoTextarea = logoLabel.closest('div')?.querySelector('textarea');
    const themeTextarea = themeLabel.closest('div')?.querySelector('textarea');
    
    // Check that they have the initial values
    expect(logoTextarea).toHaveValue(initialLogoDescription);
    expect(themeTextarea).toHaveValue(initialThemeDescription);
  });
  
  // Form validation test - empty refinement prompt
  test('validates form and prevents submission with empty refinement prompt', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
      />
    );
    
    // Find and click the submit button without filling out the refinement prompt
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Check for validation error message
    const error = screen.getByText('Please provide refinement instructions');
    expect(error).toBeInTheDocument();
    
    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });
  
  // Form validation test - refinement prompt too short
  test('validates form and prevents submission with refinement prompt that is too short', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
      />
    );
    
    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText('Refinement Instructions');
    const refinementTextarea = refinementLabel.closest('div')?.querySelector('textarea');
    
    // Fill out the refinement prompt with a value that is too short
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, { target: { value: 'Test' } });
    }
    
    // Find and click the submit button
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Check for validation error message
    const error = screen.getByText('Refinement instructions must be at least 5 characters');
    expect(error).toBeInTheDocument();
    
    // Verify that the submission handler was not called
    expect(mockSubmit).not.toHaveBeenCalled();
  });
  
  // Successful form submission test - with no preserved aspects
  test('submits form with valid refinement prompt and no preserved aspects', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
        initialLogoDescription={initialLogoDescription}
        initialThemeDescription={initialThemeDescription}
      />
    );
    
    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText('Refinement Instructions');
    const refinementTextarea = refinementLabel.closest('div')?.querySelector('textarea');
    
    // Fill out the refinement prompt with a valid value
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, { target: { value: 'Make the logo more minimalist and modern' } });
    }
    
    // Find and click the submit button
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Verify that the submission handler was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith(
      'Make the logo more minimalist and modern',
      initialLogoDescription,
      initialThemeDescription,
      []
    );
  });
  
  // Successful form submission test - with preserved aspects
  test('submits form with valid refinement prompt and selected preserved aspects', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
        initialLogoDescription={initialLogoDescription}
        initialThemeDescription={initialThemeDescription}
      />
    );
    
    // Find the refinement prompt textarea by its label
    const refinementLabel = screen.getByText('Refinement Instructions');
    const refinementTextarea = refinementLabel.closest('div')?.querySelector('textarea');
    
    // Fill out the refinement prompt with a valid value
    if (refinementTextarea) {
      fireEvent.change(refinementTextarea, { target: { value: 'Make the logo more minimalist and modern' } });
    }
    
    // Select some preserve aspects checkboxes
    const colorsCheckbox = screen.getByText('Colors').previousElementSibling;
    const styleCheckbox = screen.getByText('Style').previousElementSibling;
    
    if (colorsCheckbox && styleCheckbox) {
      fireEvent.click(colorsCheckbox);
      fireEvent.click(styleCheckbox);
    }
    
    // Find and click the submit button
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Verify that the submission handler was called with the correct values
    expect(mockSubmit).toHaveBeenCalledWith(
      'Make the logo more minimalist and modern',
      initialLogoDescription,
      initialThemeDescription,
      ['colors', 'style']
    );
  });
  
  // Test aspect selection toggle
  test('toggles preserve aspect when checkbox is clicked', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
      />
    );
    
    // Find the colors checkbox
    const colorsCheckbox = screen.getByText('Colors').previousElementSibling;
    
    // Initially, it should not be checked
    expect(colorsCheckbox).not.toBeChecked();
    
    // Click to select it
    if (colorsCheckbox) {
      fireEvent.click(colorsCheckbox);
    }
    
    // Now it should be checked
    expect(colorsCheckbox).toBeChecked();
    
    // Click to unselect it
    if (colorsCheckbox) {
      fireEvent.click(colorsCheckbox);
    }
    
    // Now it should not be checked again
    expect(colorsCheckbox).not.toBeChecked();
  });
  
  // Loading state test
  test('displays loading state when status is submitting', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="submitting" 
        onCancel={mockCancel}
      />
    );
    
    // Check for the loading button text
    const loadingButton = screen.getByText('Refining...');
    expect(loadingButton).toBeInTheDocument();
    
    // Verify that the submit button is disabled
    const submitButton = loadingButton.closest('button');
    expect(submitButton).toBeDisabled();
    
    // Verify that the textareas are disabled
    const textareas = screen.getAllByRole('textbox');
    textareas.forEach(textarea => {
      expect(textarea).toBeDisabled();
    });
    
    // Verify that the checkboxes are disabled
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toBeDisabled();
    });
  });
  
  // Error state test
  test('displays error message when provided', () => {
    const errorMessage = 'Failed to refine concept';
    
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="error" 
        error={errorMessage}
        onCancel={mockCancel}
      />
    );
    
    // Check for the error message
    const errorElement = screen.getByText(errorMessage);
    expect(errorElement).toBeInTheDocument();
  });
  
  // Cancel button test
  test('calls onCancel when cancel button is clicked', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
      />
    );
    
    // Find and click the cancel button
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);
    
    // Verify that the cancel handler was called
    expect(mockCancel).toHaveBeenCalled();
  });
  
  // Success state test - form inputs should be disabled
  test('disables form inputs when status is success', () => {
    render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="success" 
        onCancel={mockCancel}
      />
    );
    
    // Check that the form inputs are disabled
    const textareas = screen.getAllByRole('textbox');
    textareas.forEach(textarea => {
      expect(textarea).toBeDisabled();
    });
    
    // Check that the checkboxes are disabled
    const checkboxes = screen.getAllByRole('checkbox');
    checkboxes.forEach(checkbox => {
      expect(checkbox).toBeDisabled();
    });
    
    // Check that the submit button is disabled
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    expect(submitButton).toBeDisabled();
  });
  
  // Snapshot test
  test('matches snapshot', () => {
    const { container } = render(
      <ConceptRefinementForm 
        originalImageUrl={originalImageUrl}
        onSubmit={mockSubmit} 
        status="idle" 
        onCancel={mockCancel}
        initialLogoDescription={initialLogoDescription}
        initialThemeDescription={initialThemeDescription}
      />
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });
}); 