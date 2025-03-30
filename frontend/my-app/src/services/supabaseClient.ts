/**
 * Supabase client configuration for Concept Visualizer
 */

import { createClient } from '@supabase/supabase-js';

// Environment variables for Supabase
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || 'https://pstdcfittpjhxzynbdbu.supabase.co';
const SUPABASE_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBzdGRjZml0dHBqaHh6eW5iZGJ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDMyNzIxNTgsImV4cCI6MjA1ODg0ODE1OH0.u2FM0VaV_XUGmmtwhdkV2vbtKGXST25VJkJCYH9SXSI';

/**
 * Initialize and export the Supabase client
 */
export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

/**
 * Get a public URL for an image in Supabase Storage
 * 
 * @param path Path to the image in storage
 * @param bucket Storage bucket name
 * @returns Public URL for the image
 */
export const getImageUrl = (path: string, bucket: string): string => {
  return supabase.storage.from(bucket).getPublicUrl(path).data.publicUrl;
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

    // Process retrieved data to add proper image URLs
    const processedConcepts = (data || []).map(concept => {
      // Generate base image URL for the concept
      const base_image_url = getImageUrl(concept.base_image_path, 'concept-images');
      
      // Process variation images if they exist
      let variations = concept.color_variations || [];
      
      if (variations.length > 0) {
        variations = variations.map((variation: ColorVariationData) => {
          // Ensure colors is an array
          const colors = Array.isArray(variation.colors) ? variation.colors : [];
          
          return {
            ...variation,
            // Ensure critical fields have default values
            palette_name: variation.palette_name || 'Color Palette',
            colors: colors.length > 0 ? colors : ['#4F46E5', '#818CF8', '#C7D2FE', '#EEF2FF', '#312E81'],
            image_url: getImageUrl(variation.image_path, 'palette-images')
          };
        });
      }
      
      // Return the processed concept with URLs
      return {
        ...concept,
        base_image_url,
        color_variations: variations
      };
    });

    console.log('Processed concepts with URLs:', processedConcepts);
    return processedConcepts;
  } catch (error) {
    console.error('Exception fetching recent concepts:', error);
    return [];
  }
};

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
    const base_image_url = getImageUrl(data.base_image_path, 'concept-images');
    
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
          image_url: getImageUrl(variation.image_path, 'palette-images')
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