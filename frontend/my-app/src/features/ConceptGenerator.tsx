import React, { useState } from 'react';
import { ConceptForm } from '../components/concept/ConceptForm';
import { ConceptResult } from '../components/concept/ConceptResult';
import { GenerationResponse } from '../types';
import { useConceptGeneration } from '../hooks/useConceptGeneration';

/**
 * Feature component for generating new concepts
 */
export const ConceptGenerator: React.FC = () => {
  const { 
    generateConcept, 
    resetGeneration, 
    status, 
    result, 
    error,
    isLoading
  } = useConceptGeneration();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  const handleGenerateConcept = (logoDescription: string, themeDescription: string) => {
    generateConcept(logoDescription, themeDescription);
    setSelectedColor(null);
  };
  
  const handleReset = () => {
    resetGeneration();
    setSelectedColor(null);
  };
  
  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    
    // Copy color to clipboard
    navigator.clipboard.writeText(color)
      .then(() => {
        // Could show a toast notification here
        console.log(`Copied ${color} to clipboard`);
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  };
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-dark-900 mb-2">
          Create Visual Concepts
        </h1>
        <p className="text-dark-600 max-w-2xl mx-auto">
          Describe your logo and theme to generate visual concepts. Our AI will create a logo design and color palette based on your descriptions.
        </p>
      </div>
      
      <ConceptForm
        onSubmit={handleGenerateConcept}
        status={status}
        error={error}
        onReset={handleReset}
      />
      
      {status === 'success' && result && (
        <div className="mt-8 pt-8 border-t border-dark-200">
          <ConceptResult
            concept={result}
            onRefineRequest={() => {
              // This would navigate to the refinement page with the current concept
              console.log('Navigate to refinement with:', result.generationId);
            }}
            onColorSelect={(color) => handleColorSelect(color)}
          />
          
          {selectedColor && (
            <div className="mt-4 text-center text-sm text-dark-600">
              <span className="bg-dark-100 px-2 py-1 rounded font-mono">
                {selectedColor}
              </span>
              <span className="ml-2">
                copied to clipboard
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}; 