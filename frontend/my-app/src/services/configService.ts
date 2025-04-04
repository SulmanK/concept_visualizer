/**
 * Configuration service for Concept Visualizer
 * 
 * This service is responsible for fetching and managing configuration values
 * from the backend, including storage bucket names.
 */

import { useState, useEffect } from 'react';

// Storage bucket configuration interface
interface StorageBucketsConfig {
  concept: string;
  palette: string;
}

// Complete configuration interface
interface AppConfig {
  storage: StorageBucketsConfig;
}

// Default configuration with placeholder values
const defaultConfig: AppConfig = {
  storage: {
    concept: 'concept-images', // Default/fallback value
    palette: 'palette-images', // Default/fallback value
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
    const response = await fetch('/api/health/config');
    
    if (!response.ok) {
      console.error('Failed to fetch configuration:', response.statusText);
      return defaultConfig;
    }
    
    const config = await response.json();
    
    // Store the config in the singleton instance
    configInstance = config;
    
    return config;
  } catch (error) {
    console.error('Error fetching configuration:', error);
    return defaultConfig;
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