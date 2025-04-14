import React from 'react';
import { ConceptCard } from '../../../components/ui/ConceptCard';
import { SkeletonLoader } from '../../../components/ui/SkeletonLoader';
import { Link } from 'react-router-dom';
import { ConceptData } from '../../../services/supabaseClient';

interface RecentConceptsSectionProps {
  concepts: Array<ConceptData>;
  onEdit: (conceptId: string, variationId?: string | null) => void;
  onViewDetails: (conceptId: string, variationId?: string | null) => void;
  isLoading?: boolean;
}

/**
 * Helper function to adapt Concept data for the UI ConceptCard
 * with additional safety checks to prevent errors
 */
function adaptConceptForUiCard(concept: ConceptData) {
  if (!concept) {
    console.warn('Received null or undefined concept in adaptConceptForUiCard');
    // Return default data if concept is null or undefined
    return {
      title: "Missing Concept",
      description: "No data available",
      colorVariations: [['#4F46E5', '#60A5FA', '#1E293B']],
      images: [],
      initials: "NA",
      includeOriginal: false,
      gradient: { from: 'blue-400', to: 'indigo-500' },
      colorData: [],
      id: 'missing'
    };
  }

  try {
    // Get initials from the logo description (with safety checks)
    const logoDescription = concept.logo_description || "Untitled";
    const words = logoDescription.trim().split(/\s+/);
    const initials = words.length === 1 
      ? words[0].substring(0, 2).toUpperCase()
      : (words[0][0] + (words.length > 1 ? words[1][0] : '')).toUpperCase();
    
    // Create color variations array - each variation has its own set of colors
    const colorVariations = concept.color_variations?.map(variation => 
      Array.isArray(variation.colors) && variation.colors.length > 0 
        ? variation.colors 
        : ['#4F46E5']
    ) || [];
    
    // If no color variations, provide a fallback
    if (!colorVariations || colorVariations.length === 0) {
      colorVariations.push(['#4F46E5', '#60A5FA', '#1E293B']);
    }
    
    // Get images from color variations (with safety checks)
    const images = (concept.color_variations || [])
      .map(variation => variation?.image_url)
      .filter(Boolean) || [];
    
    // Add the original image as the first item if it exists
    const originalImage = concept.image_url || concept.base_image_url;
    if (originalImage) {
      images.unshift(originalImage);
    }
    
    // Create colorData for mapping indices to variation IDs
    const colorData = (concept.color_variations || []).map(variation => ({
      id: variation.id,
      colors: Array.isArray(variation.colors) ? variation.colors : ['#4F46E5']
    }));
    
    console.log(`[adaptConceptForUiCard] Adapted concept ${concept.id}:`, {
      variationsCount: colorVariations.length, 
      imagesCount: images.length
    });
    
    return {
      title: concept.logo_description || "Untitled Concept",
      description: concept.theme_description || "No description available",
      colorVariations,
      images,
      initials,
      includeOriginal: !!originalImage,
      gradient: { from: 'blue-400', to: 'indigo-500' },
      colorData,
      id: concept.id
    };
  } catch (error) {
    console.error('Error in adaptConceptForUiCard:', error);
    // Return a safe fallback on error
    return {
      title: "Error Processing Concept",
      description: "An error occurred while processing this concept",
      colorVariations: [['#4F46E5', '#60A5FA', '#1E293B']],
      images: [],
      initials: "ER",
      includeOriginal: false,
      gradient: { from: 'red-400', to: 'red-600' },
      colorData: [],
      id: concept?.id || 'error'
    };
  }
}

/**
 * Recent concepts section showing previously created concepts
 * Optimized for responsive viewing on mobile and desktop
 * Uses direct ConceptCards like in ConceptList
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
  
  // Handle click on edit button
  const handleEdit = (conceptId: string, variationId?: string | null) => {
    console.log('[RecentConceptsSection] Edit clicked:', { conceptId, variationId });
    onEdit(conceptId, variationId);
  };
  
  // Handle click on view details button
  const handleViewDetails = (conceptId: string, variationId?: string | null) => {
    console.log('[RecentConceptsSection] View details clicked:', { conceptId, variationId });
    onViewDetails(conceptId, variationId);
  };
  
  return (
    <div className="mt-10 sm:mt-16 mb-8 sm:mb-12">
      <div className="bg-white shadow-lg border border-indigo-100 p-4 sm:p-6 md:p-8 relative overflow-hidden rounded-xl">
        {/* Enhanced gradient background accents - removed for consistency with form */}
        
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
          
          {/* Grid with responsive columns */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6 md:gap-8">
            {isLoading ? renderSkeletonCards() : concepts.map((concept) => {
              // Adapt the concept for the UI card using our helper function
              const adaptedConcept = adaptConceptForUiCard(concept);
              
              // Check if sample concept (using direct image) or normal concept
              const isSampleConcept = concept.id.startsWith('sample-');
              const sampleImageUrl = isSampleConcept ? concept.image_url : undefined;
              
              return (
                <div key={concept.id} className="h-full">
                  <ConceptCard 
                    title={adaptedConcept.title}
                    description={adaptedConcept.description}
                    colorVariations={adaptedConcept.colorVariations}
                    images={adaptedConcept.images}
                    initials={adaptedConcept.initials}
                    includeOriginal={adaptedConcept.includeOriginal}
                    gradient={adaptedConcept.gradient}
                    colorData={adaptedConcept.colorData}
                    sampleImageUrl={sampleImageUrl}
                    editButtonText="Refine"
                    onEdit={(index) => {
                      // Map the index to a variation ID
                      let variationId = null;
                      
                      if (index > 0 && adaptedConcept.colorData && index - 1 < adaptedConcept.colorData.length) {
                        variationId = adaptedConcept.colorData[index - 1].id;
                      }
                      
                      handleEdit(concept.id, variationId);
                    }}
                    onViewDetails={(index) => {
                      // Map the index to a variation ID
                      let variationId = null;
                      
                      if (index > 0 && adaptedConcept.colorData && index - 1 < adaptedConcept.colorData.length) {
                        variationId = adaptedConcept.colorData[index - 1].id;
                      }
                      
                      handleViewDetails(concept.id, variationId);
                    }}
                  />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}; 