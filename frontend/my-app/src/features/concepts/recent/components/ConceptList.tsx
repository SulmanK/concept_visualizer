import React, { useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useRecentConcepts } from '../../../../hooks/useConceptQueries';
import { useAuth } from '../../../../contexts/AuthContext';
import { useQueryClient } from '@tanstack/react-query';
import { ConceptCard } from '../../../../components/ui/ConceptCard';
import { ConceptData } from '../../../../services/supabaseClient';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

/**
 * Custom hook to fetch recent concepts with logging
 * We now rely on standard React Query cache behavior
 */
function useRecentConceptsWithLogging(userId: string | undefined, limit: number = 10) {
  // Get data using the standard hook
  const result = useRecentConcepts(userId, limit);
  
  // Add debug logging
  useEffect(() => {
    if (userId) {
      console.log('[useRecentConceptsWithLogging] Using recent concepts hook for userId:', userId);
    }
  }, [userId]);
  
  return result;
}

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
  } = useRecentConceptsWithLogging(user?.id, 10);
  
  const errorLoadingConcepts = error ? (error as Error).message : null;
  const navigate = useNavigate();
  
  // Handle navigation to the edit/refine page
  const handleEdit = (conceptId: string, variationId?: string | null) => {
    console.log('[ConceptList] Edit clicked:', { conceptId, variationId });
    
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      console.warn('Cannot edit sample concept');
      return;
    }
    
    // If we have a variation ID, add it as a query parameter
    if (variationId) {
      console.log(`Navigating to refine with variation: /refine/${conceptId}?colorId=${variationId}`);
      navigate(`/refine/${conceptId}?colorId=${variationId}`);
    } else {
      // Otherwise navigate to the concept without a variation
      console.log(`Navigating to refine original: /refine/${conceptId}`);
      navigate(`/refine/${conceptId}`);
    }
  };
  
  // Handle navigation to the concept details page
  const handleViewDetails = (conceptId: string, variationId?: string | null) => {
    console.log('[ConceptList] View details clicked:', { conceptId, variationId });
    
    // Check if this is a sample concept
    if (conceptId.startsWith('sample-')) {
      console.warn('Cannot view sample concept details');
      return;
    }
    
    // If we have a variation ID, add it as a query parameter
    if (variationId) {
      console.log(`Navigating to details with variation: /concepts/${conceptId}?colorId=${variationId}`);
      navigate(`/concepts/${conceptId}?colorId=${variationId}`);
    } else {
      // Otherwise navigate to the concept without a variation
      console.log(`Navigating to details original: /concepts/${conceptId}`);
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Recent Concepts</h2>
          <Link 
            to="/create" 
            className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center"
          >
            View All
            <ChevronRightIcon className="w-4 h-4 ml-1" />
          </Link>
        </div>

        <div className="text-center py-10">
          <div className="text-gray-300 text-4xl mb-4">📁</div>
          <h3 className="text-lg font-semibold text-gray-800 mb-4">No concepts yet</h3>
          <p className="text-gray-500 mb-6 max-w-md mx-auto">
            Your recently generated concepts will appear here after you create them.
          </p>
          <Link 
            to="/create" 
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-medium hover:bg-indigo-700"
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Recent Concepts</h2>
          <Link 
            to="/concepts" 
            className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center"
          >
            View All
            <ChevronRightIcon className="w-4 h-4 ml-1" />
          </Link>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
          {[1, 2, 3].map((i) => (
            <div key={i} className="animate-pulse">
              <div className="bg-indigo-100 h-24 rounded-t-lg mb-14"></div>
              <div className="px-4">
                <div className="bg-indigo-100 h-6 w-3/4 rounded mb-4 mx-auto"></div>
                <div className="bg-indigo-50 h-4 rounded mb-2"></div>
                <div className="bg-indigo-50 h-4 w-5/6 rounded mb-4 mx-auto"></div>
                <div className="flex justify-center space-x-2 mb-4">
                  {[1, 2, 3, 4].map((j) => (
                    <div key={j} className="bg-indigo-200 w-6 h-6 rounded-full"></div>
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-2 mt-4">
                  <div className="bg-gray-100 h-8 rounded"></div>
                  <div className="bg-indigo-100 h-8 rounded"></div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Recent Concepts</h2>
          <Link 
            to="/concepts" 
            className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center"
          >
            View All
            <ChevronRightIcon className="w-4 h-4 ml-1" />
          </Link>
        </div>
        
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Error Loading Concepts</h3>
          <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
          <button 
            onClick={() => refreshConcepts()}
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-medium"
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-800">Recent Concepts</h2>
          <Link 
            to="/concepts" 
            className="text-indigo-600 text-sm font-medium hover:text-indigo-700 flex items-center"
          >
            View All
            <ChevronRightIcon className="w-4 h-4 ml-1" />
          </Link>
        </div>
        
        <div className="text-center">
          <h3 className="text-lg font-semibold text-red-600 mb-4">Something went wrong</h3>
          <p className="text-indigo-600 mb-6">Invalid data received from the server</p>
          <button 
            onClick={() => refreshConcepts()}
            className="btn-primary inline-block px-4 py-2 bg-indigo-600 text-white rounded-md font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Render the grid of concepts
  return (
    <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-modern border border-indigo-100 p-8 mb-8">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {recentConcepts.map((concept: ConceptData) => {
          // Add a safety check for each concept before rendering
          if (!concept || !concept.id) {
            console.warn('Invalid concept data:', concept);
            return null;
          }
          
          // Get gradient colors - first color from the first variation if available
          const gradientFrom = concept.color_variations?.[0]?.colors?.[0] || '#818CF8';
          const gradientTo = concept.color_variations?.[0]?.colors?.[1] || '#4F46E5';
          
          return (
            <div key={concept.id}>
              <ConceptCard 
                concept={concept}
                preventNavigation={true}
                onEdit={handleEdit}
                onViewDetails={handleViewDetails}
                gradient={{ from: gradientFrom, to: gradientTo }}
                includeOriginal={true}
                editButtonText="Refine"
              />
            </div>
          );
        })}
      </div>
    </div>
  );
}; 