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
      console.log('Proactively refreshing authentication token');
      const authSession = await initializeAnonymousAuth();
      if (authSession) {
        setSession(authSession);
        setUser(authSession.user);
        
        // Check if user is anonymous
        const anonymous = await isAnonymousUser();
        setIsAnonymous(anonymous);
      }
    } catch (err) {
      console.error('Error refreshing authentication:', err);
    }
  };
  
  // Set up token refresh timer
  useEffect(() => {
    // Clear any existing timer
    if (refreshTimerRef.current) {
      window.clearTimeout(refreshTimerRef.current);
      refreshTimerRef.current = null;
    }
    
    if (!session) return;
    
    // Calculate time until refresh is needed (5 minutes before expiration)
    const expiresAt = session.expires_at;
    if (!expiresAt) return;
    
    const now = Math.floor(Date.now() / 1000);
    const timeUntilRefresh = (expiresAt - now - 300) * 1000; // 5 minutes before expiry, in ms
    
    console.log(`Token expires in ${(expiresAt - now)} seconds, will refresh in ${timeUntilRefresh/1000} seconds`);
    
    // Set a timer to refresh if token is valid but will expire
    if (timeUntilRefresh > 0) {
      refreshTimerRef.current = window.setTimeout(() => {
        refreshAuth();
      }, timeUntilRefresh);
    } else {
      // If token is already close to expiry, refresh immediately
      refreshAuth();
    }
    
    // Cleanup function
    return () => {
      if (refreshTimerRef.current) {
        window.clearTimeout(refreshTimerRef.current);
        refreshTimerRef.current = null;
      }
    };
  }, [session]);
  
  useEffect(() => {
    // Initialize auth on mount
    const initAuth = async () => {
      try {
        setIsLoading(true);
        
        // Initialize anonymous authentication
        const authSession = await initializeAnonymousAuth();
        if (authSession) {
          setSession(authSession);
          setUser(authSession.user);
          
          // Check if user is anonymous
          const anonymous = await isAnonymousUser();
          setIsAnonymous(anonymous);
        }
        
        // Set up auth state listener
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
          async (event, newSession) => {
            console.log('Auth state changed:', event);
            setSession(newSession);
            setUser(newSession?.user || null);
            
            // Check if user is anonymous when session changes
            if (newSession) {
              const anonymous = await isAnonymousUser();
              setIsAnonymous(anonymous);
            } else {
              setIsAnonymous(true);
            }
          }
        );
        
        // Return cleanup function
        return () => {
          subscription.unsubscribe();
        };
      } catch (err) {
        console.error('Error initializing auth:', err);
        setError(err instanceof Error ? err : new Error('Failed to initialize authentication'));
      } finally {
        setIsLoading(false);
      }
    };
    
    initAuth();
  }, []);
  
  const handleSignOut = async (): Promise<boolean> => {
    try {
      const success = await signOut();
      if (!success) {
        throw new Error('Failed to sign out');
      }
      return true;
    } catch (err) {
      console.error('Error signing out:', err);
      setError(err instanceof Error ? err : new Error('Failed to sign out'));
      return false;
    }
  };
  
  const handleLinkEmail = async (email: string): Promise<boolean> => {
    try {
      const success = await linkEmailToAnonymousUser(email);
      if (!success) {
        throw new Error('Failed to link email');
      }
      setIsAnonymous(false);
      return true;
    } catch (err) {
      console.error('Error linking email:', err);
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