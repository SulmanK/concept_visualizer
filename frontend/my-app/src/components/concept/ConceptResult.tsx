import React from 'react';
import { GenerationResponse } from '../../types';
import { Card } from '../ui/Card';
import { Button } from '../ui/Button';
import { ColorPalette } from '../ui/ColorPalette';

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
}

/**
 * Component for displaying generated concept results
 */
export const ConceptResult: React.FC<ConceptResultProps> = ({
  concept,
  onRefineRequest,
  onDownload,
  onColorSelect,
}) => {
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
    link.href = concept.imageUrl;
    link.download = getFileName(concept.imageUrl);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };
  
  return (
    <div className="max-w-2xl mx-auto">
      <Card
        variant="elevated"
        className="shadow-lg"
        header={
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold text-dark-900">Generated Concept</h2>
            <span className="text-sm text-dark-500">
              {new Date(concept.createdAt).toLocaleString()}
            </span>
          </div>
        }
      >
        <div className="space-y-6">
          {/* Image display */}
          <div className="flex justify-center">
            <div className="relative overflow-hidden rounded-lg border border-dark-200 shadow-sm">
              <img 
                src={concept.imageUrl} 
                alt="Generated concept" 
                className="w-full h-auto max-h-96 object-contain"
              />
            </div>
          </div>
          
          {/* Color palette */}
          <div>
            <h3 className="text-lg font-medium text-dark-800 mb-2">Color Palette</h3>
            <ColorPalette 
              palette={concept.colorPalette} 
              selectable={!!onColorSelect}
              onColorSelect={onColorSelect}
              size="md"
            />
          </div>
          
          {/* Actions */}
          <div className="flex flex-wrap justify-end gap-3 pt-2">
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