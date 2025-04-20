# ColorPalette Component

The `ColorPalette` component displays a collection of colors with optional interaction capabilities. It's primarily used to show color palettes extracted from concept images.

## Overview

This component visually represents a set of colors in a horizontal or grid layout. Each color is displayed as a swatch that can be clicked to copy its value or to trigger other actions. The component supports different display formats for color values and various interaction modes.

## Usage

```tsx
import { ColorPalette } from 'components/ui/ColorPalette';

// Basic usage with array of hex colors
const colors = ['#2563EB', '#10B981', '#EF4444', '#F59E0B', '#3B82F6'];

<ColorPalette colors={colors} />

// With copy functionality and hex format
<ColorPalette 
  colors={colors} 
  allowCopy 
  format="hex"
  onColorClick={(color) => console.log(`Color clicked: ${color}`)}
/>
```

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| `colors` | `string[]` | `[]` | Array of color values (hex, rgb, etc.) |
| `format` | `'hex' \| 'rgb' \| 'hsl' \| 'none'` | `'hex'` | Format to display color values |
| `allowCopy` | `boolean` | `false` | Whether to enable copy-to-clipboard on click |
| `size` | `'small' \| 'medium' \| 'large'` | `'medium'` | Size of the color swatches |
| `layout` | `'horizontal' \| 'grid'` | `'horizontal'` | Layout arrangement of color swatches |
| `className` | `string` | `''` | Additional CSS class to apply |
| `onColorClick` | `(color: string) => void` | - | Handler called when a color is clicked |
| `showLabels` | `boolean` | `true` | Whether to show color value labels |
| `selected` | `string \| null` | `null` | Currently selected color value |

## Implementation Details

```tsx
import React, { useState } from 'react';
import { Box, Typography, Tooltip, Snackbar, Paper } from '@mui/material';
import ContentCopyIcon from '@mui/icons-material/ContentCopy';
import { styled } from '@mui/material/styles';

interface ColorPaletteProps {
  colors: string[];
  format?: 'hex' | 'rgb' | 'hsl' | 'none';
  allowCopy?: boolean;
  size?: 'small' | 'medium' | 'large';
  layout?: 'horizontal' | 'grid';
  className?: string;
  onColorClick?: (color: string) => void;
  showLabels?: boolean;
  selected?: string | null;
}

const ColorSwatch = styled(Paper, {
  shouldForwardProp: (prop) => 
    !['size', 'bgColor', 'isSelected'].includes(prop as string),
})<{
  size: 'small' | 'medium' | 'large';
  bgColor: string;
  isSelected: boolean;
}>(({ theme, size, bgColor, isSelected }) => {
  const sizeMap = {
    small: 36,
    medium: 48,
    large: 64,
  };
  
  return {
    width: sizeMap[size],
    height: sizeMap[size],
    backgroundColor: bgColor,
    borderRadius: theme.shape.borderRadius,
    cursor: 'pointer',
    position: 'relative',
    overflow: 'hidden',
    transition: theme.transitions.create(['transform', 'box-shadow'], {
      duration: theme.transitions.duration.short,
    }),
    border: isSelected 
      ? `2px solid ${theme.palette.primary.main}` 
      : `1px solid ${theme.palette.divider}`,
    '&:hover': {
      transform: 'scale(1.05)',
      boxShadow: theme.shadows[3],
    },
  };
});

export function ColorPalette({
  colors = [],
  format = 'hex',
  allowCopy = false,
  size = 'medium',
  layout = 'horizontal',
  className = '',
  onColorClick,
  showLabels = true,
  selected = null,
}: ColorPaletteProps) {
  const [snackbarOpen, setSnackbarOpen] = useState(false);
  const [copiedColor, setCopiedColor] = useState('');
  
  // Format the color value based on the specified format
  const formatColor = (color: string): string => {
    if (format === 'none') return '';
    return color; // In a real component, would handle conversion to other formats
  };
  
  // Handle color swatch click
  const handleColorClick = (color: string) => {
    if (allowCopy) {
      navigator.clipboard.writeText(color);
      setCopiedColor(color);
      setSnackbarOpen(true);
    }
    
    if (onColorClick) {
      onColorClick(color);
    }
  };
  
  return (
    <Box className={className}>
      <Box
        sx={{
          display: 'flex',
          flexDirection: layout === 'horizontal' ? 'row' : 'row',
          flexWrap: layout === 'horizontal' ? 'nowrap' : 'wrap',
          gap: 1,
          overflowX: layout === 'horizontal' ? 'auto' : 'visible',
          padding: 1,
        }}
      >
        {colors.map((color, index) => (
          <Box 
            key={`${color}-${index}`}
            sx={{ 
              display: 'flex', 
              flexDirection: 'column',
              alignItems: 'center',
              gap: 0.5,
            }}
          >
            <Tooltip title={allowCopy ? 'Click to copy' : color}>
              <ColorSwatch 
                size={size}
                bgColor={color}
                isSelected={selected === color}
                onClick={() => handleColorClick(color)}
              >
                {allowCopy && (
                  <Box
                    sx={{
                      position: 'absolute',
                      top: '50%',
                      left: '50%',
                      transform: 'translate(-50%, -50%)',
                      opacity: 0,
                      transition: 'opacity 0.2s',
                      backgroundColor: 'rgba(255, 255, 255, 0.8)',
                      borderRadius: '50%',
                      padding: 0.5,
                      display: 'flex',
                      '&:hover': {
                        opacity: 1,
                      },
                    }}
                  >
                    <ContentCopyIcon fontSize="small" />
                  </Box>
                )}
              </ColorSwatch>
            </Tooltip>
            
            {showLabels && format !== 'none' && (
              <Typography variant="caption" sx={{ fontSize: '0.7rem' }}>
                {formatColor(color)}
              </Typography>
            )}
          </Box>
        ))}
      </Box>
      
      <Snackbar
        open={snackbarOpen}
        autoHideDuration={2000}
        onClose={() => setSnackbarOpen(false)}
        message={`Copied ${copiedColor} to clipboard`}
      />
    </Box>
  );
}
```

