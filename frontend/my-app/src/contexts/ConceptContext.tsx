/**
 * Context for managing concept data throughout the application
 */

import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { fetchRecentConcepts, ConceptData, ColorVariationData, getPublicImageUrl } from '../services/supabaseClient';
import { getSessionId, syncSession } from '../services/sessionManager';
import { supabase } from '../services/supabaseClient';

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
  const [recentConcepts, setRecentConcepts] = useState<ConceptData[]>([]);
  const [loadingConcepts, setLoadingConcepts] = useState<boolean>(false);
  const [errorLoadingConcepts, setErrorLoadingConcepts] = useState<string | null>(null);
  
  // Sync session when component mounts
  useEffect(() => {
    const initialSync = async () => {
      console.log('ConceptContext: Performing initial session sync');
      const sessionId = getSessionId();
      
      if (!sessionId) {
        console.error('ConceptContext: No session ID available for initial sync');
        return;
      }
      
      try {
        const syncResult = await syncSession();
        console.log(`ConceptContext: Initial sync ${syncResult ? 'succeeded' : 'failed'}`);
        
        // Only refresh concepts if the sync was successful
        if (syncResult) {
          refreshConcepts();
        }
      } catch (err) {
        console.error('ConceptContext: Error during initial sync', err);
      }
    };
    
    initialSync();
  }, []);
  
  /**
   * Refresh the list of concepts from the API
   */
  const refreshConcepts = async () => {
    console.log('Refreshing concepts');
    setLoadingConcepts(true);
    setErrorLoadingConcepts(null);
    
    // Get the current session ID
    const sessionId = getSessionId();
    console.log(`Refreshing concepts with session ID: ${sessionId}`);
    
    if (!sessionId) {
      console.error('No session ID available, cannot fetch concepts');
      setErrorLoadingConcepts('No session ID available');
      setLoadingConcepts(false);
      return;
    }
    
    try {
      // First try to sync the session to ensure consistency
      console.log(`Syncing session before fetching concepts`);
      
      try {
        const syncResult = await syncSession();
        console.log(`Session sync ${syncResult ? 'succeeded' : 'failed'}`);
        
        // Get the session ID again in case it was updated by syncSession
        const updatedSessionId = getSessionId(); 
        if (updatedSessionId !== sessionId) {
          console.log(`Session ID changed after sync: ${sessionId} → ${updatedSessionId}`);
        }
      } catch (syncError) {
        console.error('Error syncing session, will try to fetch concepts anyway:', syncError);
      }
      
      // Now fetch the concepts from Supabase
      console.log('Fetching recent concepts from Supabase...');
      const { data: recentConcepts, error: fetchError } = await supabase
        .from('concepts')
        .select('*, color_variations(*)')
        .eq('session_id', sessionId)
        .order('created_at', { ascending: false })
        .limit(10);
        
      if (fetchError) {
        throw new Error(`Error fetching concepts: ${fetchError.message}`);
      }
      
      console.log(`Received ${recentConcepts?.length || 0} concepts from Supabase`);
      
      // Process concepts to add image URLs
      if (recentConcepts && recentConcepts.length > 0) {
        const processedConcepts = recentConcepts.map(concept => ({
          ...concept,
          base_image_url: getPublicImageUrl(concept.base_image_path, 'concept'),
          color_variations: (concept.color_variations || []).map((variation: any) => ({
            ...variation,
            image_url: getPublicImageUrl(variation.image_path, 'palette')
          }))
        }));
        
        setRecentConcepts(processedConcepts);
        console.log(`Processed and set ${processedConcepts.length} concepts`);
      } else {
        console.log('No concepts found for the current session');
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