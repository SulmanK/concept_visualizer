import React, { createContext, useContext, useEffect, useState } from 'react';
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
    linkEmail: handleLinkEmail
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