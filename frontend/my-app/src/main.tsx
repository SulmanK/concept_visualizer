import React from 'react'
import ReactDOM from 'react-dom/client'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import App from './App'
import './styles/global.css'
import axios from 'axios'
import { supabase } from './services/supabaseClient'

// Add window focus/blur tracking
let tabHasBeenActive = false;
let tabInactiveTime = 0;

// Get API base URL
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Handle window focus events
window.addEventListener('focus', () => {
  if (tabHasBeenActive) {
    const inactiveMs = Date.now() - tabInactiveTime;
    console.log(`[QUERY] Window regained focus after ${Math.round(inactiveMs/1000)} seconds inactive`);
    
    // Ping the backend health endpoint to check connectivity
    console.log('[QUERY] Pinging backend health endpoint after tab focus');
    axios.get(`${API_BASE_URL}/health`, { 
      timeout: 5000,
      headers: { 'Cache-Control': 'no-cache' }
    })
      .then(response => {
        console.log('[QUERY] Backend health check successful after tab focus:', response.status);
        
        // Check if Supabase connection is active by getting the current session
        supabase.auth.getSession().then(({ data }) => {
          console.log('[QUERY] Supabase connection check after tab focus:', {
            hasSession: !!data.session,
            userId: data.session?.user?.id,
            validUntil: data.session?.expires_at ? new Date(data.session.expires_at * 1000).toISOString() : 'N/A'
          });
        });
      })
      .catch(error => {
        console.error('[QUERY] Backend health check failed after tab focus:', error);
      });
    
    // If tab was inactive for more than 60 seconds, we'll invalidate queries
    if (inactiveMs > 60000 && queryClient) {
      console.log('[QUERY] Long inactivity detected, invalidating queries');
      
      // First, handle any potentially stale queries
      const staleTasks = queryClient.getQueriesData({ 
        predicate: query => 
          // Only consider task queries 
          query.queryKey[0] === 'tasks' &&
          // That have stale data
          query.isStale() 
      });
      
      if (staleTasks.length > 0) {
        console.log(`[QUERY] Found ${staleTasks.length} stale task queries, refreshing...`);
        staleTasks.forEach(([queryKey]) => {
          queryClient.invalidateQueries({ queryKey });
        });
      }
      
      // Give auth a moment to stabilize before invalidating
      setTimeout(() => {
        // Invalidate all queries
        queryClient.invalidateQueries();
        
        // Force refetch of important queries
        queryClient.invalidateQueries({ queryKey: ['rateLimits'] });
        queryClient.invalidateQueries({ queryKey: ['concepts', 'recent'] });
        
        console.log('[QUERY] All queries invalidated after tab focus');
      }, 500);
      
      // If inactive for a very long time (over 5 minutes), consider clearing some query cache
      if (inactiveMs > 300000) {
        console.log('[QUERY] Very long inactivity detected, clearing some query cache');
        
        // Give time for auth to stabilize
        setTimeout(() => {
          // Clear only specific queries that might be very stale
          queryClient.removeQueries({ 
            predicate: query => 
              // Don't remove auth-related data
              query.queryKey[0] !== 'auth' && 
              // Only remove inactive queries
              !query.isActive() &&
              // That are stale
              query.isStale()
          });
          
          console.log('[QUERY] Stale query cache cleaned after extended inactivity');
        }, 2000);
      }
    }
  }
  tabHasBeenActive = true;
});

// Track when the tab becomes inactive
window.addEventListener('blur', () => {
  if (tabHasBeenActive) {
    console.log('[QUERY] Window lost focus, tracking inactive time');
    tabInactiveTime = Date.now();
  }
});

// Create a client with improved focus handling
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 30, // 30 seconds (increased from 10 seconds)
      gcTime: 1000 * 60 * 30, // 30 minutes (formerly cacheTime)
      refetchOnWindowFocus: false, // Enable refetching on window focus for better data freshness
      retry: (failureCount, error: Error & { status?: number }) => {
        // Log retry attempts
        console.log(`[QUERY] Retry attempt ${failureCount}:`, error);
        
        // Don't retry if we're getting auth errors (401) - let auth system handle it
        if (error.status === 401) {
          console.log('[QUERY] Not retrying 401 error, letting auth system handle it');
          return false;
        }
        
        // Only retry non-auth failures up to 2 times
        return failureCount < 2;
      },
      // Add delay between retries
      retryDelay: attemptIndex => Math.min(1000 * 2 ** attemptIndex, 10000),
    },
  },
})

// Set up global error handler for unhandled promises
// This can catch query errors that bubble up
window.addEventListener('unhandledrejection', (event) => {
  console.error('[GLOBAL] Unhandled Promise Rejection:', event.reason);
  
  // Check if it's an authentication error
  if (event.reason && typeof event.reason === 'object' && 'status' in event.reason) {
    const status = (event.reason as { status: number }).status;
    if (status === 401) {
      console.error('[GLOBAL] Detected unhandled authentication error (401)');
      // Dispatch auth error event to trigger a fix
      document.dispatchEvent(new CustomEvent('auth-error-needs-logout'));
    }
  }
});

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
)
