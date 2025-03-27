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
  
  test('renders card with title when provided', () => {
    render(
      <Card title="Card Title">
        <p>Card content</p>
      </Card>
    );
    
    const title = screen.getByText('Card Title');
    expect(title).toBeInTheDocument();
    expect(title.tagName).toBe('H3');
  });
  
  // Variant tests
  test.each([
    ['primary', 'bg-violet-50'],
    ['secondary', 'bg-white'],
    ['accent', 'bg-violet-100'],
  ])('renders %s variant correctly', (variant, expectedClass) => {
    render(
      <Card variant={variant as any}>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).toContain(expectedClass);
  });
  
  // Border tests
  test('renders card with border when hasBorder is true', () => {
    render(
      <Card hasBorder>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).toContain('border');
  });
  
  test('renders card without border when hasBorder is false', () => {
    render(
      <Card hasBorder={false}>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).not.toContain('border');
  });
  
  // Shadow tests
  test('renders card with shadow when hasShadow is true', () => {
    render(
      <Card hasShadow>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).toContain('shadow');
  });
  
  test('renders card without shadow when hasShadow is false', () => {
    render(
      <Card hasShadow={false}>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).not.toContain('shadow');
  });
  
  // Padding tests
  test.each([
    ['none', 'p-0'],
    ['small', 'p-3'],
    ['medium', 'p-4'],
    ['large', 'p-6'],
  ])('renders card with %s padding correctly', (padding, expectedClass) => {
    render(
      <Card padding={padding as any}>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).toContain(expectedClass);
  });
  
  // Width tests
  test('renders card with full width when fullWidth is true', () => {
    render(
      <Card fullWidth>
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
    expect(card?.className).toContain('w-full');
  });
  
  // Custom className test
  test('applies custom className when provided', () => {
    render(
      <Card className="custom-class">
        <p>Card content</p>
      </Card>
    );
    
    const card = screen.getByText('Card content').closest('div');
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
}); 