import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import App from '../index';

describe('App component', () => {
  it('renders without crashing', () => {
    render(<App />);
    // This is a basic test to ensure the component renders
    expect(document.body).toBeDefined();
  });
}); 