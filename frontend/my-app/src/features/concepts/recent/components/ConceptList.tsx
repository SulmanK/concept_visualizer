import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useRecentConcepts } from '../../../../hooks/useConceptQueries';
import { useAuth } from '../../../../contexts/AuthContext';
import { ConceptCard } from './ConceptCard';
import { ConceptData } from '../../../../services/supabaseClient';

/**
 * Displays a list of recently generated concepts
 */
export const ConceptList: React.FC = () => {
  const { user } = useAuth();
  const { 
    data: recentConcepts = [],
    isLoading: loadingConcepts,
    error,
    refetch: refreshConcepts
  } = useRecentConcepts(user?.id, 10);
  
  const errorLoadingConcepts = error ? (error as Error).message : null;
  const navigate = useNavigate();
  
  // Handle navigation to the edit/refine page
  const handleEdit = (conceptId: string, variationIndex: number) => {
    const concept = recentConcepts.find((c: ConceptData) => c.id === conceptId);
    if (!concept) {
      navigate(`/refine/${conceptId}`);
      return;
    }
    
    // If variationIndex is -1, it means the original image is selected
    if (variationIndex === -1) {
      navigate(`/refine/${conceptId}`);
      return;
    }
    
    const variation = concept.color_variations && 
                      variationIndex < concept.color_variations.length ? 
                      concept.color_variations[variationIndex] : null;
    
    const variationId = variation ? variation.id : null;
    
    if (variationId) {
      navigate(`/refine/${conceptId}?colorId=${variationId}`);
    } else {
      navigate(`/refine/${conceptId}`);
    }
  };
  
  // Handle navigation to the concept details page
  const handleViewDetails = (conceptId: string, variationIndex: number) => {
    console.log('handleViewDetails called with:', { conceptId, variationIndex });
    
    const concept = recentConcepts.find((c: ConceptData) => c.id === conceptId);
    if (!concept) {
      console.log('Concept not found, navigating to default:', `/concepts/${conceptId}`);
      navigate(`/concepts/${conceptId}`);
      return;
    }
    
    console.log('Concept found:', { 
      id: concept.id, 
      hasVariations: (concept.color_variations?.length || 0) > 0,
      variationsCount: concept.color_variations?.length || 0 
    });
    
    // If variationIndex is -1, it means the original image is selected
    if (variationIndex === -1) {
      console.log('Original image selected, navigating to:', `/concepts/${conceptId}`);
      navigate(`/concepts/${conceptId}`);
      return;
    }
    
    const variation = concept.color_variations && 
                      variationIndex < concept.color_variations.length ? 
                      concept.color_variations[variationIndex] : null;
    
    console.log('Selected variation:', { 
      index: variationIndex, 
      variation: variation ? { id: variation.id, name: variation.palette_name } : null 
    });
    
    const variationId = variation ? variation.id : null;
    
    if (variationId) {
      console.log('Navigating to variation:', `/concepts/${conceptId}?colorId=${variationId}`);
      navigate(`/concepts/${conceptId}?colorId=${variationId}`);
    } else {
      console.log('No valid variation found, navigating to default:', `/concepts/${conceptId}`);
      navigate(`/concepts/${conceptId}`);
    }
  };
  
  // Log component state on each render for debugging
  console.log('ConceptList render state:', { 
    conceptsCount: recentConcepts.length || 0, 
    loading: loadingConcepts, 
    error: errorLoadingConcepts,
    firstConcept: recentConcepts.length > 0 ? {
      id: recentConcepts[0].id,
      base_image_url: recentConcepts[0].base_image_url,
      has_variations: (recentConcepts[0].color_variations?.length || 0) > 0
    } : null
  });
  
  // Handle empty state
  if (!loadingConcepts && (!recentConcepts || recentConcepts.length === 0)) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-xl font-semibold text-indigo-800 mb-8">Recent Concepts</h2>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-indigo-800 mb-4">No concepts yet</h3>
          <p className="text-indigo-600 mb-6">
            Your recent concepts will appear here after you generate them.
          </p>
          <Link 
            to="/create" 
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Create New Concept
          </Link>
        </div>
      </div>
    );
  }
  
  // Handle loading state
  if (loadingConcepts) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-xl font-semibold text-indigo-800 mb-8">Recent Concepts</h2>
        <div className="animate-pulse">
          <div className="h-6 bg-indigo-200 rounded mb-4 w-3/4 mx-auto"></div>
          <div className="h-20 bg-indigo-100 rounded mb-4"></div>
          <div className="h-4 bg-indigo-100 rounded mb-2 w-1/2 mx-auto"></div>
          <div className="h-4 bg-indigo-100 rounded w-2/3 mx-auto"></div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-xl font-semibold text-indigo-800 mb-8">Recent Concepts</h2>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Error Loading Concepts</h3>
          <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
          <button 
            onClick={() => refreshConcepts()}
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Safety check for null concepts array
  if (!recentConcepts || !Array.isArray(recentConcepts)) {
    console.error('recentConcepts is not an array:', recentConcepts);
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <h2 className="text-xl font-semibold text-indigo-800 mb-8">Recent Concepts</h2>
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Something went wrong</h3>
          <p className="text-indigo-600 mb-6">Invalid data received from the server</p>
          <button 
            onClick={() => refreshConcepts()}
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-semibold"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Render the list of concepts
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
      <h2 className="text-xl font-semibold text-indigo-800 mb-8">Recent Concepts</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        {recentConcepts.map((concept: ConceptData) => {
          // Add a safety check for each concept before rendering
          if (!concept || !concept.base_image_url) {
            console.warn('Invalid concept data:', concept);
            return null;
          }
          
          return (
            <div key={concept.id} className="h-full">
              <ConceptCard 
                concept={concept}
                preventNavigation={true}
                onEdit={handleEdit}
                onViewDetails={handleViewDetails}
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}; 