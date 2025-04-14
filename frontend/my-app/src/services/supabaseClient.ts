/**
 * Supabase client configuration for Concept Visualizer
 */

import { createClient, Session, User } from '@supabase/supabase-js';
import { getBucketName } from './configService';
import { fetchRateLimits } from './rateLimitService';

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
 * Fetch recent concepts for the current user
 * @param userId User ID to fetch concepts for
 * @param limit Maximum number of concepts to fetch
 * @returns Array of concept data
 */
export const fetchRecentConcepts = async (
  userId: string,
  limit: number = 10
): Promise<ConceptData[]> => {
  try {
    console.log(`Attempting to fetch concepts with user ID: ${userId}`);
    
    const { data, error } = await supabase
      .from('concepts')
      .select('*, color_variations(*)')
      .eq('user_id', userId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching concepts:', error);
      return [];
    }

    if (!data || data.length === 0) {
      console.log('No concepts found for this user');
      return [];
    }
    
    console.log(`Found ${data.length} concepts for user`);
    
    // Process the data to ensure all concepts have the required fields
    const concepts = await processConceptData(data);
    
    return concepts;
  } catch (error) {
    console.error('Error fetching concepts:', error);
    return [];
  }
};

/**
 * Process the raw concept data to add URLs and ensure proper formatting
 */
async function processConceptData(data: any[]): Promise<ConceptData[]> {
  console.log(`Processing ${data.length} concepts from Supabase`);
  
  // Process each concept using async operations to get signed URLs
  const processedConcepts = await Promise.all((data || []).map(async (concept) => {
    try {
      // Get image paths and urls, handling both old and new field names
      const image_path = concept.image_path || concept.base_image_path || '';
      let image_url = concept.image_url || concept.base_image_url || '';
      
      console.log(`Processing concept ID ${concept.id}:`, {
        has_image_url: !!concept.image_url,
        has_base_image_url: !!concept.base_image_url,
        image_path,
        image_url_snippet: image_url ? image_url.substring(0, 50) + '...' : 'none'
      });
      
      // If we don't have a valid signed URL, generate one
      if (!image_url || (!image_url.includes('/object/sign/') && !image_url.includes('token='))) {
        console.log(`Concept needs a new signed URL for path: ${image_path}`);
        // Get a signed URL for the image path
        try {
          const { data: signedData } = await supabase.storage
            .from(getBucketName('concept'))
            .createSignedUrl(image_path, 3600);
            
          if (signedData?.signedUrl) {
            image_url = signedData.signedUrl;
            console.log(`Created signed URL for image: ${image_url.substring(0, 50)}...`);
          } else {
            // Fallback to token-based URL
            image_url = getSignedImageUrl(image_path, 'concept');
            console.log(`Falling back to token-based URL for image: ${image_url.substring(0, 50)}...`);
          }
        } catch (e) {
          console.warn(`Error creating signed URL for image: ${e}`);
          // Try the fallback method
          image_url = getSignedImageUrl(image_path, 'concept');
        }
      } else {
        console.log(`Concept already has a signed URL: ${image_url.substring(0, 50)}...`);
        
        // Ensure URL has proper format with /storage/v1/
        if (image_url.startsWith('/') || (image_url.includes('/object/sign/') && !image_url.includes('/storage/v1/'))) {
          const fixedUrl = image_url.replace('/object/sign/', '/storage/v1/object/sign/');
          // Add SUPABASE_URL prefix if it's a relative URL
          if (fixedUrl.startsWith('/')) {
            image_url = `${SUPABASE_URL}${fixedUrl}`;
          } else {
            image_url = fixedUrl;
          }
          console.log(`Fixed URL format: ${image_url.substring(0, 50)}...`);
        }
      }
      
      // Process variation images if they exist
      let variations = concept.color_variations || [];
      
      if (variations.length > 0) {
        console.log(`  • Concept has ${variations.length} color variations`);
        
        // Process variations with Promise.all to handle async operations
        variations = await Promise.all(variations.map(async (variation: ColorVariationData, index: number) => {
          // Ensure colors is an array
          const colors = Array.isArray(variation.colors) ? variation.colors : [];
          
          // Generate image URL for this variation - use signed URL
          const variation_image_path = variation.image_path || '';
          let variation_image_url = variation.image_url || '';
          
          // If we don't have a valid signed URL, generate one
          if (!variation_image_url || (!variation_image_url.includes('/object/sign/') && !variation_image_url.includes('token='))) {
            console.log(`Variation ${index} needs a new signed URL for path: ${variation_image_path}`);
            // Get a signed URL for the variation image path
            try {
              const { data: signedData } = await supabase.storage
                .from(getBucketName('palette'))
                .createSignedUrl(variation_image_path, 3600);
                
              if (signedData?.signedUrl) {
                variation_image_url = signedData.signedUrl;
                console.log(`Created signed URL for variation ${index}: ${variation_image_url.substring(0, 50)}...`);
              } else {
                // Fallback to token-based URL
                variation_image_url = getSignedImageUrl(variation_image_path, 'palette');
                console.log(`Falling back to token-based URL for variation ${index}: ${variation_image_url.substring(0, 50)}...`);
              }
            } catch (e) {
              console.warn(`Error creating signed URL for variation ${index}: ${e}`);
              variation_image_url = getSignedImageUrl(variation_image_path, 'palette');
            }
          } else {
            console.log(`Variation ${index} already has a signed URL: ${variation_image_url.substring(0, 50)}...`);
            
            // Ensure URL has proper format with /storage/v1/
            if (variation_image_url.startsWith('/') || (variation_image_url.includes('/object/sign/') && !variation_image_url.includes('/storage/v1/'))) {
              const fixedUrl = variation_image_url.replace('/object/sign/', '/storage/v1/object/sign/');
              // Add SUPABASE_URL prefix if it's a relative URL
              if (fixedUrl.startsWith('/')) {
                variation_image_url = `${SUPABASE_URL}${fixedUrl}`;
              } else {
                variation_image_url = fixedUrl;
              }
              console.log(`Fixed variation URL format: ${variation_image_url.substring(0, 50)}...`);
            }
          }
          
          // Debug this variation
          console.log(`    ◦ Variation ${index}: "${variation.palette_name || 'Unnamed'}"`);
          console.log(`      - Image path: ${variation_image_path}`);
          console.log(`      - Colors: ${colors.length} colors, first color: ${colors[0] || 'none'}`);
          
          return {
            ...variation,
            // Ensure critical fields have default values
            id: variation.id || `temp-var-${index}-${Date.now()}`,
            concept_id: variation.concept_id || concept.id,
            palette_name: variation.palette_name || 'Color Palette',
            colors: colors.length > 0 ? colors : ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'],
            image_path: variation_image_path,
            image_url: variation_image_url,
            created_at: variation.created_at || new Date().toISOString()
          };
        }));
      } else {
        console.log(`  • Concept has no color variations`);
      }
      
      // Return the processed concept with URLs
      return {
        ...concept,
        // Support both old and new field names to ensure backward compatibility
        base_image_path: image_path,
        base_image_url: image_url,
        image_path: image_path,
        image_url: image_url,
        color_variations: variations
      };
    } catch (error) {
      console.error(`Error processing concept ${concept.id}:`, error);
      // Return the concept with minimal processing in case of error
      return concept;
    }
  }));
  
  return processedConcepts;
}

