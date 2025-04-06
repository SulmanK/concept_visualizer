/**
 * Concept-related TypeScript interfaces for the Concept Visualizer application.
 */

/**
 * Color palette model containing hex color codes
 */
export interface ColorPalette {
  primary: string;
  secondary: string;
  accent: string;
  background: string;
  text: string;
  additionalColors: string[];
}

/**
 * Color variation for a concept
 */
export interface ColorVariation {
  name: string;
  colors: string[];
  image_url: string;
  image_path?: string;
  description?: string;
}

/**
 * Response model for concept generation and refinement
 */
export interface GenerationResponse {
  // Backend API schema uses snake_case, while frontend uses camelCase
  // We need to support both naming conventions for compatibility
  
  // Primary fields that come from the backend
  prompt_id: string;
  logo_description: string;
  theme_description: string;
  created_at: string;
  image_url: string;
  color_palette: ColorPalette | null;
  generation_id?: string;
  variations?: ColorVariation[];
  original_image_url?: string | null;
  refinement_prompt?: string | null;
  id?: string; // ID of the saved concept in the database
  
  // These are aliases for frontend compatibility
  // They might not be in the API response
  imageUrl?: string;
  colorPalette?: ColorPalette | null;
  generationId?: string;
  createdAt?: string;
  originalImageUrl?: string | null;
}

/**
 * Stored concept data structure for recent concepts
 */
export interface StoredConcept {
  id: string;
  title?: string;
  logo_description: string;
  theme_description: string;
  image_url: string;
  image_path?: string;
  created_at: string;
  color_variations?: ColorVariation[];
} 