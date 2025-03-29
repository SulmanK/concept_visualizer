import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Home } from '../Home';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock useConceptGeneration hook
jest.mock('../../hooks/useConceptGeneration', () => ({
  useConceptGeneration: () => ({
    generateConcept: jest.fn(),
    resetGeneration: jest.fn(),
    status: 'idle',
    error: null,
  }),
}));

describe('Home Component', () => {
  test('renders home page with all sections', () => {
    render(
      <MemoryRouter>
        <Home />
      </MemoryRouter>
    );
    
    // Check for main heading
    expect(screen.getByText('Create Visual Concepts')).toBeInTheDocument();
    
    // Check for form section
    expect(screen.getByText('Create New Concept')).toBeInTheDocument();
    expect(screen.getByText('Logo Description')).toBeInTheDocument();
    expect(screen.getByText('Theme/Color Scheme Description')).toBeInTheDocument();
    expect(screen.getByText('Generate Concept')).toBeInTheDocument();
    
    // Check for recent concepts section
    expect(screen.getByText('Recent Concepts')).toBeInTheDocument();
    expect(screen.getByText('Tech Company')).toBeInTheDocument();
    expect(screen.getByText('Fashion Studio')).toBeInTheDocument();
    expect(screen.getByText('Eco Product')).toBeInTheDocument();
    
    // Check for How It Works section
    expect(screen.getByText('How It Works')).toBeInTheDocument();
    expect(screen.getByText('Describe Your Vision')).toBeInTheDocument();
    expect(screen.getByText('AI Generation')).toBeInTheDocument();
    expect(screen.getByText('Refine & Download')).toBeInTheDocument();
  });
}); 