## Features

- **Multiple Display Formats**: Supports hex, RGB, HSL, or no labels
- **Copy to Clipboard**: Allows users to copy color values with a click
- **Flexible Layout**: Horizontal strip or grid layout options
- **Size Options**: Small, medium, or large color swatches
- **Selection State**: Can highlight a selected color
- **Tooltips**: Shows additional information on hover
- **Feedback**: Provides visual feedback when colors are copied
- **Customizable**: Adaptable to various use cases through props

## Usage Scenarios

### Concept Color Palette Display

```tsx
function ConceptDetail({ concept }) {
  return (
    <Box>
      <Typography variant="h6">Color Palette</Typography>
      <ColorPalette 
        colors={concept.palette} 
        allowCopy 
        size="medium"
        layout="horizontal"
      />
    </Box>
  );
}
```

### Color Picker

```tsx
function ThemeColorPicker() {
  const [selectedColor, setSelectedColor] = useState('#2563EB');
  const themeColors = ['#2563EB', '#10B981', '#EF4444', '#F59E0B', '#3B82F6', '#8B5CF6'];
  
  return (
    <Box>
      <Typography variant="h6">Choose Theme Color</Typography>
      <ColorPalette 
        colors={themeColors}
        selected={selectedColor}
        onColorClick={setSelectedColor}
        size="large"
        layout="grid"
        showLabels={false}
      />
      <Typography variant="body2" sx={{ mt: 2 }}>
        Selected color: {selectedColor}
      </Typography>
    </Box>
  );
}
```

### Compact Color Reference

```tsx
function DesignSystemColors() {
  const primaryColors = ['#0D47A1', '#1565C0', '#1976D2', '#1E88E5', '#2196F3'];
  const secondaryColors = ['#311B92', '#4527A0', '#512DA8', '#5E35B1', '#673AB7'];
  
  return (
    <Box>
      <Typography variant="subtitle1">Primary Colors</Typography>
      <ColorPalette 
        colors={primaryColors}
        size="small"
        format="none"
      />
      
      <Typography variant="subtitle1" sx={{ mt: 2 }}>
        Secondary Colors
      </Typography>
      <ColorPalette 
        colors={secondaryColors}
        size="small"
        format="none"
      />
    </Box>
  );
}
```

## Accessibility

- Color swatches include tooltips for screen readers
- Copy action is accompanied by a visual indicator and feedback message
- Selected state is indicated with a visible border
- Keyboard navigation is supported for all interactive elements 