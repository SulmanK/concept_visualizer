import React from 'react';
import { render, screen } from '@testing-library/react';
import { HomePage } from '../HomePage';
import { MemoryRouter } from 'react-router-dom';
import { ConceptProvider } from '../../../contexts/ConceptContext';

// Mock the hooks used in HomePage
jest.mock('../../../hooks/useConceptGeneration', () => ({
  useConceptGeneration: () => ({
    generateConcept: jest.fn(),
    resetGeneration: jest.fn(),
    status: 'idle',
    error: null
  })
}));

// Mock any child components as needed
jest.mock('../components/HeroSection', () => ({
  HeroSection: () => <div data-testid="hero-section">Hero Section</div>
}));

jest.mock('../components/ConceptFormSection', () => ({
  ConceptFormSection: () => <div data-testid="concept-form-section">Concept Form</div>
}));

jest.mock('../components/RecentConceptsSection', () => ({
  RecentConceptsSection: (props: any) => (
    <div data-testid="recent-concepts-section">
      Recent Concepts ({props.concepts.length} items)
    </div>
  )
}));

jest.mock('../../../components/ui/FeatureSteps', () => ({
  FeatureSteps: () => <div data-testid="feature-steps">Feature Steps</div>
}));

describe('HomePage', () => {
  const renderHomePage = () => {
    return render(
      <MemoryRouter>
        <ConceptProvider>
          <HomePage />
        </ConceptProvider>
      </MemoryRouter>
    );
  };

  test('renders all main sections', () => {
    renderHomePage();
    
    expect(screen.getByTestId('hero-section')).toBeInTheDocument();
    expect(screen.getByTestId('concept-form-section')).toBeInTheDocument();
    expect(screen.getByTestId('recent-concepts-section')).toBeInTheDocument();
    expect(screen.getByTestId('feature-steps')).toBeInTheDocument();
  });

  test('includes text about recent concepts', () => {
    renderHomePage();
    expect(screen.getByText(/Recent Concepts \(\d+ items\)/)).toBeInTheDocument();
  });
}); 