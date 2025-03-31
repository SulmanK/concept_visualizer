/**
 * Common TypeScript interfaces for the Concept Visualizer application.
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
  variations?: Array<{
    name: string;
    colors: string[];
    image_url: string;
    description?: string;
  }>;
  original_image_url?: string | null;
  refinement_prompt?: string | null;
  
  // These are aliases for frontend compatibility
  // They might not be in the API response
  imageUrl?: string;
  colorPalette?: ColorPalette | null;
  generationId?: string;
  createdAt?: string;
  originalImageUrl?: string | null;
}

/**
 * Request model for concept generation
 */
export interface PromptRequest {
  logo_description: string;
  theme_description: string;
}

/**
 * Request model for concept refinement
 */
export interface RefinementRequest {
  original_image_url: string;
  logo_description?: string;
  theme_description?: string;
  refinement_prompt: string;
  preserve_aspects: string[];
}

/**
 * API Error response model
 */
export interface ApiError {
  status: number;
  message: string;
  details?: string;
}

/**
 * Common API response wrapper
 */
export interface ApiResponse<T> {
  data?: T;
  error?: ApiError;
  loading: boolean;
}

/**
 * Type for form submission status
 */
export type FormStatus = 'idle' | 'submitting' | 'success' | 'error'; 