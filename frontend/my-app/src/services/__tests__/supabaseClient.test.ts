import { vi, describe, it, expect, beforeEach, afterEach } from 'vitest';
import { 
  supabase, 
  initializeAnonymousAuth, 
  getUserId, 
  isAnonymousUser, 
  linkEmailToAnonymousUser,
  signOut,
  getAuthenticatedImageUrl,
  validateAndRefreshToken
} from '../supabaseClient';
import * as rateLimitService from '../rateLimitService';
import * as configService from '../configService';

// Create mock functions
const mockSignInAnonymously = vi.fn();
const mockGetSession = vi.fn();
const mockRefreshSession = vi.fn();
const mockUpdateUser = vi.fn();
const mockSignOut = vi.fn();
const mockCreateSignedUrl = vi.fn();
const mockGetPublicUrl = vi.fn();
const mockFrom = vi.fn();

// Mock dependencies
vi.mock('@supabase/supabase-js', () => {
  return {
    createClient: () => ({
      auth: {
        signInAnonymously: mockSignInAnonymously,
        getSession: mockGetSession,
        refreshSession: mockRefreshSession,
        updateUser: mockUpdateUser,
        signOut: mockSignOut
      },
      storage: {
        from: mockFrom
      }
    })
  };
});

vi.mock('../rateLimitService', () => ({
  fetchRateLimits: vi.fn().mockResolvedValue({})
}));

vi.mock('../configService', () => ({
  getBucketName: vi.fn().mockReturnValue('test-bucket')
}));

