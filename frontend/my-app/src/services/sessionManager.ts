/**
 * Session management utility for handling session cookies
 */

import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';

const SESSION_COOKIE_NAME = 'concept_session';

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
    const response = await fetch('http://localhost:8000/api/sessions/sync', {
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

// Add a debugging function to check session status
/**
 * Debug function to check if the session cookie exists and print details
 * 
 * @returns Object with session status information
 */
export const debugSessionStatus = (): {exists: boolean, value?: string, allCookies: Record<string, string>} => {
  const sessionId = Cookies.get(SESSION_COOKIE_NAME);
  const oldSessionId = Cookies.get('concept_session_id'); // Check old cookie name too
  const allCookies = Cookies.get(); // Gets all cookies as object
  
  // If we have an old session ID but not a new one, migrate it
  if (oldSessionId && !sessionId) {
    console.log(`Found old session ID format (${oldSessionId}), migrating to new cookie name`);
    setSessionId(oldSessionId);
    // Remove the old cookie
    Cookies.remove('concept_session_id');
  }
  
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
    
    // Call the special endpoint to sync the session, using the full URL
    const response = await fetch('http://localhost:8000/api/sessions/sync', {
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

/**
 * Force a specific session ID to be used.
 * This is for debugging purposes to match a known database session.
 * 
 * @param forcedSessionId The session ID to force
 */
export const forceSessionId = (forcedSessionId: string): void => {
  console.log(`IMPORTANT: Forcing session ID to: ${forcedSessionId}`);
  
  // This is ONLY for debugging - should NOT be used in production
  setSessionId(forcedSessionId);
};

/**
 * Migrate from the old cookie name (concept_session_id) 
 * to the new one (concept_session).
 * 
 * This helps during the transition period when updating the application.
 * 
 * @returns The current session ID after migration attempt
 */
export const migrateLegacySession = (): string | null => {
  const currentSessionId = Cookies.get(SESSION_COOKIE_NAME);
  const oldSessionId = Cookies.get('concept_session_id');
  
  // If we already have the new cookie, use that
  if (currentSessionId) {
    // If we also have an old cookie, clean it up
    if (oldSessionId) {
      console.log(`Found both new and old session cookies. Keeping new: ${currentSessionId}, removing old: ${oldSessionId}`);
      Cookies.remove('concept_session_id');
    }
    return currentSessionId;
  }
  
  // If we only have the old cookie, migrate it
  if (oldSessionId) {
    console.log(`Migrating from old session cookie: ${oldSessionId}`);
    setSessionId(oldSessionId);
    Cookies.remove('concept_session_id');
    return oldSessionId;
  }
  
  // No session cookies found
  return null;
}; 