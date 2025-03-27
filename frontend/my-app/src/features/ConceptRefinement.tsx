import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { ConceptRefinementForm } from '../components/concept/ConceptRefinementForm';
import { ConceptResult } from '../components/concept/ConceptResult';
import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { useConceptRefinement } from '../hooks/useConceptRefinement';

/**
 * Feature component for refining existing concepts
 */
export const ConceptRefinement: React.FC = () => {
  const { conceptId } = useParams<{ conceptId: string }>();
  const navigate = useNavigate();
  
  // In a real app, we would fetch the concept using the conceptId
  // For demo purposes, we'll use a mock concept
  const mockOriginalConcept = {
    imageUrl: 'https://placehold.co/800x800?text=Original+Concept',
    logoDescription: 'A modern logo for a tech company',
    themeDescription: 'Blue and purple futuristic theme',
  };
  
  const { 
    refineConcept, 
    resetRefinement, 
    status, 
    result, 
    error,
    isLoading
  } = useConceptRefinement();
  
  const [selectedColor, setSelectedColor] = useState<string | null>(null);
  
  const handleRefineConcept = (
    refinementPrompt: string,
    logoDescription: string,
    themeDescription: string,
    preserveAspects: string[]
  ) => {
    refineConcept(
      mockOriginalConcept.imageUrl,
      refinementPrompt,
      logoDescription || undefined,
      themeDescription || undefined,
      preserveAspects
    );
    setSelectedColor(null);
  };
  
  const handleReset = () => {
    resetRefinement();
    setSelectedColor(null);
  };
  
  const handleCancel = () => {
    navigate('/');
  };
  
  const handleColorSelect = (color: string) => {
    setSelectedColor(color);
    
    // Copy color to clipboard
    navigator.clipboard.writeText(color)
      .then(() => {
        console.log(`Copied ${color} to clipboard`);
      })
      .catch(err => {
        console.error('Could not copy text: ', err);
      });
  };
  
  // Loading skeleton for when we're fetching the original concept
  if (!mockOriginalConcept) {
    return (
      <Card isLoading={true} className="max-w-xl mx-auto">
        <div className="h-64"></div>
      </Card>
    );
  }
  
  return (
    <div className="space-y-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-dark-900 mb-2">
          Refine Your Concept
        </h1>
        <p className="text-dark-600 max-w-2xl mx-auto">
          Provide instructions to refine your existing concept. You can update the logo or theme description, or specify what aspects to preserve.
        </p>
      </div>
      
      {!result && (
        <ConceptRefinementForm
          originalImageUrl={mockOriginalConcept.imageUrl}
          onSubmit={handleRefineConcept}
          status={status}
          error={error}
          onCancel={handleCancel}
          initialLogoDescription={mockOriginalConcept.logoDescription}
          initialThemeDescription={mockOriginalConcept.themeDescription}
        />
      )}
      
      {status === 'success' && result && (
        <div className="mt-8 pt-8 border-t border-dark-200">
          <div className="flex justify-between mb-4">
            <Button variant="outline" onClick={handleReset}>
              Refine Again
            </Button>
            <Button variant="primary" onClick={() => navigate('/')}>
              Create New Concept
            </Button>
          </div>
          
          {/* Comparison view */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Original concept */}
            <div>
              <h2 className="text-xl font-semibold text-dark-800 mb-4">Original</h2>
              <div className="border border-dark-200 rounded-lg overflow-hidden shadow-sm">
                <img 
                  src={mockOriginalConcept.imageUrl} 
                  alt="Original concept" 
                  className="w-full h-auto"
                />
              </div>
            </div>
            
            {/* Refined concept */}
            <div>
              <h2 className="text-xl font-semibold text-dark-800 mb-4">Refined</h2>
              <div className="border border-dark-200 rounded-lg overflow-hidden shadow-sm">
                <img 
                  src={result.imageUrl} 
                  alt="Refined concept" 
                  className="w-full h-auto"
                />
              </div>
            </div>
          </div>
          
          {/* Result with details */}
          <div className="mt-8">
            <ConceptResult
              concept={result}
              onRefineRequest={handleReset}
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
        </div>
      )}
    </div>
  );
}; 