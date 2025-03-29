import React from 'react';
import { render, screen, fireEvent, within, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ConceptGenerator } from '../ConceptGenerator';
import * as useConceptGenerationModule from '../../hooks/useConceptGeneration';
import { vi } from 'vitest';
import { mockApiService } from '../../services/mocks/mockApiService';
import { setupMockApi, resetMockApi } from '../../services/mocks/testSetup';

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

// Mock console.log
const originalConsoleLog = console.log;
console.log = vi.fn();

// Clean up after tests
afterAll(() => {
  console.log = originalConsoleLog;
});

// Helper for renderWithRouter
const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {ui}
    </BrowserRouter>
  );
};

// Setup mockApiService for specific scenarios
const setupSuccessScenario = () => {
  setupMockApi({
    responseDelay: 0,
    customResponses: {
      generateConcept: {
        imageUrl: 'https://example.com/test-concept.png',
        colorPalette: {
          primary: '#4F46E5',
          secondary: '#818CF8',
          accent: '#C4B5FD',
          background: '#F5F3FF',
          text: '#1E1B4B'
        },
        generationId: 'test-123',
        createdAt: new Date().toISOString()
      }
    }
  });
};

describe('ConceptGenerator Component', () => {
  beforeEach(() => {
    resetMockApi();
    vi.clearAllMocks();
    
    // Restore the original implementation for all tests
    vi.restoreAllMocks();
  });
  
  test('renders form in initial state', () => {
    renderWithRouter(<ConceptGenerator />);
    
    // Form elements should be present
    expect(screen.getByLabelText(/Logo Description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Theme Description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Concept/i })).toBeInTheDocument();
    
    // No result should be visible
    expect(screen.queryByText(/Your Generated Concept/i)).not.toBeInTheDocument();
  });
  
  test('handles form submission', async () => {
    // Setup mock for successful generation
    setupSuccessScenario();
    
    renderWithRouter(<ConceptGenerator />);
    
    // Fill out the form
    const logoInput = screen.getByLabelText(/Logo Description/i);
    const themeInput = screen.getByLabelText(/Theme Description/i);
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    
    fireEvent.change(logoInput, { target: { value: 'Modern tech logo' } });
    fireEvent.change(themeInput, { target: { value: 'Gradient indigo theme' } });
    fireEvent.click(submitButton);
    
    // Should show loading state
    expect(screen.getByText(/Generating your concept.../i)).toBeInTheDocument();
    
    // Wait for the result to appear
    await waitFor(() => {
      expect(screen.getByText(/Your Generated Concept/i)).toBeInTheDocument();
    });
    
    // Check that the image is displayed
    const resultImage = screen.getByAltText(/Generated concept image/i);
    expect(resultImage).toBeInTheDocument();
    expect(resultImage).toHaveAttribute('src', 'https://example.com/test-concept.png');
    
    // Check that the color palette is displayed
    expect(screen.getByText(/Color Palette/i)).toBeInTheDocument();
  });
  
  test('displays validation errors', () => {
    renderWithRouter(<ConceptGenerator />);
    
    // Try to submit empty form
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    fireEvent.click(submitButton);
    
    // Should show validation error
    expect(screen.getByText(/Please provide both logo and theme descriptions/i)).toBeInTheDocument();
  });
  
  test('handles API errors gracefully', async () => {
    // Mock implementation for error state
    vi.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: vi.fn(),
      resetGeneration: vi.fn(),
      status: 'error',
      result: null,
      error: 'Failed to generate concept',
      isLoading: false,
      clearError: vi.fn()
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Should show error message
    expect(screen.getByText(/Failed to generate concept/i)).toBeInTheDocument();
    
    // Form should still be accessible
    expect(screen.getByRole('button', { name: /Generate Concept/i })).toBeInTheDocument();
  });
  
  test('navigates to refinement when Refine This Concept is clicked', async () => {
    // Mock implementation for success state
    const mockResult = {
      imageUrl: 'https://example.com/test-concept.png',
      colorPalette: {
        primary: '#4F46E5',
        secondary: '#818CF8',
        accent: '#C4B5FD',
        background: '#F5F3FF',
        text: '#1E1B4B'
      },
      generationId: 'test-123',
      createdAt: new Date().toISOString()
    };
    
    vi.spyOn(useConceptGenerationModule, 'useConceptGeneration').mockImplementation(() => ({
      generateConcept: vi.fn(),
      resetGeneration: vi.fn(),
      status: 'success',
      result: mockResult,
      error: null,
      isLoading: false,
      clearError: vi.fn()
    }));
    
    renderWithRouter(<ConceptGenerator />);
    
    // Find and click the Refine This Concept button
    const refineButton = screen.getByRole('button', { name: /Refine This Concept/i });
    fireEvent.click(refineButton);
    
    // Should navigate to refinement page
    expect(mockNavigate).toHaveBeenCalledWith('/refine/test-123');
  });
}); 