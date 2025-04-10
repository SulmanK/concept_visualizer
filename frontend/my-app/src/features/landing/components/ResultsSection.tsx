import React from 'react';
import { ConceptResult } from '../../../components/concept/ConceptResult';
import { useConceptDetail } from '../../../hooks/useConceptQueries';
import { Button } from '../../../components/ui/Button';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../../contexts/AuthContext';

interface ResultsSectionProps {
  conceptId: string;
  onEdit: (conceptId: string, variationId?: string | null) => void;
  onViewDetails: (conceptId: string, variationId?: string | null) => void;
  onColorSelect: (color: string) => void;
  selectedColor: string | null;
}

/**
 * Results section showing the generated concept
 * Optimized for both mobile and desktop viewing
 */
export const ResultsSection: React.FC<ResultsSectionProps> = ({
  conceptId,
  onEdit,
  onViewDetails,
  onColorSelect,
  selectedColor
}) => {
  const navigate = useNavigate();
  const { user } = useAuth();
  
  // Fetch the concept details
  const { data: concept, isLoading } = useConceptDetail(conceptId, user?.id);

  // If no concept and not loading, render nothing
  if (!concept && !isLoading) return null;

  // Handler to navigate to the concept details page
  const handleExport = (conceptId: string) => {
    navigate(`/concepts/${conceptId}?showExport=true`);
  };

  return (
    <div className="mb-8 sm:mb-16">
      <div className="bg-white/90 backdrop-blur-sm rounded-lg shadow-modern border border-indigo-100 p-4 sm:p-6 md:p-8 mb-4 sm:mb-8">
        <div className="flex flex-col sm:flex-row sm:justify-between sm:items-center mb-4 sm:mb-6">
          <h2 className="text-lg sm:text-xl font-semibold text-indigo-900 mb-3 sm:mb-0">
            {isLoading ? 'Loading Concept...' : 'Generated Concept'}
          </h2>
        </div>
        
        {isLoading ? (
          <div className="space-y-6 sm:space-y-8">
            {/* Skeleton for the image */}
            <div className="flex justify-center">
              <div className="w-full" style={{ maxWidth: '300px' }}>
                <SkeletonLoader type="image" width="100%" height="300px" />
              </div>
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
            <div className="flex flex-col sm:flex-row sm:justify-end space-y-2 sm:space-y-0 sm:space-x-3 mt-4 sm:mt-6">
              <div className="w-full sm:w-auto" style={{ maxWidth: '120px' }}>
                <SkeletonLoader type="button" width="100%" />
              </div>
              <div className="w-full sm:w-auto" style={{ maxWidth: '120px' }}>
                <SkeletonLoader type="button" width="100%" />
              </div>
            </div>
          </div>
        ) : concept ? (
          <ConceptResult
            concept={concept}
            onColorSelect={onColorSelect}
            selectedColor={selectedColor}
            variations={concept.variations || []}
            onEdit={() => onEdit(concept.id)}
            onViewDetails={() => onViewDetails(concept.id)}
            onExport={handleExport}
          />
        ) : null}
      </div>
    </div>
  );
}; 