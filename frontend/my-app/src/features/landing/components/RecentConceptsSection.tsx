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
  image_url?: string;
}

interface RecentConceptsSectionProps {
  concepts: ConceptData[];
  onEdit: (conceptId: string, variationIndex: number) => void;
  onViewDetails: (conceptId: string, variationIndex?: number) => void;
  isLoading?: boolean;
}

/**
 * Recent concepts section showing previously created concepts
 * Optimized for responsive viewing on mobile and desktop
 * 
 * Note: This component no longer uses eventService for refreshing.
 * Instead, it relies on React Query's automatic cache invalidation
 * which is triggered in the mutation hooks directly.
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
    <div className="mt-10 sm:mt-16 mb-8 sm:mb-12">
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-4 sm:p-6 md:p-8 relative overflow-hidden">
        {/* Enhanced gradient background accents */}
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-indigo-100/40 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-20 -left-20 w-60 h-60 bg-indigo-50/60 rounded-full blur-2xl"></div>
        <div className="absolute top-1/4 left-1/3 w-40 h-40 bg-purple-50/30 rounded-full blur-xl"></div>
        
        <div className="relative z-10">
          {/* Header with view all link */}
          <div className="flex justify-between items-center mb-4 sm:mb-8">
            <h2 className="text-xl sm:text-2xl font-bold text-indigo-900 flex items-center">
              {isLoading ? 'Loading Recent Concepts...' : 'Recent Concepts'}
              <span className="ml-2 text-xs py-1 px-2 bg-indigo-100 text-indigo-700 rounded-full">Gallery</span>
            </h2>
            <Link 
              to="/recent" 
              className="text-indigo-600 hover:text-indigo-800 transition-colors text-sm font-medium flex items-center"
            >
              <span className="mr-1">View All</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
              </svg>
            </Link>
          </div>
          
          {/* Grid with responsive columns - 1 column on mobile, 2 on medium screens, 3 on large */}
          {/* Added min-h-full to ensure consistent heights across cards */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
            {isLoading ? renderSkeletonCards() : concepts.map((concept) => {
              // Check if sample concept (using direct image) or normal concept (using Supabase storage)
              const isSampleConcept = concept.id.startsWith('sample-');
              
              // For sample concepts, directly use the image_url without modification
              let cardImages = concept.images || [];
              let includeOriginal = false;
              
              if (isSampleConcept && concept.image_url) {
                // For sample concepts, use the image_url directly as a simple image
                cardImages = [];  // Don't provide any images to avoid Supabase signed URL processing
              } else if (concept.originalImage) {
                // For real concepts with originalImage, use standard processing
                cardImages = concept.originalImage 
                  ? [concept.originalImage, ...(concept.images || [])] 
                  : concept.images || [];
                includeOriginal = !!concept.originalImage;
              }
              
              return (
                <div key={concept.id} className="h-full flex">
                  <div className="flex-1 flex flex-col transform transition-all duration-300 hover:-translate-y-1 hover:shadow-lg">
                    <ConceptCard
                      title={concept.title}
                      description={concept.description}
                      colorVariations={concept.colorVariations}
                      images={cardImages}
                      gradient={concept.gradient}
                      initials={concept.initials}
                      includeOriginal={includeOriginal}
                      editButtonText="Refine"
                      onEdit={(index) => {
                        const adjustedIndex = concept.originalImage && index === 0 ? -1 : index - (concept.originalImage ? 1 : 0);
                        onEdit(concept.id, adjustedIndex);
                      }}
                      onViewDetails={(index: number) => {
                        const adjustedIndex = concept.originalImage && index === 0 ? -1 : index - (concept.originalImage ? 1 : 0);
                        onViewDetails(concept.id, adjustedIndex);
                      }}
                      // Pass image_url directly for sample concepts
                      sampleImageUrl={isSampleConcept ? concept.image_url : undefined}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}; 