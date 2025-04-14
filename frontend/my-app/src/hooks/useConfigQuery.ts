import { useQuery, UseQueryResult } from '@tanstack/react-query';
import { apiClient } from '../services/apiClient';
import { useErrorHandling } from './useErrorHandling';
import { createQueryErrorHandler } from '../utils/errorUtils';

// Import necessary type definitions from configService to maintain consistency
import { AppConfig, defaultConfig } from '../services/configService';

/**
 * Hook to fetch and cache application configuration using React Query
 * 
 * @returns Query result with configuration data
 */
export function useConfigQuery(options: {
  enabled?: boolean;
  refetchOnWindowFocus?: boolean;
} = {}): UseQueryResult<AppConfig, Error> {
  const errorHandler = useErrorHandling();
  const { onQueryError } = createQueryErrorHandler(errorHandler, {
    defaultErrorMessage: 'Failed to load configuration',
    showToast: false
  });

  return useQuery<AppConfig, Error>({
    queryKey: ['appConfig'],
    queryFn: async () => {
      try {
        const response = await apiClient.get<AppConfig>('/health/config');
        return response.data;
      } catch (error) {
        console.error('Failed to fetch app configuration:', error);
        // Return default config on error
        return {
          ...defaultConfig,
          // Storage is required in default config
          storage: defaultConfig.storage,
        };
      }
    },
    staleTime: 1000 * 60 * 60, // Config is stable, cache for an hour
    cacheTime: 1000 * 60 * 60 * 24, // Keep in cache for a day
    refetchOnWindowFocus: options.refetchOnWindowFocus ?? false,
    enabled: options.enabled !== false,
    onError: onQueryError,
  });
} 