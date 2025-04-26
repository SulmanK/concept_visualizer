import { vi, describe, it, expect, beforeEach, afterEach } from "vitest";
import type { Session, User } from "@supabase/supabase-js";

// FIX: Declare mock functions *before* they are used in vi.mock
const mockSignInAnonymously = vi.fn();
const mockSignOut = vi.fn();
const mockGetSession = vi.fn();
const mockUpdateUser = vi.fn();
const mockCreateSignedUrl = vi.fn();
const mockGetPublicUrl = vi.fn();
const mockFrom = vi.fn();
const mockRefreshSession = vi.fn();

// Mock dependencies
vi.mock("@supabase/supabase-js", () => {
  return {
    // Use the pre-declared mock functions here
    createClient: () => ({
      auth: {
        signInAnonymously: mockSignInAnonymously,
        signOut: mockSignOut,
        getSession: mockGetSession,
        updateUser: mockUpdateUser,
        refreshSession: mockRefreshSession,
      },
      storage: {
        from: mockFrom,
      },
    }),
  };
});

vi.mock("../rateLimitService", () => ({
  fetchRateLimits: vi.fn().mockResolvedValue({}),
}));

vi.mock("../configService", () => ({
  getBucketName: vi.fn().mockReturnValue("test-bucket"),
}));

// Import after mocks are set up
import {
  initializeAnonymousAuth,
  getUserId,
  isAnonymousUser,
  linkEmailToAnonymousUser,
  signOut,
  getAuthenticatedImageUrl,
  validateAndRefreshToken,
  determineIsAnonymous,
} from "../supabaseClient";

