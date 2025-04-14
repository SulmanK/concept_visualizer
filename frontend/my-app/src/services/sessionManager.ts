/**
 * Session management utility for handling session cookies
 */

import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';
// Import the rate limit service to force refresh when session changes
import { fetchRateLimits } from './rateLimitService';
import { apiClient } from './apiClient';

const SESSION_COOKIE_NAME = 'concept_session';
// Use the API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Mask a string value for logging to avoid revealing full sensitive information
 * 
 * @param value String to mask
 * @param visibleChars Number of characters to leave visible at the beginning
 * @returns Masked string with first few characters visible and the rest replaced with asterisks
 */
const maskValue = (value: string, visibleChars: number = 4): string => {
  if (!value) return '[EMPTY]';
  if (value.length <= visibleChars) return '[TOO_SHORT]';
  return `${value.substring(0, visibleChars)}${'*'.repeat(Math.min(8, value.length - visibleChars))}`;
};

/**
 * Get the current session ID from cookies
 * 
 * @returns The current session ID or null if not found
 */
export const getSessionId = (): string | null => {
  const sessionId = Cookies.get(SESSION_COOKIE_NAME) || null;
  console.log(`SessionManager: Session ID ${sessionId ? 'found' : 'not found'}`);
  return sessionId;
};

/**
 * Set the session ID in cookies
 * 
 * @param sessionId The session ID to store
 * @param days Number of days until the cookie expires (default: 30)
 */
export const setSessionId = (sessionId: string, days: number = 30): void => {
  const oldSessionId = getSessionId();
  console.log(`SessionManager: Setting session ID (masked: ${maskValue(sessionId)})`);
  Cookies.set(SESSION_COOKIE_NAME, sessionId, { 
    expires: days, 
    sameSite: 'Lax',
    path: '/'
  });
  
  // If the session ID changed, force refresh the rate limits
  if (oldSessionId !== sessionId) {
    console.log('Session ID changed, refreshing rate limits');
    // Force refresh rate limits in the next tick to ensure cookie is set first
    setTimeout(() => {
      fetchRateLimits(true).catch(err => 
        console.error('Failed to refresh rate limits after session change:', err)
      );
    }, 0);
  }
};

/**
 * Remove the session ID cookie
 */
export const clearSessionId = (): void => {
  console.log('Clearing session ID and refreshing rate limits');
  Cookies.remove(SESSION_COOKIE_NAME);
  
  // Force refresh rate limits after clearing session
  setTimeout(() => {
    fetchRateLimits(true).catch(err => 
      console.error('Failed to refresh rate limits after clearing session:', err)
    );
  }, 0);
};

/**
 * Ensure that a session exists
 * If no session exists, creates one and syncs with the backend
 * 
 * @deprecated Consider using the useSessionSyncMutation hook for better React Query integration
 * @returns Promise resolving to a boolean indicating whether a new session was created
 */
export const ensureSession = async (): Promise<boolean> => {
  const currentSessionId = getSessionId();
  
  if (currentSessionId) {
    // Session already exists, sync with backend
    console.log(`Found existing session (masked: ${maskValue(currentSessionId)}), syncing with backend`);
    await syncSession();
    return false;
  }
  
  // No session exists, generate a new UUID and set it
  const newSessionId = uuidv4();
  console.log(`Generated new client-side session (masked: ${maskValue(newSessionId)})`);
  setSessionId(newSessionId);
  
  // Sync the new session ID with the backend
  try {
    const { data } = await apiClient.post('/sessions/sync', { 
      client_session_id: newSessionId
    });
    
    console.log('Session sync response:', data);
    
    // If the server returned a different session ID, update our cookie
    if (data.session_id && data.session_id !== newSessionId) {
      console.log(`Updating local session ID (masked from: ${maskValue(newSessionId)} to: ${maskValue(data.session_id)})`);
      setSessionId(data.session_id);
    }
    
    return true;
  } catch (error) {
    console.error('Error syncing new session:', error);
    return true; // We still created a session locally
  }
};

/**
 * Debug function to check if the session cookie exists and print details
 * 
 * @returns Object with session status information
 */
export const debugSessionStatus = (): {exists: boolean, value?: string, allCookies: Record<string, string>} => {
  const sessionId = Cookies.get(SESSION_COOKIE_NAME);
  const allCookies = Cookies.get(); // Gets all cookies as object
  
  // Create a safe version for logging
  const safeCookies: Record<string, string> = {};
  for (const [key, value] of Object.entries(allCookies)) {
    safeCookies[key] = maskValue(value);
  }
  
  const status = {
    exists: !!sessionId,
    value: sessionId ? maskValue(sessionId) : undefined,
    allCookies: safeCookies
  };
  
  console.log('Session debug information:', status);

  // Return actual values to caller
  return {
    exists: !!sessionId,
    value: sessionId,
    allCookies
  };
};

/**
 * Sync the session with the server to ensure consistency.
 * This can help resolve session mismatches between frontend and backend.
 * 
 * @deprecated Consider using the useSessionSyncMutation hook for better React Query integration
 * @returns True if sync was successful, false otherwise
 */
export const syncSession = async (): Promise<boolean> => {
  const currentSessionId = getSessionId();
  
  if (!currentSessionId) {
    console.error('No session ID to sync');
    return false;
  }
  
  try {
    console.log(`Attempting to sync session (masked: ${maskValue(currentSessionId)})`);
    
    // Call the special endpoint to sync the session using apiClient
    const { data } = await apiClient.post('/sessions/sync', { 
      client_session_id: currentSessionId 
    });
    
    console.log(`Session sync response:`, data);
    
    // If the server returned a different session ID, update our cookie
    if (data.session_id && data.session_id !== currentSessionId) {
      console.log(`Session sync: Updating session ID (masked from: ${maskValue(currentSessionId)} to: ${maskValue(data.session_id)})`);
      setSessionId(data.session_id);
      return true;
    }
    
    console.log('Session sync: Session ID is valid and synced with server');
    return true;
  } catch (error) {
    console.error('Error syncing session:', error);
    return false;
  }
}; 