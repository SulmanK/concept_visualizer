import { useContextSelector } from "use-context-selector";
import { AuthContext } from "../contexts/AuthContext";

/**
 * Hook to access the full auth context value
 * @returns The complete auth context
 * @throws Error if used outside of AuthProvider
 */
export const useAuth = () => {
  const context = useContextSelector(AuthContext, (state) => state);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

/**
 * Hook to access just the user object from auth context
 * @returns The current user or null
 * @throws Error if used outside of AuthProvider
 */
export const useAuthUser = () => {
  const context = useContextSelector(AuthContext, (state) => state?.user);
  if (context === undefined) {
    throw new Error("useAuthUser must be used within an AuthProvider");
  }
  return context;
};

/**
 * Hook to access just the user ID from auth context
 * @returns The current user ID or null
 */
export const useUserId = () => {
  const context = useContextSelector(AuthContext, (state) => state?.user?.id);
  if (context === undefined && process.env.NODE_ENV !== "production") {
    console.warn("useUserId called outside AuthProvider or no user exists");
  }
  return context || null;
};

/**
 * Hook to access the anonymous status from auth context
 * @returns Boolean indicating if the current user is anonymous
 * @throws Error if used outside of AuthProvider
 */
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

/**
 * Hook to access the loading state from auth context
 * @returns Boolean indicating if auth is currently loading
 * @throws Error if used outside of AuthProvider
 */
export const useAuthIsLoading = () => {
  const context = useContextSelector(AuthContext, (state) => state?.isLoading);
  if (context === undefined) {
    throw new Error("useAuthIsLoading must be used within an AuthProvider");
  }
  return context;
};
