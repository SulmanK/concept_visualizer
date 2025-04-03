/**
 * Supabase client configuration for Concept Visualizer
 */

import { createClient } from '@supabase/supabase-js';

// Environment variables for Supabase
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

/**
 * Initialize and export the Supabase client with storage options
 */
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY, {
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

/**
 * Get a URL for an image in Supabase Storage
 * Works for both public and private buckets
 * 
 * @param path Path to the image in storage
 * @param bucket Storage bucket name
 * @returns URL for the image
 */
export const getImageUrl = async (path: string, bucket: string): Promise<string> => {
  // If path is empty or null, return empty string
  if (!path) {
    console.error('No path provided to getImageUrl');
    return '';
  }
  
  // Clean up the path - remove any Supabase URL prefix
  let cleanPath = path;
  
  // If the path includes the full supabase URL, extract just the filename
  if (path.includes('supabase.co/storage')) {
    const parts = path.split('/');
    cleanPath = parts[parts.length - 1].split('?')[0]; // Get filename without query params
    console.log(`Extracted filename from path: ${cleanPath}`);
  }
  
  try {
    // Try signed URL first (for private buckets) with a 1-hour expiry
    const { data: signedData, error: signedError } = await supabase.storage
      .from(bucket)
      .createSignedUrl(cleanPath, 3600);
    
    if (signedData && signedData.signedUrl) {
      console.log(`Generated signed URL for ${cleanPath}`);
      return signedData.signedUrl;
    }
    
    // If signed URL fails, try public URL as fallback
    console.log(`Falling back to public URL for ${cleanPath} due to: ${signedError?.message}`);
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(cleanPath);
    
    if (!data || !data.publicUrl) {
      console.error(`Failed to get URL for ${cleanPath} in bucket ${bucket}`);
      return '';
    }
    
    return data.publicUrl;
  } catch (error) {
    console.error(`Error getting URL for ${cleanPath}:`, error);
    return '';
  }
};

/**
 * Synchronous version of getImageUrl that returns public URL only
 * Use this when async/await is not feasible
 * 
 * @param path Path to the image in storage
 * @param bucket Storage bucket name
 * @returns Public URL for the image
 */
export const getPublicImageUrl = (path: string, bucket: string): string => {
  // If path is empty or null, use a fallback image
  if (!path) {
    console.warn(`No path provided to getPublicImageUrl for bucket ${bucket}, using fallback`);
    return '/vite.svg'; // Use the Vite logo as a fallback
  }
  
  // If path already looks like a complete URL with http, return it directly
  if (path.startsWith('http')) {
    console.log(`Using provided URL directly: ${path}`);
    return path;
  }
  
  // NEW: If the path already contains the bucket name and looks like a Supabase URL path format
  if (path.includes(`${bucket}/`) || path.includes(`storage/v1/object/public/${bucket}`)) {
    console.log(`Path appears to be a complete storage path: ${path}`);
    return path;
  }
  
  // Clean up the path - remove any Supabase URL prefix
  let cleanPath = path;
  
  // If the path includes the full supabase URL, extract just the filename
  if (path.includes('supabase.co/storage') || path.includes('/storage/v1/object')) {
    const parts = path.split('/');
    cleanPath = parts[parts.length - 1].split('?')[0]; // Get filename without query params
    console.log(`Extracted clean path from Supabase URL: ${cleanPath}`);
  }
  
  try {
    // Get public URL (no auth required)
    const { data } = supabase.storage
      .from(bucket)
      .getPublicUrl(cleanPath);
    
    if (!data || !data.publicUrl) {
      console.error(`Failed to get public URL for ${cleanPath} in bucket ${bucket}, using fallback`);
      return '/vite.svg'; // Use the Vite logo as a fallback
    }
    
    console.log(`Generated public URL for ${cleanPath}: ${data.publicUrl}`);
    return data.publicUrl;
  } catch (error) {
    console.error(`Error getting public URL for ${cleanPath} in bucket ${bucket}:`, error);
    return '/vite.svg'; // Use the Vite logo as a fallback
  }
};

/**
 * Types for Supabase database tables
 */

export interface ConceptData {
  id: string;
  session_id: string;
  logo_description: string;
  theme_description: string;
  base_image_path: string;
  base_image_url: string;
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
    
    const { data, error } = await supabase
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
    const processedConcepts = processConceptData(data);
    
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
function processConceptData(data: any[]): ConceptData[] {
  console.log(`Processing ${data.length} concepts from Supabase`);
  
  return (data || []).map(concept => {
    // Generate base image URL for the concept
    const base_image_path = concept.base_image_path || '';
    const base_image_url = getPublicImageUrl(base_image_path, 'concept-images');
    
    // Log the base image URL for debugging
    console.log(`Concept ${concept.id.substring(0, 8)}... "${concept.logo_description.substring(0, 20)}...":`);
    console.log(`  • Base image: Path=${base_image_path}, URL=${base_image_url}`);
    
    // Process variation images if they exist
    let variations = concept.color_variations || [];
    
    if (variations.length > 0) {
      console.log(`  • Concept has ${variations.length} color variations`);
      
      variations = variations.map((variation: ColorVariationData, index: number) => {
        // Ensure colors is an array
        const colors = Array.isArray(variation.colors) ? variation.colors : [];
        
        // Generate image URL for this variation
        const image_path = variation.image_path || '';
        const image_url = getPublicImageUrl(image_path, 'palette-images');
        
        // Debug this variation
        console.log(`    ◦ Variation ${index}: "${variation.palette_name || 'Unnamed'}"`);
        console.log(`      - Image: Path=${image_path}, URL=${image_url}`);
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
      });
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
    const { data, error } = await supabase
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

    // Process the concept to add proper image URLs
    const base_image_url = getPublicImageUrl(data.base_image_path, 'concept-images');
    
    // Process variation images if they exist
    let variations = data.color_variations || [];
    
    if (variations.length > 0) {
      variations = variations.map((variation: ColorVariationData) => {
        // Ensure colors is an array
        const colors = Array.isArray(variation.colors) ? variation.colors : [];
        
        return {
          ...variation,
          // Ensure critical fields have default values
          palette_name: variation.palette_name || 'Color Palette',
          colors: colors.length > 0 ? colors : ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'],
          image_url: getPublicImageUrl(variation.image_path, 'palette-images')
        };
      });
    }
    
    // Return the processed concept with URLs
    const processedConcept = {
      ...data,
      base_image_url,
      color_variations: variations
    };

    console.log('Processed concept detail with URLs:', processedConcept);
    return processedConcept;
  } catch (error) {
    console.error('Exception fetching concept detail:', error);
    return null;
  }
}; 