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
}

/**
 * Request model for concept generation
 */
export interface PromptRequest {
  logoDescription: string;
  themeDescription: string;
}

/**
 * Request model for concept refinement
 */
export interface RefinementRequest {
  originalImageUrl: string;
  logoDescription?: string;
  themeDescription?: string;
  refinementPrompt: string;
  preserveAspects: string[];
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