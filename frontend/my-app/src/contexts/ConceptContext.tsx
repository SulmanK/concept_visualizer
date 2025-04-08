/**
 * Context for managing concept data throughout the application
 */

import React, { useMemo, ReactNode, useCallback } from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { ConceptData } from '../services/supabaseClient';
import { useAuth } from './AuthContext';
import { useRecentConcepts } from '../hooks/useConceptQueries';
import { useQueryClient } from '@tanstack/react-query';

interface ConceptContextType {
  // Recent concepts data
  recentConcepts: ConceptData[];
  loadingConcepts: boolean;
  errorLoadingConcepts: unknown;
  
  // Actions
  refreshConcepts: () => void;
}

// Create context with default values
const ConceptContext = createContext<ConceptContextType>({
  recentConcepts: [],
  loadingConcepts: false,
  errorLoadingConcepts: null,
  refreshConcepts: () => {}
});

// Selector hooks for specific context values
/**
 * Hook to access only the recent concepts data
 */
export const useRecentConceptsData = () => {
  return useContextSelector(ConceptContext, state => state.recentConcepts);
};

/**
 * Hook to access only the loading state
 */
export const useConceptsLoading = () => {
  return useContextSelector(ConceptContext, state => state.loadingConcepts);
};

/**
 * Hook to access only the error state
 */
export const useConceptsError = () => {
  return useContextSelector(ConceptContext, state => state.errorLoadingConcepts);
};

/**
 * Hook to access only the refresh function
 */
export const useRefreshConcepts = () => {
  return useContextSelector(ConceptContext, state => state.refreshConcepts);
};

// Original hook for backward compatibility that now uses selectors internally
export const useConceptContext = (): ConceptContextType => {
  const recentConcepts = useRecentConceptsData();
  const loadingConcepts = useConceptsLoading();
  const errorLoadingConcepts = useConceptsError();
  const refreshConcepts = useRefreshConcepts();
  
  // Memoize the result to prevent unnecessary re-renders
  return useMemo(() => ({
    recentConcepts,
    loadingConcepts,
    errorLoadingConcepts,
    refreshConcepts
  }), [recentConcepts, loadingConcepts, errorLoadingConcepts, refreshConcepts]);
};

interface ConceptProviderProps {
  children: ReactNode;
}

/**
 * Provider component for concept data
 * Uses React Query directly for data management
 */
export const ConceptProvider: React.FC<ConceptProviderProps> = ({ children }) => {
  const { user } = useAuth();
  const queryClient = useQueryClient();
  
  // Use React Query to fetch concepts - direct use of React Query state
  const { 
    data = [] as ConceptData[], // Explicitly type the default value
    isLoading, 
    error,
    refetch
  } = useRecentConcepts(user?.id, 10);
  
  // Create a memoized refresh function that uses the refetch function from React Query
  // and also invalidates the query cache
  const refreshConcepts = useCallback(() => {
    console.log('Manually refreshing concepts via React Query');
    
    // Approach 1: Use refetch from React Query
    refetch();
    
    // Approach 2: Invalidate the query cache to trigger a refetch
    // This is sometimes more reliable for forcing a complete refresh
    queryClient.invalidateQueries({ queryKey: ['concepts', 'recent', user?.id] });
  }, [refetch, queryClient, user?.id]);
  
  // Note: Event listeners have been removed from here.
  // Instead, we now use React Query's cache invalidation directly at event sources
  // See useConceptGeneration.ts for example where we directly invalidate the cache
  // after a successful concept creation.
  
  // Create the context value object with proper memoization
  const contextValue = useMemo(() => ({
    recentConcepts: data,
    loadingConcepts: isLoading,
    errorLoadingConcepts: error,
    refreshConcepts
  }), [data, isLoading, error, refreshConcepts]);
  
  return (
    <ConceptContext.Provider value={contextValue}>
      {children}
    </ConceptContext.Provider>
  );
}; 