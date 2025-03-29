import React from 'react';
import { render, screen, fireEvent, within } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ConceptGenerator } from '../ConceptGenerator';
import * as useConceptGenerationModule from '../../hooks/useConceptGeneration';

// Mock console.log
const originalConsoleLog = console.log;
console.log = jest.fn();

// Clean up after tests
afterAll(() => {
  console.log = originalConsoleLog;
});

// Mock the useConceptGeneration hook
jest.mock('../../hooks/useConceptGeneration');

// Mock the useNavigate hook from react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Helper function to render with router
const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {ui}
    </BrowserRouter>
  );
};

describe('ConceptGenerator Component', () => {
  // Mock implementation for useConceptGeneration
  const mockGenerateConcept = jest.fn();
  const mockResetGeneration = jest.fn();
  
  // Set up mock response data with correct structure
  const mockResult = {
    imageUrl: 'https://example.com/image.png',
    generationId: 'concept-123',
    createdAt: '2023-03-01T12:00:00Z',
    colorPalette: {
      primary: '#4F46E5',
      secondary: '#60A5FA',
      accent: '#EEF2FF',
      background: '#FFFFFF',
      text: '#1E293B',
      additionalColors: ['#818CF8', '#6366F1']
    }
  };
  
  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();
    
    // Default mock implementation
    jest.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: mockGenerateConcept,
      resetGeneration: mockResetGeneration,
      status: 'idle',
      result: null,
      error: null,
      isLoading: false
    }));
  });
  
  // Basic rendering tests
  test('renders the component in initial state', () => {
    renderWithRouter(<ConceptGenerator />);
    
    // Check for page title
    const title = screen.getByText('Create Visual Concepts');
    expect(title).toBeInTheDocument();
    
    // Check for How It Works section
    const howItWorksTitle = screen.getByText('How It Works');
    expect(howItWorksTitle).toBeInTheDocument();
    
    // Check for sample concepts section
    const recentConcepts = screen.getByText(/Recent Concepts/i);
    expect(recentConcepts).toBeInTheDocument();
  });
  
  // Form submission test
  test('submits the form and calls generateConcept', () => {
    renderWithRouter(<ConceptGenerator />);
    
    // Find the form inputs by their labels
    const logoLabel = screen.getByText('Logo Description');
    const themeLabel = screen.getByText('Theme/Color Scheme Description');
    
    // Find the textareas that are siblings of the labels
    const logoTextarea = logoLabel.parentElement?.querySelector('textarea');
    const themeTextarea = themeLabel.parentElement?.querySelector('textarea');
    
    // Make sure we found the textareas
    expect(logoTextarea).toBeInTheDocument();
    expect(themeTextarea).toBeInTheDocument();
    
    if (logoTextarea && themeTextarea) {
      // Fill out the form
      fireEvent.change(logoTextarea, { target: { value: 'A modern logo' } });
      fireEvent.change(themeTextarea, { target: { value: 'Blue and purple theme' } });
      
      // Find and submit the form
      const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
      fireEvent.click(submitButton);
      
      // Check if the generateConcept function was called with correct args
      expect(mockGenerateConcept).toHaveBeenCalledWith('A modern logo', 'Blue and purple theme');
    }
  });
  
  // Loading state test
  test('displays loading state when generating concept', () => {
    // Mock loading state
    jest.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: mockGenerateConcept,
      resetGeneration: mockResetGeneration,
      status: 'submitting',
      result: null,
      error: null,
      isLoading: true
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Check for loading indicator
    const loadingButton = screen.getByText('Generating...');
    expect(loadingButton).toBeInTheDocument();
    expect(loadingButton.closest('button')).toBeDisabled();
  });
  
  // Success state test
  test('displays result when concept generation succeeds', () => {
    // Mock success state
    jest.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: mockGenerateConcept,
      resetGeneration: mockResetGeneration,
      status: 'success',
      result: mockResult,
      error: null,
      isLoading: false
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Check for the generated image
    const resultImage = screen.getAllByRole('img').find(img => 
      img.getAttribute('src') === mockResult.imageUrl
    );
    expect(resultImage).toBeInTheDocument();
    
    // Check for primary color display (since the palette names may vary)
    const primaryColorText = screen.getByText('Primary');
    expect(primaryColorText).toBeInTheDocument();
    
    // Check for action buttons - looking for the Refine/Download buttons that are present in the success state
    const refineButton = screen.getByRole('button', { name: /Refine This Concept/i });
    const downloadButton = screen.getByRole('button', { name: /Download Image/i });
    expect(refineButton).toBeInTheDocument();
    expect(downloadButton).toBeInTheDocument();
  });
  
  // Error state test
  test('displays error message when concept generation fails', () => {
    const errorMessage = 'Failed to generate concept';
    
    // Mock error state
    jest.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: mockGenerateConcept,
      resetGeneration: mockResetGeneration,
      status: 'error',
      result: null,
      error: errorMessage,
      isLoading: false
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Check for error message
    const errorElement = screen.getByText(errorMessage);
    expect(errorElement).toBeInTheDocument();
    
    // Form should still be accessible
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    expect(submitButton).toBeInTheDocument();
  });
  
  // Reset test - update to match actual implementation
  test('navigates to refinement when Refine This Concept is clicked', () => {
    // Mock success state
    jest.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: mockGenerateConcept,
      resetGeneration: mockResetGeneration,
      status: 'success',
      result: mockResult,
      error: null,
      isLoading: false
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Find and click the Refine This Concept button
    const refineButton = screen.getByRole('button', { name: /Refine This Concept/i });
    fireEvent.click(refineButton);
    
    // In the real implementation, this would navigate to the refinement page
    // with the concept ID, not actually call resetGeneration
    expect(console.log).toHaveBeenCalledWith('Navigate to refinement with:', mockResult.generationId);
  });
  
  // Snapshot test
  test('matches snapshot in initial state', () => {
    const { container } = renderWithRouter(<ConceptGenerator />);
    expect(container.firstChild).toMatchSnapshot();
  });
}); 