import React, { useState } from 'react';
import { GenerationResponse, ColorPalette } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ColorPalette as ColorPaletteComponent } from '../ui/ColorPalette';
import { supabase, getPublicImageUrl } from '../../services/supabaseClient';

// Define styles using JavaScript objects like in ConceptForm.tsx
const containerStyle = {
  width: '100%', // Full width to match other sections
  margin: '0 auto',
  backgroundColor: 'white',
  borderRadius: '0.75rem',
  padding: '1.5rem',
};

const pageHeaderStyle = {
  display: 'flex',
  justifyContent: 'space-between',
  alignItems: 'center',
  marginBottom: '1.5rem',
};

const titleStyle = {
  fontSize: '1.5rem',
  fontWeight: 'bold',
  color: '#111827',
};

const dateStyle = {
  fontSize: '0.875rem',
  color: '#6B7280',
};

const sectionStyle = {
  marginBottom: '1.5rem',
};

const sectionTitleStyle = {
  fontSize: '1.25rem',
  fontWeight: '600',
  color: '#111827',
  marginBottom: '1rem',
  textAlign: 'center' as const,
};

const cardStyle = {
  backgroundColor: '#EEF2FF', // Light indigo background
  borderRadius: '0.75rem',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
  border: '1px solid #E5E7EB',
  padding: '1.5rem',
};

const mainImageContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  alignItems: 'center',
  width: '100%',
  padding: '1rem',
  backgroundColor: '#EEF2FF', // Match section card background color
  borderRadius: '0.75rem',
  border: '1px solid #E5E7EB',
  boxShadow: '0 1px 3px rgba(0, 0, 0, 0.05)',
};

const imageStyle = {
  maxWidth: '100%',
  maxHeight: '350px',
  objectFit: 'contain' as const,
};

const colorPaletteContainerStyle = {
  display: 'flex',
  flexWrap: 'wrap' as const,
  justifyContent: 'center',
  gap: '1.5rem',
};

const colorItemStyle = {
  display: 'flex',
  flexDirection: 'column' as const,
  alignItems: 'center',
  marginBottom: '0.5rem',
};

const colorSwatchStyle = {
  width: '48px',
  height: '48px',
  borderRadius: '50%',
  cursor: 'pointer',
  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.1)',
};

const colorLabelStyle = {
  marginTop: '0.5rem',
  fontSize: '0.75rem',
  color: '#4B5563',
  textAlign: 'center' as const,
};

const variationsGridStyle = {
  display: 'grid',
  gridTemplateColumns: 'repeat(auto-fill, minmax(160px, 1fr))',
  gap: '0.75rem',
};

const variationCardStyle = (isSelected: boolean) => ({
  backgroundColor: 'white',
  borderRadius: '0.5rem',
  overflow: 'hidden',
  boxShadow: '0 1px 2px rgba(0, 0, 0, 0.05)',
  border: isSelected ? '2px solid #4F46E5' : '1px solid #E5E7EB',
  cursor: 'pointer',
  transition: 'transform 0.2s, box-shadow 0.2s',
});

const variationHeaderStyle = {
  padding: '0.5rem',
  borderBottom: '1px solid #F3F4F6',
  textAlign: 'center' as const,
  backgroundColor: '#F9FAFB',
};

const variationTitleStyle = {
  fontWeight: '500',
  fontSize: '0.75rem',
  color: '#111827',
};

const variationContentStyle = {
  padding: '0.5rem',
};

const variationImageStyle = {
  width: '100%',
  height: '100px',
  objectFit: 'contain' as const,
  marginBottom: '0.5rem',
};

const colorDotsContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  gap: '0.25rem',
  paddingBottom: '0.25rem',
};

const colorDotStyle = {
  width: '12px',
  height: '12px',
  borderRadius: '50%',
};

const actionsContainerStyle = {
  display: 'flex',
  justifyContent: 'center',
  gap: '1rem',
  marginTop: '1.5rem',
};

const buttonStyle = {
  backgroundColor: '#4F46E5',
  color: 'white',
  padding: '0.75rem 1.5rem',
  borderRadius: '0.375rem',
  fontWeight: 600,
  border: 'none',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  marginTop: '1rem'
};

const secondaryButtonStyle = {
  backgroundColor: 'white',
  color: '#4F46E5',
  padding: '0.75rem 1.5rem',
  borderRadius: '0.375rem',
  fontWeight: 600,
  border: '1px solid #4F46E5',
  cursor: 'pointer',
  transition: 'background-color 0.2s',
  marginTop: '1rem'
};

