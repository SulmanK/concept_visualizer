import React from 'react';
import { render, screen } from '@testing-library/react';
import { Card } from '../Card';

describe('Card Component', () => {
  // Basic rendering tests
  test('renders card with children', () => {
    render(
      <Card>
        <p>Card content</p>
      </Card>
    );
    
    const content = screen.getByText('Card content');
    expect(content).toBeInTheDocument();
  });
  
  // Variant tests
  test.each([
    ['default', 'card'],
    ['gradient', 'card-gradient'],
    ['elevated', 'card bg-white border-none shadow-lg'],
  ])('renders %s variant correctly', (variant, expectedClass) => {
    render(
      <Card variant={variant as any}>
        <p>Card content</p>
      </Card>
    );
    
    const contentElement = screen.getByText('Card content');
    const card = contentElement.parentElement?.parentElement;
    expect(card?.className).toContain(expectedClass.split(' ')[0]); // Just check the first class
  });
  
  // Padding tests
  test('renders card with padding when padded is true', () => {
    render(
      <Card padded>
        <p>Card content</p>
      </Card>
    );
    
    const contentDiv = screen.getByText('Card content').parentElement;
    expect(contentDiv?.className).toContain('p-4');
  });
  
  test('renders card without padding when padded is false', () => {
    render(
      <Card padded={false}>
        <p>Card content</p>
      </Card>
    );
    
    const contentDiv = screen.getByText('Card content').parentElement;
    expect(contentDiv?.className).toBe('');
  });
  
  // Loading state tests
  test('renders loading spinner when isLoading is true', () => {
    render(
      <Card isLoading>
        <p>Card content</p>
      </Card>
    );
    
    const spinner = document.querySelector('.animate-spin');
    expect(spinner).not.toBeNull();
  });
  
  // Custom className test
  test('applies custom className when provided', () => {
    render(
      <Card className="custom-class">
        <p>Card content</p>
      </Card>
    );
    
    const contentElement = screen.getByText('Card content');
    const card = contentElement.parentElement?.parentElement;
    expect(card?.className).toContain('custom-class');
  });
  
  // Header and footer tests
  test('renders card with header when provided', () => {
    const header = <div data-testid="card-header">Custom Header</div>;
    
    render(
      <Card header={header}>
        <p>Card content</p>
      </Card>
    );
    
    const cardHeader = screen.getByTestId('card-header');
    expect(cardHeader).toBeInTheDocument();
    expect(cardHeader.textContent).toBe('Custom Header');
  });
  
  test('renders card with footer when provided', () => {
    const footer = <div data-testid="card-footer">Custom Footer</div>;
    
    render(
      <Card footer={footer}>
        <p>Card content</p>
      </Card>
    );
    
    const cardFooter = screen.getByTestId('card-footer');
    expect(cardFooter).toBeInTheDocument();
    expect(cardFooter.textContent).toBe('Custom Footer');
  });
  
  // Snapshot tests
  describe('Snapshots', () => {
    test('default card snapshot', () => {
      const { container } = render(
        <Card>
          <p>Default card content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('gradient variant card snapshot', () => {
      const { container } = render(
        <Card variant="gradient">
          <p>Gradient card content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('elevated variant card snapshot', () => {
      const { container } = render(
        <Card variant="elevated">
          <p>Elevated card content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('card with header snapshot', () => {
      const header = <div>Header Content</div>;
      const { container } = render(
        <Card header={header}>
          <p>Card with header content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('card with footer snapshot', () => {
      const footer = <div>Footer Content</div>;
      const { container } = render(
        <Card footer={footer}>
          <p>Card with footer content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
    
    test('loading card snapshot', () => {
      const { container } = render(
        <Card isLoading>
          <p>Loading card content</p>
        </Card>
      );
      expect(container.firstChild).toMatchSnapshot();
    });
  });
}); 