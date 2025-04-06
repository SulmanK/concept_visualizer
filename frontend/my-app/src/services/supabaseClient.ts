/**
 * Supabase client configuration for Concept Visualizer
 */

import { createClient } from '@supabase/supabase-js';
import { getBucketName } from './configService';
import { tokenService } from './tokenService';

// Environment variables for Supabase
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

// Create default client without JWT initially
const supabaseClient = createClient(SUPABASE_URL, SUPABASE_KEY, {
  auth: {
    persistSession: true,
    autoRefreshToken: true,
  },
  global: {
    headers: {
      'Content-Type': 'application/json',
    },
  }
});

// Export the client as 'supabase' for backward compatibility
export const supabase = supabaseClient;

/**
 * Get Supabase client with JWT authentication
 * @returns Authenticated Supabase client
 */
export async function getAuthenticatedClient() {
  try {
    // Get a valid token
    const token = await tokenService.getToken();
    
    // Create a new client with the auth header
    return createClient(SUPABASE_URL, SUPABASE_KEY, {
      auth: {
        persistSession: true,
        autoRefreshToken: true,
      },
      global: {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        }
      }
    });
  } catch (error) {
    console.error('Error getting authenticated client:', error);
    return supabaseClient; // Fallback to default client
  }
}

/**
 * Get authenticated URL for an image
 * @param bucket Supabase storage bucket name
 * @param path File path in storage
 * @returns Authenticated URL with JWT token
 */
export async function getAuthenticatedImageUrl(bucket: string, path: string): Promise<string> {
  try {
    // Use createSignedUrl with 3-day expiration
    const { data, error } = await supabaseClient.storage
      .from(bucket)
      .createSignedUrl(path, 259200); // 3 days in seconds
      
    if (data?.signedUrl) {
      return data.signedUrl;
    }
    
    // If signed URL fails, try with token
    const token = await tokenService.getToken();
    return `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${path}?token=${token}`;
  } catch (error) {
    console.error('Error generating authenticated URL:', error);
    // Create a fallback URL with token
    try {
      const token = await tokenService.getToken();
      return `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${path}?token=${token}`;
    } catch (fallbackError) {
      console.error('Error creating fallback URL:', fallbackError);
      return ''; // Return empty string to indicate failure
    }
  }
}

/**
 * Get a signed URL for an image in Supabase Storage
 * Works for both public and private buckets
 * 
 * @param path Path to the image in storage
 * @param bucketType Type of bucket ('concept' or 'palette')
 * @returns Signed URL for the image with 3-day expiration
 */
export const getImageUrl = async (path: string, bucketType: 'concept' | 'palette'): Promise<string> => {
  // Get actual bucket name from config
  const bucket = getBucketName(bucketType);
  
  // If path is empty or null, return empty string
  if (!path) {
    console.error('No path provided to getImageUrl');
    return '';
  }
  
  // If path already contains a signed URL token, it's already a complete URL - return it directly
  if (path.includes('/object/sign/') && path.includes('token=')) {
    console.log(`Path is already a complete signed URL: ${path.substring(0, 50)}...`);
    
    // Ensure the URL is absolute by adding the Supabase URL if it's relative
    if (path.startsWith('/')) {
      return `${SUPABASE_URL}${path}`;
    }
    
    return path;
  }
  
  // If path already looks like a complete URL with http, return it directly
  if (path.startsWith('http')) {
    console.log(`Using provided URL directly: ${path.substring(0, 50)}...`);
    return path;
  }
  
  // Clean up the path - remove any Supabase URL prefix
  let cleanPath = path;
  
  // If the path includes the full supabase URL, extract just the relative path
  if (path.includes('supabase.co/storage')) {
    const parts = path.split('/');
    cleanPath = parts[parts.length - 1].split('?')[0]; // Get filename without query params
    console.log(`Extracted filename from path: ${cleanPath}`);
  }
  
  try {
    // Use createSignedUrl with 3-day expiration
    const { data, error } = await supabaseClient.storage
      .from(bucket)
      .createSignedUrl(cleanPath, 259200); // 3 days in seconds
    
    if (data && data.signedUrl) {
      console.log(`Generated signed URL for ${cleanPath}`);
      return data.signedUrl;
    }
    
    // If signed URL creation fails, log error and try fallback
    console.error(`Failed to create signed URL: ${error?.message}`);
    
    // Try to get an authenticated URL as fallback (uses JWT token)
    return getAuthenticatedImageUrl(bucket, cleanPath);
  } catch (error) {
    console.error(`Error getting signed URL for ${cleanPath}:`, error);
    return '';
  }
};

/**
 * Synchronous version of getImageUrl for when async/await isn't possible
 * This tries to provide a signed URL, but may fallback to token-based URL
 * 
 * @param path Path to the image in storage
 * @param bucketType Type of bucket ('concept' or 'palette')
 * @returns URL for the image with access token
 */
