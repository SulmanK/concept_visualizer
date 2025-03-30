/**
 * Context for managing concept data throughout the application
 */

import React, { createContext, useContext, useState, useEffect, useMemo, ReactNode } from 'react';
import { fetchRecentConcepts, ConceptData } from '../services/supabaseClient';
import { getSessionId } from '../services/sessionManager';

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
  
  // Load recent concepts when the component mounts
  useEffect(() => {
    refreshConcepts();
  }, []);
  
  /**
   * Refresh the list of recent concepts
   */
  const refreshConcepts = async (): Promise<void> => {
    const sessionId = getSessionId();
    
    console.log('Refreshing concepts with session ID:', sessionId);
    
    if (!sessionId) {
      console.error('No session ID found - unable to fetch concepts');
      setErrorLoadingConcepts('No session ID found');
      return;
    }
    
    try {
      setLoadingConcepts(true);
      setErrorLoadingConcepts(null);
      
      console.log('Fetching recent concepts from Supabase...');
      const concepts = await fetchRecentConcepts(sessionId);
      console.log('Received concepts from Supabase:', concepts);
      
      setRecentConcepts(concepts);
    } catch (error) {
      console.error('Error loading recent concepts:', error);
      setErrorLoadingConcepts('Failed to load recent concepts');
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