import React from 'react';
import { ConceptResult } from '../../../components/concept/ConceptResult';
import { GenerationResponse } from '../../../types';
import { useNavigate } from 'react-router-dom';

interface ComparisonViewProps {
  originalConcept: {
    imageUrl: string;
    logoDescription?: string;
    themeDescription?: string;
  };
  refinedConcept: GenerationResponse;
  onColorSelect?: (color: string) => void;
  onRefineRequest?: () => void;
}

/**
 * Side-by-side comparison of original and refined concepts
 */
export const ComparisonView: React.FC<ComparisonViewProps> = ({
  originalConcept,
  refinedConcept,
  onColorSelect = () => {}, // Default to empty function
  onRefineRequest = () => {}, // Default to empty function
}) => {
  const navigate = useNavigate();
  
  // Handler to navigate to the concept details page
  const handleExport = (conceptId: string) => {
    navigate(`/concepts/${conceptId}?showExport=true`);
  };

  return (
    <>
      {/* Comparison view */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Original concept */}
        <div>
          <h2 className="text-xl font-semibold text-dark-800 mb-4">Original</h2>
          <div className="border border-dark-200 rounded-lg overflow-hidden shadow-sm">
            <img 
              src={originalConcept.imageUrl} 
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
              src={refinedConcept.imageUrl} 
              alt="Refined concept" 
              className="w-full h-auto"
            />
          </div>
        </div>
      </div>
      
      {/* Result details */}
      <div className="mt-8">
        <ConceptResult
          concept={refinedConcept}
          onRefineRequest={onRefineRequest}
          onColorSelect={onColorSelect}
          onExport={handleExport}
        />
      </div>
    </>
  );
}; 