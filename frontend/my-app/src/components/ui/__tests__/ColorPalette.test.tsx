import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ColorPalette } from '../ColorPalette';
import { ColorPaletteModel } from '../../../types';

describe('ColorPalette Component', () => {
  // Sample color palette data for testing
  const samplePalette: ColorPaletteModel = {
    name: 'Purple Dream',
    colors: [
      { hex: '#4C1D95', name: 'Deep Purple' },
      { hex: '#7C3AED', name: 'Violet' },
      { hex: '#A78BFA', name: 'Lavender' },
      { hex: '#C4B5FD', name: 'Light Lavender' },
      { hex: '#EDE9FE', name: 'Pale Lavender' },
    ],
    description: 'A gradient of purple shades from deep to pale',
  };

  // Basic rendering tests
  test('renders palette with correct title', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    const title = screen.getByText('Purple Dream');
    expect(title).toBeInTheDocument();
  });
  
  test('renders all color swatches', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    // Check if all colors are rendered
    const deepPurple = screen.getByText('Deep Purple');
    const violet = screen.getByText('Violet');
    const lavender = screen.getByText('Lavender');
    const lightLavender = screen.getByText('Light Lavender');
    const paleLavender = screen.getByText('Pale Lavender');
    
    expect(deepPurple).toBeInTheDocument();
    expect(violet).toBeInTheDocument();
    expect(lavender).toBeInTheDocument();
    expect(lightLavender).toBeInTheDocument();
    expect(paleLavender).toBeInTheDocument();
  });
  
  test('renders palette description when provided', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    const description = screen.getByText('A gradient of purple shades from deep to pale');
    expect(description).toBeInTheDocument();
  });
  
  // Selection tests
  test('calls onSelect when a color is clicked', () => {
    const handleSelect = jest.fn();
    render(<ColorPalette palette={samplePalette} onSelect={handleSelect} />);
    
    const deepPurpleColor = screen.getByText('Deep Purple').closest('div');
    fireEvent.click(deepPurpleColor!);
    
    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith(samplePalette.colors[0]);
  });
  
  test('highlights selected color when selectedColor matches', () => {
    render(
      <ColorPalette 
        palette={samplePalette} 
        selectedColor={samplePalette.colors[1].hex} 
      />
    );
    
    // Find the violet color swatch
    const violetColorSwatch = screen.getByText('Violet').closest('div');
    
    // Check if it has a selection indicator
    expect(violetColorSwatch?.className).toContain('ring-2');
    expect(violetColorSwatch?.className).toContain('ring-violet-600');
  });
  
  // Interactive behavior tests
  test('shows color hex on hover', async () => {
    render(<ColorPalette palette={samplePalette} />);
    
    // Find the deep purple color swatch
    const deepPurpleColor = screen.getByText('Deep Purple').closest('div');
    
    // Hover over the color swatch
    fireEvent.mouseEnter(deepPurpleColor!);
    
    // Check if the hex value is displayed
    const hexValue = await screen.findByText('#4C1D95');
    expect(hexValue).toBeInTheDocument();
    
    // Move mouse away
    fireEvent.mouseLeave(deepPurpleColor!);
    
    // Check that hex is no longer shown
    expect(screen.queryByText('#4C1D95')).not.toBeInTheDocument();
  });
  
  // Size tests
  test.each([
    ['small', 'h-8'],
    ['medium', 'h-12'],
    ['large', 'h-16'],
  ])('renders %s size correctly', (size, expectedClass) => {
    render(<ColorPalette palette={samplePalette} size={size as any} />);
    
    // Check any color swatch for the expected size class
    const colorSwatch = screen.getByText('Deep Purple').closest('div');
    expect(colorSwatch?.className).toContain(expectedClass);
  });
  
  // Variant tests
  test('renders horizontal variant by default', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    const paletteContainer = screen.getByText('Purple Dream').closest('div')?.nextElementSibling;
    expect(paletteContainer?.className).toContain('flex-row');
  });
  
  test('renders vertical variant when specified', () => {
    render(<ColorPalette palette={samplePalette} variant="vertical" />);
    
    const paletteContainer = screen.getByText('Purple Dream').closest('div')?.nextElementSibling;
    expect(paletteContainer?.className).toContain('flex-col');
  });
  
  // Empty state test
  test('renders placeholder message when palette has no colors', () => {
    const emptyPalette = {
      name: 'Empty Palette',
      colors: [],
      description: 'No colors defined',
    };
    
    render(<ColorPalette palette={emptyPalette} />);
    
    const emptyMessage = screen.getByText('No colors available');
    expect(emptyMessage).toBeInTheDocument();
  });
  
  // Interactive component test
  test('renders as interactive when onSelect is provided', () => {
    const handleSelect = jest.fn();
    render(<ColorPalette palette={samplePalette} onSelect={handleSelect} />);
    
    const colorSwatches = screen.getAllByRole('button');
    expect(colorSwatches.length).toBe(samplePalette.colors.length);
  });
  
  test('renders as non-interactive when onSelect is not provided', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    const colorSwatches = screen.queryAllByRole('button');
    expect(colorSwatches.length).toBe(0);
  });
}); 