describe('Supabase Client', () => {
  // Console spies
  const consoleLogSpy = vi.spyOn(console, 'log').mockImplementation(() => {});
  const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  
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
      getPublicUrl: mockGetPublicUrl
    }));
    
    // Default implementation for getPublicUrl
    mockGetPublicUrl.mockImplementation((path) => ({
      data: { publicUrl: `https://example.com/public/${path}` }
    }));
  });
  
  afterEach(() => {
    vi.resetAllMocks();
  });
  
  describe('initializeAnonymousAuth', () => {
    it('should sign in anonymously if no session exists', async () => {
      // Mock no existing session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Mock successful anonymous sign-in
      mockSignInAnonymously.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-access-token',
            refresh_token: 'new-refresh-token',
            expires_at: Math.floor(Date.now() / 1000) + 3600,
            user: { id: 'new-anon-user' }
          }
        },
        error: null
      });
      
      // Call the function
      const session = await initializeAnonymousAuth();
      
      // Verify anonymous auth was initiated
      expect(mockSignInAnonymously).toHaveBeenCalled();
      expect(session).not.toBeNull();
      expect(session?.access_token).toBe('new-access-token');
      
      // Verify rate limits were refreshed
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledWith(true);
      
      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('No session found'));
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Anonymous sign-in successful'));
    });
    
    it('should refresh the token if session exists but is about to expire', async () => {
      // Mock existing session that's close to expiry
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 200; // 200 seconds from now, < 5 minutes
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'old-access-token',
            refresh_token: 'old-refresh-token',
            expires_at: expiryTimestamp,
            user: { id: 'existing-user' }
          }
        },
        error: null
      });
      
      // Mock successful token refresh
      mockRefreshSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'refreshed-access-token',
            refresh_token: 'refreshed-refresh-token',
            expires_at: Math.floor(Date.now() / 1000) + 3600,
            user: { id: 'existing-user' }
          }
        },
        error: null
      });
      
      // Call the function
      const session = await initializeAnonymousAuth();
      
      // Verify anonymous auth was NOT initiated (since session exists)
      expect(mockSignInAnonymously).not.toHaveBeenCalled();
      
      // Verify token was refreshed
      expect(mockRefreshSession).toHaveBeenCalled();
      expect(session?.access_token).toBe('refreshed-access-token');
      
      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Existing session expires soon'));
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Session refreshed successfully'));
    });
    
    it('should use existing session if valid and not near expiry', async () => {
      // Mock existing session that's far from expiry
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 3000; // 50 minutes from now
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-access-token',
            refresh_token: 'valid-refresh-token',
            expires_at: expiryTimestamp,
            user: { id: 'existing-user' }
          }
        },
        error: null
      });
      
      // Call the function
      const session = await initializeAnonymousAuth();
      
      // Verify no auth changes were made
      expect(mockSignInAnonymously).not.toHaveBeenCalled();
      expect(mockRefreshSession).not.toHaveBeenCalled();
      
      // Verify existing session was returned
      expect(session?.access_token).toBe('valid-access-token');
      
      // Verify logs
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Using existing valid session'));
    });
    
    it('should handle sign-in errors', async () => {
      // Mock no existing session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Mock failed anonymous sign-in
      const authError = new Error('Auth error');
      mockSignInAnonymously.mockRejectedValueOnce(authError);
      
      // Call the function and expect it to pass through the error
      try {
        await initializeAnonymousAuth();
        // If we get here, the test should fail
        expect(true).toBe(false); // This should not execute
      } catch (error) {
        expect(error).toBe(authError);
      }
      
      // Verify error was logged
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error initializing anonymous auth'),
        expect.any(Error)
      );
    });
  });
  
  describe('getUserId', () => {
    it('should return user ID from session', async () => {
      // Mock session with user
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            user: { id: 'test-user-id' }
          }
        },
        error: null
      });
      
      // Call the function
      const userId = await getUserId();
      
      // Verify correct ID was returned
      expect(userId).toBe('test-user-id');
    });
    
    it('should return null if no session exists', async () => {
      // Mock no session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Call the function
      const userId = await getUserId();
      
      // Verify null was returned
      expect(userId).toBeNull();
    });
    
    it('should handle errors gracefully', async () => {
      // Mock error
      mockGetSession.mockRejectedValueOnce(new Error('Session error'));
      
      // Call the function
      const userId = await getUserId();
      
      // Verify null was returned and error was logged
      expect(userId).toBeNull();
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error getting user ID'),
        expect.any(Error)
      );
    });
  });
  
  describe('isAnonymousUser', () => {
    it('should return true for anonymous users', async () => {
      // Mock anonymous user session
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            user: { 
              id: 'anon-user-id',
              app_metadata: { is_anonymous: true }
            }
          }
        },
        error: null
      });
      
      // Call the function
      const isAnon = await isAnonymousUser();
      
      // Verify correct result
      expect(isAnon).toBe(true);
    });
    
    it('should return false for non-anonymous users', async () => {
      // Mock non-anonymous user session
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            user: { 
              id: 'regular-user-id',
              app_metadata: { is_anonymous: false }
            }
          }
        },
        error: null
      });
      
      // Call the function
      const isAnon = await isAnonymousUser();
      
      // Verify correct result
      expect(isAnon).toBe(false);
    });
    
    it('should return false if no session exists', async () => {
      // Mock no session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Call the function
      const isAnon = await isAnonymousUser();
      
      // Verify correct result
      expect(isAnon).toBe(false);
    });
  });
  
  describe('linkEmailToAnonymousUser', () => {
    it('should update user with email', async () => {
      // Mock successful user update
      mockUpdateUser.mockResolvedValueOnce({
        data: { user: { id: 'test-user-id', email: 'test@example.com' } },
        error: null
      });
      
      // Call the function
      const result = await linkEmailToAnonymousUser('test@example.com');
      
      // Verify update was called and result is true
      expect(mockUpdateUser).toHaveBeenCalledWith({ email: 'test@example.com' });
      expect(result).toBe(true);
    });
    
    it('should handle update errors', async () => {
      // Mock update error
      mockUpdateUser.mockResolvedValueOnce({
        data: { user: null },
        error: { message: 'Update error' }
      });
      
      // Call the function
      const result = await linkEmailToAnonymousUser('test@example.com');
      
      // Verify result is false and error was logged
      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error linking email to anonymous user'),
        expect.any(Object)
      );
    });
  });
  
  describe('signOut', () => {
    it('should sign out and initialize new anonymous session', async () => {
      // Mock successful sign out
      mockSignOut.mockResolvedValueOnce({
        error: null
      });
      
      // Mock successful anonymous sign-in after sign out
      mockGetSession.mockResolvedValue({
        data: { session: null },
        error: null
      });
      
      mockSignInAnonymously.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-anon-token',
            user: { id: 'new-anon-user' }
          }
        },
        error: null
      });
      
      // Override initializeAnonymousAuth to return a successful session
      const originalInitializeAnonymousAuth = initializeAnonymousAuth;
      globalThis.initializeAnonymousAuth = vi.fn().mockResolvedValueOnce({
        access_token: 'new-anon-token'
      });
      
      // Call the function
      const result = await signOut();
      
      // Restore original function
      globalThis.initializeAnonymousAuth = originalInitializeAnonymousAuth;
      
      // Verify sign out
      expect(mockSignOut).toHaveBeenCalled();
      expect(rateLimitService.fetchRateLimits).toHaveBeenCalledWith(true);
      expect(result).toBe(true);
    });
    
    it('should handle sign out errors', async () => {
      // Mock sign out error
      mockSignOut.mockResolvedValueOnce({
        error: { message: 'Sign out error' }
      });
      
      // Call the function
      const result = await signOut();
      
      // Verify result is false and error was logged
      expect(result).toBe(false);
      expect(consoleErrorSpy).toHaveBeenCalledWith(
        expect.stringContaining('Error signing out'),
        expect.any(Object)
      );
    });
  });
  
  describe('getAuthenticatedImageUrl', () => {
    it('should create signed URL with correct parameters', async () => {
      // Mock successful signed URL creation
      mockCreateSignedUrl.mockResolvedValueOnce({
        data: { signedUrl: 'https://example.com/signed-url' },
        error: null
      });
      
      // Call the function
      const url = await getAuthenticatedImageUrl('test-bucket', 'image/path.png');
      
      // Verify signed URL creation
      expect(mockFrom).toHaveBeenCalledWith('test-bucket');
      expect(mockCreateSignedUrl).toHaveBeenCalledWith(
        'image/path.png',
        expect.any(Number) // Expiry time
      );
      
      // Verify URL was returned
      expect(url).toBe('https://example.com/signed-url');
    });
    
    it('should handle signed URL errors', async () => {
      // Mock createSignedUrl error
      mockCreateSignedUrl.mockResolvedValueOnce({
        data: { signedUrl: null },
        error: { message: 'Signing error' }
      });
      
      // Mock getPublicUrl as fallback
      mockGetPublicUrl.mockImplementationOnce((path) => ({
        data: { publicUrl: `https://example.com/public/${path}` }
      }));
      
      // Call the function - should return public URL as fallback
      const url = await getAuthenticatedImageUrl('test-bucket', 'image/path.png');
      
      // Should return public URL
      expect(url).toBe('https://example.com/public/image/path.png');
    });
  });
  
  describe('validateAndRefreshToken', () => {
    it('should initialize anonymous auth if no session exists', async () => {
      // Mock no session
      mockGetSession.mockResolvedValueOnce({
        data: { session: null },
        error: null
      });
      
      // Mock successful anonymous sign-in
      mockSignInAnonymously.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'new-anon-token',
            user: { id: 'new-anon-user' }
          }
        },
        error: null
      });
      
      // Override initializeAnonymousAuth to return a successful session
      const originalInitializeAnonymousAuth = initializeAnonymousAuth;
      globalThis.initializeAnonymousAuth = vi.fn().mockResolvedValueOnce({
        access_token: 'new-anon-token'
      });
      
      // Call the function
      const session = await validateAndRefreshToken();
      
      // Restore original function
      globalThis.initializeAnonymousAuth = originalInitializeAnonymousAuth;
      
      // Verify anonymous auth was initiated
      expect(session?.access_token).toBe('new-anon-token');
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('No active session found'));
    });
    
    it('should refresh token if about to expire', async () => {
      // Mock session that's close to expiry
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 200; // 200 seconds from now
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'old-token',
            expires_at: expiryTimestamp,
            user: { id: 'test-user' }
          }
        },
        error: null
      });
      
      // Mock successful refresh
      mockRefreshSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'refreshed-token',
            user: { id: 'test-user' }
          }
        },
        error: null
      });
      
      // Call the function
      const session = await validateAndRefreshToken();
      
      // Verify token was refreshed
      expect(session?.access_token).toBe('refreshed-token');
      expect(consoleLogSpy).toHaveBeenCalledWith(expect.stringContaining('Token expires in'));
    });
    
    it('should return existing session if not expired', async () => {
      // Mock valid session
      const expiryTimestamp = Math.floor(Date.now() / 1000) + 3600; // 1 hour from now
      mockGetSession.mockResolvedValueOnce({
        data: {
          session: {
            access_token: 'valid-token',
            expires_at: expiryTimestamp,
            user: { id: 'test-user' }
          }
        },
        error: null
      });
      
      // Call the function
      const session = await validateAndRefreshToken();
      
      // Verify existing session was returned
      expect(session?.access_token).toBe('valid-token');
      expect(mockRefreshSession).not.toHaveBeenCalled();
    });
  });
}); 