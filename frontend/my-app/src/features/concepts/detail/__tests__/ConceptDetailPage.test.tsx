import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import { ConceptDetailPage } from '../ConceptDetailPage';
import { vi } from 'vitest';
import * as supabaseClient from '../../../../services/supabaseClient';

// Mock the necessary imports
vi.mock('../../../../services/supabaseClient', async () => ({
  fetchConceptDetail: vi.fn()
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

describe('ConceptDetailPage Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  // Mock sample concept data
  const mockConcept = {
    id: 'test-123',
    base_image_url: 'https://example.com/base-image.png',
    logo_description: 'Test Logo Description',
    theme_description: 'Test Theme Description',
    color_variations: [
      {
        id: 'var-1',
        image_url: 'https://example.com/variation-1.png',
        palette_name: 'Cool Blues',
        colors: ['#4F46E5', '#818CF8', '#C4B5FD', '#F5F3FF', '#1E1B4B'],
        description: 'A cool blue palette'
      },
      {
        id: 'var-2',
        image_url: 'https://example.com/variation-2.png',
        palette_name: 'Vibrant Purples',
        colors: ['#7E22CE', '#A855F7', '#D8B4FE', '#FAF5FF', '#4C1D95'],
        description: 'A vibrant purple palette'
      }
    ]
  };

  test('renders loading state initially', () => {
    // Mock the fetch to never resolve yet
    vi.mocked(supabaseClient.fetchConceptDetail).mockImplementation(() => 
      new Promise(() => {})
    );

    render(
      <MemoryRouter initialEntries={['/concepts/test-123']}>
        <Routes>
          <Route path="/concepts/:conceptId" element={<ConceptDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Should show loading skeleton
    expect(screen.getByTestId('loading-skeleton')).toBeInTheDocument();
  });

  test('renders concept details when loaded', async () => {
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);

    render(
      <MemoryRouter initialEntries={['/concepts/test-123']}>
        <Routes>
          <Route path="/concepts/:conceptId" element={<ConceptDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the content to load
    await waitFor(() => {
      expect(screen.getByText('Concept')).toBeInTheDocument();
    });

    // Check that the logo description is displayed
    expect(screen.getByText(mockConcept.logo_description)).toBeInTheDocument();
    
    // Check that the theme description is displayed
    expect(screen.getByText(mockConcept.theme_description)).toBeInTheDocument();
    
    // Check that the first variation palette name is displayed
    expect(screen.getByText(mockConcept.color_variations[0].palette_name)).toBeInTheDocument();
  });

  test('displays error message when concept not found', async () => {
    // Mock the fetch to return null (concept not found)
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(null);

    render(
      <MemoryRouter initialEntries={['/concepts/not-found']}>
        <Routes>
          <Route path="/concepts/:conceptId" element={<ConceptDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the error message to appear
    await waitFor(() => {
      expect(screen.getByText('Error')).toBeInTheDocument();
    });

    expect(screen.getByText('Concept not found')).toBeInTheDocument();
    expect(screen.getByText('Back to Home')).toBeInTheDocument();
  });

  test('navigates to refinement page when clicking refine', async () => {
    // Mock the fetch to return our test concept
    vi.mocked(supabaseClient.fetchConceptDetail).mockResolvedValue(mockConcept);

    render(
      <MemoryRouter initialEntries={['/concepts/test-123']}>
        <Routes>
          <Route path="/concepts/:conceptId" element={<ConceptDetailPage />} />
        </Routes>
      </MemoryRouter>
    );

    // Wait for the refine button to appear
    await waitFor(() => {
      expect(screen.getByText('Refine This Concept')).toBeInTheDocument();
    });

    // Click the refine button
    screen.getByText('Refine This Concept').click();

    // Check that navigate was called with the correct path
    expect(mockNavigate).toHaveBeenCalledWith('/refine/test-123');
  });
}); 