import axios from 'axios';

interface TokenResponse {
  token: string;
  expires_at: number;
  session_id: string;
}

interface StoredToken {
  token: string;
  expiresAt: number;
}

class TokenService {
  private token: string | null = null;
  private expiresAt: number = 0;
  private refreshPromise: Promise<string> | null = null;
  
  constructor() {
    // Try to load token from localStorage on initialization
    this.loadTokenFromStorage();
  }
  
  private loadTokenFromStorage(): void {
    try {
      const storedToken = localStorage.getItem('supabase_token');
      if (storedToken) {
        const parsedToken: StoredToken = JSON.parse(storedToken);
        
        // Check if token is still valid (with 5-minute buffer)
        const now = Math.floor(Date.now() / 1000);
        if (parsedToken.expiresAt > now + 300) {
          this.token = parsedToken.token;
          this.expiresAt = parsedToken.expiresAt;
        }
      }
    } catch (error) {
      console.error('Error loading token from storage:', error);
      // Clear any corrupted token data
      localStorage.removeItem('supabase_token');
    }
  }
  
  private saveTokenToStorage(token: string, expiresAt: number): void {
    try {
      const tokenData: StoredToken = {
        token,
        expiresAt
      };
      localStorage.setItem('supabase_token', JSON.stringify(tokenData));
    } catch (error) {
      console.error('Error saving token to storage:', error);
    }
  }
  
  private async fetchNewToken(): Promise<string> {
    try {
      const response = await axios.get<TokenResponse>('/api/session/token', {
        withCredentials: true // Include cookies for session identification
      });
      
      this.token = response.data.token;
      this.expiresAt = response.data.expires_at;
      
      // Save to localStorage for persistence
      this.saveTokenToStorage(this.token, this.expiresAt);
      
      return this.token;
    } catch (error) {
      console.error('Error fetching token:', error);
      throw new Error('Failed to get authentication token');
    }
  }
  
  private async refreshToken(): Promise<string> {
    try {
      const response = await axios.post<TokenResponse>('/api/session/refresh-token', {}, {
        withCredentials: true // Include cookies for session identification
      });
      
      this.token = response.data.token;
      this.expiresAt = response.data.expires_at;
      
      // Save to localStorage for persistence
      this.saveTokenToStorage(this.token, this.expiresAt);
      
      return this.token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      throw new Error('Failed to refresh authentication token');
    }
  }
  
  /**
   * Get a valid token, refreshing if necessary
   */
  async getToken(): Promise<string> {
    // If a refresh is already in progress, return that promise
    if (this.refreshPromise) {
      return this.refreshPromise;
    }
    
    const now = Math.floor(Date.now() / 1000);
    
    // Check if token exists and is not expired (with 5-minute buffer)
    if (this.token && this.expiresAt > now + 300) {
      return this.token;
    }
    
    // If token exists but is near expiry, refresh it
    if (this.token && this.expiresAt > now) {
      this.refreshPromise = this.refreshToken();
      const token = await this.refreshPromise;
      this.refreshPromise = null;
      return token;
    }
    
    // Otherwise, get a new token
    this.refreshPromise = this.fetchNewToken();
    const token = await this.refreshPromise;
    this.refreshPromise = null;
    return token;
  }
  
  /**
   * Clear the token (for logout)
   */
  clearToken(): void {
    this.token = null;
    this.expiresAt = 0;
    localStorage.removeItem('supabase_token');
  }
}

// Export singleton instance
export const tokenService = new TokenService(); 