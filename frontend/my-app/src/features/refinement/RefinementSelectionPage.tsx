import React, { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useConceptContext } from '../../contexts/ConceptContext';
import { ConceptCard } from '../concepts/recent/components/ConceptCard';

/**
 * Page for selecting a concept to refine
 */
export const RefinementSelectionPage: React.FC = () => {
  const navigate = useNavigate();
  const { recentConcepts, loadingConcepts, errorLoadingConcepts, refreshConcepts } = useConceptContext();
  
  // Fetch concepts on component mount
  useEffect(() => {
    refreshConcepts();
    // We intentionally exclude refreshConcepts from the dependency array
    // to prevent an infinite loop
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);
  
  // Handle selecting a concept to refine
  const handleSelectConcept = (conceptId: string) => {
    navigate(`/refine/${conceptId}`);
  };
  
  // Handle loading state
  if (loadingConcepts) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
          <p className="text-indigo-600 max-w-2xl mx-auto">
            Choose one of your concepts to refine and improve.
          </p>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center" data-testid="loading-skeleton">
          <div className="animate-pulse">
            <div className="h-8 bg-indigo-200 rounded w-1/3 mb-8 mx-auto"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {[...Array(3)].map((_, i) => (
                <div key={i} className="h-64 bg-indigo-100 rounded-lg"></div>
              ))}
            </div>
          </div>
        </div>
      </div>
    );
  }
  
  // Handle error state
  if (errorLoadingConcepts) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-red-600 mb-4">Error</h2>
          <p className="text-indigo-600 mb-6">{errorLoadingConcepts}</p>
          <button 
            onClick={() => refreshConcepts()}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }
  
  // Handle empty state
  if (!recentConcepts || recentConcepts.length === 0) {
    return (
      <div className="max-w-6xl mx-auto px-4 py-8">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-900 mb-2">
            Select a Concept to Refine
          </h1>
        </div>
        
        <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 text-center">
          <h2 className="text-xl font-semibold text-indigo-800 mb-4">No Concepts Available</h2>
          <p className="text-indigo-600 mb-6">
            You need to create concepts before you can refine them.
          </p>
          <button
            onClick={() => navigate('/create')}
            className="inline-block px-4 py-2 bg-indigo-600 text-white rounded-full"
          >
            Create New Concept
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-indigo-900 mb-2">
          Select a Concept to Refine
        </h1>
        <p className="text-indigo-600 max-w-2xl mx-auto">
          Choose one of your concepts to refine and improve.
        </p>
      </div>
      
      <div className="bg-white/90 backdrop-blur-sm rounded-xl shadow-md p-8 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {recentConcepts.map((concept) => (
            <div 
              key={concept.id}
              onClick={() => handleSelectConcept(concept.id)}
              className="cursor-pointer transform transition-transform hover:scale-105"
            >
              <ConceptCard concept={concept} />
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 