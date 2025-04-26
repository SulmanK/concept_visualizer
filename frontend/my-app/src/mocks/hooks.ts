import React from "react";
import { vi } from "vitest";

// =============================================================================
// Mock Auth Context
// =============================================================================

// Create a context for our mock auth
export const mockAuthContext = React.createContext({
  user: { id: "test-user-id", email: "test@example.com" },
  session: { user: { id: "test-user-id", email: "test@example.com" } },
  isLoading: false,
  isAuthenticated: true,
  isAnonymous: false,
  signOut: vi.fn(),
  linkEmail: vi.fn(),
  refreshSession: vi.fn(),
  error: null,
});

// Mock auth context values
export const mockAuthContextValue = {
  user: { id: "test-user-id", email: "test@example.com" },
  session: { user: { id: "test-user-id", email: "test@example.com" } },
  isLoading: false,
  isAuthenticated: true,
  isAnonymous: false,
  signOut: vi.fn(),
  linkEmail: vi.fn(),
  refreshSession: vi.fn(),
  error: null,
};

// Create the auth hooks that match the ones in the real AuthContext
export const useAuth = () => React.useContext(mockAuthContext);
export const useAuthUser = () => React.useContext(mockAuthContext).user;
export const useUserId = () => React.useContext(mockAuthContext).user?.id;
export const useIsAnonymous = () =>
  React.useContext(mockAuthContext).isAnonymous;
export const useAuthIsLoading = () =>
  React.useContext(mockAuthContext).isLoading;

// =============================================================================
// Mock Toast Context
// =============================================================================

// Create a mock Toast context
export const mockToastContext = React.createContext({
  showToast: vi.fn(),
  showSuccess: vi.fn(),
  showError: vi.fn(),
  showWarning: vi.fn(),
  showInfo: vi.fn(),
  dismissToast: vi.fn(),
  dismissAll: vi.fn(),
});

// Hook for accessing toast context
export const useToast = () => React.useContext(mockToastContext);

// Mock toast context values
export const mockToastContextValue = {
  showToast: vi.fn(),
  showSuccess: vi.fn(),
  showError: vi.fn(),
  showWarning: vi.fn(),
  showInfo: vi.fn(),
  dismissToast: vi.fn(),
  dismissAll: vi.fn(),
};
