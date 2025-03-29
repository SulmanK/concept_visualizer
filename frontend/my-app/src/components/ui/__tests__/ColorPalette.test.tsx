import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ColorPalette } from '../ColorPalette';
import { ColorPalette as ColorPaletteType } from '../../../types';

describe('ColorPalette Component', () => {
  // Sample color palette data for testing
  const samplePalette: ColorPaletteType = {
    primary: '#4C1D95',
    secondary: '#7C3AED',
    accent: '#A78BFA',
    background: '#EDE9FE',
    text: '#1F1F1F',
    additionalColors: ['#C4B5FD', '#DDD6FE']
  };

  // Basic rendering tests
  test('renders all main color swatches', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    // Check if all color labels are rendered
    expect(screen.getByText('Primary')).toBeInTheDocument();
    expect(screen.getByText('Secondary')).toBeInTheDocument();
    expect(screen.getByText('Accent')).toBeInTheDocument();
    expect(screen.getByText('Background')).toBeInTheDocument();
    expect(screen.getByText('Text')).toBeInTheDocument();
    
    // Check if correct number of color swatches are present (5 main + 2 additional)
    const colorSwatches = document.querySelectorAll('[style*="background-color"]');
    expect(colorSwatches.length).toBe(7);
  });
  
  test('renders additional colors when provided', () => {
    render(<ColorPalette palette={samplePalette} />);
    
    // Check if additional colors section is rendered
    expect(screen.getByText('Additional Colors')).toBeInTheDocument();
    expect(screen.getByText('A1')).toBeInTheDocument();
    expect(screen.getByText('A2')).toBeInTheDocument();
  });
  
  // Selection tests
  test('calls onColorSelect when a color is clicked and selectable is true', () => {
    const handleSelect = jest.fn();
    render(
      <ColorPalette 
        palette={samplePalette} 
        onColorSelect={handleSelect} 
        selectable={true}
      />
    );
    
    // Find the primary color swatch and click it
    const primarySwatch = screen.getByText('Primary').previousElementSibling;
    fireEvent.click(primarySwatch!);
    
    expect(handleSelect).toHaveBeenCalledTimes(1);
    expect(handleSelect).toHaveBeenCalledWith('#4C1D95', 'primary');
  });
  
  test('does not call onColorSelect when selectable is false', () => {
    const handleSelect = jest.fn();
    render(
      <ColorPalette 
        palette={samplePalette} 
        onColorSelect={handleSelect} 
        selectable={false}
      />
    );
    
    // Find the primary color swatch and click it
    const primarySwatch = screen.getByText('Primary').previousElementSibling;
    fireEvent.click(primarySwatch!);
    
    expect(handleSelect).not.toHaveBeenCalled();
  });
  
  test('highlights selected color when selectedColor matches', () => {
    render(
      <ColorPalette 
        palette={samplePalette} 
        selectedColor={samplePalette.secondary}
        selectable={true}
      />
    );
    
    // Find the secondary color swatch (which should have the ring styling)
    const swatches = document.querySelectorAll('[style*="background-color"]');
    const secondarySwatch = swatches[1]; // Secondary is the second swatch
    
    // Check if it has a selection indicator
    expect(secondarySwatch.className).toContain('ring-2');
  });
  
  // Size tests
  test.each([
    ['sm', 'h-6'],
    ['md', 'h-8'],
    ['lg', 'h-12'],
  ])('renders %s size correctly', (size, expectedClass) => {
    render(<ColorPalette palette={samplePalette} size={size as any} />);
    
    // Check any color swatch for the expected size class
    const swatch = document.querySelector('[style*="background-color"]');
    expect(swatch?.className).toContain(expectedClass);
  });
  
  // Label visibility test
  test('shows labels when showLabels is true', () => {
    render(<ColorPalette palette={samplePalette} showLabels={true} />);
    
    expect(screen.getByText('Primary')).toBeInTheDocument();
    expect(screen.getByText('Secondary')).toBeInTheDocument();
  });
  
  test('hides labels when showLabels is false', () => {
    render(<ColorPalette palette={samplePalette} showLabels={false} />);
    
    expect(screen.queryByText('Primary')).not.toBeInTheDocument();
    expect(screen.queryByText('Secondary')).not.toBeInTheDocument();
  });
  
  // Interactive component test
  test('renders as interactive when selectable is true', () => {
    render(
      <ColorPalette
        palette={samplePalette}
        selectable={true}
        onColorSelect={() => {}}
      />
    );
    
    const swatch = document.querySelector('[style*="background-color"]');
    expect(swatch?.className).toContain('cursor-pointer');
  });
  
  test('renders as non-interactive when selectable is false', () => {
    render(<ColorPalette palette={samplePalette} selectable={false} />);
    
    const swatch = document.querySelector('[style*="background-color"]');
    expect(swatch?.className).not.toContain('cursor-pointer');
  });
}); 