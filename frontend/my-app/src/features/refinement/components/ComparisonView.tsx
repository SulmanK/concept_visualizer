import React from 'react';
import { ConceptResult } from '../../../components/concept/ConceptResult';
import { useConceptDetail } from '../../../hooks/useConceptQueries';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';
import { Card } from '../../../components/ui/Card';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';

interface ComparisonViewProps {
  originalImageUrl: string;
  refinedConceptId: string;
  onColorSelect?: (color: string) => void;
  selectedColor?: string | null;
}

/**
 * Side-by-side comparison of original and refined concepts
 */
export const ComparisonView: React.FC<ComparisonViewProps> = ({
  originalImageUrl,
  refinedConceptId,
  onColorSelect = () => {}, // Default to empty function
  selectedColor = null,
}) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Fetch the refined concept details
  const { 
    data: refinedConcept, 
    isLoading,
    error 
  } = useConceptDetail(refinedConceptId, user?.id);
  
  // Handler to navigate to the concept details page
  const handleExport = (conceptId: string) => {
    navigate(`/concepts/${conceptId}?showExport=true`);
  };

  // Handler to view details
  const handleViewDetails = () => {
    if (refinedConcept?.id) {
      navigate(`/concepts/${refinedConcept.id}`);
    }
  };

  if (isLoading) {
    return (
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-indigo-900 mb-4">Comparing Results</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <SkeletonLoader type="image" height="250px" />
          <SkeletonLoader type="image" height="250px" />
        </div>
      </div>
    );
  }

  if (error || !refinedConcept) {
    return (
      <Card className="p-6 text-center">
        <h2 className="text-xl font-semibold text-red-600 mb-4">Error Loading Refined Concept</h2>
        <p className="text-indigo-700 mb-6">
          We encountered an error while loading the refined concept.
        </p>
        <button
          onClick={() => navigate('/')}
          className="px-4 py-2 bg-indigo-600 text-white rounded-lg"
        >
          Return Home
        </button>
      </Card>
    );
  }

  return (
    <>
      {/* Comparison view */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
        {/* Original concept */}
        <div>
          <h2 className="text-xl font-semibold text-indigo-900 mb-4">Original</h2>
          <div className="border border-indigo-100 rounded-lg overflow-hidden shadow-md">
            <img 
              src={originalImageUrl} 
              alt="Original concept" 
              className="w-full h-auto"
            />
          </div>
        </div>
        
        {/* Refined concept */}
        <div>
          <h2 className="text-xl font-semibold text-indigo-900 mb-4">Refined</h2>
          <div className="border border-indigo-100 rounded-lg overflow-hidden shadow-md">
            <img 
              src={refinedConcept.image_url} 
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
          onColorSelect={onColorSelect}
          selectedColor={selectedColor}
          variations={refinedConcept.variations || []}
          onViewDetails={handleViewDetails}
          onExport={handleExport}
        />
      </div>
      
      {/* Selected color feedback */}
      {selectedColor && (
        <div className="mt-4 text-center text-sm text-indigo-600">
          <span className="bg-indigo-50 px-2 py-1 rounded font-mono">
            {selectedColor}
          </span>
          <span className="ml-2">
            copied to clipboard
          </span>
        </div>
      )}
    </>
  );
}; 