describe("Supabase Client", () => {
  // Mock console methods
  const consoleErrorSpy = vi
    .spyOn(console, "error")
    .mockImplementation(() => {});

  beforeEach(() => {
    vi.clearAllMocks();

    // Reset all mock implementations
    mockGetSession.mockReset();
    mockSignInAnonymously.mockReset();
    mockRefreshSession.mockReset();
    mockUpdateUser.mockReset();
    mockSignOut.mockReset();
    mockCreateSignedUrl.mockReset();
    mockGetPublicUrl.mockReset();

    // Set up storage.from mock
    mockFrom.mockImplementation(() => ({
      createSignedUrl: mockCreateSignedUrl,
      getPublicUrl: mockGetPublicUrl,
    }));

    // Default implementation for getPublicUrl
    mockGetPublicUrl.mockImplementation((path) => ({
      data: { publicUrl: `https://example.com/public/${path}` },
    }));
  });

  afterEach(() => {
    vi.resetAllMocks();
  });

  describe("signOut", () => {
    it("should call supabase.auth.signOut", async () => {
      // Setup mock return
      mockSignOut.mockResolvedValueOnce({ error: null });

      // Call function
      const result = await signOut();

      // Verify
      expect(mockSignOut).toHaveBeenCalledTimes(1);
      expect(result).toBe(true);
    });

    it("should return false if signOut fails", async () => {
      // Setup mock return
      mockSignOut.mockResolvedValueOnce({
        error: { message: "Sign out failed" },
      });

      // Call function
      const result = await signOut();

      // Verify
      expect(mockSignOut).toHaveBeenCalledTimes(1);
      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("sign out failed"),
        expect.anything(),
      );
    });
  });

  describe("initializeAnonymousAuth", () => {
    it("should return existing session if available", async () => {
      // Setup mock session
      const mockSession: Session = {
        access_token: "mock-token",
        token_type: "bearer",
        expires_in: 3600,
        expires_at: 1600000000,
        refresh_token: "mock-refresh",
        user: { id: "user-123" } as User,
      };

      mockGetSession.mockResolvedValueOnce({
        data: { session: mockSession },
        error: null,
      });

      // Call function
      const result = await initializeAnonymousAuth();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockSession);
    });

    it("should sign in anonymously if no session exists", async () => {
      // Setup mocks
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });

      const mockSession: Session = {
        access_token: "mock-token",
        token_type: "bearer",
        expires_in: 3600,
        expires_at: 1600000000,
        refresh_token: "mock-refresh",
        user: { id: "anon-123" } as User,
      };

      mockSignInAnonymously.mockResolvedValueOnce({
        data: { session: mockSession },
        error: null,
      });

      // Call function
      const result = await initializeAnonymousAuth();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(mockSignInAnonymously).toHaveBeenCalledTimes(1);
      expect(result).toEqual(mockSession);
    });

    it("should handle errors during session retrieval", async () => {
      // Setup mock
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: { message: "Session error" },
      });

      // Call function
      const result = await initializeAnonymousAuth();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(result).toBeNull();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error retrieving session"),
        expect.anything(),
      );
    });

    it("should handle errors during anonymous sign-in", async () => {
      // Setup mocks
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });

      mockSignInAnonymously.mockResolvedValueOnce({
        data: { session: null },
        error: { message: "Sign in error" },
      });

      // Call function
      const result = await initializeAnonymousAuth();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(mockSignInAnonymously).toHaveBeenCalledTimes(1);
      expect(result).toBeNull();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error signing in anonymously"),
        expect.anything(),
      );
    });
  });

  describe("getUserId", () => {
    it("should return user id if session exists", async () => {
      // Setup mock
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            user: { id: "user-123" },
          },
        },
        error: null,
      });

      // Call function
      const result = await getUserId();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(result).toBe("user-123");
    });

    it("should return null if no session exists", async () => {
      // Setup mock
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });

      // Call function
      const result = await getUserId();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(result).toBeNull();
    });

    it("should return null if error occurs", async () => {
      // Setup mock
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: { message: "Session error" },
      });

      // Call function
      const result = await getUserId();

      // Verify
      expect(mockGetSession).toHaveBeenCalledTimes(1);
      expect(result).toBeNull();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error retrieving user ID"),
        expect.anything(),
      );
    });
  });

  describe("isAnonymousUser", () => {
    it("should return true for anonymous user", async () => {
      // Setup mock
      const mockUser = {
        id: "anon-123",
        app_metadata: {
          provider: "anonymous",
        },
      } as User;

      // Call function
      const result = isAnonymousUser(mockUser);

      // Verify
      expect(result).toBe(true);
    });

    it("should return false for non-anonymous user", async () => {
      // Setup mock
      const mockUser = {
        id: "user-123",
        app_metadata: {
          provider: "email",
        },
      } as User;

      // Call function
      const result = isAnonymousUser(mockUser);

      // Verify
      expect(result).toBe(false);
    });

    it("should return false if user is null", async () => {
      // Call function
      const result = isAnonymousUser(null);

      // Verify
      expect(result).toBe(false);
    });
  });

  describe("linkEmailToAnonymousUser", () => {
    it("should update user with email", async () => {
      // Setup mock
      mockUpdateUser.mockResolvedValueOnce({
        data: { user: { id: "user-123", email: "test@example.com" } },
        error: null,
      });

      // Call function
      const result = await linkEmailToAnonymousUser("test@example.com");

      // Verify
      expect(mockUpdateUser).toHaveBeenCalledWith({
        email: "test@example.com",
      });
      expect(result).toBe(true);
    });

    it("should return false if update fails", async () => {
      // Setup mock
      mockUpdateUser.mockResolvedValueOnce({
        data: { user: null },
        error: { message: "Update error" },
      });

      // Call function
      const result = await linkEmailToAnonymousUser("test@example.com");

      // Verify
      expect(mockUpdateUser).toHaveBeenCalledWith({
        email: "test@example.com",
      });
      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining("Error linking email to anonymous user"),
        expect.anything(),
      );
    });
  });

  describe("determineIsAnonymous", () => {
    it("should return true for anonymous user session", () => {
      const mockSession = {
        user: {
          id: "anon-123",
          app_metadata: {
            provider: "anonymous",
          },
        },
      } as Session;

      const result = determineIsAnonymous(mockSession);
      expect(result).toBe(true);
    });

    it("should return false for non-anonymous user session", () => {
      const mockSession = {
        user: {
          id: "user-123",
          app_metadata: {
            provider: "email",
          },
        },
      } as Session;

      const result = determineIsAnonymous(mockSession);
      expect(result).toBe(false);
    });

    it("should return true if session is null", () => {
      const result = determineIsAnonymous(null);
      expect(result).toBe(true);
    });
  });

  describe("getAuthenticatedImageUrl", () => {
    it("should create signed URL with correct parameters", async () => {
      // Mock successful signed URL creation
      mockCreateSignedUrl.mockResolvedValueOnce({
        data: { signedUrl: "https://example.com/signed-url" },
        error: null,
      });

      // Call the function
      const url = await getAuthenticatedImageUrl(
        "test-bucket",
        "image/path.png",
      );

      // Verify signed URL creation
      expect(mockFrom).toHaveBeenCalledWith("test-bucket");
      expect(mockCreateSignedUrl).toHaveBeenCalledWith(
        "image/path.png",
        expect.any(Number), // Expiry time
      );

      // Verify URL was returned
      expect(url).toBe("https://example.com/signed-url");
    });

    it("should handle signed URL errors", async () => {
      // Mock createSignedUrl error
      mockCreateSignedUrl.mockResolvedValueOnce({
        data: { signedUrl: null },
        error: { message: "Signing error" },
      });

      // Mock getPublicUrl as fallback
      mockGetPublicUrl.mockImplementationOnce((path) => ({
        data: { publicUrl: `https://example.com/public/${path}` },
      }));

      // Call the function - should return public URL as fallback
      const url = await getAuthenticatedImageUrl(
        "test-bucket",
        "image/path.png",
      );

      // Should return public URL
      expect(url).toBe("https://example.com/public/image/path.png");
    });
  });

  describe("validateAndRefreshToken", () => {
    it("should initialize anonymous auth if no session exists", async () => {
      // Mock no session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null,
      });

      // Mock successful anonymous sign-in
      mockSignInAnonymously.mockResolvedValueOnce({
        data: {
          session: {
            access_token: "new-anon-token",
            user: { id: "new-anon-user" },
          },
        },
        error: null,
      });

      // Override initializeAnonymousAuth to return a successful session
      const originalInitializeAnonymousAuth = initializeAnonymousAuth;
      globalThis.initializeAnonymousAuth = vi.fn().mockResolvedValueOnce({
        access_token: "new-anon-token",
      });

      // Call the function
      const session = await validateAndRefreshToken();

      // Restore original function
      globalThis.initializeAnonymousAuth = originalInitializeAnonymousAuth;

      // Verify anonymous auth was initiated
      expect(session?.access_token).toBe("new-anon-token");
    });

    it("should refresh token if about to expire", async () => {
      // Mock session that's close to expiry
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 200; // 200 seconds from now
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: "old-token",
            expires_at: expiryTimestamp,
            user: { id: "test-user" },
          },
        },
        error: null,
      });

      // Mock successful refresh
      mockRefreshSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: "refreshed-token",
            user: { id: "test-user" },
          },
        },
        error: null,
      });

      // Call the function
      const session = await validateAndRefreshToken();

      // Verify token was refreshed
      expect(session?.access_token).toBe("refreshed-token");
    });

    it("should return existing session if not expired", async () => {
      // Mock valid session
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: "valid-token",
            expires_at: expiryTimestamp,
            user: { id: "test-user" },
          },
        },
        error: null,
      });

      // Call the function
      const session = await validateAndRefreshToken();

      // Verify existing session was returned
      expect(session?.access_token).toBe("valid-token");
      expect(mockRefreshSession).not.toHaveBeenCalled();
    });
  });
});