export interface ConceptResultProps {
  /**
   * The generated concept data
   */
  concept: GenerationResponse;
  
  /**
   * Handler for requesting refinement
   */
  onRefineRequest?: () => void;
  
  /**
   * Handler for downloading the image
   */
  onDownload?: () => void;
  
  /**
   * Handler for selecting a color
   */
  onColorSelect?: (color: string) => void;
  
  /**
   * Optional color variations
   */
  variations?: Array<{
    name: string;
    colors: string[];
    image_url: string;
    description?: string;
  }>;
}

/**
 * Component for displaying generated concept results
 */
export const ConceptResult: React.FC<ConceptResultProps> = ({
  concept,
  onRefineRequest,
  onDownload,
  onColorSelect,
  variations = [],
}) => {
  const [selectedVariation, setSelectedVariation] = useState<number | null>(null);
  const [imageLoadErrors, setImageLoadErrors] = useState<Record<string, boolean>>({});
  
  // Debug the concept and variations data
  React.useEffect(() => {
    console.log('ConceptResult - concept data:', concept);
    console.log('ConceptResult - variations data:', variations);
    
    // Check for the original image URL using the correct field name
    const originalImageUrl = concept?.image_url;
    console.log('Original image URL:', originalImageUrl);
    
    // Add more detailed logging specifically for debugging image display issues
    if (originalImageUrl) {
      console.log('Original image URL found:', originalImageUrl);
      const formattedUrl = getFormattedUrl(originalImageUrl, 'concept-images');
      console.log('Formatted original image URL:', formattedUrl);
    } else {
      console.warn('⚠️ Original image URL is missing from concept data!');
      console.warn('Concept data structure:', concept);
    }
  }, [concept, variations]);
  
  // Image error handler
  const handleImageError = (event: React.SyntheticEvent<HTMLImageElement>) => {
    // Get the target element and its src attribute
    const imgElement = event.currentTarget;
    const imgSrc = imgElement.src;
    
    console.error(`Image failed to load: ${imgSrc}`, event);
    
    // Mark this image URL as failed in our state
    setImageLoadErrors(prev => ({
      ...prev,
      [imgSrc]: true
    }));
  };
  
  const getFormattedUrl = (url: string | undefined, bucketName = 'concept-images') => {
    if (!url) return '';
    
    // If the URL already has the domain in it, return it as is
    if (url.startsWith('http')) {
      return url;
    }
    
    // Otherwise, assume it's a path/key and format it appropriately for Supabase
    try {
      // Assume the URL is a path in the Supabase bucket
      return getPublicImageUrl(bucketName, url) || '';
    } catch (error) {
      console.error('Error formatting URL:', error);
      return '';
    }
  };
  
  const getFileName = (url: string): string => {
    if (!url) return '';
    
    // Extract the file name from the URL
    const parts = url.split('/');
    const fileName = parts[parts.length - 1];
    
    // If the file name contains a query string, remove it
    if (fileName.includes('?')) {
      return fileName.split('?')[0];
    }
    
    return fileName;
  };
  
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
      return;
    }
    
    const imageUrl = getCurrentImageUrl();
    if (!imageUrl) return;
    
    // Create a link and trigger download
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = getFileName(imageUrl) || 'concept-image.png';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  const getCurrentPalette = (): ColorPalette | string[] => {
    // If a variation is selected, return its colors
    if (selectedVariation !== null && variations[selectedVariation]) {
      return variations[selectedVariation].colors;
    }
    
    // Otherwise, fallback to the original concept's color palette
    if (concept && concept.color_palette) {
      return concept.color_palette;
    }
    
    // If no colors are available, return an empty array
    return [];
  };
  
  const getOriginalImageUrl = (): string => {
    if (!concept || !concept.image_url) {
      console.warn('Original image URL is missing in concept data', concept);
      return '';
    }
    
    return getFormattedUrl(concept.image_url, 'concept-images');
  };
  
  const getCurrentImageUrl = () => {
    // If a variation is selected, return its image URL
    if (selectedVariation !== null && variations[selectedVariation]) {
      const variationUrl = variations[selectedVariation].image_url;
      return getFormattedUrl(variationUrl, 'palette-images');
    }
    
    // Otherwise, return the original image URL
    return getOriginalImageUrl();
  };
  
  const getCurrentVariationName = () => {
    if (selectedVariation !== null && variations[selectedVariation]) {
      return variations[selectedVariation].name;
    }
    return 'Original';
  };
  
  const handleColorSelect = (color: string) => {
    if (onColorSelect) {
      onColorSelect(color);
    }
  };
  
  const getCurrentPaletteColors = () => {
    return getCurrentPalette();
  };
  
  const getImageElements = () => {
    const imageUrl = getCurrentImageUrl();
    const palette = getCurrentPaletteColors();
    
    // Create a valid ColorPalette object
    const createColorPaletteObject = (colors: string[] | ColorPalette): ColorPalette => {
      if (Array.isArray(colors)) {
        return {
          primary: colors[0] || '#4F46E5',
          secondary: colors[1] || '#818CF8',
          accent: colors[2] || '#C7D2FE',
          background: colors[3] || '#EEF2FF',
          text: colors[4] || '#312E81',
          additionalColors: colors.slice(5) || []
        };
      } else if (colors && typeof colors === 'object') {
        return colors;
      }
      
      // Default palette if nothing valid is provided
      return {
        primary: '#4F46E5',
        secondary: '#818CF8',
        accent: '#C7D2FE',
        background: '#EEF2FF',
        text: '#312E81',
        additionalColors: []
      };
    };
    
    return (
      <div className="space-y-6">
        <div className="rounded-lg p-4 bg-indigo-50 border border-gray-200 shadow-sm flex justify-center items-center">
          {imageUrl ? (
            <img 
              src={imageUrl} 
              alt={`${concept.prompt_id || 'Logo'} concept`}
              className="max-w-full max-h-[350px] object-contain"
              onError={handleImageError} 
            />
          ) : (
            <div className="text-gray-500 text-center p-8">
              Image not available
            </div>
          )}
        </div>
        
        {palette && (Array.isArray(palette) ? palette.length > 0 : true) && (
          <div className="mt-6">
            <h3 className="text-xl font-semibold text-indigo-900 mb-3 text-center">
              {getCurrentVariationName()} Color Palette
            </h3>
            <div className="flex justify-center">
              <ColorPaletteComponent 
                palette={createColorPaletteObject(palette)}
                onColorSelect={handleColorSelect} 
              />
            </div>
          </div>
        )}
      </div>
    );
  };
  
  const renderVariations = () => {
    if (!variations || variations.length === 0) return null;
    
    return (
      <div className="mt-8">
        <h3 className="text-xl font-semibold text-indigo-900 mb-4 text-center">
          Color Variations
        </h3>
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3">
          {variations.map((variation, index) => (
            <div 
              key={`variation-${index}`}
              className={`rounded-lg overflow-hidden shadow-sm cursor-pointer transition-all duration-200 hover:shadow-md ${
                selectedVariation === index 
                  ? 'border-2 border-primary' 
                  : 'border border-gray-200'
              }`}
              onClick={() => setSelectedVariation(index)}
            >
              <div className="p-2 border-b border-gray-100 bg-gray-50 text-center">
                <h4 className="text-xs font-medium text-gray-900">
                  {variation.name}
                </h4>
              </div>
              <div className="p-2">
                <img 
                  src={getFormattedUrl(variation.image_url, 'palette-images')}
                  alt={`${variation.name} variation`}
                  className="w-full h-[100px] object-contain mb-2"
                  onError={handleImageError}
                />
                <div className="flex justify-center gap-1 pb-1">
                  {variation.colors.slice(0, 5).map((color, colorIndex) => (
                    <div 
                      key={`dot-${index}-${colorIndex}`}
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                  ))}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  };
  
  if (!concept) {
    return <div className="text-center p-8 text-gray-500">No concept data available</div>;
  }
  
  return (
    <div className="w-full bg-white rounded-xl p-6">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-2xl font-bold text-gray-900">
          Concept
        </h2>
        <div className="text-sm text-gray-500">
          {new Date().toLocaleDateString()}
        </div>
      </div>
      
      <div className="mb-6">
        {getImageElements()}
      </div>
      
      {renderVariations()}
      
      <div className="flex justify-center gap-4 mt-6">
        <Button
          variant="primary"
          onClick={handleDownload}
        >
          Download
        </Button>
        
        {onRefineRequest && (
          <Button
            variant="outline"
            onClick={onRefineRequest}
          >
            Refine Concept
          </Button>
        )}
      </div>
    </div>
  );
}; 