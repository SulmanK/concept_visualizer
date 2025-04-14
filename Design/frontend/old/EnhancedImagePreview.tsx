import React, { useState, useRef, MouseEvent, WheelEvent } from 'react';
import { Modal, IconButton, Box, Typography } from '@mui/material';
import ZoomInIcon from '@mui/icons-material/ZoomIn';
import ZoomOutIcon from '@mui/icons-material/ZoomOut';
import RestartAltIcon from '@mui/icons-material/RestartAlt';
import CloseIcon from '@mui/icons-material/Close';

interface EnhancedImagePreviewProps {
  isOpen: boolean;
  onClose: () => void;
  imageUrl: string;
  format: string;
}

/**
 * Enhanced Image Preview component with zoom and pan functionality
 */
const EnhancedImagePreview: React.FC<EnhancedImagePreviewProps> = ({
  isOpen,
  onClose,
  imageUrl,
  format
}) => {
  // State for zoom and pan
  const [scale, setScale] = useState(1);
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  
  // Reference to container for bounds checking
  const containerRef = useRef<HTMLDivElement>(null);
  
  // Handle zooming in
  const handleZoomIn = () => {
    setScale((prevScale) => Math.min(5, prevScale + 0.5));
  };
  
  // Handle zooming out
  const handleZoomOut = () => {
    setScale((prevScale) => Math.max(0.5, prevScale - 0.5));
  };
  
  // Handle resetting zoom and position
  const handleReset = () => {
    setScale(1);
    setPosition({ x: 0, y: 0 });
  };
  
  // Handle mouse wheel for zooming
  const handleWheel = (e: WheelEvent<HTMLDivElement>) => {
    e.preventDefault();
    if (e.deltaY < 0) {
      setScale((prevScale) => Math.min(5, prevScale + 0.1));
    } else {
      setScale((prevScale) => Math.max(0.5, prevScale - 0.1));
    }
  };
  
  // Handle starting drag operation
  const handleMouseDown = (e: MouseEvent<HTMLDivElement>) => {
    if (e.button !== 0) return; // Only left mouse button
    setIsDragging(true);
    setDragStart({ x: e.clientX, y: e.clientY });
  };
  
  // Handle drag movement
  const handleMouseMove = (e: MouseEvent<HTMLDivElement>) => {
    if (!isDragging) return;
    
    const deltaX = e.clientX - dragStart.x;
    const deltaY = e.clientY - dragStart.y;
    
    setPosition((prev) => ({
      x: prev.x + deltaX,
      y: prev.y + deltaY
    }));
    
    setDragStart({ x: e.clientX, y: e.clientY });
  };
  
  // Handle ending drag operation
  const handleMouseUp = () => {
    setIsDragging(false);
  };
  
  // Handle closing modal (reset zoom/position state)
  const handleClose = () => {
    onClose();
    setTimeout(() => {
      // Reset state after animation completes
      setScale(1);
      setPosition({ x: 0, y: 0 });
    }, 300);
  };
  
  return (
    <Modal
      open={isOpen}
      onClose={handleClose}
      aria-labelledby="image-preview-modal"
      aria-describedby="modal-for-previewing-image"
      closeAfterTransition
    >
      <Box sx={{
        position: 'absolute',
        top: '50%',
        left: '50%',
        transform: 'translate(-50%, -50%)',
        width: '90%',
        maxWidth: 1000,
        bgcolor: 'background.paper',
        boxShadow: 24,
        outline: 'none',
        borderRadius: '0.75rem',
        overflow: 'hidden',
      }}>
        <Box sx={{ 
          display: 'flex', 
          justifyContent: 'space-between', 
          alignItems: 'center',
          px: 3,
          py: 2,
          bgcolor: '#ffffff',
          borderBottom: '1px solid #f0f0f0'
        }}>
          <Typography 
            variant="h6" 
            component="h3" 
            sx={{ 
              color: '#4f46e5', 
              fontWeight: 600, 
              fontSize: '1.1rem' 
            }}
          >
            Preview ({format.toUpperCase()})
          </Typography>
          <Box>
            <IconButton 
              onClick={handleZoomOut} 
              title="Zoom out"
              sx={{ color: '#6b7280' }}
            >
              <ZoomOutIcon />
            </IconButton>
            <IconButton 
              onClick={handleZoomIn} 
              title="Zoom in"
              sx={{ color: '#6b7280' }}
            >
              <ZoomInIcon />
            </IconButton>
            <IconButton 
              onClick={handleReset} 
              title="Reset zoom"
              sx={{ color: '#6b7280' }}
            >
              <RestartAltIcon />
            </IconButton>
            <IconButton 
              onClick={handleClose} 
              title="Close preview"
              sx={{ color: '#6b7280' }}
            >
              <CloseIcon />
            </IconButton>
          </Box>
        </Box>
        
        <Box
          ref={containerRef}
          sx={{
            overflow: 'hidden',
            position: 'relative',
            height: '70vh',
            bgcolor: '#eef2ff', // Indigo background to match the application theme
            cursor: isDragging ? 'grabbing' : 'grab',
            p: 4,
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
          }}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          onWheel={handleWheel}
        >
          {imageUrl && (
            <Box
              component="img"
              src={imageUrl}
              alt={`Preview in ${format} format`}
              sx={{
                position: 'absolute',
                top: '50%',
                left: '50%',
                transform: `translate(calc(-50% + ${position.x}px), calc(-50% + ${position.y}px)) scale(${scale})`,
                maxWidth: 'calc(100% - 4rem)',
                maxHeight: 'calc(100% - 4rem)',
                transition: isDragging ? 'none' : 'transform 0.2s',
                transformOrigin: 'center',
                objectFit: 'contain',
                pointerEvents: 'none', // Prevents the image from capturing mouse events
                boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
              }}
            />
          )}
        </Box>
      </Box>
    </Modal>
  );
};

export default EnhancedImagePreview; 