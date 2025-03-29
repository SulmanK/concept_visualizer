import React from 'react';
import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { Header } from '../Header';
import styles from '../header.module.css';

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
    
    // Check for logo text
    const logo = screen.getByText('CV');
    expect(logo).toBeInTheDocument();
    
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
    
    // Test CSS classes instead of inline styles
    expect(createLink).toHaveClass(styles.activeNavLink);
    expect(refineLink).toHaveClass(styles.inactiveNavLink);
  });
  
  test('highlights Refine link when on refine route', () => {
    renderWithRouter(<Header activeRoute="/refine" />);
    
    const createLink = screen.getByText(/Create/i).closest('a');
    const refineLink = screen.getByText(/Refine/i).closest('a');
    
    // Check that correct link is highlighted via CSS classes
    expect(refineLink).toHaveClass(styles.activeNavLink);
    expect(createLink).toHaveClass(styles.inactiveNavLink);
  });
  
  // Home route test
  test('treats root route as create route', () => {
    renderWithRouter(<Header activeRoute="/" />);
    
    const createLink = screen.getByText(/Create/i).closest('a');
    
    // Check that Create is highlighted on home route
    expect(createLink).toHaveClass(styles.activeNavLink);
  });
  
  // Snapshot tests
  describe('Snapshots', () => {
    test('default header snapshot', () => {
      const { container } = renderWithRouter(<Header />);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('header with create route active snapshot', () => {
      const { container } = renderWithRouter(<Header activeRoute="/create" />);
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('header with refine route active snapshot', () => {
      const { container } = renderWithRouter(<Header activeRoute="/refine" />);
      expect(container.firstChild).toMatchSnapshot();
    });
  });
}); 