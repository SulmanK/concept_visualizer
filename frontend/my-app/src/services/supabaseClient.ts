/**
 * Supabase client configuration for Concept Visualizer
 */

import { createClient, Session, User } from '@supabase/supabase-js';
import { getBucketName } from './configService';
import { fetchRateLimits } from './rateLimitService';
import { fetchRecentConceptsFromApi, fetchConceptDetailFromApi } from './conceptService';

// Environment variables for Supabase
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create default client
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
    // Set a shorter refresh threshold (5 minutes before expiry)
    detectSessionInUrl: true,
  },
  global: {
    headers: {
      'Content-Type': 'application/json',
    },
  }
});

/**
 * Validate and refresh token if needed
 * @returns Promise with refreshed session data if needed
 */
export const validateAndRefreshToken = async (): Promise<Session | null> => {
  try {
    // Get current session
    const { data: { session } } = await supabase.auth.getSession();
    
    // If no session, create one
    if (!session) {
      console.log('No active session found, creating new anonymous session');
      return initializeAnonymousAuth();
    }
    
    // Check if token is about to expire (within 5 minutes)
    const now = Math.floor(Date.now() / 1000);
    const expiresAt = session.expires_at || 0;
    
    if (expiresAt - now < 300) {
      console.log(`Token expires in ${expiresAt - now} seconds, refreshing now`);
      // Refresh the session
      const { data } = await supabase.auth.refreshSession();
      return data.session;
    }
    
    // Token is still valid
    return session;
  } catch (error) {
    console.error('Error validating/refreshing token:', error);
    return null;
  }
};

/**
 * Initialize anonymous authentication
 * @returns Promise with session data
 */
export const initializeAnonymousAuth = async (): Promise<Session | null> => {
  try {
    // Check if we have an existing session
    const { data: { session } } = await supabase.auth.getSession();
    
    // If no session exists, sign in anonymously
    if (!session) {
      console.log('No session found, signing in anonymously');
      const { data, error } = await supabase.auth.signInAnonymously();
      
      if (error) {
        console.error('Error signing in anonymously:', error);
        throw error;
      }
      
      console.log('Anonymous sign-in successful');
      
      // Force refresh rate limits after creating a new session
      console.log('Refreshing rate limits after anonymous sign-in');
      fetchRateLimits(true).catch(err => 
        console.error('Failed to refresh rate limits after anonymous sign-in:', err)
      );
      
      return data.session;
    } else {
      // If session exists but is near expiry, refresh it
      const now = Math.floor(Date.now() / 1000);
      const expiresAt = session.expires_at || 0;
      
      if (expiresAt - now < 300) {
        console.log(`Existing session expires soon (${expiresAt - now}s), refreshing`);
        const { data } = await supabase.auth.refreshSession();
        console.log('Session refreshed successfully');
        return data.session;
      }
      
      console.log('Using existing valid session');
      return session;
    }
  } catch (error) {
    console.error('Error initializing anonymous auth:', error);
    return null;
  }
};

/**
 * Get the current user ID
 * @returns User ID string or null if not authenticated
 */
export const getUserId = async (): Promise<string | null> => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    return session?.user?.id || null;
  } catch (error) {
    console.error('Error getting user ID:', error);
    return null;
  }
};

/**
 * Check if the current user is anonymous
 * @returns Boolean indicating if user is anonymous
 */
export const isAnonymousUser = async (): Promise<boolean> => {
  try {
    const { data: { session } } = await supabase.auth.getSession();
    if (!session) return false;
    
    // Check is_anonymous claim in JWT
    const claims = session.user.app_metadata;
    return claims.is_anonymous === true;
  } catch (error) {
    console.error('Error checking if user is anonymous:', error);
    return false;
  }
};

/**
 * Convert anonymous user to permanent by linking email
 * @param email User's email address
 * @returns Promise with result
 */
export const linkEmailToAnonymousUser = async (email: string): Promise<boolean> => {
  try {
    const { data, error } = await supabase.auth.updateUser({ email });
    
    if (error) {
      console.error('Error linking email to anonymous user:', error);
      return false;
    }
    
    return !!data.user;
  } catch (error) {
    console.error('Error linking email to anonymous user:', error);
    return false;
  }
};

/**
 * Sign out the current user
 * @returns Promise with sign out result
 */
