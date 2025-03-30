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
  imageUrl: string;
  colorPalette: ColorPalette;
  generationId: string;
  createdAt: string;
  originalImageUrl?: string;
  refinementPrompt?: string;
  variations?: Array<{
    name: string;
    colors: string[];
    image_url: string;
    description?: string;
  }>;
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