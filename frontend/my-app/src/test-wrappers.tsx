import React, { ReactElement, ReactNode } from "react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { vi } from "vitest";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";

// Create a context for our mock
const mockAuthContext = React.createContext({
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
const mockAuthContextValue = {
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

// Create mock rate limit context values
const mockRateLimitContextValue = {
  limits: {
    concept_generation: { remaining: 10, total: 20 },
    concept_refinement: { remaining: 10, total: 20 },
    image_export: { remaining: 10, total: 20 },
  },
  isLoading: false,
  decrementLimit: vi.fn(),
  refetchLimits: vi.fn(),
};

// Mock task context values
const mockTaskContextValue = {
  activeTaskId: null,
  hasActiveTask: false,
  activeTaskData: null,
  isTaskInitiating: false,
  latestResultId: null,
  setActiveTask: vi.fn(),
  clearActiveTask: vi.fn(),
  setIsTaskInitiating: vi.fn(),
  refreshTaskStatus: vi.fn(),
};

// Create a mock Toast context
const mockToastContext = React.createContext({
  showToast: vi.fn(),
  showSuccess: vi.fn(),
  showError: vi.fn(),
  showWarning: vi.fn(),
  showInfo: vi.fn(),
  dismissToast: vi.fn(),
  dismissAll: vi.fn(),
});

// This function is exported and can be used directly in tests
export const useToast = () => React.useContext(mockToastContext);

// Create a new QueryClient for each test
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
        gcTime: 0,
        staleTime: 0,
        refetchOnWindowFocus: false,
      },
    },
  });

// Define type for children prop
interface ProviderProps {
  children: ReactNode;
}

// Create mock context providers
const AuthContext = {
  Provider: ({ children }: ProviderProps) => (
    <mockAuthContext.Provider value={mockAuthContextValue}>
      {children}
    </mockAuthContext.Provider>
  ),
};

// Create mock contexts without value prop to avoid type errors
const RateLimitContext = {
  Provider: ({ children }: ProviderProps) => <>{children}</>,
};

const TaskContext = {
  Provider: ({ children }: ProviderProps) => <>{children}</>,
};

const ToastContext = {
  Provider: ({ children }: ProviderProps) => (
    <mockToastContext.Provider
      value={{
        showToast: vi.fn(),
        showSuccess: vi.fn(),
        showError: vi.fn(),
        showWarning: vi.fn(),
        showInfo: vi.fn(),
        hideToast: vi.fn(),
        toasts: [],
      }}
    >
      {children}
    </mockToastContext.Provider>
  ),
};

// Wrapper with QueryClientProvider only
export function createQueryClientWrapper() {
  const testQueryClient = createTestQueryClient();
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={testQueryClient}>
      {children}
    </QueryClientProvider>
  );
}

// Wrapper with all providers
export function AllProvidersWrapper({
  children,
}: {
  children: React.ReactNode;
}) {
  const testQueryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={testQueryClient}>
      <AuthContext.Provider>
        <RateLimitContext.Provider>
          <TaskContext.Provider>
            <ToastContext.Provider>
              <MemoryRouter>{children}</MemoryRouter>
            </ToastContext.Provider>
          </TaskContext.Provider>
        </RateLimitContext.Provider>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}

// Wrapper with router for specific route testing
export function withRoutesWrapper(
  initialEntries = ["/"],
  routePath = "/",
  element: ReactElement,
) {
  const testQueryClient = createTestQueryClient();

  return (
    <QueryClientProvider client={testQueryClient}>
      <AuthContext.Provider>
        <RateLimitContext.Provider>
          <TaskContext.Provider>
            <ToastContext.Provider>
              <MemoryRouter initialEntries={initialEntries}>
                <Routes>
                  <Route path={routePath} element={element} />
                </Routes>
              </MemoryRouter>
            </ToastContext.Provider>
          </TaskContext.Provider>
        </RateLimitContext.Provider>
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}
