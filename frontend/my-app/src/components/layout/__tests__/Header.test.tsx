import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from '../Header';

// Helper function to render with router
const renderWithRouter = (ui: React.ReactElement, { route = '/' } = {}) => {
  return render(
    <MemoryRouter initialEntries={[route]}>
      {ui}
    </MemoryRouter>
  );
};

describe('Header Component', () => {
  // Basic rendering tests
  test('renders header with logo and title', () => {
    renderWithRouter(<Header />);
    
    // Check for logo text (there are multiple elements with 'CV')
    const logoElements = screen.getAllByText('CV');
    expect(logoElements.length).toBeGreaterThan(0);
    
    // Check for title
    const title = screen.getByText('Concept Visualizer');
    expect(title).toBeInTheDocument();
  });
  
  // Navigation tests
  test('renders navigation links', () => {
    renderWithRouter(<Header />);
    
    // Check for navigation links
    const createLink = screen.getByText(/Create/i);
    const refineLink = screen.getByText(/Refine/i);
    
    expect(createLink).toBeInTheDocument();
    expect(refineLink).toBeInTheDocument();
  });
  
  // Active route tests
  test('highlights Create link when on create route', () => {
    renderWithRouter(<Header activeRoute="/create" />);
    
    const createLink = screen.getByText(/Create/i).closest('a');
    const refineLink = screen.getByText(/Refine/i).closest('a');
    
    // Testing active/inactive CSS classes
    expect(createLink).toHaveAttribute('href', '/create');
    expect(refineLink).toHaveAttribute('href', '/refine');
    
    // Test CSS classes with actual class names from implementation
    expect(createLink).toHaveClass('nav-link-active');
    expect(refineLink).toHaveClass('nav-link-inactive');
  });
  
  test('highlights Refine link when on refine route', () => {
    renderWithRouter(<Header activeRoute="/refine" />);
    
    const createLink = screen.getByText(/Create/i).closest('a');
    const refineLink = screen.getByText(/Refine/i).closest('a');
    
    // Check that correct link is highlighted via CSS classes
    expect(refineLink).toHaveClass('nav-link-active');
    expect(createLink).toHaveClass('nav-link-inactive');
  });
  
  // Home route test
  test('treats root route as create route', () => {
    renderWithRouter(<Header activeRoute="/" />);
    
    const createLink = screen.getByText(/Create/i).closest('a');
    
    // Check that Create is highlighted on home route
    expect(createLink).toHaveClass('nav-link-active');
  });
  
  // Update snapshot tests to use inline snapshots
  describe('Snapshots', () => {
    test('default header structure', () => {
      const { container } = renderWithRouter(<Header />);
      
      // Test specific elements instead of full snapshot
      const header = container.firstChild as HTMLElement;
      const navigation = header.querySelector('nav');
      const links = navigation?.querySelectorAll('a');
      
      // Check header has proper classes
      expect(header).toHaveClass('sticky', 'top-0', 'w-full');
      
      // Check we have the expected navigation links
      expect(links?.length).toBe(3);
      
      // First link should be active (Create)
      expect(links?.[0]).toHaveClass('nav-link-active');
    });
    
    test('header with create route active', () => {
      const { container } = renderWithRouter(<Header activeRoute="/create" />);
      
      // Get all navigation links
      const navigation = container.querySelector('nav');
      const links = navigation?.querySelectorAll('a');
      
      // Check Create link is active
      expect(links?.[0]).toHaveClass('nav-link-active');
      expect(links?.[2]).toHaveClass('nav-link-inactive');
    });
    
    test('header with refine route active', () => {
      const { container } = renderWithRouter(<Header activeRoute="/refine" />);
      
      // Get all navigation links
      const navigation = container.querySelector('nav');
      const links = navigation?.querySelectorAll('a');
      
      // Check Refine link is active
      expect(links?.[0]).toHaveClass('nav-link-inactive');
      expect(links?.[2]).toHaveClass('nav-link-active');
    });
  });
}); 