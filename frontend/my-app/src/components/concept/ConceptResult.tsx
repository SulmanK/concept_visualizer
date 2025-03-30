import React, { useState } from 'react';
import { GenerationResponse } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ColorPalette } from '../ui/ColorPalette';

// Custom styles for the component to match the mockup
const styles = {
  container: "max-w-6xl mx-auto",
  card: "shadow-lg rounded-xl overflow-hidden",
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
  actions: "flex flex-wrap justify-end gap-3 pt-4 border-t border-gray-200 mt-4"
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
  onColorSelect?: (color: string, role: string) => void;
  
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

// Add these styles to improve the visual appearance
const variationItemStyles = `
  cursor-pointer 
  rounded-lg 
  overflow-hidden 
  border-2 
  transition-all 
  duration-200 
  hover:shadow-md 
  hover:-translate-y-1
`;

const selectedVariationStyles = `
  border-indigo-500
`;

const nonSelectedVariationStyles = `
  border-transparent 
  hover:border-indigo-200
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
  
  // Function to extract filename from URL for download
  const getFileName = (url: string): string => {
    const urlParts = url.split('/');
    const fileName = urlParts[urlParts.length - 1];
    return fileName.includes('.') 
      ? fileName 
      : `concept-${concept.generationId.slice(0, 8)}.png`;
  };
  
  // Handle download click
  const handleDownload = () => {
    if (onDownload) {
      onDownload();
      return;
    }
    
    // Default download behavior
    const link = document.createElement('a');
    link.href = selectedVariation !== null && variations[selectedVariation] 
      ? variations[selectedVariation].image_url 
      : concept.imageUrl;
    link.download = getFileName(concept.imageUrl);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  // Get current palette based on selection
  const getCurrentPalette = () => {
    if (selectedVariation !== null && variations[selectedVariation]) {
      return {
        primary: variations[selectedVariation].colors[0] || '#4F46E5',
        secondary: variations[selectedVariation].colors[1] || '#818CF8',
        accent: variations[selectedVariation].colors[2] || '#C7D2FE',
        background: variations[selectedVariation].colors[3] || '#EEF2FF',
        text: variations[selectedVariation].colors[4] || '#312E81',
        additionalColors: variations[selectedVariation].colors.slice(5) || []
      };
    }
    return concept.colorPalette;
  };
  
  // Get current image URL
  const getCurrentImageUrl = () => {
    return selectedVariation !== null && variations[selectedVariation]
      ? variations[selectedVariation].image_url
      : concept.imageUrl;
  };
  
  // Get variation name
  const getCurrentVariationName = () => {
    return selectedVariation !== null && variations[selectedVariation]
      ? variations[selectedVariation].name
      : "Original";
  };
  
  return (
    <div className={styles.container}>
      <Card
        variant="elevated"
        className={styles.card}
        header={
          <div className={styles.header}>
            <h2 className={styles.title}>Generated Concept</h2>
            <span className={styles.date}>
              {new Date(concept.createdAt).toLocaleString()}
            </span>
          </div>
        }
      >
        <div className="space-y-6 p-6">
          {/* Main image display */}
          <div className={styles.mainImage}>
            <div className={styles.imageContainer}>
              <img 
                src={getCurrentImageUrl()} 
                alt="Generated concept" 
                className={styles.image}
              />
            </div>
          </div>
          
          {/* Color palette for selected/main image */}
          <div className="mb-6">
            <h3 className={styles.sectionTitle}>Color Palette</h3>
            <ColorPalette 
              palette={getCurrentPalette()} 
              selectable={!!onColorSelect}
              onColorSelect={onColorSelect}
              size="md"
            />
          </div>
          
          {/* Color variations display */}
          {variations.length > 0 && (
            <div className="mb-6">
              <h3 className={styles.sectionTitle}>Color Variations</h3>
              <div className={styles.variationsGrid}>
                {/* Original concept */}
                <div
                  className={`variation-item ${variationItemStyles} ${selectedVariation === null ? selectedVariationStyles : nonSelectedVariationStyles}`}
                  onClick={() => setSelectedVariation(null)}
                >
                  <div className="bg-gray-50 rounded-lg overflow-hidden">
                    <img 
                      src={concept.imageUrl} 
                      alt="Original concept" 
                      className="w-full h-32 object-contain"
                    />
                  </div>
                  <div className="p-1 text-center bg-white text-xs">
                    <span className="font-medium text-gray-700">Original</span>
                    <div className={styles.colorDotsContainer}>
                      {concept.colorPalette && Object.entries(concept.colorPalette)
                        .filter(([key]) => key !== 'additionalColors')
                        .map(([_, color], colorIndex) => (
                          <div 
                            key={`color-original-${colorIndex}`}
                            className={styles.colorDot}
                            style={{ backgroundColor: color as string }}
                            title={color as string}
                          />
                        ))}
                    </div>
                  </div>
                </div>
                
                {/* Color variations */}
                {variations.map((variation, index) => (
                  <div
                    key={`variation-${index}`}
                    className={`variation-item ${variationItemStyles} ${selectedVariation === index ? selectedVariationStyles : nonSelectedVariationStyles}`}
                    onClick={() => setSelectedVariation(index)}
                  >
                    <div className="bg-gray-50 rounded-lg overflow-hidden">
                      <img 
                        src={variation.image_url} 
                        alt={`Color variation: ${variation.name}`} 
                        className="w-full h-32 object-contain"
                        onError={(e) => {
                          console.error('Error loading variation image:', variation.image_url);
                          e.currentTarget.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMjAwIiBoZWlnaHQ9IjIwMCIgZmlsbD0iI2YwZjBmZiIvPjx0ZXh0IHg9IjUwJSIgeT0iNTAlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTYiIGZpbGw9IiM5OTk5OTkiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGFsaWdubWVudC1iYXNlbGluZT0ibWlkZGxlIj5JbWFnZSBOb3QgTG9hZGVkPC90ZXh0Pjwvc3ZnPg==';
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
              <Button
                variant="secondary"
                onClick={onRefineRequest}
              >
                Refine This Concept
              </Button>
            )}
            
            <Button
              variant="primary"
              onClick={handleDownload}
            >
              Download Image
            </Button>
          </div>
        </div>
      </Card>
    </div>
  );
}; 