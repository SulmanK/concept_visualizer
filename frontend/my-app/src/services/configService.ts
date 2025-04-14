/**
 * Configuration service for Concept Visualizer
 * 
 * This service is responsible for fetching and managing configuration values
 * from the backend, including storage bucket names.
 */

import { useState, useEffect } from 'react';
import { apiClient } from './apiClient';

// Storage bucket configuration interface
interface StorageBucketsConfig {
  concept: string;
  palette: string;
}

// Complete configuration interface
interface AppConfig {
  storage: StorageBucketsConfig;
  maxUploadSize: number;
  supportedFileTypes: string[];
  features: {
    refinement: boolean;
    palette: boolean;
    export: boolean;
  };
  limits: {
    maxConcepts: number;
    maxPalettes: number;
  };
}

// Default configuration with placeholder values
const defaultConfig: AppConfig = {
  storage: {
    concept: 'concept-images', // Default/fallback value
    palette: 'palette-images', // Default/fallback value
  },
  maxUploadSize: 5 * 1024 * 1024, // 5MB
  supportedFileTypes: ['png', 'jpg', 'jpeg'],
  features: {
    refinement: true,
    palette: true,
    export: true
  },
  limits: {
    // Default limits
    maxConcepts: 50,
    maxPalettes: 5
  }
};

// Singleton configuration instance
let configInstance: AppConfig | null = null;

/**
 * Fetch configuration from the backend API
 * 
 * @returns Promise resolving to the application configuration
 */
export const fetchConfig = async (): Promise<AppConfig> => {
  try {
    const { data } = await apiClient.get<AppConfig>('/health/config');
    return data;
  } catch (error) {
    console.error('Failed to fetch app configuration:', error);
    // Return default config
    return {
      // Default config values
      maxUploadSize: 5 * 1024 * 1024, // 5MB
      supportedFileTypes: ['png', 'jpg', 'jpeg'],
      features: {
        refinement: true,
        palette: true,
        export: true
      },
      limits: {
        // Default limits
        maxConcepts: 50,
        maxPalettes: 5
      }
    };
  }
};

/**
 * Get the current configuration
 * 
 * If configuration hasn't been fetched yet, returns the default configuration
 * 
 * @returns The current application configuration
 */
export const getConfig = (): AppConfig => {
  return configInstance || defaultConfig;
};

/**
 * Get bucket name for a specific storage type
 * 
 * @param type 'concept' or 'palette'
 * @returns The bucket name for the specified type
 */
export const getBucketName = (type: 'concept' | 'palette'): string => {
  const config = getConfig();
  return config.storage[type];
};

/**
 * React hook for using configuration in components
 * 
 * @returns Configuration object and loading state
 */
export const useConfig = () => {
  const [config, setConfig] = useState<AppConfig>(getConfig());
  const [loading, setLoading] = useState<boolean>(!configInstance);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    const loadConfig = async () => {
      if (configInstance) {
        setConfig(configInstance);
        return;
      }
      
      setLoading(true);
      
      try {
        const freshConfig = await fetchConfig();
        setConfig(freshConfig);
        setError(null);
      } catch (err) {
        setError('Failed to load configuration');
        console.error('Error loading configuration:', err);
      } finally {
        setLoading(false);
      }
    };
    
    loadConfig();
  }, []);
  
  return { config, loading, error };
};

// Initialize configuration on module load
fetchConfig().catch(err => {
  console.error('Error initializing configuration:', err);
});

export default {
  fetchConfig,
  getConfig,
  getBucketName,
  useConfig
}; 