/**
 * Synchronous version of processConceptData for cases where async isn't possible
 * This will use token-based URLs instead of signed URLs as a fallback
 */
function processConceptDataSync(data: any[]): ConceptData[] {
  console.log(`Processing ${data.length} concepts synchronously (token-based URLs only)`);
  
  return (data || []).map(concept => {
    try {
      // For synchronous processing, we'll use simpler URL generation
      const base_image_path = concept.base_image_path || '';
      let base_image_url = concept.base_image_url || '';
      
      // If base_image_url doesn't look like a signed URL, generate a token-based URL
      if (!(base_image_url && (base_image_url.includes('/object/sign/') || base_image_url.includes('token=')))) {
        base_image_url = getSignedImageUrl(base_image_path, 'concept');
        console.log(`Using token-based URL for base image: ${base_image_url.substring(0, 50)}...`);
      }
      
      // Process variation images if they exist
      let variations = concept.color_variations || [];
      
      if (variations.length > 0) {
        variations = variations.map((variation: ColorVariationData, index: number) => {
          // Generate signed URL for the image
          const image_path = variation.image_path || '';
          let image_url = variation.image_url || '';
          
          // If image_url doesn't look like a signed URL, generate a token-based URL
          if (!(image_url && (image_url.includes('/object/sign/') || image_url.includes('token=')))) {
            image_url = getSignedImageUrl(image_path, 'palette');
          }
          
          // Return the processed variation with URL
          return {
            ...variation,
            image_path: image_path,
            image_url: image_url,
            colors: Array.isArray(variation.colors) && variation.colors.length > 0 ? 
              variation.colors : 
              ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81']
          };
        });
      }
      
      return {
        ...concept,
        base_image_path: base_image_path,
        base_image_url: base_image_url,
        color_variations: variations
      };
    } catch (error) {
      console.error(`Error processing concept ${concept.id}:`, error);
      return concept;
    }
  });
}

