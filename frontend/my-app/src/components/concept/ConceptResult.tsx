import React, { useState } from 'react';
import { GenerationResponse } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ColorPalette } from '../ui/ColorPalette';
import { supabase, getPublicImageUrl } from '../../services/supabaseClient';

// Custom styles for the component to match the mockup
const styles = {
  container: "max-w-6xl mx-auto",
  card: "bg-white shadow-lg rounded-xl overflow-hidden",
  header: "flex justify-between items-center mb-6",
  title: "text-xl font-bold text-gray-900",
  date: "text-sm text-gray-500",
  mainImage: "flex justify-center mb-8",
  imageContainer: "overflow-hidden rounded-lg border border-gray-200 shadow-sm",
  image: "w-full max-h-96 object-contain",
  sectionTitle: "text-lg font-medium text-gray-800 mb-3",
  variationsGrid: "grid grid-cols-2 sm:grid-cols-3 md:grid-cols-6 gap-3",
  colorDot: "w-2 h-2 rounded-full inline-block",
  colorDotsContainer: "flex justify-center space-x-1 mt-1",
  actions: "flex justify-end space-x-3 pt-4 border-t border-gray-200 mt-4",
  colorSwatch: "w-16 h-16 rounded-full",
  colorItem: "flex flex-col items-center"
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

// Styles for variation items
const variationItemStyles = `
  cursor-pointer 
  rounded-lg 
  overflow-hidden 
  border
  transition-all 
  duration-200 
  hover:shadow-md 
  hover:-translate-y-0.5
`;

const selectedVariationStyles = `
  border-2 border-indigo-500
`;

const nonSelectedVariationStyles = `
  border border-gray-200
`;

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
      <div className={styles.container}>
        <div className={styles.card}>
          <div className="p-6">
            <div className={styles.header}>
              <h2 className={styles.title}>Generated Concept</h2>
              <span className={styles.date}>No data available</span>
            </div>
            <div className="flex justify-center items-center h-64">
              <p className="text-gray-500">Waiting for generation results...</p>
            </div>
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

  // Get current palette labels
  const paletteLabels = ['Primary', 'Secondary', 'Accent', 'Background', 'Text'];
  
  return (
    <div className={styles.container}>
      <div className={styles.card}>
        {/* Header */}
        <div className="p-6">
          <div className={styles.header}>
            <h2 className={styles.title}>Generated Concept</h2>
            <span className={styles.date}>
              {concept?.created_at ? new Date(concept.created_at).toLocaleString() : 'Just now'}
            </span>
          </div>

          {/* Main image display */}
          <div className={styles.mainImage}>
            <div className={styles.imageContainer}>
              <img 
                src={getCurrentImageUrl()} 
                alt="Generated concept" 
                className={styles.image}
                onLoad={() => console.log('Main image loaded successfully')}
                onError={(e) => {
                  console.error('Error loading main image:', e);
                  console.error('Current image URL:', getCurrentImageUrl());
                  e.currentTarget.src = fallbackImage;
                  // Add class to show user there was an error
                  e.currentTarget.classList.add('image-error');
                }}
              />
            </div>
          </div>
          
          {/* Color palette for selected/main image */}
          <div className="mb-6">
            <h3 className={styles.sectionTitle}>Color Palette</h3>
            <div className="flex flex-wrap gap-3">
              {getCurrentPaletteColors().slice(0, 5).map((color, index) => (
                <div key={`color-${index}`} className={styles.colorItem}>
                  <div 
                    className={styles.colorSwatch} 
                    style={{ backgroundColor: color }}
                    onClick={() => handleColorSelect(color)}
                    title={color}
                  ></div>
                  <span className="text-xs mt-1 text-gray-600">{paletteLabels[index]}</span>
                </div>
              ))}
            </div>
          </div>
          
          {/* Color variations display */}
          {variations.length > 0 && (
            <div className="mb-6">
              <h3 className={styles.sectionTitle}>Color Variations</h3>
              <div className={styles.variationsGrid}>
                {/* Original concept - make sure this is using the concept-images bucket */}
                <div
                  className={`${variationItemStyles} ${selectedVariation === null ? selectedVariationStyles : nonSelectedVariationStyles}`}
                  onClick={() => setSelectedVariation(null)}
                >
                  <div className="bg-gray-50">
                    <img 
                      src={getOriginalImageUrl()} 
                      alt="Original concept" 
                      className="w-full h-32 object-contain"
                      onLoad={() => console.log('Original concept thumbnail loaded successfully')}
                      onError={(e) => {
                        console.error('Error loading original concept thumbnail:', e);
                        console.error('Original image URL attempt:', getOriginalImageUrl());
                        e.currentTarget.src = fallbackImage;
                        e.currentTarget.classList.add('image-error');
                      }}
                    />
                  </div>
                  <div className="p-1 text-center bg-white text-xs">
                    <span className="font-medium text-gray-700">Original</span>
                    <div className={styles.colorDotsContainer}>
                      {concept?.color_palette ? (
                        getCurrentPaletteColors().slice(0, 5).map((color, colorIndex) => (
                          <div 
                            key={`color-original-${colorIndex}`}
                            className={styles.colorDot}
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))
                      ) : (
                        <span className="text-xs text-gray-500">No palette</span>
                      )}
                    </div>
                  </div>
                </div>
                
                {/* Color variations */}
                {variations.map((variation, index) => (
                  <div
                    key={`variation-${index}`}
                    className={`${variationItemStyles} ${selectedVariation === index ? selectedVariationStyles : nonSelectedVariationStyles}`}
                    onClick={() => setSelectedVariation(index)}
                  >
                    <div className="bg-gray-50">
                      <img 
                        src={getFormattedUrl(variation.image_url, 'palette-images')} 
                        alt={`Color variation: ${variation.name}`} 
                        className="w-full h-32 object-contain"
                        onLoad={() => console.log(`Variation image ${index} loaded successfully`)}
                        onError={(e) => {
                          console.error(`Error loading variation image ${index}`);
                          e.currentTarget.src = fallbackImage;
                          e.currentTarget.classList.add('image-error');
                        }}
                      />
                    </div>
                    <div className="p-1 text-center bg-white text-xs">
                      <span className="font-medium text-gray-700">{variation.name}</span>
                      <div className={styles.colorDotsContainer}>
                        {variation.colors.slice(0, 5).map((color, colorIndex) => (
                          <div 
                            key={`color-${index}-${colorIndex}`}
                            className={styles.colorDot}
                            style={{ backgroundColor: color }}
                            title={color}
                          />
                        ))}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {/* Actions */}
          <div className={styles.actions}>
            {onRefineRequest && (
              <button 
                className="px-4 py-2 bg-white text-indigo-600 font-medium border border-indigo-600 rounded hover:bg-indigo-50"
                onClick={onRefineRequest}
              >
                Refine This Concept
              </button>
            )}
            
            <button 
              className="px-4 py-2 bg-indigo-600 text-white font-medium rounded hover:bg-indigo-700"
              onClick={handleDownload}
            >
              Download Image
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}; 