export const getSignedImageUrl = (path: string, bucketType: 'concept' | 'palette'): string => {
  // If path is empty or null, use a fallback image
  if (!path) {
    console.warn(`No path provided to getSignedImageUrl, using fallback`);
    return '/vite.svg'; // Use the Vite logo as a fallback
  }
  
  // If path already contains a signed URL token, it's already a complete URL - return it directly
  if (path.includes('/object/sign/') && path.includes('token=')) {
    console.log(`Path is already a complete signed URL: ${path.substring(0, 50)}...`);
    
    // Check if this is a double-signed URL (a URL within a URL)
    if (path.indexOf('/object/sign/') !== path.lastIndexOf('/object/sign/')) {
      console.log('Detected doubly-signed URL, attempting to fix it');
      
      // Extract the path part after the second bucket occurrence
      const bucketName = bucketType === 'concept' ? 'concept-images' : 'palette-images';
      const partAfterFirstBucket = path.split(`${bucketName}/`)[1];
      
      if (partAfterFirstBucket && partAfterFirstBucket.includes(`${bucketName}/`)) {
        // Find the second bucket occurrence and extract the real path
        const realPath = partAfterFirstBucket.split(`${bucketName}/`)[1].split('?')[0];
        console.log('Extracted real path:', realPath);
        
        // Generate a fresh signed URL with the clean path
        // Use the try-catch to handle localStorage safely
        try {
          const token = localStorage.getItem('supabase_token');
          if (token) {
            return `${SUPABASE_URL}/storage/v1/object/public/${bucketName}/${realPath}?token=${token}`;
          }
        } catch (e) {
          console.warn('Failed to get token from localStorage', e);
        }
        
        // Return a direct URL as fallback
        return `${SUPABASE_URL}/storage/v1/object/public/${bucketName}/${realPath}`;
      }
    }
    
    // Ensure the URL is absolute by adding the Supabase URL if it's relative
    if (path.startsWith('/')) {
      return `${SUPABASE_URL}${path}`;
    }
    
    return path;
  }
  
  // If path already looks like a complete URL with http, return it directly
  if (path.startsWith('http')) {
    // Check if this is a malformed URL with duplicated base URL
    // Example: https://project.supabase.co/storage/v1/object/public/bucket/https://project.supabase.co/...
    if (path.includes(`${SUPABASE_URL}/storage/v1/object/public/`) && 
        path.includes(`${SUPABASE_URL}`, path.indexOf('/storage/v1/object/public/') + 20)) {
      
      // Extract the correct portion of the URL
      const dupeIndex = path.indexOf(SUPABASE_URL, path.indexOf('/storage/v1/object/public/') + 20);
      if (dupeIndex > 0) {
        console.warn(`Found and fixed malformed URL with duplicated base`);
        return path.substring(dupeIndex);
      }
    }
    
    // Try to extract path from URLs like /storage/v1/object/public/concept-images/123/image.png
    const bucketName = bucketType === 'concept' ? 'concept-images' : 'palette-images';
    if (path.includes(`/storage/v1/object/public/${bucketName}/`)) {
      const pathParts = path.split(`/storage/v1/object/public/${bucketName}/`);
      if (pathParts.length > 1) {
        const cleanPath = pathParts[1].split('?')[0];
        console.log(`Extracted clean path from URL: ${cleanPath}`);
        
        // Generate a fresh token-based URL
        try {
          const token = localStorage.getItem('supabase_token');
          if (token) {
            return `${SUPABASE_URL}/storage/v1/object/public/${bucketName}/${cleanPath}?token=${token}`;
          }
        } catch (e) {
          console.warn('Failed to get token from localStorage', e);
        }
      }
    }
    
    console.log(`Using provided URL directly: ${path.substring(0, 50)}...`);
    return path;
  }
  
  // Get actual bucket name from config
  const bucket = getBucketName(bucketType);
  
  // Clean up the path - remove any Supabase URL prefix
  let cleanPath = path;
  
  // Check if path is already a storage path that includes the bucket name
  if (path.includes(`/${bucket}/`) || path.includes(`storage/v1/object/public/${bucket}`)) {
    // This is already a complete path - extract just the path portion
    const bucketPrefix = `${bucket}/`;
    const bucketIndex = path.indexOf(bucketPrefix);
    
    if (bucketIndex >= 0) {
      cleanPath = path.substring(bucketIndex + bucketPrefix.length);
      console.log(`Extracted clean path from full path: ${cleanPath}`);
    }
  }
  
  // Try to get an API key from local storage
  try {
    const token = localStorage.getItem('supabase_token');
    if (token) {
      // Use the token directly in a URL
      const tokenUrl = `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${cleanPath}?token=${token}`;
      console.log(`Using token-based URL for ${cleanPath}`);
      return tokenUrl;
    }
  } catch (e) {
    console.warn('Failed to get token from localStorage', e);
  }
  
  // Not ideal but necessary for synchronous operation - return a direct URL
  // This will likely redirect to sign-in page if bucket is private
  console.warn(`Returning direct URL for ${cleanPath} - this may fail for private buckets`);
  return `${SUPABASE_URL}/storage/v1/object/public/${bucket}/${cleanPath}`;
};

