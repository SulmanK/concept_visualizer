import React from "react";
import {
  render,
  screen,
  waitFor,
  act,
  renderHook,
} from "@testing-library/react";
import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import {
  AuthProvider,
  useAuth,
  useAuthUser,
  useIsAnonymous,
  useAuthIsLoading,
} from "../AuthContext";
import * as supabaseClient from "../../services/supabaseClient";

// Mock supabaseClient
vi.mock("../../services/supabaseClient", () => {
  const subscription = {
    unsubscribe: vi.fn(),
  };

  return {
    supabase: {
      auth: {
        getSession: vi.fn(),
        onAuthStateChange: vi.fn(() => ({
          data: { subscription },
        })),
        refreshSession: vi.fn(),
      },
    },
    initializeAnonymousAuth: vi.fn(),
    isAnonymousUser: vi.fn(),
    linkEmailToAnonymousUser: vi.fn(),
    signOut: vi.fn(),
  };
});

// Mock document events
const mockDispatchEvent = vi.fn();
const originalDispatchEvent = document.dispatchEvent;

// Helper function to create a session object
const createMockSession = (
  isAnonymous = true,
  id = "test-user-id",
  expiresAt = Math.floor(Date.now() / 1000) + 3600,
) => ({
  access_token: "mock-token",
  refresh_token: "mock-refresh-token",
  expires_at: expiresAt,
  user: {
    id,
    app_metadata: { is_anonymous: isAnonymous },
    user_metadata: {},
    aud: "authenticated",
    created_at: new Date().toISOString(),
  },
});

// Test wrapper component
const TestAuthConsumer = () => {
  const auth = useAuth();
  const user = useAuthUser();
  const isAnonymous = useIsAnonymous();
  const isAuthenticated = user !== null;
  const isLoading = useAuthIsLoading();

  return (
    <div>
      <div data-testid="auth-loading">{String(isLoading)}</div>
      <div data-testid="auth-user">{user ? user.id : "no-user"}</div>
      <div data-testid="auth-anonymous">{String(isAnonymous)}</div>
      <div data-testid="auth-authenticated">{String(isAuthenticated)}</div>
      <button data-testid="auth-signout" onClick={() => auth.signOut()}>
        Sign Out
      </button>
      <button
        data-testid="auth-link"
        onClick={() => auth.linkEmail("test@example.com")}
      >
        Link Email
      </button>
    </div>
  );
};

