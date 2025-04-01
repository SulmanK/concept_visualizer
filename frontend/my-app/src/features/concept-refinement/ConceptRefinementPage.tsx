import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useConceptRefinement } from '../../hooks/useConceptRefinement';
import { RefinementHeader } from './components/RefinementHeader';
import { RefinementForm } from './components/RefinementForm';
import { ComparisonView } from './components/ComparisonView';
import { RefinementActions } from './components/RefinementActions';
import { Card } from '../../components/ui/Card';

/**
 * Main page component for the Concept Refinement feature
 */
export const ConceptRefinementPage: React.FC = () => {
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
      <RefinementHeader />
      
      {!result && (
        <RefinementForm
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
          <RefinementActions 
            onReset={handleReset} 
            onCreateNew={() => navigate('/')} 
          />
          
          <ComparisonView 
            originalConcept={mockOriginalConcept} 
            refinedConcept={result} 
            onColorSelect={handleColorSelect}
            onRefineRequest={handleReset}
          />
          
          {/* Selected color feedback */}
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