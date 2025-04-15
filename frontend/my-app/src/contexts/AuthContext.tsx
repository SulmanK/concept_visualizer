import React, { useContext, useEffect, useState } from 'react';
import { createContext, useContextSelector } from 'use-context-selector';
import { Session, User } from '@supabase/supabase-js';
import { 
  supabase, 
  initializeAnonymousAuth, 
  isAnonymousUser, 
  linkEmailToAnonymousUser, 
  signOut 
} from '../services/supabaseClient';

interface AuthContextType {
  session: Session | null;
  user: User | null;
  isAnonymous: boolean;
  isLoading: boolean;
  error: Error | null;
  signOut: () => Promise<boolean>;
  linkEmail: (email: string) => Promise<boolean>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  
  // We're removing the refreshAuth function and the refresh timer logic
  // since the Axios interceptors will now handle token refreshing
  
  // Add window focus/blur event listeners to track session state
  useEffect(() => {
    // Function to check session validity on window focus
    const handleWindowFocus = async () => {
      console.log('[AUTH:Context] Window focused, checking session validity');
      try {
        const { data: { session: currentSession } } = await supabase.auth.getSession();
        console.log('[AUTH:Context] Session on window focus:', {
          exists: !!currentSession,
          userId: currentSession?.user?.id,
          expiresAt: currentSession?.expires_at ? new Date(currentSession.expires_at * 1000).toISOString() : 'N/A',
          tokenExpiry: currentSession?.expires_at 
            ? Math.floor((currentSession.expires_at * 1000 - Date.now()) / 1000) + ' seconds' 
            : 'N/A',
          tokenValid: currentSession?.expires_at ? Date.now() < currentSession.expires_at * 1000 : false
        });

        // If session exists but might be nearing expiry, preemptively refresh
        if (currentSession && currentSession.expires_at) {
          const expiryTime = currentSession.expires_at * 1000;
          const timeToExpiry = expiryTime - Date.now();
          
          // If token expires in less than 5 minutes, refresh it proactively
          if (timeToExpiry < 300000 && timeToExpiry > 0) {
            console.log('[AUTH:Context] Token expires soon, proactively refreshing on window focus');
            const { data, error: refreshError } = await supabase.auth.refreshSession();
            if (data.session) {
              console.log('[AUTH:Context] Proactive token refresh successful');
              setSession(data.session);
              setUser(data.session.user);
            } else if (refreshError) {
              console.error('[AUTH:Context] Proactive token refresh failed:', refreshError);
            }
          }
        }
      } catch (err) {
        console.error('[AUTH:Context] Error checking session on window focus:', err);
      }
    };

    const handleWindowBlur = () => {
      console.log('[AUTH:Context] Window blurred, tab inactive');
    };

    // Add event listeners
    window.addEventListener('focus', handleWindowFocus);
    window.addEventListener('blur', handleWindowBlur);

    // Initial check on mount
    handleWindowFocus();

    // Cleanup
    return () => {
      window.removeEventListener('focus', handleWindowFocus);
      window.removeEventListener('blur', handleWindowBlur);
    };
  }, []);
  
  // Set up auth-error-needs-logout event listener
  useEffect(() => {
    const handleAuthError = () => {
      console.log('[AUTH:Context] Received auth-error-needs-logout event, signing out');
      handleSignOut();
    };
    
    // Add event listener
    document.addEventListener('auth-error-needs-logout', handleAuthError);
    
    // Cleanup
    return () => {
      document.removeEventListener('auth-error-needs-logout', handleAuthError);
    };
  }, []);
  
