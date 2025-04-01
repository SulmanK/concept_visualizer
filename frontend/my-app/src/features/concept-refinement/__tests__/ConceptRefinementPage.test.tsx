import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ConceptRefinementPage } from '../ConceptRefinementPage';
import * as useConceptRefinementModule from '../../../hooks/useConceptRefinement';
import { vi } from 'vitest';
import { mockApiService } from '../../../services/mocks/mockApiService';
import { setupMockApi, resetMockApi, mockApiFailure } from '../../../services/mocks/testSetup';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ conceptId: 'mock-concept-123' })
  };
});

// Helper for renderWithRouter
const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <Routes>
        <Route path="*" element={ui} />
      </Routes>
    </BrowserRouter>
  );
};

// Setup mockApiService for specific scenarios
const setupSuccessScenario = () => {
  setupMockApi({
    responseDelay: 0,
    customResponses: {
      refineConcept: {
        imageUrl: 'https://example.com/refined-concept.png',
        colorPalette: {
          primary: '#6366F1',
          secondary: '#A5B4FC',
          accent: '#E0E7FF',
          background: '#EEF2FF',
          text: '#312E81'
        },
        generationId: 'refined-concept-123',
        createdAt: new Date().toISOString(),
        originalImageUrl: 'https://example.com/original-concept.png',
        refinementPrompt: 'Make it more vibrant'
      }
    }
  });
};

describe('ConceptRefinementPage Component', () => {
  beforeEach(() => {
    resetMockApi();
    vi.clearAllMocks();
    
    // Restore the original implementation for all tests
    vi.restoreAllMocks();
    
    // Mock localStorage to provide a test concept
    const mockLocalStorage = {
      getItem: vi.fn().mockImplementation((key) => {
        if (key === 'savedConcepts') {
          return JSON.stringify([
            {
              imageUrl: 'https://example.com/original-concept.png',
              colorPalette: {
                primary: '#4F46E5',
                secondary: '#818CF8',
                accent: '#C4B5FD',
                background: '#F5F3FF',
                text: '#1E1B4B'
              },
              generationId: 'mock-concept-123',
              createdAt: new Date().toISOString()
            }
          ]);
        }
        return null;
      }),
      setItem: vi.fn()
    };
    
    Object.defineProperty(window, 'localStorage', {
      value: mockLocalStorage,
      writable: true
    });
  });
  
  test('renders form with original concept data', () => {
    renderWithRouter(<ConceptRefinementPage />);
    
    // Header should be present
    expect(screen.getByText(/Refine Your Concept/i)).toBeInTheDocument();
    
    // Original concept should be displayed
    const originalImage = screen.getByAltText(/Original concept/i);
    expect(originalImage).toBeInTheDocument();
    expect(originalImage).toHaveAttribute('src', 'https://placehold.co/800x800?text=Original+Concept');
    
    // Form elements should be present
    expect(screen.getByLabelText(/Refinement Instructions/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Refine Concept/i })).toBeInTheDocument();
  });
  
  test('handles form submission for refinement', async () => {
    // Setup mock for successful refinement
    setupSuccessScenario();
    
    renderWithRouter(<ConceptRefinementPage />);
    
    // Fill out the refinement form
    const instructionsInput = screen.getByLabelText(/Refinement Instructions/i);
    fireEvent.change(instructionsInput, { target: { value: 'Make it more vibrant with brighter colors' } });
    
    // Check some preserve aspects options
    const colorCheckbox = screen.getByLabelText(/Preserve color scheme/i);
    fireEvent.click(colorCheckbox);
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Should show loading state
    expect(screen.getByText(/Refining your concept.../i)).toBeInTheDocument();
    
    // Wait for the result to appear
    await waitFor(() => {
      expect(screen.getByAltText(/Refined concept/i)).toBeInTheDocument();
    });
    
    // Check that the refined image is displayed
    const refinedImage = screen.getByAltText(/Refined concept/i);
    expect(refinedImage).toBeInTheDocument();
    expect(refinedImage).toHaveAttribute('src', 'https://example.com/refined-concept.png');
    
    // Should show both original and refined concept
    expect(screen.getByText(/Original/i)).toBeInTheDocument();
    expect(screen.getByText(/Refined/i)).toBeInTheDocument();
  });
  
  test('displays validation errors', () => {
    renderWithRouter(<ConceptRefinementPage />);
    
    // Try to submit with empty instructions
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Should show validation error
    expect(screen.getByText(/Please provide refinement instructions/i)).toBeInTheDocument();
  });
  
  test('handles API errors gracefully', async () => {
    // Mock API failure
    mockApiFailure();
    
    renderWithRouter(<ConceptRefinementPage />);
    
    // Fill out the refinement form
    const instructionsInput = screen.getByLabelText(/Refinement Instructions/i);
    fireEvent.change(instructionsInput, { target: { value: 'Make it more vibrant' } });
    
    // Submit the form
    const submitButton = screen.getByRole('button', { name: /Refine Concept/i });
    fireEvent.click(submitButton);
    
    // Wait for the error to appear
    await waitFor(() => {
      expect(screen.getByText(/Failed to refine concept/i)).toBeInTheDocument();
    });
    
    // Form should still be accessible
    expect(screen.getByRole('button', { name: /Refine Concept/i })).toBeInTheDocument();
  });
  
  test('navigates back to home when cancel is clicked', () => {
    renderWithRouter(<ConceptRefinementPage />);
    
    // Find and click the Cancel button
    const cancelButton = screen.getByRole('button', { name: /Cancel/i });
    fireEvent.click(cancelButton);
    
    // Should navigate back to home
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });
}); 