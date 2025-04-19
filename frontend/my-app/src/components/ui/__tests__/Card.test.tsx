import React from 'react';
import { render, screen } from '../../../test-utils';
import { Card } from '../Card';

describe('Card Component', () => {
  // Basic rendering tests
  test('renders children inside card', () => {
    render(
      <Card>
        <p data-testid="card-content">Card Content</p>
      </Card>
    );
    
    expect(screen.getByTestId('card-content')).toBeInTheDocument();
  });
  
  test('applies default classes', () => {
    const { container } = render(<Card>Default Card</Card>);
    const cardElement = container.firstChild as HTMLElement;
    
    expect(cardElement.className).toContain('bg-white');
    expect(cardElement.className).toContain('rounded-lg');
    expect(cardElement.className).toContain('shadow-modern');
  });
  
  // Props tests
  test('applies custom className when provided', () => {
    const { container } = render(
      <Card className="custom-class">Card with custom class</Card>
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement.className).toContain('custom-class');
  });
  
  test('has hover effect with shadow by default', () => {
    const { container } = render(
      <Card>Card with hover effect</Card>
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement.className).toContain('hover:shadow-lg');
  });
  
  test('applies border by default', () => {
    const { container } = render(
      <Card>Bordered Card</Card>
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement.className).toContain('border');
    expect(cardElement.className).toContain('border-indigo-100');
  });
  
  test('includes transition for animations', () => {
    const { container } = render(
      <Card>Card with transition</Card>
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement.className).toContain('transition-all');
    expect(cardElement.className).toContain('duration-300');
  });
  
  test('has hover translate effect', () => {
    const { container } = render(
      <Card>Card with hover translate</Card>
    );
    
    const cardElement = container.firstChild as HTMLElement;
    expect(cardElement.className).toContain('hover:translate-y-[-4px]');
  });
}); 