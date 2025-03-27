import React from 'react';
import { ColorPalette as ColorPaletteType } from '../../types';

export interface ColorPaletteProps {
  /**
   * The color palette to display
   */
  palette: ColorPaletteType;
  
  /**
   * Show color labels
   */
  showLabels?: boolean;
  
  /**
   * Allow color selection
   */
  selectable?: boolean;
  
  /**
   * Currently selected color
   */
  selectedColor?: string;
  
  /**
   * Handler for color selection
   */
  onColorSelect?: (color: string, role: string) => void;
  
  /**
   * Size of the color swatches
   */
  size?: 'sm' | 'md' | 'lg';
  
  /**
   * Additional CSS classes
   */
  className?: string;
}

/**
 * Component for displaying a color palette
 */
export const ColorPalette: React.FC<ColorPaletteProps> = ({
  palette,
  showLabels = true,
  selectable = false,
  selectedColor,
  onColorSelect,
  size = 'md',
  className = '',
}) => {
  const handleColorSelect = (color: string, role: string) => {
    if (selectable && onColorSelect) {
      onColorSelect(color, role);
    }
  };
  
  const getSwatchSize = () => {
    switch (size) {
      case 'sm': return 'h-6 w-6';
      case 'lg': return 'h-12 w-12';
      default: return 'h-8 w-8';
    }
  };
  
  const swatchSize = getSwatchSize();
  const interactionClasses = selectable ? 'cursor-pointer hover:scale-110 transition-transform' : '';
  
  const colorItems = [
    { color: palette.primary, label: 'Primary' },
    { color: palette.secondary, label: 'Secondary' },
    { color: palette.accent, label: 'Accent' },
    { color: palette.background, label: 'Background' },
    { color: palette.text, label: 'Text' },
  ];
  
  return (
    <div className={`flex flex-col space-y-4 ${className}`}>
      <div className="flex flex-wrap gap-3">
        {colorItems.map(({ color, label }) => (
          <div key={`${color}-${label}`} className="flex flex-col items-center">
            <div
              className={`
                ${swatchSize} rounded-full shadow-sm border border-dark-200 
                ${interactionClasses}
                ${selectedColor === color ? 'ring-2 ring-primary-500 ring-offset-2' : ''}
              `}
              style={{ backgroundColor: color }}
              onClick={() => handleColorSelect(color, label.toLowerCase())}
              title={`${label}: ${color}`}
            />
            {showLabels && (
              <span className="mt-1 text-xs text-dark-600">{label}</span>
            )}
          </div>
        ))}
      </div>
      
      {palette.additionalColors.length > 0 && (
        <div className="mt-2">
          <p className="text-sm text-dark-600 mb-1">Additional Colors</p>
          <div className="flex flex-wrap gap-2">
            {palette.additionalColors.map((color, index) => (
              <div key={`${color}-${index}`} className="flex flex-col items-center">
                <div
                  className={`
                    ${swatchSize} rounded-full shadow-sm border border-dark-200
                    ${interactionClasses}
                    ${selectedColor === color ? 'ring-2 ring-primary-500 ring-offset-2' : ''}
                  `}
                  style={{ backgroundColor: color }}
                  onClick={() => handleColorSelect(color, `additional-${index}`)}
                  title={`Additional color: ${color}`}
                />
                {showLabels && (
                  <span className="mt-1 text-xs text-dark-600">A{index + 1}</span>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}; 