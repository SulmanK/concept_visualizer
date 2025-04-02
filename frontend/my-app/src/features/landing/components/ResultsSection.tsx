import React from 'react';
import { ConceptResult } from '../../../components/concept/ConceptResult';
import { GenerationResponse, FormStatus } from '../../../types';
import { Button } from '../../../components/ui/Button';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { useNavigate } from 'react-router-dom';

interface ResultsSectionProps {
  result: GenerationResponse | null;
  onReset: () => void;
  selectedColor: string | null;
  onColorSelect: (color: string) => void;
  status?: FormStatus;
}

/**
 * Results section showing the generated concept
 */
export const ResultsSection: React.FC<ResultsSectionProps> = ({
  result,
  onReset,
  selectedColor,
  onColorSelect,
  status = 'idle'
}) => {
  const navigate = useNavigate();
  const isLoading = status === 'submitting';
  
  // If no result and not loading, render nothing
  if (!result && !isLoading) return null;

  // Handler to navigate to the concept details page
  const handleExport = (conceptId: string) => {
    navigate(`/concepts/${conceptId}?showExport=true`);
  };

  return (
    <div className="mb-16">
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-indigo-900">
            {isLoading ? 'Generating Concept...' : 'Generated Concept'}
          </h2>
          <Button 
            variant="outline" 
            onClick={onReset} 
            size="sm"
            disabled={isLoading}
          >
            Start Over
          </Button>
        </div>
        
        {isLoading ? (
          <div className="space-y-8">
            {/* Skeleton for the image */}
            <div className="flex justify-center">
              <SkeletonLoader type="image" width="300px" height="300px" />
            </div>
            
            {/* Skeleton for the title */}
            <div>
              <SkeletonLoader type="text" lineHeight="lg" width="60%" />
              <div className="mt-2">
                <SkeletonLoader type="text" lines={2} width="100%" />
              </div>
            </div>
            
            {/* Skeleton for color palette */}
            <div className="mt-4">
              <SkeletonLoader type="text" width="120px" className="mb-2" />
              <div className="flex space-x-2">
                <SkeletonLoader type="circle" width="40px" height="40px" />
                <SkeletonLoader type="circle" width="40px" height="40px" />
                <SkeletonLoader type="circle" width="40px" height="40px" />
                <SkeletonLoader type="circle" width="40px" height="40px" />
              </div>
            </div>
            
            {/* Skeleton for buttons */}
            <div className="flex justify-end space-x-3 mt-6">
              <SkeletonLoader type="button" width="120px" />
              <SkeletonLoader type="button" width="120px" />
            </div>
          </div>
        ) : result ? (
          <ConceptResult
            concept={result}
            onColorSelect={onColorSelect}
            variations={result.variations || []}
            onExport={handleExport}
          />
        ) : null}
      </div>
    </div>
  );
}; 