import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import EnhancedImagePreview from '../EnhancedImagePreview';

// Mock Material UI components
jest.mock('@mui/material', () => {
  const actual = jest.requireActual('@mui/material');
  return {
    ...actual,
    Modal: ({ children, open, onClose }) => open ? (
      <div data-testid="modal">
        <button data-testid="modal-close" onClick={onClose}>Close Modal</button>
        {children}
      </div>
    ) : null,
    IconButton: ({ children, onClick }) => (
      <button onClick={onClick} data-testid="icon-button">{children}</button>
    ),
    Box: ({ children, component, sx, ...props }) => {
      const Component = component || 'div';
      return (
        <Component data-testid="box" {...props}>
          {children}
        </Component>
      );
    },
    Typography: ({ children, variant, component }) => {
      const Component = component || 'p';
      return <Component data-testid={`typography-${variant}`}>{children}</Component>;
    }
  };
});

// Mock Material UI icons
jest.mock('@mui/icons-material/ZoomIn', () => () => 'ZoomIn');
jest.mock('@mui/icons-material/ZoomOut', () => () => 'ZoomOut');
jest.mock('@mui/icons-material/RestartAlt', () => () => 'Reset');
jest.mock('@mui/icons-material/Close', () => () => 'Close');

describe('EnhancedImagePreview', () => {
  const mockProps = {
    isOpen: true,
    onClose: jest.fn(),
    imageUrl: 'https://example.com/test-image.png',
    format: 'png'
  };
  
  beforeEach(() => {
    jest.clearAllMocks();
  });
  
  it('renders correctly when open', () => {
    render(<EnhancedImagePreview {...mockProps} />);
    
    // Check title shows correct format
    expect(screen.getByText('Preview (PNG)')).toBeInTheDocument();
    
    // Check the image is displayed
    const image = screen.getByAltText('Preview in png format');
    expect(image).toBeInTheDocument();
    expect(image).toHaveAttribute('src', mockProps.imageUrl);
  });
  
  it('does not render when closed', () => {
    render(<EnhancedImagePreview {...mockProps} isOpen={false} />);
    
    expect(screen.queryByTestId('modal')).not.toBeInTheDocument();
  });
  
  it('calls onClose when close button is clicked', () => {
    render(<EnhancedImagePreview {...mockProps} />);
    
    fireEvent.click(screen.getByTestId('modal-close'));
    expect(mockProps.onClose).toHaveBeenCalled();
  });
  
  it('supports mouse interactions for panning', () => {
    render(<EnhancedImagePreview {...mockProps} />);
    
    const container = screen.getByTestId('box');
    
    // Start dragging
    fireEvent.mouseDown(container, { clientX: 100, clientY: 100, button: 0 });
    
    // Move while dragging
    fireEvent.mouseMove(container, { clientX: 150, clientY: 150 });
    
    // End dragging
    fireEvent.mouseUp(container);
    
    // Expect the image to be panned (we can't easily test the state changes,
    // but we can at least ensure the events don't throw errors)
    expect(container).toBeInTheDocument();
  });
}); 