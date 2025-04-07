/**
 * Context for managing concept data throughout the application
 */

import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { fetchRecentConcepts, ConceptData, ColorVariationData, supabase } from '../services/supabaseClient';
import { getBucketName } from '../services/configService';
import { useAuth } from './AuthContext';

interface ConceptContextType {
  // Recent concepts data
  recentConcepts: ConceptData[];
  loadingConcepts: boolean;
  errorLoadingConcepts: string | null;
  
  // Actions
  refreshConcepts: () => Promise<void>;
  clearError: () => void;
}

// Create context with default values
const ConceptContext = createContext<ConceptContextType>({
  recentConcepts: [],
  loadingConcepts: false,
  errorLoadingConcepts: null,
  refreshConcepts: async () => {},
  clearError: () => {}
});

// Hook for using the concept context
export const useConceptContext = () => useContext(ConceptContext);

interface ConceptProviderProps {
  children: ReactNode;
}

/**
 * Provider component for concept data
 */
export const ConceptProvider: React.FC<ConceptProviderProps> = ({ children }) => {
  const { user, isLoading: authLoading } = useAuth();
  const [recentConcepts, setRecentConcepts] = useState<ConceptData[]>([]);
  const [loadingConcepts, setLoadingConcepts] = useState<boolean>(false);
  const [errorLoadingConcepts, setErrorLoadingConcepts] = useState<string | null>(null);
  
  // Fetch concepts when authentication is ready
  useEffect(() => {
    if (!authLoading && user) {
      console.log('ConceptContext: Auth ready, refreshing concepts');
      refreshConcepts();
    }
  }, [authLoading, user]);
  
  /**
   * Refresh the list of concepts from the API
   */
  const refreshConcepts = async () => {
    console.log('Refreshing concepts');
    setLoadingConcepts(true);
    setErrorLoadingConcepts(null);
    
    // Get the current user ID
    const userId = user?.id;
    console.log(`Refreshing concepts for user ID: ${userId}`);
    
    if (!userId) {
      console.error('No user ID available, cannot fetch concepts');
      setErrorLoadingConcepts('No user ID available');
      setLoadingConcepts(false);
      return;
    }
    
    try {
      // Use the improved fetchRecentConcepts function that handles signed URLs
      console.log('Fetching recent concepts from Supabase...');
      const concepts = await fetchRecentConcepts(userId, 10);
      
      if (concepts && concepts.length > 0) {
        // Log the first concept's image URL fields to help with debugging
        const firstConcept = concepts[0];
        console.log(`First concept image URLs:`, {
          image_url: firstConcept.image_url,
          base_image_url: firstConcept.base_image_url,
          has_variations: firstConcept.color_variations && firstConcept.color_variations.length > 0
        });
        
        setRecentConcepts(concepts);
        console.log(`Processed and set ${concepts.length} concepts`);
      } else {
        console.log('No concepts found for the current user');
        setRecentConcepts([]);
      }
    } catch (error) {
      console.error('Error refreshing concepts:', error);
      setErrorLoadingConcepts(error instanceof Error ? error.message : 'Unknown error loading concepts');
    } finally {
      setLoadingConcepts(false);
    }
  };
  
  /**
   * Clear any error messages
   */
  const clearError = (): void => {
    setErrorLoadingConcepts(null);
  };
  
  // Create the context value object
  const contextValue = useMemo(() => ({
    recentConcepts,
    loadingConcepts,
    errorLoadingConcepts,
    refreshConcepts,
    clearError
  }), [recentConcepts, loadingConcepts, errorLoadingConcepts]);
  
  return (
    <ConceptContext.Provider value={contextValue}>
      {children}
    </ConceptContext.Provider>
  );
}; 