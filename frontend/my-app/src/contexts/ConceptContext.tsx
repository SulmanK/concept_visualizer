/**
 * Context for managing concept data throughout the application
 */

import React, { createContext, useContext, useState, useMemo, ReactNode, useEffect } from 'react';
import { ConceptData } from '../services/supabaseClient';
import { useAuth } from './AuthContext';
import { useRecentConcepts } from '../hooks/useConceptQueries';
import { useQueryClient } from '@tanstack/react-query';
import { eventService, AppEvent } from '../services/eventService';

interface ConceptContextType {
  // Recent concepts data
  recentConcepts: ConceptData[];
  loadingConcepts: boolean;
  errorLoadingConcepts: string | null;
  
  // Actions
  refreshConcepts: () => void;
  clearError: () => void;
}

// Create context with default values
const ConceptContext = createContext<ConceptContextType>({
  recentConcepts: [],
  loadingConcepts: false,
  errorLoadingConcepts: null,
  refreshConcepts: () => {},
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
  const { user } = useAuth();
  const queryClient = useQueryClient();
  const [errorLoadingConcepts, setErrorLoadingConcepts] = useState<string | null>(null);
  
  // Use React Query to fetch concepts
  const { 
    data: recentConcepts = [], 
    isLoading: loadingConcepts, 
    error 
  } = useRecentConcepts(user?.id, 10);
  
  // Update error state from React Query error
  React.useEffect(() => {
    if (error) {
      console.error('Error loading concepts:', error);
      setErrorLoadingConcepts(error instanceof Error ? error.message : 'Unknown error loading concepts');
    } else {
      setErrorLoadingConcepts(null);
    }
  }, [error]);
  
  /**
   * Refresh the list of concepts from the API
   */
  const refreshConcepts = () => {
    console.log('Manually refreshing concepts via React Query');
    // Invalidate the query cache to trigger a refetch
    queryClient.invalidateQueries({ queryKey: ['concepts', 'recent', user?.id] });
  };
  
  // Listen for global concept events and refresh data
  useEffect(() => {
    // Listen for concept created and updated events
    const createdUnsubscribe = eventService.subscribe(AppEvent.CONCEPT_CREATED, () => {
      console.log('[ConceptContext] Concept created event received, refreshing data');
      refreshConcepts();
    });
    
    const updatedUnsubscribe = eventService.subscribe(AppEvent.CONCEPT_UPDATED, () => {
      console.log('[ConceptContext] Concept updated event received, refreshing data');
      refreshConcepts();
    });
    
    // Clean up subscriptions on unmount
    return () => {
      createdUnsubscribe();
      updatedUnsubscribe();
    };
  }, [user?.id]); // Re-subscribe when user changes
  
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