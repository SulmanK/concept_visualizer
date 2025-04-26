import React, { ReactElement, ReactNode } from "react";
import { MemoryRouter, Routes, Route } from "react-router-dom";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  mockAuthContext,
  mockAuthContextValue,
  mockToastContext,
  mockToastContextValue,
} from "./mocks/hooks";

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
    <mockToastContext.Provider value={mockToastContextValue}>
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
