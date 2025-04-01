/**
 * API-related TypeScript interfaces for the Concept Visualizer application.
 */

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