/**
 * Fetch a concept by ID for a specific user
 * @param conceptId Concept ID to fetch
 * @param userId User ID the concept should belong to
 * @returns Concept data or null if not found
 */
export const fetchConceptDetail = async (
  conceptId: string,
  userId: string
): Promise<ConceptData | null> => {
  try {
    console.log(`Fetching concept detail for concept ID: ${conceptId}, user ID: ${userId}`);
    
    const { data, error } = await supabase
      .from('concepts')
      .select('*, color_variations(*)')
      .eq('id', conceptId)
      .eq('user_id', userId)
      .single();

    if (error) {
      console.error('Error fetching concept detail:', error);
      return null;
    }

    if (!data) {
      console.log('No concept found with that ID for this user');
      return null;
    }
    
    // Process the data to ensure the concept has the required fields
    const concepts = await processConceptData([data]);
    
    return concepts[0] || null;
  } catch (error) {
    console.error('Error fetching concept detail:', error);
    return null;
  }
};

/**
 * Fetch a specific concept by ID
 */
export const fetchConceptById = async (conceptId: string): Promise<ConceptData | null> => {
  try {
    console.log(`Fetching concept with ID: ${conceptId}`);
    
    const { data, error } = await supabase
      .from('concepts')
      .select('*, color_variations(*)')
      .eq('id', conceptId)
      .single();
    
    if (error) {
      console.error('Error fetching concept by ID:', error);
      return null;
    }
    
    if (!data) {
      console.log(`No concept found with ID ${conceptId}`);
      return null;
    }
    
    // Process the concept to add signed URLs
    const [processedConcept] = await processConceptData([data]);
    return processedConcept;
  } catch (error) {
    console.error('Exception fetching concept by ID:', error);
    return null;
  }
};

/**
 * Get concept image details for detail page
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
    console.log(`Getting concept details for ID: ${conceptId}`);
    
    // Fetch the concept with variations
    const concept = await fetchConceptById(conceptId);
    
    if (!concept) {
      console.error(`Concept ${conceptId} not found`);
      return { base_image_url: '', variations: [] };
    }
    
    // Get base image URL
    const base_image_path = concept.base_image_path || '';
    let base_image_url = concept.base_image_url || '';
    
    // If we don't have a valid URL already, try to get a signed URL
    if (!base_image_url.includes('/object/sign/') && !base_image_url.includes('token=')) {
      try {
        const { data } = await supabase.storage
          .from(getBucketName('concept'))
          .createSignedUrl(base_image_path, 259200); // 3-day URL
          
        if (data?.signedUrl) {
          base_image_url = data.signedUrl;
          console.log(`Created signed URL for concept detail: ${base_image_url.substring(0, 50)}...`);
        } else {
          // Fallback to token-based URL
          base_image_url = getSignedImageUrl(base_image_path, 'concept');
        }
      } catch (e) {
        console.warn(`Error creating signed URL for concept detail: ${e}`);
        base_image_url = getSignedImageUrl(base_image_path, 'concept');
      }
    }
    
    // Process variations
    const variations = await Promise.all((concept.color_variations || []).map(async (variation) => {
      const image_path = variation.image_path || '';
      let image_url = variation.image_url || '';
      
      // If the URL isn't already signed, get a signed URL
      if (!image_url.includes('/object/sign/') && !image_url.includes('token=')) {
        try {
          const { data } = await supabase.storage
            .from(getBucketName('palette'))
            .createSignedUrl(image_path, 259200); // 3-day URL
            
          if (data?.signedUrl) {
            image_url = data.signedUrl;
            console.log(`Created signed URL for variation detail: ${image_url.substring(0, 50)}...`);
          } else {
            // Fallback to token-based URL
            image_url = getSignedImageUrl(image_path, 'palette');
          }
        } catch (e) {
          console.warn(`Error creating signed URL for variation detail: ${e}`);
          image_url = getSignedImageUrl(image_path, 'palette');
        }
      }
      
      return {
        id: variation.id,
        name: variation.palette_name || 'Color Variation',
        colors: Array.isArray(variation.colors) ? variation.colors : [],
        image_url
      };
    }));
    
    return {
      base_image_url,
      variations
    };
  } catch (error) {
    console.error('Error getting concept details:', error);
    return { base_image_url: '', variations: [] };
  }
};

export default supabase; 