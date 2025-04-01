import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { RefinementPage } from '../RefinementPage';
import { vi } from 'vitest';
import * as supabaseClient from '../../../services/supabaseClient';
import * as sessionManager from '../../../services/sessionManager';
import * as useConceptRefinementModule from '../../../hooks/useConceptRefinement';

// Mock the necessary imports
vi.mock('../../../services/supabaseClient', async () => ({
  fetchConceptDetail: vi.fn()
}));

vi.mock('../../../services/sessionManager', async () => ({
  getSessionId: vi.fn()
}));

vi.mock('../../../hooks/useConceptRefinement', async () => ({
  useConceptRefinement: vi.fn()
}));

// Mock the components
vi.mock('../components/RefinementHeader', () => ({
  RefinementHeader: () => <div data-testid="refinement-header">Refine Your Concept</div>
}));

vi.mock('../components/RefinementForm', () => ({
  RefinementForm: ({ onSubmit }) => (
    <div data-testid="refinement-form">
      <button onClick={() => onSubmit('Make it blue', 'Updated logo', 'Updated theme', ['colors'])}>
        Submit Form
      </button>
    </div>
  )
}));

vi.mock('../components/ComparisonView', () => ({
  ComparisonView: () => <div data-testid="comparison-view">Comparison View</div>
}));

vi.mock('../components/RefinementActions', () => ({
  RefinementActions: ({ onReset, onCreateNew }) => (
    <div data-testid="refinement-actions">
      <button data-testid="reset-button" onClick={onReset}>Reset</button>
      <button data-testid="create-new-button" onClick={onCreateNew}>Create New</button>
    </div>
  )
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

describe('RefinementPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock for useConceptRefinement
    vi.mocked(useConceptRefinementModule.useConceptRefinement).mockReturnValue({
      refineConcept: vi.fn(),
      resetRefinement: vi.fn(),
      status: 'idle',
      result: null,
      error: null,
      isLoading: false
    });
  });

  // Mock sample concept data
  const mockConcept = {
    id: 'test-123',
    base_image_url: 'https://example.com/base-image.png',
    logo_description: 'Test Logo Description',
    theme_description: 'Test Theme Description'
  };

  test('renders loading state initially', () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to never resolve yet
    vi.mocked(supabaseClient.fetchConceptDetail).mockImplementation(() => 
      new Promise(() => {})
    );

    render(
      <MemoryRouter initialEntries={['/refine/test-123']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Should show refinement header
    expect(screen.getByTestId('refinement-header')).toBeInTheDocument();
    
    // Should show loading state
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  test('renders form when concept is loaded', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);

    render(
      <MemoryRouter initialEntries={['/refine/test-123']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the form to appear
    await waitFor(() => {
      expect(screen.getByTestId('refinement-form')).toBeInTheDocument();
    });
  });

  test('handles form submission', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);
    
    // Mock refineConcept function
    const mockRefineConcept = vi.fn();
    vi.mocked(useConceptRefinementModule.useConceptRefinement).mockReturnValue({
      refineConcept: mockRefineConcept,
      resetRefinement: vi.fn(),
      status: 'idle',
      result: null,
      error: null,
      isLoading: false
    });

    render(
      <MemoryRouter initialEntries={['/refine/test-123']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the form to appear
    await waitFor(() => {
      expect(screen.getByTestId('refinement-form')).toBeInTheDocument();
    });

    // Submit the form
    fireEvent.click(screen.getByText('Submit Form'));

    // Check that refineConcept was called with the right arguments
    expect(mockRefineConcept).toHaveBeenCalledWith(
      'https://example.com/base-image.png',
      'Make it blue',
      'Updated logo',
      'Updated theme',
      ['colors']
    );
  });

  test('displays comparison view when refinement succeeds', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);
    
    // Mock useConceptRefinement to return a successful result
    vi.mocked(useConceptRefinementModule.useConceptRefinement).mockReturnValue({
      refineConcept: vi.fn(),
      resetRefinement: vi.fn(),
      status: 'success',
      result: {
        imageUrl: 'https://example.com/refined-image.png',
        colorPalette: {
          primary: '#0000FF',
          secondary: '#AAAAFF'
        }
      },
      error: null,
      isLoading: false
    });

    render(
      <MemoryRouter initialEntries={['/refine/test-123']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the comparison view to appear
    await waitFor(() => {
      expect(screen.getByTestId('comparison-view')).toBeInTheDocument();
    });

    // Check that the actions are shown
    expect(screen.getByTestId('refinement-actions')).toBeInTheDocument();
  });

  test('displays error message when concept not found', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return null (concept not found)
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(null);

    render(
      <MemoryRouter initialEntries={['/refine/not-found']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    // Check if the error message and back button are shown
    expect(screen.getByText('Concept not found')).toBeInTheDocument();
    expect(screen.getByText('Back to Home')).toBeInTheDocument();
  });

  test('navigates back home when clicking back button on error', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return null (concept not found)
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(null);

    render(
      <MemoryRouter initialEntries={['/refine/not-found']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Back to Home')).toBeInTheDocument();
    });

    // Click the back button
    fireEvent.click(screen.getByText('Back to Home'));

    // Check that navigate was called with the correct path
    expect(mockNavigate).toHaveBeenCalledWith('/');
  });

  test('resets refinement when clicking reset button', async () => {
    // Mock session ID
    vi.mocked(sessionManager.getSessionId).mockReturnValue('test-session');
    
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);
    
    // Mock resetRefinement function
    const mockResetRefinement = vi.fn();
    vi.mocked(useConceptRefinementModule.useConceptRefinement).mockReturnValue({
      refineConcept: vi.fn(),
      resetRefinement: mockResetRefinement,
      status: 'success',
      result: {
        imageUrl: 'https://example.com/refined-image.png',
        colorPalette: {
          primary: '#0000FF',
          secondary: '#AAAAFF'
        }
      },
      error: null,
      isLoading: false
    });

    render(
      <MemoryRouter initialEntries={['/refine/test-123']}>
        <Routes>
          <Route path="/refine/:conceptId" element={<RefinementPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the reset button to appear
    await waitFor(() => {
      expect(screen.getByTestId('reset-button')).toBeInTheDocument();
    });

    // Click the reset button
    fireEvent.click(screen.getByTestId('reset-button'));

    // Check that resetRefinement was called
    expect(mockResetRefinement).toHaveBeenCalled();
  });
}); 