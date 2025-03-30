/**
 * Session management utility for handling session cookies
 */

import Cookies from 'js-cookie';

const SESSION_COOKIE_NAME = 'concept_session_id';

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
 * via the backend API (which will set the cookie).
 * 
 * @returns True if a new session was created, false if an existing one was found
 */
export const ensureSession = async (): Promise<boolean> => {
  const currentSessionId = getSessionId();
  
  if (currentSessionId) {
    // Session already exists
    return false;
  }
  
  // No session exists, get one from the backend
  try {
    const response = await fetch('/api/sessions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      }
    });
    
    if (!response.ok) {
      console.error('Failed to create session:', await response.text());
      return false;
    }
    
    // The backend should set the cookie via Set-Cookie header
    // We don't need to manually set it here
    return true;
  } catch (error) {
    console.error('Error creating session:', error);
    return false;
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
  const allCookies = Cookies.get(); // Gets all cookies as object
  
  const status = {
    exists: !!sessionId,
    value: sessionId,
    allCookies
  };
  
  console.log('Session debug information:', status);
  return status;
}; 