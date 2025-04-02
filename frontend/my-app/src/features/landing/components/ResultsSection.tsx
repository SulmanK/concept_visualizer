import React from 'react';
import { ConceptResult } from '../../../components/concept/ConceptResult';
import { GenerationResponse } from '../../../types';
import { Button } from '../../../components/ui/Button';
import { useNavigate } from 'react-router-dom';

interface ResultsSectionProps {
  result: GenerationResponse | null;
  onReset: () => void;
  selectedColor: string | null;
  onColorSelect: (color: string) => void;
}

/**
 * Results section showing the generated concept
 */
export const ResultsSection: React.FC<ResultsSectionProps> = ({
  result,
  onReset,
  selectedColor,
  onColorSelect
}) => {
  const navigate = useNavigate();
  
  if (!result) return null;

  // Handler to navigate to the concept details page
  const handleExport = (conceptId: string) => {
    navigate(`/concepts/${conceptId}?showExport=true`);
  };

  return (
    <div className="mb-16">
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-indigo-900">Generated Concept</h2>
          <Button 
            variant="outline" 
            onClick={onReset} 
            size="sm"
          >
            Start Over
          </Button>
        </div>
        
        <ConceptResult
          concept={result}
          onColorSelect={onColorSelect}
          variations={result.variations || []}
          onExport={handleExport}
        />
      </div>
    </div>
  );
}; 