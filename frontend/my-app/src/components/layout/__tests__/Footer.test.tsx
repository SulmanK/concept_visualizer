import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Footer } from '../Footer';

// Helper function to render with router
const renderWithRouter = (ui: React.ReactElement) => {
  return render(
    <MemoryRouter>
      {ui}
    </MemoryRouter>
  );
};

describe('Footer Component', () => {
  // Basic rendering tests
  test('renders footer with logo and title', () => {
    renderWithRouter(<Footer />);
    
    // Check for logo text
    const logo = screen.getByText('CV');
    expect(logo).toBeInTheDocument();
    
    // Check for title
    const title = screen.getByText('Concept Visualizer');
    expect(title).toBeInTheDocument();
  });
  
  test('renders tagline', () => {
    renderWithRouter(<Footer />);
    
    const tagline = screen.getByText('Create and refine visual concepts with AI');
    expect(tagline).toBeInTheDocument();
  });
  
  // Features section tests
  test('renders features section with links', () => {
    renderWithRouter(<Footer />);
    
    // Check for section title
    const featuresHeading = screen.getByText('Features');
    expect(featuresHeading).toBeInTheDocument();
    
    // Check for feature links
    const createLink = screen.getByText('Create Concepts');
    const refineLink = screen.getByText('Refine Concepts');
    
    expect(createLink).toBeInTheDocument();
    expect(refineLink).toBeInTheDocument();
  });
  
  // Resources section tests
  test('renders resources section with links', () => {
    renderWithRouter(<Footer />);
    
    // Check for section title
    const resourcesHeading = screen.getByText('Resources');
    expect(resourcesHeading).toBeInTheDocument();
    
    // Check for resource links
    const githubLink = screen.getByText('GitHub Repository');
    const jigsawStackLink = screen.getByText('JigsawStack API');
    
    expect(githubLink).toBeInTheDocument();
    expect(jigsawStackLink).toBeInTheDocument();
  });
  
  // Copyright test
  test('renders copyright with current year', () => {
    // Mock current year
    const currentYear = new Date().getFullYear();
    renderWithRouter(<Footer />);
    
    const copyright = screen.getByText(`© ${currentYear} Concept Visualizer. All rights reserved.`);
    expect(copyright).toBeInTheDocument();
  });
  
  test('renders copyright with custom year', () => {
    renderWithRouter(<Footer year={2025} />);
    
    const copyright = screen.getByText('© 2025 Concept Visualizer. All rights reserved.');
    expect(copyright).toBeInTheDocument();
  });
  
  // Snapshot tests
  describe('Snapshots', () => {
    test('default footer snapshot', () => {
      const { container } = renderWithRouter(<Footer />);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('footer with custom year snapshot', () => {
      const { container } = renderWithRouter(<Footer year={2025} />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });
}); 