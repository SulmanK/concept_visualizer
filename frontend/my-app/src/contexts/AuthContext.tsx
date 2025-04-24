import React, {
  useContext,
  useEffect,
  useState,
  useRef,
  useCallback,
  useMemo,
} from "react";
import { createContext, useContextSelector } from "use-context-selector";
import { Session, User } from "@supabase/supabase-js";
import {
  supabase,
  initializeAnonymousAuth,
  isAnonymousUser,
  linkEmailToAnonymousUser,
  signOut,
} from "../services/supabaseClient";

interface AuthContextType {
  session: Session | null;
  user: User | null;
  isAnonymous: boolean;
  isLoading: boolean;
  error: Error | null;
  signOut: () => Promise<boolean>;
  linkEmail: (email: string) => Promise<boolean>;
}

/**
 * Determines if a user is anonymous based on app_metadata
 */
function determineIsAnonymous(session: Session | null): boolean {
  if (!session || !session.user) return true;
  return session.user.app_metadata?.is_anonymous === true;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({
  children,
}) => {
  const [session, setSession] = useState<Session | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [isAnonymous, setIsAnonymous] = useState<boolean>(true);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<Error | null>(null);

  // Refs to track previous state for comparison
  const previousUserIdRef = useRef<string | null>(null);
  const previousIsAnonymousRef = useRef<boolean>(true);

  // We're removing the refreshAuth function and the refresh timer logic
  // since the Axios interceptors will now handle token refreshing

  // Set up auth-error-needs-logout event listener
  useEffect(() => {
    const handleAuthError = () => {
      console.log(
        "[AUTH:Context] Received auth-error-needs-logout event, signing out",
      );
      handleSignOut();
    };

    // Add event listener
    document.addEventListener("auth-error-needs-logout", handleAuthError);

    // Cleanup
    return () => {
      document.removeEventListener("auth-error-needs-logout", handleAuthError);
    };
  }, []);

  useEffect(() => {
    // Initialize auth on mount
    const initAuth = async () => {
      console.log("[AUTH:Context] Initializing authentication");
      try {
        setIsLoading(true);

        // Initialize anonymous authentication
        const authSession = await initializeAnonymousAuth();
        if (authSession) {
          const currentUserId = authSession.user?.id || null;
          const currentIsAnonymous = determineIsAnonymous(authSession);

          console.log("[AUTH:Context] Initial auth session established", {
            userId: currentUserId,
            isAnonymous: currentIsAnonymous,
            expiresAt: new Date(authSession.expires_at! * 1000).toISOString(),
          });

          // Always update session for the token
          setSession(authSession);

          // Update user and isAnonymous state
          setUser(authSession.user);
          setIsAnonymous(currentIsAnonymous);

          // Initialize refs
          previousUserIdRef.current = currentUserId;
          previousIsAnonymousRef.current = currentIsAnonymous;

          console.log(
            "[AUTH:Context] Initial user anonymous status:",
            currentIsAnonymous,
          );
        } else {
          console.error(
            "[AUTH:Context] Failed to establish initial auth session",
          );
        }

        // Set up auth state listener
        const {
          data: { subscription },
        } = supabase.auth.onAuthStateChange(async (event, newSession) => {
          const prevUserId = previousUserIdRef.current;
          const prevIsAnonymous = previousIsAnonymousRef.current;

          const currentUserId = newSession?.user?.id || null;
          const currentIsAnonymous = determineIsAnonymous(newSession);

          console.log("[AUTH:Context] Auth state changed:", event, {
            userId: currentUserId,
            prevUserId: prevUserId,
            isAnonymous: currentIsAnonymous,
            prevIsAnonymous: prevIsAnonymous,
            expiresAt: newSession?.expires_at
              ? new Date(newSession.expires_at * 1000).toISOString()
              : null,
          });

          // Always update session if it exists, for token refresh interceptor
          if (newSession) {
            setSession(newSession);
            // Log if only token changed
            if (
              currentUserId === prevUserId &&
              currentIsAnonymous === prevIsAnonymous
            ) {
              console.log(
                "[AUTH:Context] Session updated (token likely refreshed), user identity unchanged.",
              );
            }
          } else {
            setSession(null);
          }

          // Update user/anonymous state only if they actually changed
          const isSignificantChange =
            currentUserId !== prevUserId ||
            currentIsAnonymous !== prevIsAnonymous ||
            event === "SIGNED_IN" ||
            event === "SIGNED_OUT";

          if (isSignificantChange) {
            console.log(
              `[AUTH:Context] Significant auth change detected (Event: ${event}, User Change: ${
                currentUserId !== prevUserId
              }, Anon Change: ${
                currentIsAnonymous !== prevIsAnonymous
              }). Updating user state.`,
            );
            setUser(newSession?.user || null);
            setIsAnonymous(currentIsAnonymous);

            // Update refs
            previousUserIdRef.current = currentUserId;
            previousIsAnonymousRef.current = currentIsAnonymous;
          }
        });

        // Return cleanup function
        return () => {
          console.log(
            "[AUTH:Context] Cleaning up auth subscription on unmount",
          );
          subscription.unsubscribe();
        };
      } catch (err) {
        console.error("[AUTH:Context] Error initializing auth:", err);
        setError(
          err instanceof Error
            ? err
            : new Error("Failed to initialize authentication"),
        );
      } finally {
        setIsLoading(false);
        console.log("[AUTH:Context] Auth initialization complete");
      }
    };

    initAuth();
  }, []);

  const handleSignOut = useCallback(async (): Promise<boolean> => {
    console.log("[AUTH:Context] Sign out requested");
    try {
      const success = await signOut();
      if (!success) {
        console.error("[AUTH:Context] Sign out operation failed");
        throw new Error("Failed to sign out");
      }
      console.log("[AUTH:Context] Sign out successful");
      return true;
    } catch (err) {
      console.error("[AUTH:Context] Error signing out:", err);
      setError(err instanceof Error ? err : new Error("Failed to sign out"));
      return false;
    }
  }, []);

  const handleLinkEmail = useCallback(
    async (email: string): Promise<boolean> => {
      console.log("[AUTH:Context] Email linking requested");
      try {
        const success = await linkEmailToAnonymousUser(email);
        if (!success) {
          console.error("[AUTH:Context] Email linking operation failed");
          throw new Error("Failed to link email");
        }
        setIsAnonymous(false);
        console.log("[AUTH:Context] Email linking successful");
        return true;
      } catch (err) {
        console.error("[AUTH:Context] Error linking email:", err);
        setError(
          err instanceof Error ? err : new Error("Failed to link email"),
        );
        return false;
      }
    },
    [],
  );

  const value = useMemo(
    () => ({
      session,
      user,
      isAnonymous,
      isLoading,
      error,
      signOut: handleSignOut,
      linkEmail: handleLinkEmail,
    }),
    [
      session,
      user,
      isAnonymous,
      isLoading,
      error,
      handleSignOut,
      handleLinkEmail,
    ],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

export const useAuth = () => {
  const context = useContextSelector(AuthContext, (state) => state);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export const useAuthUser = () => {
  const context = useContextSelector(AuthContext, (state) => state?.user);
  if (context === undefined) {
    throw new Error("useAuthUser must be used within an AuthProvider");
  }
  return context;
};

export const useUserId = () => {
  const context = useContextSelector(AuthContext, (state) => state?.user?.id);
  if (context === undefined && process.env.NODE_ENV !== "production") {
    console.warn("useUserId called outside AuthProvider or no user exists");
  }
  return context || null;
};

export const useIsAnonymous = () => {
  const context = useContextSelector(
    AuthContext,
    (state) => state?.isAnonymous,
  );
  if (context === undefined) {
    throw new Error("useIsAnonymous must be used within an AuthProvider");
  }
  return context;
};

export const useAuthIsLoading = () => {
  const context = useContextSelector(AuthContext, (state) => state?.isLoading);
  if (context === undefined) {
    throw new Error("useAuthIsLoading must be used within an AuthProvider");
  }
  return context;
};