describe("AuthContext", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    document.dispatchEvent = mockDispatchEvent;

    // Set up default mock implementations
    vi.mocked(supabaseClient.supabase.auth.getSession).mockResolvedValue({
      data: { session: null },
      error: null,
    });

    vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(null);
    vi.mocked(supabaseClient.isAnonymousUser).mockResolvedValue(true);
  });

  afterEach(() => {
    document.dispatchEvent = originalDispatchEvent;
  });

  describe("AuthProvider", () => {
    it("should initialize with loading state", async () => {
      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Initial loading state should be true
      expect(screen.getByTestId("auth-loading").textContent).toBe("true");

      // Wait for initialization to complete
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });
    });

    it("should call initializeAnonymousAuth on mount", async () => {
      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      await waitFor(() => {
        expect(supabaseClient.initializeAnonymousAuth).toHaveBeenCalledTimes(1);
      });
    });

    it("should set up auth state change listener", async () => {
      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      await waitFor(() => {
        expect(
          supabaseClient.supabase.auth.onAuthStateChange,
        ).toHaveBeenCalledTimes(1);
      });
    });

    it("should update state when session is available", async () => {
      // Mock a session
      const mockSession = createMockSession();
      vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(
        mockSession,
      );

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Verify user and anonymous states
      expect(screen.getByTestId("auth-user").textContent).toBe(
        mockSession.user.id,
      );
      expect(screen.getByTestId("auth-anonymous").textContent).toBe("true");
    });
  });

  describe("Auth State Changes", () => {
    it("should handle SIGNED_IN event", async () => {
      // Mock initial anonymous session
      const anonymousSession = createMockSession(true, "anonymous-id");
      vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(
        anonymousSession,
      );

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for initial state to be set
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Extract the onAuthStateChange callback
      const onAuthStateChange = vi.mocked(
        supabaseClient.supabase.auth.onAuthStateChange,
      ).mock.calls[0][0];

      // Create a new non-anonymous session
      const newSession = createMockSession(false, "signed-in-id");

      // Simulate SIGNED_IN event
      await act(async () => {
        onAuthStateChange("SIGNED_IN", newSession);
      });

      // Verify state updates
      expect(screen.getByTestId("auth-user").textContent).toBe("signed-in-id");
      expect(screen.getByTestId("auth-anonymous").textContent).toBe("false");
      expect(screen.getByTestId("auth-authenticated").textContent).toBe("true");
    });

    it("should handle SIGNED_OUT event", async () => {
      // Mock initial session
      const initialSession = createMockSession(false, "signed-in-id");
      vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(
        initialSession,
      );

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for initial state to be set
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Extract the onAuthStateChange callback
      const onAuthStateChange = vi.mocked(
        supabaseClient.supabase.auth.onAuthStateChange,
      ).mock.calls[0][0];

      // Simulate SIGNED_OUT event
      await act(async () => {
        onAuthStateChange("SIGNED_OUT", null);
      });

      // Verify state updates
      expect(screen.getByTestId("auth-user").textContent).toBe("no-user");
      expect(screen.getByTestId("auth-authenticated").textContent).toBe(
        "false",
      );
    });

    it("should handle token refresh (non-significant change)", async () => {
      // Mock initial session
      const initialSession = createMockSession(false, "user-id");
      vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(
        initialSession,
      );

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for initial state to be set
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Extract the onAuthStateChange callback
      const onAuthStateChange = vi.mocked(
        supabaseClient.supabase.auth.onAuthStateChange,
      ).mock.calls[0][0];

      // Create a new session with same ID but new token
      const refreshedSession = {
        ...initialSession,
        access_token: "new-token",
        expires_at: initialSession.expires_at + 3600,
      };

      // Simulate TOKEN_REFRESHED event
      await act(async () => {
        onAuthStateChange("TOKEN_REFRESHED", refreshedSession);
      });

      // Verify the session was updated but user remains the same
      expect(screen.getByTestId("auth-user").textContent).toBe("user-id");
    });
  });

  describe("Auth Actions", () => {
    it("should call signOut function", async () => {
      // Mock successful sign out
      vi.mocked(supabaseClient.signOut).mockResolvedValue(true);

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Click sign out button
      await act(async () => {
        screen.getByTestId("auth-signout").click();
      });

      // Verify signOut was called
      expect(supabaseClient.signOut).toHaveBeenCalledTimes(1);
    });

    it("should call linkEmail function", async () => {
      // Mock successful link
      vi.mocked(supabaseClient.linkEmailToAnonymousUser).mockResolvedValue(
        true,
      );

      render(
        <AuthProvider>
          <TestAuthConsumer />
        </AuthProvider>,
      );

      // Wait for loading to complete
      await waitFor(() => {
        expect(screen.getByTestId("auth-loading").textContent).toBe("false");
      });

      // Click link email button
      await act(async () => {
        screen.getByTestId("auth-link").click();
      });

      // Verify linkEmailToAnonymousUser was called with the right email
      expect(supabaseClient.linkEmailToAnonymousUser).toHaveBeenCalledWith(
        "test@example.com",
      );
    });
  });

  describe("useAuth hooks", () => {
    it("should throw error if used outside provider", () => {
      // Silence console.error to avoid noisy output
      const originalConsoleError = console.error;
      console.error = vi.fn();

      try {
        expect(() => {
          renderHook(() => useAuth());
        }).toThrow("useAuth must be used within an AuthProvider");
      } finally {
        console.error = originalConsoleError;
      }
    });

    it("should retrieve correct values from context", async () => {
      // Mock a session
      const mockSession = createMockSession(true, "test-id");
      vi.mocked(supabaseClient.initializeAnonymousAuth).mockResolvedValue(
        mockSession,
      );

      const wrapper = ({ children }) => <AuthProvider>{children}</AuthProvider>;

      const { result } = renderHook(
        () => ({
          auth: useAuth(),
          user: useAuthUser(),
          isAnonymous: useIsAnonymous(),
          isAuthenticated: useAuthUser() !== null,
          isLoading: useAuthIsLoading(),
        }),
        { wrapper },
      );

      // Wait for loading to complete
      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      // Verify hooks return the correct values
      expect(result.current.user).toEqual(mockSession.user);
      expect(result.current.isAnonymous).toBe(true);
      expect(result.current.isAuthenticated).toBe(true);
      expect(typeof result.current.auth.signOut).toBe("function");
      expect(typeof result.current.auth.linkEmail).toBe("function");
    });
  });
});
