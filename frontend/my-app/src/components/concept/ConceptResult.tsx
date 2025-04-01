import React, { useState } from 'react';
import { GenerationResponse } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ColorPalette } from '../ui/ColorPalette';
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
  
  // Add better error listening for CORS issues
  React.useEffect(() => {
    const corsErrorHandler = (event: Event) => {
      // Check if it's a CORS error
      if (event instanceof ErrorEvent && 
          (event.message.includes('CORS') || 
           event.message.includes('cross-origin') || 
           event.message.includes('OpaqueResponseBlocking'))) {
        console.error('CORS error detected:', event.message);
        console.log('If you continue to see CORS errors, check these common solutions:');
        console.log('1. Ensure your Storage bucket CORS settings allow access from your app domain');
        console.log('2. Check if your bucket is public or if private, use signed URLs');
        console.log('3. Verify image paths are correct in your database');
      }
    };
    
    // Add global error listener
    window.addEventListener('error', corsErrorHandler);
    
    // Cleanup
    return () => {
      window.removeEventListener('error', corsErrorHandler);
    };
  }, []);
  
  // Handle case where concept is undefined or null
  const hasValidData = !!concept;

  // Display placeholder if no concept data
  if (!hasValidData && variations.length === 0) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <div style={pageHeaderStyle}>
            <h2 style={titleStyle}>Generated Concept</h2>
            <span style={dateStyle}>No data available</span>
          </div>
          <div style={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '16rem',
          }}>
            <p style={{ color: '#6B7280' }}>Waiting for generation results...</p>
          </div>
        </div>
      </div>
    );
  }
  
  // Default fallback image
  const fallbackImage = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YwZjBmZiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5JbWFnZSBOb3QgTG9hZGVkPC90ZXh0Pjwvc3ZnPg==';
  
  // Helper function to ensure URL is properly formatted for Supabase storage
  const getFormattedUrl = (url: string | undefined, bucketName = 'concept-images') => {
    if (!url) {
      console.log('No URL provided, using fallback image');
      return fallbackImage;
    }
    
    console.log('Original URL:', url);
    
    // If it's already a full URL (which it should be now that buckets are public), use it directly
    if (url.startsWith('http')) {
      // Clean up the URL by removing any trailing question mark
      const cleanUrl = url.endsWith('?') ? url.slice(0, -1) : url;
      return cleanUrl;
    }
    
    // If it's not a full URL, construct it (fallback)
    try {
      // Construct direct public URL (now that buckets are public)
      // Remove any trailing question marks from the filename
      const cleanFilename = url.endsWith('?') ? url.slice(0, -1) : url;
      const publicUrl = `https://pstdcfittpjhxzynbdbu.supabase.co/storage/v1/object/public/${bucketName}/${cleanFilename}`;
      console.log('Constructed URL:', publicUrl);
      return publicUrl;
    } catch (error) {
      console.error('Error formatting URL:', error);
      return fallbackImage;
    }
  };
  
  // Function to extract filename from URL for download
  const getFileName = (url: string): string => {
    if (!url || url.startsWith('data:')) {
      const id = concept?.prompt_id || concept?.generation_id || 'download';
      return `concept-${id.slice(0, 8)}.png`;
    }
    
    try {
      const urlParts = url.split('/');
      const fileName = urlParts[urlParts.length - 1];
      const id = concept?.prompt_id || concept?.generation_id || 'download';
      return fileName.includes('.') 
        ? fileName 
        : `concept-${id.slice(0, 8)}.png`;
    } catch (error) {
      return `concept-download.png`;
    }
  };
  
  // Handle download click
  const handleDownload = () => {
    try {
      if (onDownload) {
        onDownload();
        return;
      }
      
      // Get the URL to download
      const imageUrl = getCurrentImageUrl();
      if (!imageUrl || imageUrl.startsWith('data:')) {
        console.error('Cannot download image: Invalid image URL');
        return;
      }
      
      // Default download behavior
      const link = document.createElement('a');
      link.href = imageUrl;
      link.download = getFileName(imageUrl);
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    } catch (error) {
      console.error('Error downloading image:', error);
    }
  };

  // Get current palette based on selection
  const getCurrentPalette = () => {
    // For selected variation
    if (selectedVariation !== null && variations[selectedVariation]) {
      const colors = variations[selectedVariation].colors || [];
      return {
        primary: colors[0] || '#4F46E5',
        secondary: colors[1] || '#818CF8',
        accent: colors[2] || '#C7D2FE',
        background: colors[3] || '#EEF2FF',
        text: colors[4] || '#312E81',
        additionalColors: colors.slice(5) || []
      };
    }
    
    // For original concept
    if (!concept || !concept.color_palette) {
      return {
        primary: '#4F46E5',
        secondary: '#818CF8',
        accent: '#C7D2FE',
        background: '#EEF2FF',
        text: '#312E81',
        additionalColors: []
      };
    }
    
    return concept.color_palette;
  };
  
  // Helper function to get the original image URL from the concept data
  const getOriginalImageUrl = (): string => {
    // Use the correct field name from the API response
    const imageUrl = concept?.image_url;
    
    if (!imageUrl) {
      console.warn('⚠️ No image URL found in concept data!');
      return fallbackImage;
    }
    
    return getFormattedUrl(imageUrl, 'concept-images');
  };
  
  // Get current image URL
  const getCurrentImageUrl = () => {
    // For selected variation
    if (selectedVariation !== null && variations[selectedVariation]) {
      const variationUrl = getFormattedUrl(variations[selectedVariation].image_url, 'palette-images');
      console.log('Using variation image URL:', variationUrl);
      return variationUrl;
    }
    
    // For original concept - ensure we're getting from the correct bucket
    // The original image is stored in the 'concept-images' bucket
    console.log('Loading original image from concept-images bucket');
    return getOriginalImageUrl();
  };
  
  // Get variation name
  const getCurrentVariationName = () => {
    return selectedVariation !== null && variations[selectedVariation]
      ? variations[selectedVariation].name
      : "Original";
  };

  // Handle color selection
  const handleColorSelect = (color: string) => {
    if (onColorSelect) {
      onColorSelect(color);
    }
  };
  
  // Get current palette colors as array
  const getCurrentPaletteColors = () => {
    const palette = getCurrentPalette();
    if (!palette) {
      // Return default colors if palette is undefined
      return ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'];
    }
    return [
      palette.primary || '#4F46E5',
      palette.secondary || '#818CF8',
      palette.accent || '#C7D2FE',
      palette.background || '#EEF2FF',
      palette.text || '#312E81',
      ...(Array.isArray(palette.additionalColors) ? palette.additionalColors : [])
    ];
  };

  // Labels for the color palette
  const paletteLabels = ['Primary', 'Secondary', 'Accent', 'Background', 'Text'];
  
  return (
    <div style={containerStyle}>
      {/* Page Header */}
      <div style={pageHeaderStyle}>
        <h1 style={titleStyle}>Generated Concept</h1>
        <span style={dateStyle}>
          {concept?.created_at ? new Date(concept.created_at).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
          }) : 'March 31, 2023'}
        </span>
      </div>

      {/* Main Content */}
      <div style={sectionStyle}>
        <h2 style={sectionTitleStyle}>Concept</h2>
        <div style={mainImageContainerStyle}>
          <img 
            src={getCurrentImageUrl()} 
            alt="Generated concept" 
            style={imageStyle}
            onLoad={() => console.log('Main image loaded successfully')}
            onError={(e) => {
              console.error('Error loading main image:', e);
              console.error('Current image URL:', getCurrentImageUrl());
              e.currentTarget.src = fallbackImage;
            }}
          />
        </div>
      </div>
      
      {/* Color Palette Section */}
      <div style={sectionStyle}>
        <h2 style={sectionTitleStyle}>Color Palette</h2>
        <div style={cardStyle}>
          <div style={colorPaletteContainerStyle}>
            {getCurrentPaletteColors().slice(0, 5).map((color, index) => (
              <div key={`color-${index}`} style={colorItemStyle}>
                <div 
                  style={{ ...colorSwatchStyle, backgroundColor: color }}
                  onClick={() => handleColorSelect(color)}
                  title={color}
                ></div>
                <span style={colorLabelStyle}>{paletteLabels[index]}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
      
      {/* Color Variations Section */}
      {variations.length > 0 && (
        <div style={sectionStyle}>
          <h2 style={sectionTitleStyle}>Color Variations</h2>
          <div style={cardStyle}>
            <div style={variationsGridStyle}>
              {/* Original variation */}
              <div 
                style={variationCardStyle(selectedVariation === null)}
                onClick={() => setSelectedVariation(null)}
              >
                <div style={variationHeaderStyle}>
                  <span style={variationTitleStyle}>Original</span>
                </div>
                <div style={variationContentStyle}>
                  <img 
                    src={getOriginalImageUrl()} 
                    alt="Original concept" 
                    style={variationImageStyle}
                    onError={(e) => {
                      e.currentTarget.src = fallbackImage;
                    }}
                  />
                  <div style={colorDotsContainerStyle}>
                    {getCurrentPaletteColors().slice(0, 5).map((color, colorIndex) => (
                      <div 
                        key={`color-original-${colorIndex}`}
                        style={{ ...colorDotStyle, backgroundColor: color }}
                        title={color}
                      />
                    ))}
                  </div>
                </div>
              </div>
              
              {/* Other variations */}
              {variations.map((variation, index) => (
                <div
                  key={`variation-${index}`}
                  style={variationCardStyle(selectedVariation === index)}
                  onClick={() => setSelectedVariation(index)}
                >
                  <div style={variationHeaderStyle}>
                    <span style={variationTitleStyle}>{variation.name}</span>
                  </div>
                  <div style={variationContentStyle}>
                    <img 
                      src={getFormattedUrl(variation.image_url, 'palette-images')} 
                      alt={`${variation.name}`} 
                      style={variationImageStyle}
                      onError={(e) => {
                        e.currentTarget.src = fallbackImage;
                      }}
                    />
                    <div style={colorDotsContainerStyle}>
                      {variation.colors.slice(0, 5).map((color, colorIndex) => (
                        <div 
                          key={`color-${index}-${colorIndex}`}
                          style={{ ...colorDotStyle, backgroundColor: color }}
                          title={color}
                        />
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
      
      {/* Actions */}
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '1rem' }}>
        {onRefineRequest && (
          <button 
            style={secondaryButtonStyle}
            onClick={onRefineRequest}
          >
            Refine This Concept
          </button>
        )}
        
        <button 
          style={buttonStyle}
          onClick={handleDownload}
        >
          Download Image
        </button>
      </div>
    </div>
  );
}; 