export const signOut = async (): Promise<boolean> => {
  try {
    const { error } = await supabase.auth.signOut();
    
    if (error) {
      console.error('Error signing out:', error);
      return false;
    }
    
    // After sign out, initialize a new anonymous session
    await initializeAnonymousAuth();
    
    // Force refresh rate limits after signing out and getting a new session
    console.log('Refreshing rate limits after sign out');
    fetchRateLimits(true).catch(err => 
      console.error('Failed to refresh rate limits after sign out:', err)
    );
    
    return true;
  } catch (error) {
    console.error('Error signing out:', error);
    return false;
  }
};

/**
 * Get Supabase client with JWT authentication
 * @returns Authenticated Supabase client
 */
export async function getAuthenticatedClient() {
  try {
    // Get the current session
    const { data: { session } } = await supabase.auth.getSession();
    if (session) {
      // We already have a valid session, return the default client
      return supabase;
    }
    
    // If no session, try to sign in anonymously
    await initializeAnonymousAuth();
    return supabase;
  } catch (error) {
    console.error('Error getting authenticated client:', error);
    return supabase; // Fallback to default client
  }
}

/**
 * Get authenticated URL for an image - simplified since backend provides full URLs
 * Only used as a fallback if the backend URL is not available
 * 
 * @param bucket Supabase storage bucket name
 * @param path File path in storage
 * @returns Authenticated URL with JWT token
 */
export async function getAuthenticatedImageUrl(bucket: string, path: string): Promise<string> {
  try {
    if (!path) return '';
    
    // Use createSignedUrl with 3-day expiration
    const { data, error } = await supabase.storage
      .from(bucket)
      .createSignedUrl(path, 259200); // 3 days in seconds
      
    if (data?.signedUrl) {
      return data.signedUrl;
    }
    
    if (error) {
      console.error('Error generating signed URL:', error);
    }
    
    // If signed URL creation fails, use the public URL as fallback
    const { data: { publicUrl } } = supabase.storage
      .from(bucket)
      .getPublicUrl(path);
      
    return publicUrl;
  } catch (error) {
    console.error('Error generating authenticated URL:', error);
    
    // Create a fallback public URL as last resort
    try {
      const { data: { publicUrl } } = supabase.storage
        .from(bucket)
        .getPublicUrl(path);
        
      return publicUrl;
    } catch (fallbackError) {
      console.error('Error creating fallback URL:', fallbackError);
      return ''; // Return empty string to indicate failure
    }
  }
}

/**
 * Format image URL - simplified since backend now provides complete URLs
 * Only used as a fallback or for directly provided URLs that need processing
 * 
 * @param imageUrl The URL to format
 * @returns Properly formatted URL
 */
export const formatImageUrl = (imageUrl: string | null | undefined): string => {
  // If URL is null or undefined, return empty string
  if (!imageUrl) {
    return '';
  }
  
  // If URL is already a complete URL (starts with http or https), return it directly
  if (imageUrl.startsWith('http')) {
    return imageUrl;
  }
  
  // If URL is a relative path starting with /, prepend the Supabase URL
  if (imageUrl.startsWith('/')) {
    return `${SUPABASE_URL}${imageUrl}`;
  }
  
  // Return the URL as is
  return imageUrl;
};

/**
 * Legacy function - kept for backward compatibility
 * Use formatImageUrl for new code
 */
export const getImageUrl = async (path: string, bucketType: 'concept' | 'palette'): Promise<string> => {
  if (!path) return '';
  
  // If path already looks like a complete URL, just format it
  if (path.startsWith('http') || path.startsWith('/')) {
    return formatImageUrl(path);
  }
  
  // Otherwise, generate a signed URL
  const bucket = getBucketName(bucketType);
  const { data, error } = await supabase.storage
    .from(bucket)
    .createSignedUrl(path, 259200); // 3 days in seconds
  
  if (data?.signedUrl) {
    return data.signedUrl;
  }
  
  if (error) {
    console.error(`Failed to create signed URL: ${error.message}`);
  }
  
  // Fallback to public URL
  const { data: { publicUrl } } = supabase.storage
    .from(bucket)
    .getPublicUrl(path);
    
  return publicUrl;
};

/**
 * Legacy function - kept for backward compatibility
 * Use formatImageUrl for new code
 */
