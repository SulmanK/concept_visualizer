import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { RefinementSelectionPage } from '../RefinementSelectionPage';
import { vi } from 'vitest';

// Mock the ConceptContext
vi.mock('../../../contexts/ConceptContext', () => ({
  useConceptContext: vi.fn()
}));

// Mock the ConceptCard component
vi.mock('../../concepts/recent/components/ConceptCard', () => ({
  ConceptCard: ({ concept }) => (
    <div data-testid={`concept-card-${concept.id}`}>
      {concept.logo_description}
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
    Link: ({ children, to }) => <a href={to}>{children}</a>
  };
});

// Import the mocked context
import { useConceptContext } from '../../../contexts/ConceptContext';

describe('RefinementSelectionPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  test('renders loading state', () => {
    // Mock the context to return loading state
    vi.mocked(useConceptContext).mockReturnValue({
      recentConcepts: [],
      loadingConcepts: true,
      errorLoadingConcepts: null,
      refreshConcepts: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the loading animation is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  test('renders empty state', () => {
    // Mock the context to return empty state
    vi.mocked(useConceptContext).mockReturnValue({
      recentConcepts: [],
      loadingConcepts: false,
      errorLoadingConcepts: null,
      refreshConcepts: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the empty state message is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByText('No Concepts Available')).toBeInTheDocument();
    expect(screen.getByText('Create New Concept')).toBeInTheDocument();
  });

  test('renders error state', () => {
    // Mock the context to return error state
    vi.mocked(useConceptContext).mockReturnValue({
      recentConcepts: [],
      loadingConcepts: false,
      errorLoadingConcepts: 'Failed to load concepts',
      refreshConcepts: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the error message is shown
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument();
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

    // Mock the context to return concepts
    vi.mocked(useConceptContext).mockReturnValue({
      recentConcepts: mockConcepts,
      loadingConcepts: false,
      errorLoadingConcepts: null,
      refreshConcepts: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Check that the concept cards are rendered
    expect(screen.getByText('Select a Concept to Refine')).toBeInTheDocument();
    expect(screen.getByTestId('concept-card-concept-1')).toBeInTheDocument();
    expect(screen.getByTestId('concept-card-concept-2')).toBeInTheDocument();
  });

  test('navigates to refinement page when selecting a concept', () => {
    // Mock concepts data
    const mockConcepts = [
      {
        id: 'concept-1',
        base_image_url: 'https://example.com/concept1.png',
        logo_description: 'First Test Concept',
        theme_description: 'Test theme 1',
        color_variations: []
      }
    ];

    // Mock the context to return concepts
    vi.mocked(useConceptContext).mockReturnValue({
      recentConcepts: mockConcepts,
      loadingConcepts: false,
      errorLoadingConcepts: null,
      refreshConcepts: vi.fn()
    });

    render(
      <BrowserRouter>
        <RefinementSelectionPage />
      </BrowserRouter>
    );

    // Click on a concept card
    fireEvent.click(screen.getByTestId('concept-card-concept-1'));

    // Check that navigate was called with the correct path
    expect(mockNavigate).toHaveBeenCalledWith('/refine/concept-1');
  });
}); 