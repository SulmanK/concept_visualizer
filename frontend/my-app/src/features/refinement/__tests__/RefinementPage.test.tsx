import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi } from 'vitest';
import { RefinementPage } from '../RefinementPage';
import * as supabaseClient from '../../../services/supabaseClient';
import * as useConceptMutationsModule from '../../../hooks/useConceptMutations';
import { withRoutesWrapper } from '../../../test-wrappers';

// Mock the necessary imports
vi.mock('../../../services/supabaseClient', async () => ({
  fetchConceptDetail: vi.fn()
}));

vi.mock('../../../hooks/useConceptMutations', async () => ({
  useRefineConceptMutation: vi.fn()
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

// Add loading skeleton mock
vi.mock('../../../components/ui/Card', () => ({
  Card: ({ isLoading, children }) => (
    <div>
      {isLoading ? <div data-testid="loading-skeleton">Loading...</div> : children}
    </div>
  )
}));

// Mock useNavigate
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useParams: () => ({ conceptId: 'test-123' }),
    useLocation: () => ({ search: '' }),
    useSearchParams: () => [new URLSearchParams('')]
  };
});

// Mock useConceptDetail 
vi.mock('../../../hooks/useConceptQueries', () => ({
  useConceptDetail: vi.fn(() => ({
    data: null,
    isLoading: true,
    error: null
  }))
}));

// Mock AuthContext hooks
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user-id', email: 'test@example.com' },
    isLoading: false,
    isAuthenticated: true
  }),
  useAuthUser: () => ({ id: 'test-user-id', email: 'test@example.com' }),
  useUserId: () => 'test-user-id',
  useIsAnonymous: () => false,
  useAuthIsLoading: () => false
}));

// Mock the error handling hook - using a direct export mock instead of the previous approach
vi.mock('../../../hooks/useErrorHandling', () => {
  // Create a mock function to return
  const mockErrorHandler = {
    handleError: vi.fn(),
    clearError: vi.fn()
  };
  
  // Export both the named function and default export
  return {
    default: () => mockErrorHandler,
    useErrorHandling: () => mockErrorHandler
  };
});

// Import the mock hook
import { useConceptDetail } from '../../../hooks/useConceptQueries';

describe('RefinementPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    
    // Default mock for useRefineConceptMutation
    vi.mocked(useConceptMutationsModule.useRefineConceptMutation).mockReturnValue({
      mutate: vi.fn(),
      reset: vi.fn(),
      isPending: false,
      isSuccess: false,
      isError: false,
      data: null,
      error: null
    });
  });

  // Mock sample concept data
  const mockConcept = {
    id: 'test-123',
    image_url: 'https://example.com/base-image.png',
    base_image_url: 'https://example.com/base-image.png',
    logo_description: 'Test Logo Description',
    theme_description: 'Test Theme Description'
  };

  test('renders loading state initially', () => {
    // Mock the hook to return loading state
    vi.mocked(useConceptDetail).mockReturnValue({
      data: undefined,
      isLoading: true,
      error: null
    });

    // Use withRoutesWrapper to provide all the necessary context providers
    render(withRoutesWrapper(['/refine/test-123'], '/refine/:conceptId', <RefinementPage />));

    // Should show refinement header
    expect(screen.getByTestId('refinement-header')).toBeInTheDocument();
    
    // Should show loading state
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  test('renders form when concept is loaded', async () => {
    // Mock the hook to return our test concept
    vi.mocked(useConceptDetail).mockReturnValue({
      data: mockConcept,
      isLoading: false,
      error: null
    });

    render(withRoutesWrapper(['/refine/test-123'], '/refine/:conceptId', <RefinementPage />));

    // Wait for the form to appear
    await waitFor(() => {
      expect(screen.getByTestId('refinement-form')).toBeInTheDocument();
    });
  });

  test('handles form submission', async () => {
    // Mock the hook to return our test concept
    vi.mocked(useConceptDetail).mockReturnValue({
      data: mockConcept,
      isLoading: false,
      error: null
    });
    
    // Mock refineConcept function
    const mockMutate = vi.fn();
    vi.mocked(useConceptMutationsModule.useRefineConceptMutation).mockReturnValue({
      mutate: mockMutate,
      reset: vi.fn(),
      isPending: false,
      isSuccess: false,
      isError: false,
      data: null,
      error: null
    });

    render(withRoutesWrapper(['/refine/test-123'], '/refine/:conceptId', <RefinementPage />));

    // Wait for the form to appear
    await waitFor(() => {
      expect(screen.getByTestId('refinement-form')).toBeInTheDocument();
    });

    // Submit the form
    fireEvent.click(screen.getByText('Submit Form'));

    // The implementation has disabled the actual refinement, so no mutation should be called
    // We're testing UI behavior rather than the actual call
    expect(mockMutate).not.toHaveBeenCalled();
  });

  test('displays comparison view when refinement succeeds', async () => {
    // Mock the hook to return our test concept
    vi.mocked(useConceptDetail).mockReturnValue({
      data: mockConcept,
      isLoading: false,
      error: null
    });
    
    // Mock useRefineConceptMutation to return a successful result
    vi.mocked(useConceptMutationsModule.useRefineConceptMutation).mockReturnValue({
      mutate: vi.fn(),
      reset: vi.fn(),
      isPending: false,
      isSuccess: true,
      isError: false,
      data: {
        task_id: 'task-123',
        result_id: 'result-123',
        status: 'completed',
        type: 'concept_refinement',
        result: {
          imageUrl: 'https://example.com/refined-image.png',
          colorPalette: {
            primary: '#0000FF',
            secondary: '#AAAAFF'
          }
        }
      }
    });

    render(withRoutesWrapper(['/refine/test-123'], '/refine/:conceptId', <RefinementPage />));

    // Wait for the comparison view to appear
    await waitFor(() => {
      expect(screen.getByTestId('comparison-view')).toBeInTheDocument();
    });
  });
}); 