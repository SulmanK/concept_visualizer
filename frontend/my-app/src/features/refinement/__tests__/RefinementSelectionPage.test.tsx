import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { RefinementSelectionPage } from '../RefinementSelectionPage';
import { vi } from 'vitest';

// Mock the React Query hooks
vi.mock('../../../hooks/useConceptQueries', () => ({
  useRecentConcepts: vi.fn()
}));

// Mock the AuthContext
vi.mock('../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user-id' }
  })
}));

// Mock the QueryClient
vi.mock('@tanstack/react-query', () => ({
  useQueryClient: vi.fn().mockReturnValue({
    invalidateQueries: vi.fn()
  })
}));

// Mock the navigate function
const mockNavigate = vi.fn();
vi.mock('react-router-dom', async (importOriginal) => {
  const actual = await importOriginal();
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

// Import the mocked hook
import { useRecentConcepts } from '../../../hooks/useConceptQueries';

describe('RefinementSelectionPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state', () => {
    // Mock the hook to return loading state
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: [],
      isLoading: true,
      error: null,
      refetch: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the loading state is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  test('renders error state', () => {
    // Mock the hook to return error state
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: [],
      isLoading: false,
      error: new Error('Failed to load concepts'),
      refetch: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the error state is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
    expect(screen.getByText('Failed to load concepts')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('renders empty state', () => {
    // Mock the hook to return empty state
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the empty state is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByText('No Concepts Available')).toBeInTheDocument();
    expect(screen.getByText('You need to create concepts before you can refine them.')).toBeInTheDocument();
    expect(screen.getByText('Create New Concept')).toBeInTheDocument();
  });

  test('navigates to create page when clicking create button in empty state', () => {
    // Mock the hook to return empty state
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: [],
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Click the Create New Concept button
    fireEvent.click(screen.getByText('Create New Concept'));

    // Check that navigate was called with the correct path
    expect(mockNavigate).toHaveBeenCalledWith('/create');
  });

  test('renders concepts when available', () => {
    // Mock concepts data
    const mockConcepts = [
      {
        id: 'concept-1',
        image_url: 'https://example.com/concept1.png',
        base_image_url: 'https://example.com/concept1.png',
        logo_description: 'First Test Concept',
        theme_description: 'Test theme 1',
        color_variations: []
      },
      {
        id: 'concept-2',
        image_url: 'https://example.com/concept2.png',
        base_image_url: 'https://example.com/concept2.png',
        logo_description: 'Second Test Concept',
        theme_description: 'Test theme 2',
        color_variations: []
      }
    ];

    // Mock the hook to return concepts
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: mockConcepts,
      isLoading: false,
      error: null,
      refetch: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the concept rows are rendered
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByText('First Test Concept')).toBeInTheDocument();
    expect(screen.getByText('Second Test Concept')).toBeInTheDocument();
  });
}); 