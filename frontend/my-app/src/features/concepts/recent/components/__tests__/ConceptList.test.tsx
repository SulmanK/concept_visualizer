import React from 'react';
import { fireEvent, render, screen } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { ConceptList } from '../ConceptList';
import { vi } from 'vitest';

// Mock the hooks
vi.mock('../../../../../hooks/useConceptQueries', () => ({
  useRecentConcepts: vi.fn(),
  useFreshRecentConcepts: vi.fn()
}));

vi.mock('../../../../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: { id: 'test-user-id' }
  })
}));

vi.mock('@tanstack/react-query', () => ({
  useQueryClient: vi.fn().mockReturnValue({
    invalidateQueries: vi.fn(),
  })
}));

// Import the mocked hooks
import { useRecentConcepts } from '../../../../../hooks/useConceptQueries';

describe('ConceptList Component', () => {
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
        <ConceptList />
      </BrowserRouter>
    );

    // Check that the loading animation is shown
    expect(screen.getByText('Recent Concepts')).toBeInTheDocument();
    expect(screen.getByTestId('loading-animation')).toBeInTheDocument();
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
        <ConceptList />
      </BrowserRouter>
    );

    // Check that the empty state message is shown
    expect(screen.getByText('Recent Concepts')).toBeInTheDocument();
    expect(screen.getByText('No concepts yet')).toBeInTheDocument();
    expect(screen.getByText('Create New Concept')).toBeInTheDocument();
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
        <ConceptList />
      </BrowserRouter>
    );

    // Check that the error message is shown
    expect(screen.getByText('Recent Concepts')).toBeInTheDocument();
    expect(screen.getByText('Error Loading Concepts')).toBeInTheDocument();
    expect(screen.getByText('Failed to load concepts')).toBeInTheDocument();
    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('renders concepts when available', () => {
    // Mock concepts data
    const mockConcepts = [
      {
        id: 'concept-1',
        base_image_url: 'https://example.com/concept1.png',
        logo_description: 'First Test Concept',
        theme_description: 'Test theme 1',
        color_variations: []
      },
      {
        id: 'concept-2',
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
        <ConceptList />
      </BrowserRouter>
    );

    // Check that the concept cards are rendered
    expect(screen.getByText('Recent Concepts')).toBeInTheDocument();
    expect(screen.getByTestId('concept-card-concept-1')).toBeInTheDocument();
    expect(screen.getByTestId('concept-card-concept-2')).toBeInTheDocument();
    expect(screen.getByText('First Test Concept')).toBeInTheDocument();
    expect(screen.getByText('Second Test Concept')).toBeInTheDocument();
  });

  test('triggers refresh when trying again after error', () => {
    // Mock refresh function
    const mockRefetch = vi.fn();
    
    // Mock the hook to return error state
    vi.mocked(useRecentConcepts).mockReturnValue({
      data: [],
      isLoading: false,
      error: new Error('Failed to load concepts'),
      refetch: mockRefetch
    });

    render(
      <BrowserRouter>
        <ConceptList />
      </BrowserRouter>
    );

    // Click the "Try Again" button
    fireEvent.click(screen.getByText('Try Again'));

    // Check that the refresh function was called
    expect(mockRefetch).toHaveBeenCalled();
  });
}); 