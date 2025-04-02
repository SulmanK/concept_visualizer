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

  /**
   * Handler for navigating to concept detail page
   */
  onExport?: (conceptId: string) => void;
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
  onExport,
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
    
    // Open the image in a new tab instead of direct download
    window.open(imageUrl, '_blank');
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
          {/* Original concept */}
          <div 
            key="variation-original"
            className={`rounded-lg overflow-hidden shadow-sm cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-md ${
              selectedVariation === null 
                ? 'border-2 border-indigo-600' 
                : 'border border-gray-200'
            }`}
            onClick={() => setSelectedVariation(null)}
          >
            <div className="p-2 border-b border-gray-100 bg-gray-50 text-center">
              <h4 className="text-xs font-medium text-gray-900">
                Original
              </h4>
            </div>
            <div className="p-2">
              <img 
                src={getOriginalImageUrl()}
                alt="Original concept"
                className="w-full h-[100px] object-contain mb-2"
                onError={handleImageError}
              />
              <div className="flex justify-center gap-1 pb-1">
                {concept.color_palette && (Array.isArray(concept.color_palette) 
                  ? concept.color_palette.slice(0, 5).map((color, colorIndex) => (
                    <div 
                      key={`dot-original-${colorIndex}`}
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color }}
                    />
                  ))
                  : Object.values(concept.color_palette).slice(0, 5).map((color, colorIndex) => (
                    <div 
                      key={`dot-original-${colorIndex}`}
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: color as string }}
                    />
                  ))
                )}
              </div>
            </div>
          </div>
          
          {/* Color variations */}
          {variations.map((variation, index) => (
            <div 
              key={`variation-${index}`}
              className={`rounded-lg overflow-hidden shadow-sm cursor-pointer transition-all duration-300 hover:scale-105 hover:shadow-md ${
                selectedVariation === index 
                  ? 'border-2 border-indigo-600' 
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
  
  const handleExport = () => {
    // Log the concept ID data to debug the issue
    console.log('Export button clicked, concept data:', {
      hasId: concept && 'id' in concept,
      id: concept?.id,
      hasGenerationId: concept && 'generation_id' in concept,
      generationId: concept?.generation_id,
      promptId: concept?.prompt_id
    });
    
    // Try to get a valid ID from either id, generation_id, or prompt_id
    const conceptId = concept?.id || concept?.generation_id || concept?.prompt_id;
    
    // Check if onExport is provided and if we have a valid conceptId
    if (onExport && conceptId && typeof conceptId === 'string') {
      console.log('Calling onExport with conceptId:', conceptId);
      onExport(conceptId);
      return;
    }
    
    console.log('Falling back to download function');
    // If onExport is not provided or concept.id is missing, fall back to download
    handleDownload();
  };
  
  if (!concept) {
    return <div className="text-center p-8 text-gray-500">No concept data available</div>;
  }
  
  return (
    <div className="w-full bg-white/90 backdrop-blur-sm rounded-xl p-8 shadow-modern border border-indigo-100 relative overflow-hidden">
      {/* Subtle gradient background accents */}
      <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-100/30 rounded-full blur-3xl"></div>
      <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-indigo-50/50 rounded-full blur-2xl"></div>
      
      <div className="relative z-10">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-indigo-900">
            Your Concept
          </h2>
          <div className="flex items-center gap-2">
            <div className="px-3 py-1 bg-indigo-100 rounded-full text-sm text-indigo-800 font-medium">
              {new Date().toLocaleDateString()}
            </div>
          </div>
        </div>
        
        <div className="mb-6">
          {getImageElements()}
        </div>
        
        {renderVariations()}
        
        <div className="flex justify-center gap-4 mt-8">
          <Button
            variant="primary"
            onClick={handleExport}
            className="px-6 py-2 text-base font-medium shadow-lg hover:shadow-xl transition-all duration-300 transform hover:-translate-y-0.5"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 inline-block" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            Export
          </Button>
          
          {onRefineRequest && (
            <Button
              variant="outline"
              onClick={onRefineRequest}
              className="px-6 py-2 text-base font-medium shadow-sm hover:shadow-md transition-all duration-300 transform hover:-translate-y-0.5"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 inline-block" viewBox="0 0 20 20" fill="currentColor">
                <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
              </svg>
              Refine Concept
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}; 