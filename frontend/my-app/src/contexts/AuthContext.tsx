import React, { createContext, useContext, useEffect, useState, useRef } from 'react';
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
  refreshAuth: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);
  const refreshTimerRef = useRef<number | null>(null);
  
  // Function to refresh authentication
  const refreshAuth = async (): Promise<void> => {
    try {
      console.log('[AUTH:Context] Proactively refreshing authentication token');
      const authSession = await initializeAnonymousAuth();
      if (authSession) {
        console.log('[AUTH:Context] Auth session refreshed successfully', { 
          userId: authSession.user?.id,
          expiresAt: new Date(authSession.expires_at! * 1000).toISOString()
        });
        setSession(authSession);
        setUser(authSession.user);
        
        // Check if user is anonymous
        const anonymous = await isAnonymousUser();
        setIsAnonymous(anonymous);
        console.log('[AUTH:Context] User anonymous status:', anonymous);
      } else {
        console.error('[AUTH:Context] Failed to refresh auth session - no session returned');
      }
    } catch (err) {
      console.error('[AUTH:Context] Error refreshing authentication:', err);
    }
  };
  
  // Set up token refresh timer
  useEffect(() => {
    // Clear any existing timer
    if (refreshTimerRef.current) {
      window.clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
    
    if (!session) {
      console.log('[AUTH:Context] No session available, skipping refresh timer setup');
      return;
    }
    
    // Calculate time until refresh is needed (5 minutes before expiration)
    const expiresAt = session.expires_at;
    if (!expiresAt) {
      console.warn('[AUTH:Context] Session missing expires_at timestamp');
      return;
    }
    
    const now = Math.floor(Date.now() / 1000);
    const timeUntilRefresh = (expiresAt - now - 300) * 1000; // 5 minutes before expiry, in ms
    
    console.log(`[AUTH:Context] Token expires in ${(expiresAt - now)} seconds, will refresh in ${timeUntilRefresh/1000} seconds`);
    
    // Set a timer to refresh if token is valid but will expire
    if (timeUntilRefresh > 0) {
      console.log(`[AUTH:Context] Setting refresh timer for ${new Date(Date.now() + timeUntilRefresh).toISOString()}`);
      refreshTimerRef.current = window.setTimeout(() => {
        console.log('[AUTH:Context] Refresh timer triggered, refreshing auth');
        refreshAuth();
      }, timeUntilRefresh);
    } else {
      // If token is already close to expiry, refresh immediately
      console.log('[AUTH:Context] Token close to expiry, refreshing immediately');
      refreshAuth();
    }
    
    // Cleanup function
    return () => {
      if (refreshTimerRef.current) {
        console.log('[AUTH:Context] Cleaning up refresh timer on unmount/update');
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
    };
  }, [session]);
  
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
              expiresAt: newSession?.expires_at ? new Date(newSession.expires_at * 1000).toISOString() : null
            });
            setSession(newSession);
            setUser(newSession?.user || null);
            
            // Check if user is anonymous when session changes
            if (newSession) {
              const anonymous = await isAnonymousUser();
              setIsAnonymous(anonymous);
              console.log('[AUTH:Context] Updated user anonymous status:', anonymous);
            } else {
              setIsAnonymous(true);
              console.log('[AUTH:Context] No session, setting anonymous status to true');
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
    linkEmail: handleLinkEmail,
    refreshAuth
  };
  
  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 