  useEffect(() => {
    // Initialize auth on mount
    const initAuth = async () => {
      console.log('[AUTH:Context] Initializing authentication');
      try {
        setIsLoading(true);
        
        // Initialize anonymous authentication
        const authSession = await initializeAnonymousAuth();
        if (authSession) {
          console.log('[AUTH:Context] Initial auth session established', {
            userId: authSession.user?.id,
            expiresAt: new Date(authSession.expires_at! * 1000).toISOString()
          });
          setSession(authSession);
          setUser(authSession.user);
          
          // Check if user is anonymous
          const anonymous = await isAnonymousUser();
          setIsAnonymous(anonymous);
          console.log('[AUTH:Context] Initial user anonymous status:', anonymous);
        } else {
          console.error('[AUTH:Context] Failed to establish initial auth session');
        }
        
        // Set up auth state listener
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
          async (event, newSession) => {
            console.log('[AUTH:Context] Auth state changed:', event, {
              userId: newSession?.user?.id,
              expiresAt: newSession?.expires_at ? new Date(newSession.expires_at * 1000).toISOString() : null,
              reason: 'AuthStateChange event'
            });
            
            // If we get a SIGNED_OUT event but the app expects to be signed in, try to recover
            if (event === 'SIGNED_OUT' && session !== null) {
              console.warn('[AUTH:Context] Unexpected SIGNED_OUT event when session should exist, attempting recovery');
              
              try {
                // Try to recover the session
                const recoveredSession = await initializeAnonymousAuth();
                if (recoveredSession) {
                  console.log('[AUTH:Context] Successfully recovered session after unexpected sign-out');
                  setSession(recoveredSession);
                  setUser(recoveredSession.user);
                  
                  // Check if user is anonymous
                  const anonymous = await isAnonymousUser();
                  setIsAnonymous(anonymous);
                  
                  // Return early to avoid setting null session
                  return;
                }
              } catch (recoveryError) {
                console.error('[AUTH:Context] Failed to recover from unexpected sign-out:', recoveryError);
              }
            }
            
            // For TOKEN_REFRESHED events, update our state with the new session
            if (event === 'TOKEN_REFRESHED' && newSession) {
              console.log('[AUTH:Context] Token refreshed, updating session state');
              setSession(newSession);
              setUser(newSession.user);
              // No need to check anonymous status on token refresh
              return;
            }
            
            // For other events with a valid session
            if (newSession) {
              setSession(newSession);
              setUser(newSession.user);
              
              // Check if user is anonymous when session changes
              const anonymous = await isAnonymousUser();
              setIsAnonymous(anonymous);
              console.log('[AUTH:Context] Updated user anonymous status:', anonymous);
            } else {
              // No session, reset state and try to create anonymous session
              setSession(null);
              setUser(null);
              setIsAnonymous(true);
              console.log('[AUTH:Context] No session after auth state change, setting anonymous status to true');
              
              // If we unexpectedly lost the session, try to re-establish an anonymous session
              if (event !== 'SIGNED_OUT') {
                console.log('[AUTH:Context] Attempting to re-establish anonymous session after unexpected session loss');
                const newAnonymousSession = await initializeAnonymousAuth();
                if (newAnonymousSession) {
                  console.log('[AUTH:Context] Successfully re-established anonymous session');
                  setSession(newAnonymousSession);
                  setUser(newAnonymousSession.user);
                  setIsAnonymous(true);
                }
              }
            }
          }
        );
        
        // Return cleanup function
        return () => {
          console.log('[AUTH:Context] Cleaning up auth subscription on unmount');
          subscription.unsubscribe();
        };
      } catch (err) {
        console.error('[AUTH:Context] Error initializing auth:', err);
        setError(err instanceof Error ? err : new Error('Failed to initialize authentication'));
      } finally {
        setIsLoading(false);
        console.log('[AUTH:Context] Auth initialization complete');
      }
    };
    
    initAuth();
  }, []);
  
  const handleSignOut = async (): Promise<boolean> => {
    console.log('[AUTH:Context] Sign out requested');
    try {
      const success = await signOut();
      if (!success) {
        console.error('[AUTH:Context] Sign out operation failed');
        throw new Error('Failed to sign out');
      }
      console.log('[AUTH:Context] Sign out successful');
      return true;
    } catch (err) {
      console.error('[AUTH:Context] Error signing out:', err);
      setError(err instanceof Error ? err : new Error('Failed to sign out'));
      return false;
    }
  };
  
  const handleLinkEmail = async (email: string): Promise<boolean> => {
    console.log('[AUTH:Context] Email linking requested');
    try {
      const success = await linkEmailToAnonymousUser(email);
      if (!success) {
        console.error('[AUTH:Context] Email linking operation failed');
        throw new Error('Failed to link email');
      }
      setIsAnonymous(false);
      console.log('[AUTH:Context] Email linking successful');
      return true;
    } catch (err) {
      console.error('[AUTH:Context] Error linking email:', err);
      setError(err instanceof Error ? err : new Error('Failed to link email'));
      return false;
    }
  };
  
  const value = {
    session,
    user,
    isAnonymous,
    isLoading,
    error,
    signOut: handleSignOut,
    linkEmail: handleLinkEmail
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContextSelector(AuthContext, (state) => state);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const useAuthUser = () => useContextSelector(AuthContext, state => state.user);
export const useUserId = () => useContextSelector(AuthContext, state => state.user?.id);
export const useIsAnonymous = () => useContextSelector(AuthContext, state => state.isAnonymous);
export const useAuthIsLoading = () => useContextSelector(AuthContext, state => state.isLoading); 