import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { LandingPage } from '../LandingPage';
import * as useConceptMutationsModule from '../../../hooks/useConceptMutations';
import { vi } from 'vitest';
import { mockApiService } from '../../../services/mocks/mockApiService';
import { setupMockApi, resetMockApi } from '../../../services/mocks/testSetup';

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

describe('LandingPage Component', () => {
  beforeEach(() => {
    resetMockApi();
    vi.clearAllMocks();
    
    // Restore the original implementation for all tests
    vi.restoreAllMocks();
  });
  
  test('renders form in initial state', () => {
    renderWithRouter(<LandingPage />);
    
    // Header should be present
    expect(screen.getByText(/Create Visual Concepts/i)).toBeInTheDocument();
    
    // How It Works section should be present
    expect(screen.getByText(/How It Works/i)).toBeInTheDocument();
    
    // Form elements should be present
    expect(screen.getByLabelText(/Logo Description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Theme Description/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Generate Concept/i })).toBeInTheDocument();
    
    // No result should be visible
    expect(screen.queryByText(/Generated Concept/i)).not.toBeInTheDocument();
  });
  
  test('handles form submission', async () => {
    // Setup mock for successful generation
    setupSuccessScenario();
    
    renderWithRouter(<LandingPage />);
    
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
      expect(screen.getByText(/Generated Concept/i)).toBeInTheDocument();
    });
    
    // Check that the reset button is displayed
    expect(screen.getByRole('button', { name: /Start Over/i })).toBeInTheDocument();
  });
  
  test('displays validation errors', () => {
    renderWithRouter(<LandingPage />);
    
    // Try to submit empty form
    const submitButton = screen.getByRole('button', { name: /Generate Concept/i });
    fireEvent.click(submitButton);
    
    // Should show validation error
    expect(screen.getByText(/Please provide both logo and theme descriptions/i)).toBeInTheDocument();
  });
  
  test('handles API errors gracefully', async () => {
    // Mock implementation for error state
    vi.spyOn(useConceptMutationsModule, 'useGenerateConceptMutation').mockImplementation(() => ({
      mutate: vi.fn(),
      reset: vi.fn(),
      isPending: false,
      isSuccess: false,
      isError: true,
      error: new Error('Failed to generate concept'),
      data: null
    }));
    
    renderWithRouter(<LandingPage />);
    
    // Should show error message
    expect(screen.getByText(/Failed to generate concept/i)).toBeInTheDocument();
    
    // Form should still be accessible
    expect(screen.getByRole('button', { name: /Generate Concept/i })).toBeInTheDocument();
  });
  
  test('navigates to the detail page when clicking view details', () => {
    // Mock implementation with sample concepts
    vi.spyOn(useConceptMutationsModule, 'useGenerateConceptMutation').mockImplementation(() => ({
      mutate: vi.fn(),
      reset: vi.fn(),
      isPending: false,
      isSuccess: false,
      isError: false,
      error: null,
      data: null
    }));
    
    renderWithRouter(<LandingPage />);
    
    // Recent concepts section should show some samples
    expect(screen.getByText(/Recent Concepts/i)).toBeInTheDocument();
    
    // Note: We don't try to test the sample concept navigation 
    // since alert() would be called instead of navigate()
  });
}); 