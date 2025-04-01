/**
 * Session management utility for handling session cookies
 */

import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';

const SESSION_COOKIE_NAME = 'concept_session';
// Use the API base URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

/**
 * Get the current session ID from cookies
 * 
 * @returns The current session ID or null if not found
 */
export const getSessionId = (): string | null => {
  const sessionId = Cookies.get(SESSION_COOKIE_NAME) || null;
  console.log(`SessionManager: Current session ID is ${sessionId ? sessionId : 'not found'}`);
  return sessionId;
};

/**
 * Set the session ID in cookies
 * 
 * @param sessionId The session ID to store
 * @param days Number of days until the cookie expires (default: 30)
 */
export const setSessionId = (sessionId: string, days: number = 30): void => {
  console.log(`SessionManager: Setting session ID to ${sessionId}`);
  Cookies.set(SESSION_COOKIE_NAME, sessionId, { 
    expires: days, 
    sameSite: 'Lax',
    path: '/'
  });
};

/**
 * Remove the session ID cookie
 */
export const clearSessionId = (): void => {
  Cookies.remove(SESSION_COOKIE_NAME);
};

/**
 * Ensure a session ID exists in cookies. If not, a new one will be created
 * as a UUID and synchronized with the backend.
 * 
 * @returns True if a new session was created, false if an existing one was found
 */
export const ensureSession = async (): Promise<boolean> => {
  const currentSessionId = getSessionId();
  
  if (currentSessionId) {
    // Session already exists, sync with backend
    console.log(`Found existing session ID: ${currentSessionId}, syncing with backend`);
    await syncSession();
    return false;
  }
  
  // No session exists, generate a new UUID and set it
  const newSessionId = uuidv4();
  console.log(`Generated new client-side session ID: ${newSessionId}`);
  setSessionId(newSessionId);
  
  // Sync the new session ID with the backend
  try {
    const response = await fetch(`${API_BASE_URL}/sessions/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include',
      body: JSON.stringify({ 
        client_session_id: newSessionId
      })
    });
    
    if (!response.ok) {
      console.error('Failed to sync new session:', await response.text());
      return true; // We still created a session locally
    }
    
    const data = await response.json();
    console.log('Session sync response:', data);
    
    // If the server returned a different session ID, update our cookie
    if (data.session_id && data.session_id !== newSessionId) {
      console.log(`Updating local session ID from ${newSessionId} to ${data.session_id}`);
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
  
  const status = {
    exists: !!sessionId,
    value: sessionId,
    allCookies
  };
  
  console.log('Session debug information:', status);
  return status;
};

/**
 * Sync the session with the server to ensure consistency.
 * This can help resolve session mismatches between frontend and backend.
 * 
 * @returns True if sync was successful, false otherwise
 */
export const syncSession = async (): Promise<boolean> => {
  const currentSessionId = getSessionId();
  
  if (!currentSessionId) {
    console.error('No session ID to sync');
    return false;
  }
  
  try {
    console.log(`Attempting to sync session: ${currentSessionId}`);
    
    // Call the special endpoint to sync the session, using the API base URL
    const response = await fetch(`${API_BASE_URL}/sessions/sync`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      credentials: 'include', // Include cookies in the request
      body: JSON.stringify({ 
        client_session_id: currentSessionId 
      })
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Failed to sync session: ${errorText}`);
      return false;
    }
    
    const data = await response.json();
    console.log(`Session sync response:`, data);
    
    // If the server returned a different session ID, update our cookie
    if (data.session_id && data.session_id !== currentSessionId) {
      console.log(`Session sync: Updating session ID from ${currentSessionId} to ${data.session_id}`);
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