import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ConceptResult } from '../ConceptResult';
import { GenerationResponse } from '../../../types';

// Simple mock for window.open to test download functionality
window.open = jest.fn();

describe('ConceptResult Component', () => {
  // Mock handlers
  const mockRefineRequest = jest.fn();
  const mockDownload = jest.fn();
  const mockColorSelect = jest.fn();
  
  // Sample concept data for testing
  const sampleConcept: GenerationResponse = {
    imageUrl: 'https://example.com/generated-concept.png',
    generationId: 'concept-123',
    createdAt: '2023-04-15T12:30:45Z',
    colorPalette: {
      primary: '#4F46E5',
      secondary: '#60A5FA',
      accent: '#EEF2FF',
      background: '#FFFFFF',
      text: '#1E293B',
      additionalColors: ['#818CF8', '#6366F1'],
    },
  };
  
  // Reset mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  // Basic rendering test
  test('renders the concept image and color palette', () => {
    render(
      <ConceptResult 
        concept={sampleConcept}
        onRefineRequest={mockRefineRequest}
        onColorSelect={mockColorSelect}
      />
    );
    
    // Check for the generated image
    const conceptImage = screen.getByAltText('Generated concept');
    expect(conceptImage).toBeInTheDocument();
    expect(conceptImage).toHaveAttribute('src', sampleConcept.imageUrl);
    
    // Check for the color palette heading
    const paletteHeading = screen.getByText('Color Palette');
    expect(paletteHeading).toBeInTheDocument();
    
    // Check for buttons
    const refineButton = screen.getByRole('button', { name: /Refine This Concept/i });
    const downloadButton = screen.getByRole('button', { name: /Download Image/i });
    expect(refineButton).toBeInTheDocument();
    expect(downloadButton).toBeInTheDocument();
  });
  
  // Refine button test
  test('calls onRefineRequest when Refine This Concept button is clicked', () => {
    render(
      <ConceptResult 
        concept={sampleConcept}
        onRefineRequest={mockRefineRequest}
        onColorSelect={mockColorSelect}
      />
    );
    
    // Find and click the refine button
    const refineButton = screen.getByRole('button', { name: /Refine This Concept/i });
    fireEvent.click(refineButton);
    
    // Verify that the refine handler was called
    expect(mockRefineRequest).toHaveBeenCalled();
  });
  
  // Download button with custom handler test
  test('calls onDownload when Download Image button is clicked and onDownload is provided', () => {
    render(
      <ConceptResult 
        concept={sampleConcept}
        onRefineRequest={mockRefineRequest}
        onDownload={mockDownload}
        onColorSelect={mockColorSelect}
      />
    );
    
    // Find and click the download button
    const downloadButton = screen.getByRole('button', { name: /Download Image/i });
    fireEvent.click(downloadButton);
    
    // Verify that the download handler was called
    expect(mockDownload).toHaveBeenCalled();
  });
  
  // Test without refine button
  test('does not render Refine This Concept button when onRefineRequest is not provided', () => {
    render(
      <ConceptResult 
        concept={sampleConcept}
        onColorSelect={mockColorSelect}
      />
    );
    
    // Check that the refine button is not rendered
    const refineButton = screen.queryByRole('button', { name: /Refine This Concept/i });
    expect(refineButton).not.toBeInTheDocument();
    
    // But the download button should still be there
    const downloadButton = screen.getByRole('button', { name: /Download Image/i });
    expect(downloadButton).toBeInTheDocument();
  });
  
  // Snapshot test
  test('matches snapshot', () => {
    const { container } = render(
      <ConceptResult 
        concept={sampleConcept}
        onRefineRequest={mockRefineRequest}
        onColorSelect={mockColorSelect}
      />
    );
    
    expect(container.firstChild).toMatchSnapshot();
  });
}); 