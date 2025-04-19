import React from 'react';
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { SkeletonLoader } from '../SkeletonLoader';

describe('SkeletonLoader', () => {
  it('renders text skeleton by default', () => {
    render(<SkeletonLoader />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton).toBeInTheDocument();
    expect(skeleton.classList.contains('rounded')).toBe(true);
    expect(skeleton.classList.contains('animate-pulse')).toBe(true);
  });
  
  it('renders multiple lines for text skeleton when lines > 1', () => {
    const lines = 3;
    render(<SkeletonLoader type="text" lines={lines} />);
    
    const skeleton = screen.getByRole('status');
    const skeletonLines = skeleton.querySelectorAll('div');
    expect(skeletonLines.length).toBe(lines);
    
    // Last line should have 75% width if not explicitly set
    const lastLine = skeletonLines[lines - 1];
    expect(lastLine.style.width).toBe('75%');
  });
  
  it('applies correct height for different lineHeight props', () => {
    // Test for lg lineHeight
    const { rerender } = render(<SkeletonLoader type="text" lineHeight="lg" />);
    
    let skeleton = screen.getByRole('status');
    // Check if the class contains h-6 directly
    expect(skeleton.classList.contains('h-6')).toBe(true);
    
    // Test for md lineHeight
    rerender(<SkeletonLoader type="text" lineHeight="md" />);
    skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains('h-4')).toBe(true);
    
    // Test for sm lineHeight
    rerender(<SkeletonLoader type="text" lineHeight="sm" />);
    skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains('h-3')).toBe(true);
  });
  
  it('renders circle skeleton with correct default classes', () => {
    render(<SkeletonLoader type="circle" />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains('rounded-full')).toBe(true);
    
    // Check default dimensions applied correctly
    expect(skeleton.style.width).toBe('48px');
    expect(skeleton.style.height).toBe('48px');
  });
  
  it('renders rectangle skeleton with correct default classes', () => {
    render(<SkeletonLoader type="rectangle" />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains('rounded-md')).toBe(true);
    expect(skeleton.style.height).toBe('100px');
  });
  
  it('renders special card skeleton with appropriate content', () => {
    render(<SkeletonLoader type="card" />);
    
    const skeleton = screen.getByRole('status', { name: /loading card/i });
    
    // Card should be structured correctly
    expect(skeleton).toBeInTheDocument();
    
    // Card should have at least some divs for sections
    const divs = skeleton.querySelectorAll('div');
    expect(divs.length).toBeGreaterThan(0);
    
    // Verify it has the card class
    expect(skeleton.classList.contains('rounded-lg') || 
           skeleton.querySelector('.rounded-lg')).toBeTruthy();
  });
  
  it('renders button skeleton with correct default dimensions', () => {
    render(<SkeletonLoader type="button" />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.style.width).toBe('120px');
    expect(skeleton.style.height).toBe('40px');
    expect(skeleton.classList.contains('rounded-md')).toBe(true);
  });
  
  it('applies custom width and height', () => {
    const customWidth = '200px';
    const customHeight = '150px';
    
    render(
      <SkeletonLoader 
        type="rectangle" 
        width={customWidth} 
        height={customHeight} 
      />
    );
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.style.width).toBe(customWidth);
    expect(skeleton.style.height).toBe(customHeight);
  });
  
  it('applies custom border radius', () => {
    const customBorderRadius = 'rounded-none';
    
    render(<SkeletonLoader borderRadius={customBorderRadius} />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains(customBorderRadius)).toBe(true);
    expect(skeleton.classList.contains('rounded')).toBe(false);
  });
  
  it('applies custom className', () => {
    const customClass = 'custom-skeleton-class';
    
    render(<SkeletonLoader className={customClass} />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.classList.contains(customClass)).toBe(true);
  });
  
  it('applies custom style', () => {
    const customStyle = { opacity: 0.7, margin: '10px' };
    
    render(<SkeletonLoader style={customStyle} />);
    
    const skeleton = screen.getByRole('status');
    expect(skeleton.style.opacity).toBe('0.7');
    expect(skeleton.style.margin).toBe('10px');
  });
}); 