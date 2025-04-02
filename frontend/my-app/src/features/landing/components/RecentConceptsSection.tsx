import React from 'react';
import { ConceptCard } from '../../../components/ui/ConceptCard';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { Link } from 'react-router-dom';

interface ConceptData {
  id: string;
  title: string;
  description: string;
  colorVariations: string[][];
  gradient: {
    from: string;
    to: string;
  };
  initials: string;
  images?: string[];
  originalImage?: string;
}

interface RecentConceptsSectionProps {
  concepts: ConceptData[];
  onEdit: (conceptId: string, variationIndex: number) => void;
  onViewDetails: (conceptId: string) => void;
  isLoading?: boolean;
}

/**
 * Recent concepts section showing previously created concepts
 */
export const RecentConceptsSection: React.FC<RecentConceptsSectionProps> = ({
  concepts,
  onEdit,
  onViewDetails,
  isLoading = false
}) => {
  // If there are no concepts and not loading, don't render the section
  if (!concepts || concepts.length === 0 && !isLoading) {
    return null;
  }
  
  // Render skeleton cards when loading
  const renderSkeletonCards = () => {
    return Array.from({ length: 3 }).map((_, index) => (
      <div key={`skeleton-${index}`} className="h-full">
        <SkeletonLoader type="card" height="360px" className="rounded-xl" />
      </div>
    ));
  };
  
  return (
    <div className="mt-16 mb-12">
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 relative overflow-hidden">
        {/* Subtle gradient background accents */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-100/30 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-indigo-50/50 rounded-full blur-2xl"></div>
        
        <div className="relative z-10">
          {/* Header with view all link */}
          <div className="flex justify-between items-center mb-8">
            <h2 className="text-2xl font-bold text-indigo-900">
              {isLoading ? 'Loading Recent Concepts...' : 'Recent Concepts'}
            </h2>
            <Link 
              to="/recent" 
              className="text-indigo-600 hover:text-indigo-800 transition-colors text-sm font-medium flex items-center"
            >
              View All
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-1" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          </div>
          
          {/* Grid with consistent card heights */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {isLoading ? renderSkeletonCards() : concepts.map((concept) => (
              <div key={concept.id} className="h-full transform transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                <ConceptCard
                  title={concept.title}
                  description={concept.description}
                  colorVariations={concept.colorVariations}
                  images={concept.originalImage 
                    ? [concept.originalImage, ...(concept.images || [])] 
                    : concept.images}
                  gradient={concept.gradient}
                  initials={concept.initials}
                  includeOriginal={!!concept.originalImage}
                  editButtonText="Refine"
                  onEdit={(index) => {
                    const adjustedIndex = concept.originalImage && index === 0 ? -1 : index - (concept.originalImage ? 1 : 0);
                    onEdit(concept.id, adjustedIndex);
                  }}
                  onViewDetails={() => onViewDetails(concept.id)}
                />
              </div>
            ))}
          </div>
          
          {/* Additional CTA for empty spots or if we have fewer than 3 concepts */}
          {!isLoading && concepts.length < 3 && (
            <div className="mt-8 text-center">
              <Link 
                to="/create" 
                className="inline-flex items-center px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700 transition-colors"
              >
                <span className="mr-2">✨</span>
                Create Another Concept
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}; 