/**
 * Types for Supabase database tables
 */

export interface ConceptData {
  id: string;
  session_id: string;
  logo_description: string;
  theme_description: string;
  image_path: string;
  image_url: string;
  // Legacy fields - keep for backward compatibility during migration
  base_image_path?: string;
  base_image_url?: string;
  created_at: string;
  color_variations?: ColorVariationData[];
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
}

/**
 * Fetch recent concepts for the current session
 * 
 * @param sessionId The current session ID
 * @param limit Maximum number of concepts to return
 * @returns List of concepts with their variations
 */
export const fetchRecentConcepts = async (
  sessionId: string,
  limit: number = 10
): Promise<ConceptData[]> => {
  try {
    // Check if we have a valid session ID
    if (!sessionId) {
      console.error('No session ID provided to fetchRecentConcepts');
      return [];
    }
    
    console.log(`Attempting to fetch concepts with session ID: ${sessionId}`);
    
    const { data, error } = await supabaseClient
      .from('concepts')
      .select('*, color_variations(*)')
      .eq('session_id', sessionId)
      .order('created_at', { ascending: false })
      .limit(limit);

    if (error) {
      console.error('Error fetching recent concepts:', error);
      return [];
    }

    // Check if we found any concepts
    if (!data || data.length === 0) {
      console.log(`No concepts found for session ${sessionId}`);
      return [];
    }
    
    console.log(`Found ${data.length} concepts for session ${sessionId}`);
    
    // Process retrieved data to add proper image URLs
    const processedConcepts = await processConceptData(data);
    
    // Log detailed information about the first concept for debugging
    if (processedConcepts.length > 0) {
      const firstConcept = processedConcepts[0];
      console.log('First concept details:', {
        id: firstConcept.id,
        logo_description: firstConcept.logo_description,
        base_image_path: firstConcept.base_image_path,
        base_image_url: firstConcept.base_image_url,
        variations_count: firstConcept.color_variations?.length || 0
      });
    }
    
    return processedConcepts;
  } catch (error) {
    console.error('Exception fetching recent concepts:', error);
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
      // Generate base image URL for the concept - use signed URL
      const base_image_path = concept.base_image_path || '';
      let base_image_url = concept.base_image_url || '';
      
      // If we already have a signed URL in base_image_url, use it
      if (base_image_url && (base_image_url.includes('/object/sign/') || base_image_url.includes('token='))) {
        console.log(`Concept already has a signed URL: ${base_image_url.substring(0, 50)}...`);
      } else {
        // Otherwise, try to get a signed URL
        try {
          const { data: signedData } = await supabaseClient.storage
            .from(getBucketName('concept'))
            .createSignedUrl(base_image_path, 3600);
            
          if (signedData?.signedUrl) {
            base_image_url = signedData.signedUrl;
            console.log(`Created signed URL for base image: ${base_image_url.substring(0, 50)}...`);
          } else {
            // Fallback to token-based URL
            base_image_url = getSignedImageUrl(base_image_path, 'concept');
            console.log(`Falling back to token-based URL for base image: ${base_image_url.substring(0, 50)}...`);
          }
        } catch (e) {
          console.warn(`Error creating signed URL for base image: ${e}`);
          base_image_url = getSignedImageUrl(base_image_path, 'concept');
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
          const image_path = variation.image_path || '';
          let image_url = variation.image_url || '';
          
          // If we already have a signed URL in image_url, use it
          if (image_url && (image_url.includes('/object/sign/') || image_url.includes('token='))) {
            console.log(`Variation already has a signed URL: ${image_url.substring(0, 50)}...`);
          } else {
            // Otherwise, try to get a signed URL
            try {
              const { data: signedData } = await supabaseClient.storage
                .from(getBucketName('palette'))
                .createSignedUrl(image_path, 3600);
                
              if (signedData?.signedUrl) {
                image_url = signedData.signedUrl;
                console.log(`Created signed URL for variation ${index}: ${image_url.substring(0, 50)}...`);
              } else {
                // Fallback to token-based URL
                image_url = getSignedImageUrl(image_path, 'palette');
                console.log(`Falling back to token-based URL for variation ${index}: ${image_url.substring(0, 50)}...`);
              }
            } catch (e) {
              console.warn(`Error creating signed URL for variation ${index}: ${e}`);
              image_url = getSignedImageUrl(image_path, 'palette');
            }
          }
          
          // Debug this variation
          console.log(`    ◦ Variation ${index}: "${variation.palette_name || 'Unnamed'}"`);
          console.log(`      - Image path: ${image_path}`);
          console.log(`      - Colors: ${colors.length} colors, first color: ${colors[0] || 'none'}`);
          
          return {
            ...variation,
            // Ensure critical fields have default values
            id: variation.id || `temp-var-${index}-${Date.now()}`,
            concept_id: variation.concept_id || concept.id,
            palette_name: variation.palette_name || 'Color Palette',
            colors: colors.length > 0 ? colors : ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'],
            image_path: image_path,
            image_url: image_url,
            created_at: variation.created_at || new Date().toISOString()
          };
        }));
      } else {
        console.log(`  • Concept has no color variations`);
      }
      
      // Return the processed concept with URLs
      return {
        ...concept,
        base_image_path: base_image_path,
        base_image_url: base_image_url,
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
 * Fetch a single concept by ID
 * 
 * @param conceptId The concept ID to fetch
 * @param sessionId The current session ID (for security validation)
 * @returns The concept with its variations or null if not found
 */
export const fetchConceptDetail = async (
  conceptId: string,
  sessionId: string
): Promise<ConceptData | null> => {
  try {
    const { data, error } = await supabaseClient
      .from('concepts')
      .select('*, color_variations(*)')
      .eq('id', conceptId)
      .eq('session_id', sessionId)
      .single();

    if (error) {
      console.error('Error fetching concept detail:', error);
      return null;
    }

    if (!data) return null;

    // Process the concept to add proper image URLs - using signed URLs
    const base_image_path = data.base_image_path || '';
    let base_image_url = data.base_image_url || '';
    
    // If base_image_url doesn't look like a signed URL, try to get one
    if (!(base_image_url && (base_image_url.includes('/object/sign/') || base_image_url.includes('token=')))) {
      try {
        const { data: signedData } = await supabaseClient.storage
          .from(getBucketName('concept'))
          .createSignedUrl(base_image_path, 3600);
          
        if (signedData?.signedUrl) {
          base_image_url = signedData.signedUrl;
          console.log(`Created signed URL for concept detail base image: ${base_image_url.substring(0, 50)}...`);
        } else {
          // Fallback to token-based URL
          base_image_url = getSignedImageUrl(base_image_path, 'concept');
        }
      } catch (e) {
        console.warn(`Error creating signed URL for concept detail: ${e}`);
        base_image_url = getSignedImageUrl(base_image_path, 'concept');
      }
    }
    
    // Process variation images if they exist
    let variations = data.color_variations || [];
    
    if (variations.length > 0) {
      variations = await Promise.all(variations.map(async (variation: ColorVariationData) => {
        // Ensure colors is an array
        const colors = Array.isArray(variation.colors) ? variation.colors : [];
        
        // Generate image URL for this variation - use signed URL
        const image_path = variation.image_path || '';
        let image_url = variation.image_url || '';
        
        // If image_url doesn't look like a signed URL, try to get one
        if (!(image_url && (image_url.includes('/object/sign/') || image_url.includes('token=')))) {
          try {
            const { data: signedData } = await supabaseClient.storage
              .from(getBucketName('palette'))
              .createSignedUrl(image_path, 3600);
              
            if (signedData?.signedUrl) {
              image_url = signedData.signedUrl;
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
          ...variation,
          // Ensure critical fields have default values
          palette_name: variation.palette_name || 'Color Palette',
          colors: colors.length > 0 ? colors : ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'],
          image_path,
          image_url
        };
      }));
    }
    
    // Return the processed concept with URLs
    const processedConcept = {
      ...data,
      // Include both new and legacy fields
      image_path: data.image_path || data.base_image_path || '',
      image_url: data.image_url || base_image_url,
      base_image_path,
      base_image_url,
      color_variations: variations
    };

    console.log('Processed concept detail with URLs:', {
      id: processedConcept.id,
      imageFields: {
        image_path: processedConcept.image_path,
        image_url: processedConcept.image_url,
        base_image_path: processedConcept.base_image_path,
        base_image_url: processedConcept.base_image_url,
      }
    });
    return processedConcept;
  } catch (error) {
    console.error('Exception fetching concept detail:', error);
    return null;
  }
};

/**
 * Fetch a specific concept by ID
 */
export const fetchConceptById = async (conceptId: string): Promise<ConceptData | null> => {
  try {
    console.log(`Fetching concept with ID: ${conceptId}`);
    
    const { data, error } = await supabaseClient
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
        const { data } = await supabaseClient.storage
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
          const { data } = await supabaseClient.storage
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

export default supabaseClient; 