export const getSignedImageUrl = (path: string | null | undefined, bucketType: 'concept' | 'palette'): string => {
  // Handle null or empty path
  if (!path) return '';
  
  // If path already looks like a complete URL, just format it
  if (path.startsWith('http') || path.startsWith('/')) {
    return formatImageUrl(path);
  }
  
  // For direct paths, create a public URL
  const bucket = getBucketName(bucketType);
  return `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${path}`;
};

/**
 * Types for Supabase database tables
 */

export interface ConceptData {
  id: string;
  user_id: string;
  logo_description: string;
  theme_description: string;
  image_path: string;
  image_url: string;
  // Legacy fields - keep for backward compatibility during migration
  base_image_path?: string;
  base_image_url?: string;
  created_at: string;
  color_variations?: ColorVariationData[];
  storage_path?: string;
}

export interface ColorVariationData {
  id: string;
  concept_id: string;
  palette_name: string;
  colors: string[];
  description?: string;
  image_path: string;
  image_url: string;
  created_at: string;
  storage_path?: string;
}

/**
 * Fetch recent concepts
 * This function now uses the backend API instead of direct Supabase access
 * 
 * @param userId User ID for which to fetch concepts
 * @param limit Maximum number of concepts to return
 * @returns Promise with array of concept data
 */
export const fetchRecentConcepts = async (
  userId: string,
  limit: number = 10
): Promise<ConceptData[]> => {
  try {
    console.log(`[supabaseClient] Fetching recent concepts for user ${userId.substring(0, 6)}... using API`);
    return await fetchRecentConceptsFromApi(userId, limit);
  } catch (error) {
    console.error('[supabaseClient] Error fetching recent concepts:', error);
    throw error;
  }
};

/**
 * Fetch concept detail
 * This function now uses the backend API instead of direct Supabase access
 * 
 * @param conceptId ID of the concept to fetch
 * @param userId User ID for security validation
 * @returns Promise with concept data or null if not found
 */
export const fetchConceptDetail = async (
  conceptId: string,
  userId: string
): Promise<ConceptData | null> => {
  try {
    console.log(`[supabaseClient] Fetching concept detail for ID ${conceptId} using API`);
    return await fetchConceptDetailFromApi(conceptId);
  } catch (error) {
    console.error('[supabaseClient] Error fetching concept detail:', error);
    throw error;
  }
};

/**
 * Fetch a concept by ID (regardless of user)
 * This function now uses the backend API instead of direct Supabase access
 * 
 * @param conceptId ID of the concept to fetch
 * @returns Promise with concept data or null if not found
 */
export const fetchConceptById = async (conceptId: string): Promise<ConceptData | null> => {
  try {
    console.log(`[supabaseClient] Fetching concept with ID: ${conceptId} using API`);
    // Just use the same API endpoint but don't check user ownership
    return await fetchConceptDetailFromApi(conceptId);
  } catch (error) {
    console.error('[supabaseClient] Exception fetching concept by ID:', error);
    return null;
  }
};

/**
 * Get concept image details for detail page
 * This function now uses the backend API instead of direct Supabase access
 * 
 * @param conceptId ID of the concept to get details for
 * @returns Promise with concept details
 */
export const getConceptDetails = async (conceptId: string): Promise<{
  base_image_url: string;
  variations: Array<{
    id: string;
    name: string;
    colors: string[];
    image_url: string;
  }>;
}> => {
  try {
    console.log(`[supabaseClient] Getting concept details for ID: ${conceptId} using API`);
    
    // Fetch the concept with variations using the API
    const concept = await fetchConceptDetailFromApi(conceptId);
    
    if (!concept) {
      console.error(`[supabaseClient] Concept ${conceptId} not found`);
      return { base_image_url: '', variations: [] };
    }
    
    // Use the pre-signed URLs from the API response
    const base_image_url = concept.image_url || '';
    
    // Process variations using pre-signed URLs from the API
    const variations = (concept.color_variations || []).map((variation) => {
      return {
        id: variation.id,
        name: variation.palette_name || 'Color Variation',
        colors: Array.isArray(variation.colors) ? variation.colors : [],
        image_url: variation.image_url || ''
      };
    });
    
    return {
      base_image_url,
      variations
    };
  } catch (error) {
    console.error('[supabaseClient] Error getting concept details:', error);
    return { base_image_url: '', variations: [] };
  }
};

export default supabase; 