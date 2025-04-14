import { useState, useEffect, useCallback } from 'react';
import { useToast } from './useToast';
import { apiClient } from '../services/apiClient';

export interface NetworkStatus {
  /**
   * Whether the browser is currently online
   */
  isOnline: boolean;
  
  /**
   * Network connection type if available
   */
  connectionType?: string;
  
  /**
   * Whether the browser is on a slow connection
   */
  isSlowConnection: boolean;
  
  /**
   * Last time connection status was checked
   */
  lastCheckedAt: Date;
  
  /**
   * Manually check connection status
   */
  checkConnection: () => Promise<boolean>;
  
  /**
   * Timestamp when the connection was last lost (if applicable)
   */
  offlineSince?: Date;
}

/**
 * Hook for monitoring network status with offline support
 * 
 * @param options.notifyOnStatusChange Whether to show toast notifications when network status changes
 * @param options.checkEndpoint URL to check for internet connectivity
 * @param options.checkInterval Interval in milliseconds to check connection status
 * @returns Network status information and methods
 */
export const useNetworkStatus = (options?: {
  notifyOnStatusChange?: boolean;
  checkEndpoint?: string;
  checkInterval?: number;
}): NetworkStatus => {
  const {
    notifyOnStatusChange = true,
    checkEndpoint = '/health',
    checkInterval = 120000, // 2 minutes
  } = options || {};
  
  const [isOnline, setIsOnline] = useState<boolean>(navigator.onLine);
  const [connectionType, setConnectionType] = useState<string | undefined>(undefined);
  const [isSlowConnection, setIsSlowConnection] = useState<boolean>(false);
  const [lastCheckedAt, setLastCheckedAt] = useState<Date>(new Date());
  const [offlineSince, setOfflineSince] = useState<Date | undefined>(
    navigator.onLine ? undefined : new Date()
  );
  
  const toast = useToast();
  
  // Check connection by fetching a small resource
  const checkConnection = useCallback(async (): Promise<boolean> => {
    try {
      // Try the main endpoint, but if it fails, we'll consider the app online anyway
      // as long as the browser reports we're online
      try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 5000); // 5 second timeout
        
        await apiClient.get(checkEndpoint, {
          headers: { 'Cache-Control': 'no-cache' },
          signal: controller.signal,
          showToastOnRateLimit: false // Don't show rate limit toasts for health checks
        });
        
        clearTimeout(timeoutId);
        setLastCheckedAt(new Date());
        
        updateOnlineStatus(true);
        return true;
      } catch (error) {
        console.warn('Health check endpoint error:', error);
        // If the health check endpoint fails but the browser says we're online,
        // we'll consider ourselves online
        setLastCheckedAt(new Date());
        
        // Use the browser's online status as a fallback
        updateOnlineStatus(navigator.onLine);
        return navigator.onLine;
      }
    } catch (error) {
      // Final fallback - network error or timeout
      setLastCheckedAt(new Date());
      
      if (isOnline) {
        setIsOnline(false);
        setOfflineSince(new Date());
        if (notifyOnStatusChange) {
          toast.showWarning('You appear to be offline. Some features may be unavailable.');
        }
      }
      
      return false;
    }
  }, [checkEndpoint, isOnline, notifyOnStatusChange, toast]);
  
  // Helper function to update the online status and show notifications
  const updateOnlineStatus = useCallback((online: boolean) => {
    if (online !== isOnline) {
      setIsOnline(online);
      
      if (online) {
        // We're back online
        setOfflineSince(undefined);
        if (notifyOnStatusChange) {
          toast.showSuccess('Your internet connection has been restored');
        }
      } else {
        // We've gone offline
        setOfflineSince(new Date());
        if (notifyOnStatusChange) {
          toast.showWarning('You appear to be offline. Some features may be unavailable.');
        }
      }
    }
  }, [isOnline, notifyOnStatusChange, toast]);
  
  // Handle browser's online/offline events
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true);
      setOfflineSince(undefined);
      setLastCheckedAt(new Date());
      if (notifyOnStatusChange) {
        toast.showSuccess('Your internet connection has been restored');
      }
      // Verify the connection actually works
      checkConnection();
    };
    
    const handleOffline = () => {
      setIsOnline(false);
      setOfflineSince(new Date());
      setLastCheckedAt(new Date());
      if (notifyOnStatusChange) {
        toast.showWarning('You appear to be offline. Some features may be unavailable.');
      }
    };
    
    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);
    
    // Get network connection type if available
    if ('connection' in navigator) {
      const connection = (navigator as any).connection;
      
      if (connection) {
        setConnectionType(connection.effectiveType);
        setIsSlowConnection(['slow-2g', '2g', '3g'].includes(connection.effectiveType));
        
        const handleConnectionChange = () => {
          setConnectionType(connection.effectiveType);
          setIsSlowConnection(['slow-2g', '2g', '3g'].includes(connection.effectiveType));
          setLastCheckedAt(new Date());
        };
        
        connection.addEventListener('change', handleConnectionChange);
        return () => {
          connection.removeEventListener('change', handleConnectionChange);
          window.removeEventListener('online', handleOnline);
          window.removeEventListener('offline', handleOffline);
        };
      }
    }
    
    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [checkConnection, notifyOnStatusChange, toast]);
  
  // Periodically check connection
  useEffect(() => {
    if (checkInterval <= 0) return;
    
    const intervalId = setInterval(() => {
      checkConnection();
    }, checkInterval);
    
    return () => clearInterval(intervalId);
  }, [checkConnection, checkInterval]);
  
  // Initial connection check
  useEffect(() => {
    checkConnection();
  }, [checkConnection]);
  
  return {
    isOnline,
    connectionType,
    isSlowConnection,
    lastCheckedAt,
    offlineSince,
    checkConnection,
  };
};

export default useNetworkStatus; 